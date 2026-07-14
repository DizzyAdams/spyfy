"""
SpyFy — Offer Discovery & Metrics Service
=========================================
Camada que transforma o backend em "produto": expõe as **melhores /
mais escaladas** ofertas das Ad Libraries (Meta / Google / TikTok reais
quando há token; fallback estruturado determinístico) já enriquecidas
com **escala, ROI e win-probability** (via `roi` + `radar`), e agrega
**métricas de mercado** para o dashboard.

Projeto para ser 100% offline-safe: nunca quebra por falta de rede/API
key — se a biblioteca real falhar, cai no gerador estruturado e ainda
assim devolve ofertas ranqueadas e com ROI estimado.
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from .radar import RadarOffer, win_probability
from .roi import AdSignals, NicheEconomics, estimate_offer
from .scraper_bridge import GRADIENTS, mine

# Redes suportadas para busca real/fallback.
NETWORKS = ["meta", "tiktok", "google", "youtube", "native", "pinterest"]

# Mapa rótulo de nicho (PT, usado no front) -> chave do scraper.
NICHE_KEY = {
    "emagrecimento": "keto",
    "finanças": "finance",
    "beleza / nutra": "beauty",
    "beleza": "beauty",
    "nutra": "beauty",
    "relacionamento": "finance",
    "marketing / saas": "finance",
    "investimentos": "finance",
    "keto": "keto",
    "finance": "finance",
    "beauty": "beauty",
}


def _niche_key(label: str | None) -> str:
    if not label:
        return "finance"
    return NICHE_KEY.get(label.strip().lower(), "finance")


def _enrich(o: dict[str, Any]) -> dict[str, Any]:
    """Anexa escala/ROI/win-prob a uma oferta minerada."""
    now = datetime.now(timezone.utc)
    long = int(o.get("longevityDays") or 0)
    first = now - timedelta(days=long)
    impr = int(o.get("estImpressions") or 0)
    variants = max(1, len(o.get("funnel") or []))

    sig = AdSignals(
        first_seen=first,
        last_seen=now,
        creative_variants=variants,
        est_impressions_low=int(impr * 0.8),
        est_impressions_high=int(impr * 1.2),
        engagement=int(o.get("engagement") or 0),
        networks=1,
        countries=1,
    )
    est = estimate_offer(sig, NicheEconomics())

    radar = RadarOffer(
        offer_id=o.get("id") or "x",
        niche=o.get("niche") or "Geral",
        network=o.get("network") or "meta",
        country=o.get("country") or "BR",
        winning_score=est.winning_score,
        longevity_days=long,
        creative_variants=variants,
        scaling_signal=est.scaling_signal,
        first_seen_rank=0.5,
    )
    win = win_probability(radar)

    out = dict(o)
    out.update(
        {
            "winningScore": est.winning_score,
            "scalingSignal": est.scaling_signal,
            "estRoas": est.est_roas,
            "estRoiPct": est.est_roi_pct,
            "estDailySpend": est.est_daily_spend,
            "estDailyRevenue": est.est_daily_revenue,
            "estDailyProfit": est.est_daily_profit,
            "estDailyImpressions": est.est_daily_impressions,
            "winProb": win,
            "confidence": est.confidence,
            "scaleIndex": round(
                0.5 * est.winning_score
                + 0.3 * min(100, math.log10(impr + 1) * 12)
                + 0.2 * min(100, long * 1.2),
                1,
            ),
            "spendPerDay": round(est.est_daily_spend, 2),
            "source": o.get("source", "library"),
        }
    )
    # Campos obrigatórios do modelo Offer do front (fallbacks seguros).
    out.setdefault("thumbnailHue", int(abs(hash(o.get("id", ""))) % 360))
    out.setdefault("gradient", list(GRADIENTS[0]))
    out.setdefault("image", "")
    out.setdefault("thumb", "")
    out.setdefault("bullets", ["Ângulo extraído", "Funil detectado"])
    out.setdefault("cta", "Ver oferta")
    # `link` é o DESTINO REAL da oferta. Se ausente, derivamos do snapshot/Meta
    # snapshot para nunca ficar vazio (o frontend abre em nova aba).
    if not out.get("link"):
        out["link"] = o.get("snapshotUrl") or o.get("pageUrl") or ""
    out.setdefault("transcript", [])
    return out

def discover_offers(
    *,
    niche: str | None = None,
    network: str | None = None,
    country: str = "BR",
    limit: int = 24,
    simulate: bool = True,
    token: str = "",
) -> list[dict[str, Any]]:
    """Busca e ranqueia as melhores ofertas das Ad Libraries.

    Ordem (tudo offline-safe, nada quebra):
      1. Anúncios nativos REAIS já coletados (real_ads_store) — fonte primária.
      2. Scrapers reais (Meta/TikTok/Google) quando há token/sessão.
      3. Gerador estruturado (mídia+KPIs reais) — fallback 100% funcional.
    """
    # 1) Anúncios nativos REAIS coletados (cookie logado / dump de anúncios).
    try:
        from .real_ads_store import query as query_real
        real = query_real(niche=niche, network=network, country=country, limit=limit)
    except Exception:  # noqa: BLE001
        real = []

    key = _niche_key(niche)
    if network and network != "all" and network in NETWORKS:
        nets = [network]
    else:
        nets = NETWORKS
    per = max(2, (limit // len(nets)) + 2)

    raw: list[dict[str, Any]] = []
    # Real ads first (they win the ranking tiebreak via source weight).
    for j, m in enumerate(real):
        m = dict(m)
        m["id"] = f"real_{m.get('network','meta')}_{key}_{j}"
        m["source"] = "real_native"
        raw.append(m)

    # 2+3) scrapers reais + gerador estruturado.
    for net in nets:
        try:
            mined = mine(key, net, count=per, simulate=simulate, token=token, country=country)
        except Exception:  # noqa: BLE001 - fallback explícito
            mined = []
        for j, m in enumerate(mined):
            m["id"] = f"ofr_{net}_{key}_{j}"
            m.setdefault("source", "library")
            raw.append(m)

    enriched = [_enrich(o) for o in raw]
    # Real native ads float to the top when scores tie (source weight).
    enriched.sort(key=lambda x: (x.get("source") == "real_native", x["winningScore"]),
                  reverse=True)
    return enriched[:limit]


def get_offer_by_id(
    offer_id: str, *, simulate: bool = True, token: str = "", country: str = "BR"
) -> dict[str, Any] | None:
    """Recupera uma oferta específica por ID (determinístico).

    Os IDs têm o formato ``ofr_{network}_{niche_key}_{i}``; re-mineramos
    a rede/nicho e devolvemos o i-ésimo item enriquecido. Permite que
    a página de detalhe do front recupere a mesma oferta clicada no feed.
    """
    parts = offer_id.split("_")
    if len(parts) < 4 or parts[0] != "ofr":
        return None
    _, net, key, *rest = parts
    if net not in NETWORKS:
        return None
    try:
        idx = int(rest[-1])
    except (ValueError, IndexError):
        return None
    try:
        mined = mine(key, net, count=max(idx + 1, 1), simulate=simulate, token=token, country=country)
    except Exception:  # noqa: BLE001 - fallback explícito
        mined = []
    if idx < len(mined):
        o = dict(mined[idx])
        o["id"] = offer_id
        o.setdefault("source", "library")
        return _enrich(o)
    return None


def compute_metrics(offers: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrega métricas de mercado a partir de um conjunto de ofertas."""
    total = len(offers)
    by_network = dict(Counter(o.get("network", "meta") for o in offers))
    by_niche = dict(Counter(o.get("niche", "Geral") for o in offers))
    by_signal = dict(Counter(o.get("scalingSignal", "cold") for o in offers))

    def _avg(xs: list[float]) -> float:
        return round(sum(xs) / len(xs), 2) if xs else 0.0

    scores = [float(o.get("winningScore", 0)) for o in offers]
    longevity = [float(o.get("longevityDays", 0)) for o in offers]
    roi = [float(o.get("estRoiPct", 0)) for o in offers]
    profit = [float(o.get("estDailyProfit", 0)) for o in offers]
    winprob = [float(o.get("winProb", 0)) for o in offers]

    top = sorted(offers, key=lambda o: float(o.get("winningScore", 0)), reverse=True)[:6]
    top_scaled = [
        {
            "id": o.get("id"),
            "headline": o.get("headline"),
            "advertiser": o.get("advertiser"),
            "network": o.get("network"),
            "niche": o.get("niche"),
            "winningScore": o.get("winningScore"),
            "scalingSignal": o.get("scalingSignal"),
            "estRoiPct": o.get("estRoiPct"),
            "winProb": o.get("winProb"),
            "estImpressions": o.get("estImpressions"),
        }
        for o in top
    ]

    return {
        "total": total,
        "byNetwork": by_network,
        "byNiche": by_niche,
        "bySignal": by_signal,
        "avgWinningScore": _avg(scores),
        "avgLongevityDays": _avg(longevity),
        "avgRoiPct": _avg(roi),
        "avgDailyProfit": _avg(profit),
        "avgWinProb": _avg(winprob),
        "scalingShare": round(
            (by_signal.get("scaling", 0) + by_signal.get("hot", 0)) / total, 3
        )
        if total
        else 0.0,
        "topScaled": top_scaled,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
