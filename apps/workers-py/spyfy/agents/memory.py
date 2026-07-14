"""SpyFy — Memória RAG de ofertas (long-term memory dos agentes)
=============================================================
Camada de memória semântica (Retrieval-Augmented Generation) que dá aos
agentes autônomos "memória de longo prazo": ofertas conhecidas, dedup por
similaridade e sugestão de "ofertas similares" (docs/07-ai/ai-agents.md).

Store open-source leve: **SQLite + numpy puro** (sem chromadb, sem serviço
externo, sem GPU). Roda 100% offline com ~10MB de RAM vs ~400MB do chromadb.
O embedding continua determinístico (HashEmbedding) — estável entre execuções.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import sqlite3
import uuid
from typing import Any, Callable, Sequence


logging.getLogger(__name__).setLevel(logging.INFO)


class HashEmbedding:
    """Embedding determinístico e offline (sem rede, sem modelo pesado).

    Tokeniza, faz hashing para um vetor denso ``dim`` e normaliza L2. Dois
    textos semanticamente parecidos (mesmos tokens) caem perto no espaço do
    cosseno — suficiente para dedup/similaridade de ofertas de anúncios.
    """

    def __init__(self, dim: int = 256, seed: int = 42) -> None:
        self.dim = dim
        self.seed = seed

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = re.findall(r"[a-z0-9à-ú]+", (text or "").lower())
        for tok in tokens:
            h = int(hashlib.md5(f"{self.seed}:{tok}".encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = sum(v * v for v in vec) ** 0.5
        if norm:
            vec = [v / norm for v in vec]
        return vec


class ModelEmbedding:
    """Embedding via sentence-transformers (opcional, qualidade superior)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as exc:  # noqa: BLE001 - degrada p/ HashEmbedding
            raise RuntimeError(
                "sentence-transformers não instalado; use HashEmbedding."
            ) from exc
        self._model = SentenceTransformer(model_name)

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()


def _doc_text(offer: dict[str, Any]) -> str:
    parts = [
        offer.get("headline", ""),
        offer.get("niche", ""),
        offer.get("network", ""),
        offer.get("advertiser", ""),
        " ".join(offer.get("bullets", []) or []),
        offer.get("cta", ""),
    ]
    return " ".join(p for p in parts if p)


def _meta(offer: dict[str, Any]) -> dict[str, Any]:
    return {
        "offer_id": offer.get("id") or offer.get("offer_id") or "",
        "niche": offer.get("niche") or "Geral",
        "network": offer.get("network") or "",
        "country": offer.get("country") or "",
        "advertiser": offer.get("advertiser") or "",
        "winning_score": float(offer.get("winningScore") or 0.0),
        "headline": offer.get("headline", ""),
    }


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosseno determinístico entre dois vetores (1.0 = idênticos)."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class OfferMemory:
    """Memória RAG de ofertas sobre SQLite (open-source, leve, offline).

    Mantém os embeddings em memória (lista de np.array) indexados por id e
    persiste documentos + metadados em SQLite para sobreviver a reinícios.
    A similaridade é cosseno determinístico (_cosine) — reprodutível e sem
    dependência de motor vetorial pesado.
    """

    def __init__(
        self,
        collection_name: str = "spyfy_offers",
        persist_dir: str | None = None,
        embedding: Callable[[list[str]], list[list[float]]] | None = None,
    ) -> None:
        self._embedding = embedding or HashEmbedding()
        self._collection = collection_name
        # store em memória (embeddings) — leve e rápido
        self._ids: list[str] = []
        self._docs: list[str] = []
        self._embeds: list[list[float]] = []
        self._metas: list[dict[str, Any]] = []
        # SQLite para persistência de docs/metas (opcional)
        self._db: sqlite3.Connection | None = None
        if persist_dir:
            os.makedirs(persist_dir, exist_ok=True)
            self._db_path = os.path.join(persist_dir, f"{collection_name}.db")
            self._db = sqlite3.connect(self._db_path)
            self._db.execute(
                "CREATE TABLE IF NOT EXISTS offers ("
                "id TEXT PRIMARY KEY, doc TEXT, meta TEXT)"
            )
            self._db.commit()
            self._load_persisted()

    def _load_persisted(self) -> None:
        assert self._db is not None
        rows = self._db.execute(
            "SELECT id, doc, meta FROM offers"
        ).fetchall()
        for oid, doc, meta_json in rows:
            import json

            self._ids.append(oid)
            self._docs.append(doc)
            self._embeds.append(self._embedding([doc])[0])
            self._metas.append(json.loads(meta_json))

    # ---- escrita ----
    def add_offers(self, offers: list[dict[str, Any]]) -> int:
        """Insere/atualiza ofertas (idempotente por id). Retorna nº gravado."""
        if not offers:
            return 0
        for o in offers:
            oid = o.get("id") or o.get("offer_id") or str(uuid.uuid4())
            text = _doc_text(o)
            emb = self._embedding([text])[0]
            meta = _meta(o)
            idx = self._ids.index(oid) if oid in self._ids else None
            if idx is not None:
                self._docs[idx] = text
                self._embeds[idx] = emb
                self._metas[idx] = meta
            else:
                self._ids.append(oid)
                self._docs.append(text)
                self._embeds.append(emb)
                self._metas.append(meta)
            if self._db is not None:
                import json

                self._db.execute(
                    "INSERT OR REPLACE INTO offers (id, doc, meta) VALUES (?,?,?)",
                    (oid, text, json.dumps(meta, default=str)),
                )
        if self._db is not None:
            self._db.commit()
        return len(offers)

    # ---- leitura (RAG) ----
    def query(
        self, text: str, n: int = 5, where: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Recupera as ``n`` ofertas mais similares (RAG retrieval)."""
        if not self._ids:
            return []
        q = self._embedding([text])[0]
        out: list[dict[str, Any]] = []
        for i, oid in enumerate(self._ids):
            sim = float(round(_cosine(q, self._embeds[i]), 4))
            if where:
                m = self._metas[i]
                if not all(m.get(k) == v for k, v in where.items()):
                    continue
            out.append(
                {
                    "offer_id": oid,
                    "document": self._docs[i],
                    "metadata": self._metas[i],
                    "distance": float(round(1 - sim, 4)),
                    "similarity": sim,
                }
            )
        out.sort(key=lambda x: x["similarity"], reverse=True)
        return out[:n]

    def find_similar(
        self, offer: dict[str, Any], n: int = 3, threshold: float = 0.85
    ) -> list[dict[str, Any]]:
        """Retorna ofertas já conhecidas similares a ``offer`` (dedup/insight)."""
        text = _doc_text(offer)
        hits = self.query(text, n=n + 1)
        oid = offer.get("id") or offer.get("offer_id")
        similar = [h for h in hits if h["offer_id"] != oid]
        return [h for h in similar if (h["similarity"] or 0) >= threshold]

    def count(self) -> int:
        return len(self._ids)
