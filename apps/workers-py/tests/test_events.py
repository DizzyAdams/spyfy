"""Testes do Event Bus."""
from spyfy.events import DomainEvent, EventBus, DeadLetter


def test_wildcard_subscription():
    bus = EventBus()
    hits = []
    bus.subscribe("offer.*", lambda e: hits.append(e.type))
    bus.publish(DomainEvent("1", "offer.scaling"))
    bus.publish(DomainEvent("2", "offer.discovered"))
    bus.publish(DomainEvent("3", "order.paid"))
    assert hits == ["offer.scaling", "offer.discovered"]


def test_exact_subscription():
    bus = EventBus()
    hits = []
    bus.subscribe("order.paid", lambda e: hits.append(e.data))
    bus.publish(DomainEvent("1", "order.paid", {"amount": 10}))
    assert hits == [{"amount": 10}]


def test_dedup_by_event_id():
    bus = EventBus()
    hits = []
    bus.subscribe("*", lambda e: hits.append(e.event_id))
    bus.publish(DomainEvent("dup", "offer.scaling"))
    bus.publish(DomainEvent("dup", "offer.scaling"))
    assert hits == ["dup"]
    assert bus.published == 1


def test_middleware_runs():
    bus = EventBus()
    seen = []
    bus.use(lambda e: seen.append(e.type))
    bus.subscribe("*", lambda e: None)
    bus.publish(DomainEvent("1", "clone.completed"))
    assert seen == ["clone.completed"]


def test_failing_handler_goes_to_dead_letter():
    bus = EventBus()
    def boom(e): raise ValueError("boom")
    bus.subscribe("*", boom)
    bus.publish(DomainEvent("1", "order.paid"))
    assert len(bus.dead_letters) == 1
    assert isinstance(bus.dead_letters[0], DeadLetter)


def test_replay_dead_letters():
    bus = EventBus()
    state = {"fail": True}
    def flaky(e):
        if state["fail"]:
            raise RuntimeError("later")
    bus.subscribe("*", flaky)
    bus.publish(DomainEvent("1", "order.paid"))
    assert len(bus.dead_letters) == 1
    state["fail"] = False
    ok = bus.replay_dead_letters()
    assert ok == 1 and bus.dead_letters == []


def test_delivered_count():
    bus = EventBus()
    bus.subscribe("offer.*", lambda e: None)
    bus.subscribe("*", lambda e: None)
    assert bus.publish(DomainEvent("1", "offer.scaling")) == 2
