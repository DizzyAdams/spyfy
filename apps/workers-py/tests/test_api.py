"""Testes da SpyFy API (FastAPI TestClient)."""
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from spyfy.api import create_app
from spyfy.notifiers import NotificationDispatcher
from spyfy.webhooks import sign_payload

NOW = datetime.now(timezone.utc)


class _FakeNotifier:
    name = "fake"
    def send(self, channel, recipient, notif):
        return True


@pytest.fixture
def client():
    fake = _FakeNotifier()
    dispatcher = NotificationDispatcher(
        {"novu": fake, "apprise": fake, "ntfy": fake, "native": fake})
    return TestClient(create_app(dispatcher=dispatcher))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_version(client):
    r = client.get("/v1/version")
    assert r.status_code == 200
    assert "version" in r.json()


def test_event_types(client):
    r = client.get("/v1/events/types")
    assert r.status_code == 200
    assert "offer.scaling" in r.json()["types"]


def test_estimate_winner(client):
    body = {
        "first_seen": (NOW - timedelta(days=63)).isoformat(),
        "last_seen": NOW.isoformat(),
        "creative_variants": 9,
        "est_impressions_low": 1_000_000,
        "est_impressions_high": 5_000_000,
        "engagement": 8200, "networks": 2, "countries": 3,
        "avg_ticket": 57, "cvr": 0.025, "ctr": 0.014, "cpm": 14,
    }
    r = client.post("/v1/offers/estimate", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["longevity_days"] == 63
    assert data["winning_score"] > 70
    assert data["scaling_signal"] == "hot"


def test_estimate_invalid_date(client):
    r = client.post("/v1/offers/estimate",
                    json={"first_seen": "not-a-date", "last_seen": "x"})
    assert r.status_code == 422


def test_notify_pro(client):
    r = client.post("/v1/notify", json={
        "event_id": "evt_1", "type": "offer.scaling", "plan": "pro",
        "user_id": "u1", "email": "u@x.com", "hour_local": 14,
        "data": {"title": "Escalando", "body": "Keto BR", "priority": "high"},
    })
    assert r.status_code == 200
    assert r.json()["suppressed"] is False


def test_notify_free_limited(client):
    r = client.post("/v1/notify", json={
        "event_id": "evt_2", "type": "offer.scaling", "plan": "free",
        "user_id": "u2", "email": "u@x.com", "hour_local": 14,
        "data": {"title": "t", "body": "b"},
    })
    assert set(r.json()["delivered"]) <= {"in_app", "email"}


def test_webhook_valid_signature(client):
    body = json.dumps({"event_id": "wh_1", "type": "order.paid",
                       "data": {"amount": 96}})
    sig, ts = sign_payload(body, "dev")
    r = client.post("/v1/webhooks/darkfy", content=body,
                    headers={"X-SpyFy-Signature": sig, "X-SpyFy-Timestamp": ts,
                             "Content-Type": "application/json"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_webhook_invalid_signature(client):
    body = json.dumps({"event_id": "wh_2", "type": "order.paid", "data": {}})
    r = client.post("/v1/webhooks/darkfy", content=body,
                    headers={"X-SpyFy-Signature": "sha256=bad",
                             "X-SpyFy-Timestamp": "0"})
    assert r.status_code == 401


def test_webhook_dedup(client):
    body = json.dumps({"event_id": "wh_dup", "type": "order.paid", "data": {}})
    sig, ts = sign_payload(body, "dev")
    h = {"X-SpyFy-Signature": sig, "X-SpyFy-Timestamp": ts,
         "Content-Type": "application/json"}
    r1 = client.post("/v1/webhooks/darkfy", content=body, headers=h)
    r2 = client.post("/v1/webhooks/darkfy", content=body, headers=h)
    assert r1.json()["dedup"] is False
    assert r2.json()["dedup"] is True
