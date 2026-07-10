"""Testes do Notification Engine (entitlements por plano, quiet hours, limites)."""
from spyfy.notifications import (Channel, Notification, NotificationPrefs,
                                 Priority, resolve_channels, PLAN_CHANNELS)

PREFS = NotificationPrefs(
    enabled_channels={Channel.IN_APP, Channel.EMAIL, Channel.SLACK,
                      Channel.TELEGRAM, Channel.PUSH},
    quiet_hours=(22, 7),
)
NOTIF = Notification("evt_1", "offer.scaling", "t", "b", Priority.HIGH)


def test_free_plan_limited_channels():
    d = resolve_channels("free", PREFS, NOTIF, 14, 0)
    assert set(d.channels) == {Channel.IN_APP, Channel.EMAIL}


def test_pro_plan_more_channels():
    d = resolve_channels("pro", PREFS, NOTIF, 14, 0)
    assert Channel.SLACK in d.channels and Channel.TELEGRAM in d.channels


def test_quiet_hours_falls_back_to_inapp():
    d = resolve_channels("pro", PREFS, NOTIF, 23, 0)
    assert d.channels == [Channel.IN_APP]
    assert d.reason == "quiet_hours_inapp_only"


def test_urgent_bypasses_quiet_hours():
    urgent = Notification("e2", "billing.failed", "t", "b", Priority.URGENT)
    d = resolve_channels("pro", PREFS, urgent, 23, 0)
    assert not d.suppressed
    assert Channel.PUSH in d.channels


def test_daily_limit_suppresses():
    d = resolve_channels("pro", PREFS, NOTIF, 14, 2000)
    assert d.suppressed and d.reason == "daily_limit_reached"


def test_urgent_bypasses_daily_limit():
    urgent = Notification("e3", "billing.failed", "t", "b", Priority.URGENT)
    d = resolve_channels("pro", PREFS, urgent, 14, 999999)
    assert not d.suppressed


def test_dedup_suppresses():
    d = resolve_channels("pro", PREFS, NOTIF, 14, 0, seen_event=True)
    assert d.suppressed and d.reason == "duplicate_event"


def test_muted_type_suppressed():
    prefs = NotificationPrefs(enabled_channels={Channel.EMAIL},
                              muted_types={"offer.scaling"})
    d = resolve_channels("pro", prefs, NOTIF, 14, 0)
    assert d.suppressed and d.reason == "muted_type"


def test_channel_intersection_plan_and_prefs():
    # usuário quer whatsapp mas plano pro nao tem -> nao entra
    prefs = NotificationPrefs(enabled_channels={Channel.WHATSAPP, Channel.EMAIL})
    d = resolve_channels("pro", prefs, NOTIF, 14, 0)
    assert Channel.WHATSAPP not in d.channels
    assert Channel.EMAIL in d.channels


def test_enterprise_has_all_channels():
    assert PLAN_CHANNELS["enterprise"] == set(Channel)


def test_channels_sorted_by_intrusiveness():
    d = resolve_channels("pro", PREFS, NOTIF, 14, 0)
    assert d.channels[0] == Channel.IN_APP
