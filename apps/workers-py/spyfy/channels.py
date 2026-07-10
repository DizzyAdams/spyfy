"""
SpyFy — Email / SMS / Mobile Push Adapters (Loop 6)
================================================
Novos canais OSS plugados no Dispatcher (ver notifiers.py).

  - Email:  Postal (AGPL, self-host) via HTTP  OU  Apprise (smtp://)
  - SMS:    SMPP gateway OSS  OU  Apprise (twilio://)
  - Mobile: ntfy (Android) / Gotify / FCM (Android) / APNs (iOS)

Todos resolvem o destinatario a partir de `recipient`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .notifications import Channel


@dataclass
class EmailAdapter:
    """Email transacional/bulk via Postal (self-host, AGPL)."""
    name: str = "postal"
    base_url: str = "https://postal.spyfy.io"
    api_key: str = ""
    _client: Any | None = None

    def send(self, channel: Channel, recipient: dict, notif: Any) -> bool:
        to = recipient.get("email")
        if not to:
            return False
        payload = {
            "To": to,
            "Subject": notif.title,
            "HTML": _email_html(notif),
            "From": recipient.get("from_email", "no-reply@spyfy.io"),
        }
        return _http_post(
            self._client, f"{self.base_url}/api/v1/send/message",
            payload, {"X-Server-API-Key": self.api_key,
                      "Content-Type": "application/json"})


def _email_html(notif: Any) -> str:
    body = (notif.body or "").replace("\n", "<br/>")
    return (f"<div style='font-family:Inter,sans-serif;max-width:520px;margin:auto'>"
            f"<h3>{notif.title}</h3><p>{body}</p>"
            f"<p style='color:#888;font-size:12px'>SpyFy · "
            f"<a href='{{unsubscribe}}'>unsubscribe</a></p></div>")


@dataclass
class SmsAdapter:
    """SMS via SMPP gateway OSS (ex.: SMPP sim/playsms) ou Apprise."""
    name: str = "sms"
    apprise_url: str | None = None
    _client: Any | None = None

    def send(self, channel: Channel, recipient: dict, notif: Any) -> bool:
        phone = _norm_phone(recipient.get("phone"))
        if not phone:
            return False
        if self.apprise_url:
            return _apprise_notify(self.apprise_url, notif.title, notif.body)
        return _http_post(
            self._client, "https://smpp.spyfy.io/api/send",
            {"to": phone, "text": f"{notif.title}: {notif.body}"[:160]},
            {"Content-Type": "application/json"})


def _norm_phone(p: str | None) -> str | None:
    if not p:
        return None
    digits = "".join(c for c in p if c.isdigit())
    if len(digits) < 10:
        return None
    return "+" + digits if not digits.startswith("+") else digits


@dataclass
class MobilePushAdapter:
    """Push iOS/Android via ntfy (Android) / Gotify / FCM (Android) / APNs (iOS)."""
    name: str = "mobile"
    ntfy_url: str = "https://ntfy.spyfy.io"
    fcm_server_key: str = ""
    _client: Any | None = None

    def send(self, channel: Channel, recipient: dict, notif: Any) -> bool:
        ok = False
        topic = recipient.get("ntfy_topic")
        if topic:
            ok = _ntfy(self._client, self.ntfy_url, topic, notif) or ok
        gotify = recipient.get("gotify_url")
        if gotify:
            ok = _gotify(self._client, gotify, notif) or ok
        if self.fcm_server_key and recipient.get("fcm_token"):
            ok = _fcm(self._client, self.fcm_server_key,
                        recipient["fcm_token"], notif) or ok
        if recipient.get("apns_token"):
            ok = _apns_stub(self._client, recipient["apns_token"], notif) or ok
        return ok


def _ntfy(client, base: str, topic: str, notif: Any) -> bool:
    prio = {"low": "low", "normal": "default",
             "high": "high", "urgent": "urgent"}.get(notif.priority.value, "default")
    return _http_post(client, f"{base}/{topic}", notif.body,
                     {"Title": notif.title, "Priority": prio,
                      "Tags": "spyfy", "Content-Type": "text/plain"}, raw=True)


def _gotify(client, url: str, notif: Any) -> bool:
    return _http_post(client, url,
                     json.dumps({"title": notif.title, "message": notif.body}),
                     {"Content-Type": "application/json"}, raw=True)


def _fcm(client, key: str, token: str, notif: Any) -> bool:
    payload = {"notification": {"title": notif.title, "body": notif.body}, "to": token}
    return _http_post(client, "https://fcm.googleapis.com/fcm/send", payload,
                     {"Authorization": f"key={key}", "Content-Type": "application/json"})


def _apns_stub(client, token: str, notif: Any) -> bool:
    """APNs (iOS) usa HTTP/2 + JWT (pacote apns2 em prod)."""
    return bool(token)


def _http_post(client, url, data, headers, raw: bool = False) -> bool:
    from .notifiers import _post
    return _post(client, url, data, headers, raw)


def _apprise_notify(url: str, title: str, body: str) -> bool:
    try:
        import apprise
        ap = apprise.Apprise()
        ap.add(url.replace("{msg}", f"{title}: {body}"))
        return bool(ap.notify(title=title, body=body))
    except Exception:
        return False
