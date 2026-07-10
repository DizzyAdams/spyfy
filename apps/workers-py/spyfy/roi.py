"""
SpyFy — Scale & ROI Engine
==========================
Estima escala (volume/investimento), ROI e "winning score" de ofertas de ads
a partir de sinais públicos: longevidade, nº de criativos ativos, engajamento,
faixas de impressões (Ad Library) e economia de checkout do nicho.

Todas as saídas de dinheiro/volume são ESTIMATIVAS (rotuladas), nunca fatos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import log10, tanh


@dataclass
class AdSignals:
    """Sinais observados de uma oferta/anúncio (dados públicos)."""
    first_seen: datetime
    last_seen: datetime
    creative_variants: int = 1
    est_impressions_low: int = 0
    est_impressions_high: int = 0
    engagement: int = 0
    networks: int = 1
    countries: int = 1


@dataclass
class NicheEconomics:
    """Economia típica do nicho (calibrável por dados históricos)."""
    avg_ticket: float = 47.0
    cvr: float = 0.02
    ctr: float = 0.012
    cpm: float = 12.0
    upsell_take: float = 0.35
    upsell_ticket: float = 30.0
    refund_rate: float = 0.08


@dataclass
class ScoreWeights:
    longevity: float = 1.0
    volume: float = 2.0
    variants: float = 0.6
    engagement: float = 0.8
    spread: float = 0.5


@dataclass
class OfferEstimate:
    longevity_days: int
    est_impressions: int
    est_daily_impressions: float
    est_daily_spend: float
    est_daily_clicks: float
    est_daily_sales: float
    est_daily_revenue: float
    est_daily_profit: float
    est_roas: float
    est_roi_pct: float
    winning_score: float
    scaling_signal: str
    confidence: float
    notes: list[str] = field(default_factory=list)


def _longevity_days(sig: AdSignals) -> int:
    return max(0, (sig.last_seen - sig.first_seen).days)


def _est_impressions(sig: AdSignals) -> int:
    if sig.est_impressions_high > 0:
        lo = max(1, sig.est_impressions_low)
        hi = max(lo, sig.est_impressions_high)
        return int((lo * hi) ** 0.5)          # média geométrica da faixa
    days = max(1, _longevity_days(sig))
    return int(days * sig.creative_variants * 5000)


def _norm(value: float, scale: float) -> float:
    if value <= 0:
        return 0.0
    return tanh(value / scale)


def _scaling_signal(days: int, variants: int, daily_impr: float) -> str:
    heat = 0
    if days >= 7:
        heat += 1
    if days >= 30:
        heat += 1
    if variants >= 5:
        heat += 1
    if daily_impr >= 50_000:
        heat += 1
    return ["cold", "warming", "scaling", "hot", "hot"][min(heat, 4)]


def estimate_offer(
    sig: AdSignals,
    econ: NicheEconomics | None = None,
    weights: ScoreWeights | None = None,
) -> OfferEstimate:
    econ = econ or NicheEconomics()
    weights = weights or ScoreWeights()
    notes: list[str] = []

    days = _longevity_days(sig)
    impressions = _est_impressions(sig)
    daily_impr = impressions / max(1, days)

    daily_spend = daily_impr / 1000.0 * econ.cpm
    daily_clicks = daily_impr * econ.ctr
    daily_sales = daily_clicks * econ.cvr

    front_rev = daily_sales * econ.avg_ticket
    upsell_rev = daily_sales * econ.upsell_take * econ.upsell_ticket
    gross_rev = (front_rev + upsell_rev) * (1 - econ.refund_rate)

    daily_profit = gross_rev - daily_spend
    roas = (gross_rev / daily_spend) if daily_spend > 0 else 0.0
    roi_pct = ((daily_profit / daily_spend) * 100) if daily_spend > 0 else 0.0

    score = (
        weights.longevity * _norm(days, 45)
        + weights.volume * _norm(log10(impressions + 1), 6)
        + weights.variants * _norm(sig.creative_variants, 8)
        + weights.engagement * _norm(sig.engagement, 5000)
        + weights.spread * _norm(sig.networks * sig.countries, 6)
    )
    total_w = (weights.longevity + weights.volume + weights.variants
               + weights.engagement + weights.spread)
    winning_score = round(100 * score / total_w, 1)

    scaling_signal = _scaling_signal(days, sig.creative_variants, daily_impr)

    confidence = 0.4
    if sig.est_impressions_high > 0:
        confidence += 0.35
    else:
        notes.append("Impressoes estimadas por proxy (sem faixa da Ad Library).")
    if sig.engagement > 0:
        confidence += 0.15
    if days >= 14:
        confidence += 0.10
    confidence = round(min(confidence, 0.95), 2)

    if roi_pct > 0 and days >= 21:
        notes.append("Longevidade alta + ROI positivo -> provavel vencedora.")

    return OfferEstimate(
        longevity_days=days,
        est_impressions=impressions,
        est_daily_impressions=round(daily_impr, 1),
        est_daily_spend=round(daily_spend, 2),
        est_daily_clicks=round(daily_clicks, 1),
        est_daily_sales=round(daily_sales, 2),
        est_daily_revenue=round(gross_rev, 2),
        est_daily_profit=round(daily_profit, 2),
        est_roas=round(roas, 2),
        est_roi_pct=round(roi_pct, 1),
        winning_score=winning_score,
        scaling_signal=scaling_signal,
        confidence=confidence,
        notes=notes,
    )


def rank_offers(offers: list[tuple[str, AdSignals]],
                econ: NicheEconomics | None = None) -> list[dict]:
    rows = []
    for offer_id, sig in offers:
        est = estimate_offer(sig, econ)
        rows.append({"offer_id": offer_id, "score": est.winning_score,
                     "roi_pct": est.est_roi_pct, "signal": est.scaling_signal,
                     "daily_profit": est.est_daily_profit})
    return sorted(rows, key=lambda r: r["score"], reverse=True)


if __name__ == "__main__":
    from datetime import timedelta
    now = datetime.now(timezone.utc)

    keto = NicheEconomics(avg_ticket=57, cvr=0.025, ctr=0.014, cpm=14,
                          upsell_take=0.4, upsell_ticket=39, refund_rate=0.09)

    winner = AdSignals(first_seen=now - timedelta(days=63), last_seen=now,
                       creative_variants=9, est_impressions_low=1_000_000,
                       est_impressions_high=5_000_000, engagement=8200,
                       networks=2, countries=3)
    loser = AdSignals(first_seen=now - timedelta(days=3), last_seen=now,
                      creative_variants=1, engagement=40)

    for name, sig in [("WINNER", winner), ("LOSER", loser)]:
        e = estimate_offer(sig, keto)
        print(f"\n=== {name} ===")
        print(f"longevidade: {e.longevity_days}d | score: {e.winning_score} "
              f"| sinal: {e.scaling_signal} | conf: {e.confidence}")
        print(f"impressoes(est): {e.est_impressions:,} "
              f"| gasto/dia: ${e.est_daily_spend:,.0f} "
              f"| receita/dia: ${e.est_daily_revenue:,.0f}")
        print(f"lucro/dia(est): ${e.est_daily_profit:,.0f} "
              f"| ROAS: {e.est_roas} | ROI: {e.est_roi_pct}%")
        for n in e.notes:
            print(f"  - {n}")
