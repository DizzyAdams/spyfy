"""Testes do Scale & ROI Engine."""
from datetime import datetime, timedelta, timezone

from spyfy.roi import (AdSignals, NicheEconomics, estimate_offer, rank_offers)

NOW = datetime.now(timezone.utc)


def _winner():
    return AdSignals(first_seen=NOW - timedelta(days=60), last_seen=NOW,
                     creative_variants=9, est_impressions_low=1_000_000,
                     est_impressions_high=5_000_000, engagement=8000,
                     networks=2, countries=3)


def _loser():
    return AdSignals(first_seen=NOW - timedelta(days=2), last_seen=NOW,
                     creative_variants=1, engagement=10)


def test_winner_scores_higher_than_loser():
    w = estimate_offer(_winner())
    loser_est = estimate_offer(_loser())
    assert w.winning_score > loser_est.winning_score


def test_longevity_calculated():
    assert estimate_offer(_winner()).longevity_days == 60


def test_scaling_signal_levels():
    assert estimate_offer(_winner()).scaling_signal == "hot"
    assert estimate_offer(_loser()).scaling_signal == "cold"


def test_confidence_higher_with_impression_range():
    assert estimate_offer(_winner()).confidence > estimate_offer(_loser()).confidence


def test_geometric_mean_impressions():
    # sqrt(1e6 * 5e6) ~= 2.236e6
    est = estimate_offer(_winner())
    assert 2_000_000 <= est.est_impressions <= 2_500_000


def test_roi_positive_for_profitable_econ():
    econ = NicheEconomics(avg_ticket=57, cvr=0.03, ctr=0.015, cpm=12)
    assert estimate_offer(_winner(), econ).est_roi_pct > 0


def test_rank_orders_by_score():
    ranked = rank_offers([("loser", _loser()), ("winner", _winner())])
    assert ranked[0]["offer_id"] == "winner"


def test_score_bounds():
    s = estimate_offer(_winner()).winning_score
    assert 0 <= s <= 100
