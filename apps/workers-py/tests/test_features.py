"""Testes dos 5 loops de features (retenção + moat competitivo)."""
from spyfy.personalization import (Persona, UserContext, build_home_tab,
                                   infer_persona)
from spyfy.retention import (UsageSnapshot, ChurnRisk, health_score,
                             should_trigger_winback, expansion_ready)
from spyfy.gamification import (GameState, apply_action, level_for,
                                register_daily_login, progress_to_next_level)
from spyfy.digest import (FeedOffer, UserFeedPrefs, rank_feed, build_digest,
                          personalized_score, optimal_send_hour)
from spyfy.radar import (RadarQuery, RadarOffer, run_radar, win_probability,
                         should_alert, radar_report)


# ---- Loop 1: Personalization ----
def test_home_tab_differs_by_persona():
    mb = build_home_tab(UserContext("u", Persona.MEDIA_BUYER, "pro", onboarded=True))
    cw = build_home_tab(UserContext("u", Persona.COPYWRITER, "pro", onboarded=True))
    assert [w.key for w in mb] != [w.key for w in cw]


def test_onboarding_first_when_not_onboarded():
    tab = build_home_tab(UserContext("u", Persona.AFFILIATE, "free"))
    assert tab[0].key == "onboarding"


def test_free_plan_locks_pro_widgets():
    tab = build_home_tab(UserContext("u", Persona.MEDIA_BUYER, "free", onboarded=True))
    cw = next(w for w in tab if w.key == "competitor_watch")
    assert "🔒" in cw.title


def test_infer_persona():
    assert infer_persona(["clone", "clone", "save"]) == Persona.AFFILIATE
    assert infer_persona(["transcribe"]) == Persona.COPYWRITER


# ---- Loop 2: Retention ----
def test_healthy_vs_critical():
    power = UsageSnapshot(120, 1, 25, 80, 60, 5, plan="pro")
    idle = UsageSnapshot(60, 40, 1, 2, 0, 0, plan="starter")
    assert health_score(power).risk == ChurnRisk.HEALTHY
    assert health_score(idle).risk in (ChurnRisk.CRITICAL, ChurnRisk.CHURNED)


def test_winback_and_expansion():
    idle = UsageSnapshot(60, 40, 1, 2, 0, 0, plan="starter")
    power = UsageSnapshot(120, 1, 25, 80, 60, 5, seats_used=2, plan="pro")
    assert should_trigger_winback(idle) is True
    assert expansion_ready(power) is True


def test_no_clone_lowers_score():
    a = UsageSnapshot(30, 1, 10, 5, 0, 1)
    b = UsageSnapshot(30, 1, 10, 5, 3, 1)
    assert health_score(a).score < health_score(b).score


# ---- Loop 3: Gamification ----
def test_first_clone_bonus_and_badge():
    s = GameState("u")
    ev = apply_action(s, "clone")
    assert ev.xp_gained == 125          # 25 + 100 first_clone
    assert "first_clone" in s.badges


def test_level_up():
    assert level_for(0) == "Explorador"
    assert level_for(600) == "Analista"


def test_streak_and_progress():
    s = GameState("u")
    register_daily_login(s, consecutive=True)
    assert s.streak_days == 1
    p = progress_to_next_level(s.xp)
    assert 0 <= p["pct"] <= 100


# ---- Loop 4: Digest ----
def test_fav_niche_boosts_score():
    prefs = UserFeedPrefs(fav_niches=["keto"])
    fav = FeedOffer("a", "keto", "meta", 50, "warming", 20)
    other = FeedOffer("b", "finance", "meta", 50, "warming", 20)
    assert personalized_score(fav, prefs) > personalized_score(other, prefs)


def test_seen_offer_penalized():
    prefs = UserFeedPrefs(seen_offer_ids={"a"})
    seen = FeedOffer("a", "keto", "meta", 80, "hot", 60)
    fresh = FeedOffer("b", "keto", "meta", 80, "hot", 60, is_new=True)
    ranked = rank_feed([seen, fresh], prefs)
    assert ranked[0].offer_id == "b"


def test_digest_and_send_hour():
    prefs = UserFeedPrefs(fav_niches=["keto"])
    d = build_digest([FeedOffer("a", "keto", "meta", 70, "hot", 60, is_new=True)],
                     prefs)
    assert d["items"]
    assert optimal_send_hour([9, 9, 20]) == 8


# ---- Loop 5: Radar / Win Probability ----
def test_radar_filters_and_ranks():
    q = RadarQuery("q", "u", niche="keto", min_score=60, min_days=14)
    offers = [RadarOffer("a", "keto", "meta", "BR", 88, 63, 9, "hot"),
              RadarOffer("b", "finance", "tiktok", "US", 95, 80, 10, "hot")]
    hits = run_radar(q, offers)
    assert [o.offer_id for o in hits] == ["a"]


def test_win_probability_hot_higher_than_cold():
    hot = RadarOffer("a", "k", "meta", "BR", 88, 63, 9, "hot")
    cold = RadarOffer("b", "k", "meta", "BR", 40, 3, 1, "cold")
    assert win_probability(hot) > win_probability(cold)
    assert 0 <= win_probability(hot) <= 1


def test_radar_alerts_only_new():
    q = RadarQuery("q", "u", niche="keto", min_score=0)
    offers = [RadarOffer("a", "keto", "meta", "BR", 80, 30, 5, "hot"),
              RadarOffer("b", "keto", "meta", "BR", 70, 20, 4, "scaling")]
    new = should_alert({"a"}, run_radar(q, offers))
    assert new == ["b"]


def test_radar_report_structure():
    q = RadarQuery("q", "u", niche="keto", min_score=0)
    rep = radar_report(q, [RadarOffer("a", "keto", "meta", "BR", 88, 63, 9, "hot")])
    assert rep["hits"] == 1 and rep["top"]["offer_id"] == "a"
