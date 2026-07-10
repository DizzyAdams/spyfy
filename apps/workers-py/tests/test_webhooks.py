"""Testes de segurança de webhook (HMAC + anti-replay)."""
import json
import time

import pytest

from spyfy.webhooks import (DedupStore, parse_event, sign_payload,
                            verify_webhook)

SECRET = "whsec_test_abc"
BODY = json.dumps({"event_id": "evt_1", "type": "order.paid",
                   "data": {"amount": 96.0}})


def test_valid_signature():
    header, ts = sign_payload(BODY, SECRET)
    assert verify_webhook(BODY, header, ts, SECRET) is True


def test_tampered_body_fails():
    header, ts = sign_payload(BODY, SECRET)
    assert verify_webhook(BODY + "tampered", header, ts, SECRET) is False


def test_wrong_secret_fails():
    header, ts = sign_payload(BODY, SECRET)
    assert verify_webhook(BODY, header, ts, "whsec_wrong") is False


def test_replay_old_timestamp_fails():
    header, _ = sign_payload(BODY, SECRET, timestamp=int(time.time()) - 10_000)
    old_ts = str(int(time.time()) - 10_000)
    assert verify_webhook(BODY, header, old_ts, SECRET) is False


def test_invalid_timestamp_fails():
    header, _ = sign_payload(BODY, SECRET)
    assert verify_webhook(BODY, header, "not-a-number", SECRET) is False


def test_missing_prefix_still_validates():
    header, ts = sign_payload(BODY, SECRET)
    assert verify_webhook(BODY, header.removeprefix("sha256="), ts, SECRET) is True


def test_parse_event_requires_fields():
    assert parse_event(BODY)["type"] == "order.paid"
    with pytest.raises(ValueError):
        parse_event(json.dumps({"type": "x"}))


def test_dedup_store():
    store = DedupStore()
    assert store.seen("evt_1") is False
    assert store.seen("evt_1") is True
