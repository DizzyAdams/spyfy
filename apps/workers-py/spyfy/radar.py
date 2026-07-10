"""
SpyFy — Offer Radar & Win Probability (Loop 5)
==============================================
Moat competitivo: saved-searches que rodam sozinhas, detecção de
"primeiro a ver" (early mover) e probabilidade de a oferta vencer.
Retém porque o usuário confia no radar para não perder nada.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass
class RadarQuery:
    id: str
    user_id: str
    niche: str | None = None
    network: str | None = None
    country: str | None = None
    min_score: float = 0.0
    min_days: int = 0


@dataclass
class RadarOffer:
    offer_id: str
    niche: str
    network: str
    country: str
    winning_score: float
    longevity_days: int
    creative_variants: int
    scaling_signal: str
    first_seen_rank: float = 0.5   # 0=voce viu primeiro, 1=todo mundo ja viu


def matches(q: RadarQuery, o: RadarOffer) -> bool:
    if q.niche and q.niche != o.niche:
        return False
    if q.network and q.network != o.network:
        return False
    if q.country and q.country != o.country:
        return False
    return o.winning_score >= q.min_score and o.longevity_days >= q.min_days


def run_radar(query: RadarQuery, offers: list[RadarOffer]) -> list[RadarOffer]:
    """Executa uma saved-search (roda sozinha em background)."""
    hits = [o for o in offers if matches(query, o)]
    return sorted(hits, key=lambda o: o.winning_score, reverse=True)


def win_probability(o: RadarOffer) -> float:
    """
    Probabilidade (0..1) de a oferta continuar vencedora, via logística
    sobre sinais: longevidade, variantes e sinal de escala.
    """
    signal_w = {"hot": 2.0, "scaling": 1.2, "warming": 0.4, "cold": -0.5}
    z = (
        -1.2
        + 0.05 * min(o.longevity_days, 90)
        + 0.15 * min(o.creative_variants, 12)
        + signal_w.get(o.scaling_signal, 0)
    )
    return round(1 / (1 + exp(-z)), 3)


def early_mover_bonus(o: RadarOffer) -> str:
    """Rótulo de vantagem competitiva por quem vê primeiro."""
    if o.first_seen_rank <= 0.1:
        return "🥇 Você é dos primeiros a ver (vantagem máxima)"
    if o.first_seen_rank <= 0.3:
        return "⚡ Ainda pouco explorada"
    if o.first_seen_rank >= 0.8:
        return "⚠️ Já saturando (muitos viram)"
    return "Em disputa"


def radar_report(query: RadarQuery, offers: list[RadarOffer]) -> dict:
    hits = run_radar(query, offers)
    items = [{
        "offer_id": o.offer_id,
        "win_prob": win_probability(o),
        "edge": early_mover_bonus(o),
        "score": o.winning_score,
    } for o in hits]
    best = items[0] if items else None
    return {"query_id": query.id, "hits": len(items), "top": best, "items": items}


def should_alert(prev_hits: set[str], new_hits: list[RadarOffer]) -> list[str]:
    """Detecta ofertas NOVAS no radar desde a última execução -> alerta."""
    return [o.offer_id for o in new_hits if o.offer_id not in prev_hits]


if __name__ == "__main__":
    q = RadarQuery("q1", "u1", niche="keto", min_score=60, min_days=14)
    offers = [
        RadarOffer("a", "keto", "meta", "BR", 88, 63, 9, "hot", 0.05),
        RadarOffer("b", "keto", "meta", "BR", 72, 20, 4, "scaling", 0.4),
        RadarOffer("c", "finance", "tiktok", "US", 95, 80, 10, "hot", 0.9),
    ]
    import json
    print(json.dumps(radar_report(q, offers), indent=2, ensure_ascii=False))
    print("novas p/ alertar:", should_alert({"b"}, run_radar(q, offers)))
