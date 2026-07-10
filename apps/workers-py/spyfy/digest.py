"""
SpyFy — Smart Digest & Personalized Feed (Loop 4)
=================================================
Ranking personalizado de ofertas por usuário (nicho fav, persona, histórico)
+ montagem de digest (daily/weekly). Aumenta relevância -> retenção.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FeedOffer:
    offer_id: str
    niche: str
    network: str
    winning_score: float
    scaling_signal: str          # cold|warming|scaling|hot
    longevity_days: int
    is_new: bool = False         # apareceu desde o último digest


@dataclass
class UserFeedPrefs:
    fav_niches: list[str] = field(default_factory=list)
    fav_networks: list[str] = field(default_factory=list)
    seen_offer_ids: set[str] = field(default_factory=set)
    min_score: float = 0.0


SIGNAL_BOOST = {"hot": 25, "scaling": 15, "warming": 5, "cold": 0}


def personalized_score(offer: FeedOffer, prefs: UserFeedPrefs) -> float:
    """Score de relevância personalizado (não é só winning_score global)."""
    s = offer.winning_score
    if offer.niche in prefs.fav_niches:
        s += 20
    if offer.network in prefs.fav_networks:
        s += 8
    s += SIGNAL_BOOST.get(offer.scaling_signal, 0)
    if offer.is_new and offer.offer_id not in prefs.seen_offer_ids:
        s += 12                      # novidade prende atenção
    if offer.offer_id in prefs.seen_offer_ids:
        s -= 30                      # evita repetir o que já viu
    return round(s, 1)


def rank_feed(offers: list[FeedOffer], prefs: UserFeedPrefs) -> list[FeedOffer]:
    eligible = [o for o in offers if o.winning_score >= prefs.min_score]
    return sorted(eligible, key=lambda o: personalized_score(o, prefs),
                  reverse=True)


def build_digest(offers: list[FeedOffer], prefs: UserFeedPrefs,
                 limit: int = 5) -> dict:
    """Monta um digest personalizado (o 'Daily Winners' de cada usuário)."""
    ranked = rank_feed(offers, prefs)
    top = ranked[:limit]
    new_count = sum(1 for o in ranked if o.is_new
                    and o.offer_id not in prefs.seen_offer_ids)
    if not top:
        return {"title": "Nada novo por agora", "items": [], "cta": "Ajustar filtros"}
    lead = top[0]
    return {
        "title": f"{new_count} novas ofertas no seu radar",
        "highlight": f"{lead.niche} — score {lead.winning_score} ({lead.scaling_signal})",
        "items": [{"offer_id": o.offer_id, "niche": o.niche,
                   "signal": o.scaling_signal,
                   "rel_score": personalized_score(o, prefs)} for o in top],
        "cta": "Ver e clonar",
    }


def optimal_send_hour(login_hours: list[int]) -> int:
    """Melhor horário de envio: hora de login mais frequente (menos 1h)."""
    if not login_hours:
        return 8
    counts = {h: login_hours.count(h) for h in set(login_hours)}
    peak = max(counts, key=lambda h: counts[h])
    return (peak - 1) % 24


if __name__ == "__main__":
    prefs = UserFeedPrefs(fav_niches=["keto"], fav_networks=["meta"],
                          seen_offer_ids={"old1"})
    offers = [
        FeedOffer("a", "keto", "meta", 70, "hot", 60, is_new=True),
        FeedOffer("b", "finance", "tiktok", 85, "scaling", 40),
        FeedOffer("old1", "keto", "meta", 90, "hot", 90),   # já visto -> penalizado
    ]
    import json
    print(json.dumps(build_digest(offers, prefs), indent=2, ensure_ascii=False))
    print("melhor hora:", optimal_send_hour([9, 9, 9, 20, 14]))
