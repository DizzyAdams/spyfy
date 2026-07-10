"""Testes de integração: EventBus -> NotifyAgent -> Dispatcher (E2E)."""
from spyfy.events import DomainEvent, EventBus
from spyfy.notifications import Channel, NotificationPrefs
from spyfy.notifiers import NotificationDispatcher
from spyfy.agents import NotifyAgent


class FakeNotifier:
    name = "fake"
    def __init__(self): self.sent = []
    def send(self, channel, recipient, notif):
        self.sent.append((channel, recipient["user_id"], notif.type, notif.title))
        return True


def _wire(plan="pro", hour=12, sent_today=0):
    fake = FakeNotifier()
    dispatcher = NotificationDispatcher(
        {"novu": fake, "apprise": fake, "ntfy": fake, "native": fake})
    prefs = NotificationPrefs(enabled_channels={Channel.IN_APP, Channel.EMAIL,
                                                Channel.SLACK, Channel.PUSH})
    recipients = [{"user_id": "u1", "email": "u@x.com", "hour_local": hour,
                   "apprise_urls": {"slack": "slack://T/C"}, "ntfy_topic": "t"}]
    agent = NotifyAgent(
        dispatcher,
        resolve_recipients=lambda e: recipients,
        resolve_context=lambda uid: (plan, prefs, sent_today),
    )
    bus = EventBus()
    agent.register(bus)
    return bus, agent, fake


def test_offer_scaling_notifies():
    bus, agent, fake = _wire()
    bus.publish(DomainEvent("e1", "offer.scaling",
                            {"headline": "Keto BR", "score": 91}))
    assert agent.total_delivered > 0
    types = {s[2] for s in fake.sent}
    assert "offer.scaling" in types


def test_billing_failed_is_urgent_even_in_quiet_hours():
    # 23h com quiet hours (22-7): urgente deve furar
    fake = FakeNotifier()
    dispatcher = NotificationDispatcher({"novu": fake, "ntfy": fake,
                                         "apprise": fake, "native": fake})
    prefs = NotificationPrefs(
        enabled_channels={Channel.IN_APP, Channel.EMAIL, Channel.PUSH},
        quiet_hours=(22, 7))
    agent = NotifyAgent(
        dispatcher,
        resolve_recipients=lambda e: [{"user_id": "u1", "email": "u@x.com",
                                       "hour_local": 23, "ntfy_topic": "t"}],
        resolve_context=lambda uid: ("pro", prefs, 0))
    bus = EventBus()
    agent.register(bus)
    bus.publish(DomainEvent("e2", "billing.failed", {}))
    assert agent.total_delivered > 0


def test_free_plan_limits_channels_e2e():
    bus, agent, fake = _wire(plan="free")
    bus.publish(DomainEvent("e3", "clone.completed", {"clone_id": "cl_1"}))
    channels = {s[0] for s in fake.sent}
    assert channels <= {Channel.IN_APP, Channel.EMAIL}


def test_unmapped_event_ignored():
    bus, agent, fake = _wire()
    bus.publish(DomainEvent("e4", "offer.enriched", {}))  # não mapeado no A13
    assert fake.sent == []


def test_dedup_prevents_double_notify():
    bus, agent, fake = _wire()
    bus.publish(DomainEvent("dup", "order.paid", {"amount": 96}))
    bus.publish(DomainEvent("dup", "order.paid", {"amount": 96}))
    assert len([s for s in fake.sent if s[2] == "order.paid"]) >= 1
    assert bus.published == 1
