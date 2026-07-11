"""
SpyFy — Memória RAG de ofertas (long-term memory dos agentes)
=============================================================
Camada de memória semântica (Retrieval-Augmented Generation) que dá aos
agentes autônomos "memória de longo prazo": ofertas conhecidas, dedup por
similaridade e sugestão de "ofertas similares" (docs/07-ai/ai-agents.md).

Backed by `chromadb`. Por padrão usa um **embedding determinístico** (bag-of-
words com hashing) que roda 100% offline e é estável entre execuções — ideal
para testes e para ambientes sem GPU/rede. Quando `use_models=True` e o
`sentence-transformers` está instalado, usa um modelo real (all-MiniLM-L6-v2).
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
import uuid
from typing import Any, Callable, Sequence

# Desliga telemetria do chromadb (evita chamadas de rede e ruído de log/posthog).
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY_DISABLED", "True")
# chromadb 0.5.0 tem incompatibilidade de assinatura com a lib posthog instalada
# (capture() recebe args a mais) e loga erro em stderr mesmo com telemetria off.
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)


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
    """Memória RAG de ofertas sobre chromadb (Ephemeral em memória ou Persistent)."""

    def __init__(
        self,
        collection_name: str = "spyfy_offers",
        persist_dir: str | None = None,
        embedding: Callable[[list[str]], list[list[float]]] | None = None,
    ) -> None:
        import chromadb

        self._embedding = embedding or HashEmbedding()
        # EphemeralClient do chromadb é um singleton de processo: para não
        # vazar dados entre instâncias (ex.: testes), nomeia a collection de
        # forma única quando é em-memória. Em disco (persist_dir) reaproveita.
        if persist_dir is None and collection_name == "spyfy_offers":
            collection_name = f"spyfy_offers_{uuid.uuid4().hex[:8]}"
        if persist_dir:
            client = chromadb.PersistentClient(
                path=persist_dir,
                settings=chromadb.Settings(anonymized_telemetry=False),
            )
        else:
            client = chromadb.EphemeralClient(
                settings=chromadb.Settings(anonymized_telemetry=False),
            )
        self.collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ---- escrita ----
    def add_offers(self, offers: list[dict[str, Any]]) -> int:
        """Insere/atualiza ofertas (idempotente por id). Retorna nº gravado."""
        if not offers:
            return 0
        ids: list[str] = []
        docs: list[str] = []
        embeds: list[list[float]] = []
        metas: list[dict[str, Any]] = []
        for o in offers:
            oid = o.get("id") or o.get("offer_id") or str(uuid.uuid4())
            text = _doc_text(o)
            ids.append(oid)
            docs.append(text)
            embeds.append(self._embedding([text])[0])
            metas.append(_meta(o))
        self.collection.upsert(
            ids=ids, documents=docs, embeddings=embeds, metadatas=metas  # type: ignore[arg-type]  # stubs do chromadb são invariantes em list[Sequence]
        )
        return len(ids)

    # ---- leitura (RAG) ----
    def query(
        self, text: str, n: int = 5, where: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Recupera as ``n`` ofertas mais similares (RAG retrieval).

        A similaridade é calculada por **cosseno determinístico** sobre os
        embeddings armazenados (``_cosine``), e não pela distância do índice
        HNSW do chromadb — que se mostrou instável para embeddings hash
        pequenos. O chromadb continua sendo o store persistente; a ordenação
        e o score ficam reproduzíveis e offline.
        """
        if self.collection.count() == 0:
            return []
        q = self._embedding([text])[0]
        stored = self.collection.get(
            include=["embeddings", "documents", "metadatas"], where=where
        )
        ids = stored.get("ids", []) or []
        docs = stored.get("documents", []) or []
        metas = stored.get("metadatas", []) or []
        embeds = stored.get("embeddings", []) or []
        out: list[dict[str, Any]] = []
        for i, oid in enumerate(ids):
            emb = embeds[i] if i < len(embeds) else None
            sim = round(_cosine(q, emb), 4) if emb else 0.0
            out.append({
                "offer_id": oid,
                "document": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
                "distance": round(1 - sim, 4),
                "similarity": sim,
            })
        out.sort(key=lambda x: x["similarity"], reverse=True)
        return out[:n]

    def find_similar(self, offer: dict[str, Any], n: int = 3,
                     threshold: float = 0.85) -> list[dict[str, Any]]:
        """Retorna ofertas já conhecidas similares a ``offer`` (dedup/insight)."""
        text = _doc_text(offer)
        hits = self.query(text, n=n + 1)
        oid = offer.get("id") or offer.get("offer_id")
        similar = [h for h in hits if h["offer_id"] != oid]
        return [h for h in similar if (h["similarity"] or 0) >= threshold]

    def count(self) -> int:
        return self.collection.count()

