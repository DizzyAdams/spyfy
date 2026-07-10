"""
SpyFy — Webhook security (HMAC + anti-replay)
=============================================
Assinatura e verificação de webhooks das integrações (NexusTracker,
DarkfyCheckout). Assinatura = HMAC_SHA256(secret, "{timestamp}.{body}").
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time


def sign_payload(body: str, secret: str, timestamp: int | None = None) -> tuple[str, str]:
    """Gera (signature_header, timestamp) para um corpo de webhook."""
    ts = str(timestamp if timestamp is not None else int(time.time()))
    mac = hmac.new(secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256)
    return f"sha256={mac.hexdigest()}", ts


def verify_webhook(
    raw_body: str,
    signature_header: str,
    timestamp: str,
    secret: str,
    tolerance_sec: int = 300,
) -> bool:
    """Valida assinatura HMAC + janela anti-replay. Timing-safe."""
    # anti-replay
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    if abs(int(time.time()) - ts) > tolerance_sec:
        return False

    expected = hmac.new(
        secret.encode(), f"{ts}.{raw_body}".encode(), hashlib.sha256
    ).hexdigest()
    provided = (signature_header or "").removeprefix("sha256=")
    # comparação timing-safe
    return hmac.compare_digest(expected, provided)


def parse_event(raw_body: str) -> dict:
    """Faz parse do envelope padrão de evento."""
    event = json.loads(raw_body)
    for field in ("event_id", "type"):
        if field not in event:
            raise ValueError(f"webhook sem campo obrigatorio: {field}")
    return event


class DedupStore:
    """Idempotência simples em memória (em prod: Redis SET + TTL)."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def seen(self, event_id: str) -> bool:
        if event_id in self._seen:
            return True
        self._seen.add(event_id)
        return False


if __name__ == "__main__":
    secret = "whsec_demo_123"
    body = json.dumps({"event_id": "evt_1", "type": "order.paid",
                       "data": {"amount": 96.0}})
    header, ts = sign_payload(body, secret)
    print("assinado:", header, "ts:", ts)
    print("valido?  ", verify_webhook(body, header, ts, secret))
    print("adulterado?", verify_webhook(body + "x", header, ts, secret))
    print("replay?    ", verify_webhook(body, header, str(int(ts) - 999), secret))
