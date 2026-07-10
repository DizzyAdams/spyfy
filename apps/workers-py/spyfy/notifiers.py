"""
SpyFy — Notification Delivery Adapters + Dispatcher
==================================================
Adapters concretos para os backends OPEN-SOURCE e um Dispatcher que:
  1. roteia via resolve_channels (plano/prefs/quiet-hours/limite/dedup)
  2. entrega por cada canal usando o adapter certo
  3. aplica retry e coleta resultados por canal
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .notifications import (Channel, Notification, NotificationPrefs,
                            RouteDecision, resolve_channels, CHANNEL_BACKEND)


class Notifier(Protocol):
    name: str
    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool:
        ...


@dataclass
class DeliveryResult:
    channel: Channel
    ok: bool
    backend: str
    attempts: int
    error: str = ""


@dataclass
class DispatchReport:
    route: RouteDecision
    deliveries: list[DeliveryResult] = field(default_factory=list)

    @property
    def delivered(self) -> list[Channel]:
        return [d.channel for d in self.deliveries if d.ok]

    @property
    def failed(self) -> list[Channel]:
        return [d.channel for d in self.deliveries if not d.ok]

    @property
    def all_ok(self) -> bool:
        return bool(self.deliveries) and all(d.ok for d in self.deliveries)
@dataclass
class NovuAdapter:
    """Novu: in-app inbox + email (workflows self-host)."""
    name: str = "novu"
    base_url: str = "http://novu-api:3000"
    api_key: str = ""
    _client: object | None = None

    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool:
        payload = {
            "name": _workflow_for(notif.type),
            "to": {"subscriberId": recipient["user_id"],
                   "email": recipient.get("email")},
            "payload": {"title": notif.title, "body": notif.body, **notif.data},
        }
        return _post(self._client, f"{self.base_url}/v1/events/trigger",
                     payload, {"Authorization": f"ApiKey {self.api_key}"})


@dataclass
class AppriseAdapter:
    """Apprise: fan-out chat (Slack/Discord/Telegram/WhatsApp)."""
    name: str = "apprise"

    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool:
        url = (recipient.get("apprise_urls") or {}).get(channel.value)
        if not url:
            return False
        try:
            import apprise
            ap = apprise.Apprise()
            ap.add(url)
            return bool(ap.notify(title=notif.title, body=notif.body))
        except Exception:
            return False


@dataclass
class NtfyAdapter:
    """ntfy.sh: push self-host."""
    name: str = "ntfy"
    base_url: str = "https://ntfy.spyfy.io"
    _client: object | None = None

    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool:
        topic = recipient.get("ntfy_topic", f"user-{recipient['user_id']}")
        headers = {"Title": notif.title, "Priority": _ntfy_prio(notif.priority.value)}
        return _post(self._client, f"{self.base_url}/{topic}",
                     notif.body.encode(), headers, raw=True)


@dataclass
class WebhookAdapter:
    """Webhook nativo (assinado) — ver spyfy.webhooks."""
    name: str = "native"
    secret: str = ""
    _client: object | None = None

    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool:
        import json
        from .webhooks import sign_payload
        url = recipient.get("webhook_url")
        if not url:
            return False
        body = json.dumps({"event_id": notif.event_id, "type": notif.type,
                           "title": notif.title, "body": notif.body,
                           "data": notif.data})
        sig, ts = sign_payload(body, self.secret)
        return _post(self._client, url, body.encode(),
                     {"X-SpyFy-Signature": sig, "X-SpyFy-Timestamp": ts,
                      "Content-Type": "application/json"}, raw=True)


class NotificationDispatcher:
    def __init__(self, notifiers: dict[str, Notifier], max_retries: int = 2):
        self.notifiers = notifiers
        self.max_retries = max_retries

    def dispatch(self, *, plan: str, prefs: NotificationPrefs,
                 notif: Notification, recipient: dict, hour_local: int,
                 sent_today: int, seen_event: bool = False) -> DispatchReport:
        route = resolve_channels(plan, prefs, notif, hour_local,
                                 sent_today, seen_event)
        report = DispatchReport(route=route)
        if route.suppressed:
            return report
        for channel in route.channels:
            backend = CHANNEL_BACKEND.get(channel, "native")
            notifier = self.notifiers.get(backend)
            report.deliveries.append(
                self._deliver(notifier, backend, channel, recipient, notif))
        return report

    def _deliver(self, notifier, backend, channel, recipient, notif) -> DeliveryResult:
        if notifier is None:
            return DeliveryResult(channel, False, backend, 0, "no_adapter")
        attempts, last_err = 0, ""
        while attempts <= self.max_retries:
            attempts += 1
            try:
                if notifier.send(channel, recipient, notif):
                    return DeliveryResult(channel, True, backend, attempts)
                last_err = "send_returned_false"
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
        return DeliveryResult(channel, False, backend, attempts, last_err)





def _workflow_for(event_type: str) -> str:
    return event_type.replace(".", "-")


def _ntfy_prio(priority: str) -> str:
    return {"low": "low", "normal": "default",
            "high": "high", "urgent": "urgent"}.get(priority, "default")


def _post(client, url, data, headers, raw: bool = False) -> bool:
    if client is None:
        try:
            import httpx
            client = httpx.Client(timeout=10)
        except Exception:
            return False
    try:
        if raw:
            r = client.post(url, content=data, headers=headers)
        else:
            r = client.post(url, json=data, headers=headers)
        return 200 <= r.status_code < 300
    except Exception:
        return False
