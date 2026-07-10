"""
SpyFy — Notification Engine
===========================
Roteamento multicanal de notificações com entitlements por plano,
prioridade, quiet hours e deduplicação. Projetado para orquestrar
projetos OPEN-SOURCE de notificação:

  - Novu      (infra de notificação self-host)   -> orquestração/inbox
  - Apprise   (lib py, 100+ serviços)             -> fan-out multicanal
  - ntfy.sh   (push simples self-host)            -> push/mobile
  - Gotify    (push self-host)                     -> push server

Este módulo decide O QUE enviar, POR QUAIS canais e PARA QUEM,
respeitando o plano do usuário. O envio real é delegado aos adapters OSS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Channel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"            # SMPP/Apprise
    PUSH = "push"          # ntfy / Gotify / FCM+APNs
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"       # ignora quiet hours


# Entitlements de canais por plano (os "melhores planos")
PLAN_CHANNELS: dict[str, set[Channel]] = {
    "free":    {Channel.IN_APP, Channel.EMAIL},
    "starter": {Channel.IN_APP, Channel.EMAIL, Channel.PUSH, Channel.TELEGRAM},
    "pro":     {Channel.IN_APP, Channel.EMAIL, Channel.PUSH, Channel.TELEGRAM,
                Channel.SLACK, Channel.DISCORD, Channel.WEBHOOK},
    "agency":  set(Channel),
    "enterprise": set(Channel),
}

# Limite diário de notificações por plano (anti-spam / custo)
PLAN_DAILY_LIMIT: dict[str, int] = {
    "free": 20, "starter": 200, "pro": 2000,
    "agency": 20000, "enterprise": 10**9,
}


@dataclass
class NotificationPrefs:
    """Preferências do usuário."""
    enabled_channels: set[Channel] = field(default_factory=lambda: {Channel.IN_APP})
    quiet_hours: tuple[int, int] | None = None   # (start_h, end_h) 24h local
    muted_types: set[str] = field(default_factory=set)


@dataclass
class Notification:
    event_id: str
    type: str                     # ex.: "offer.scaling", "clone.completed"
    title: str
    body: str
    priority: Priority = Priority.NORMAL
    data: dict = field(default_factory=dict)


@dataclass
class RouteDecision:
    channels: list[Channel]
    suppressed: bool
    reason: str = ""


def resolve_channels(
    plan: str,
    prefs: NotificationPrefs,
    notif: Notification,
    hour_local: int,
    sent_today: int,
    seen_event: bool = False,
) -> RouteDecision:
    """Decide para quais canais enviar, respeitando plano/prefs/limites."""
    # dedup
    if seen_event:
        return RouteDecision([], True, "duplicate_event")

    # tipo silenciado
    if notif.type in prefs.muted_types:
        return RouteDecision([], True, "muted_type")

    # limite diário (urgentes furam o limite)
    limit = PLAN_DAILY_LIMIT.get(plan, 0)
    if sent_today >= limit and notif.priority != Priority.URGENT:
        return RouteDecision([], True, "daily_limit_reached")

    # quiet hours (urgentes furam)
    if prefs.quiet_hours and notif.priority != Priority.URGENT:
        start, end = prefs.quiet_hours
        if _in_quiet(hour_local, start, end):
            # cai só para in-app (não intrusivo) se permitido
            allowed = PLAN_CHANNELS.get(plan, set())
            if Channel.IN_APP in allowed and Channel.IN_APP in prefs.enabled_channels:
                return RouteDecision([Channel.IN_APP], False, "quiet_hours_inapp_only")
            return RouteDecision([], True, "quiet_hours")

    # interseção: plano ∩ preferências
    allowed = PLAN_CHANNELS.get(plan, set())
    chosen = [c for c in prefs.enabled_channels if c in allowed]

    # urgentes garantem ao menos push/email se disponível
    if notif.priority == Priority.URGENT:
        for c in (Channel.PUSH, Channel.EMAIL, Channel.IN_APP):
            if c in allowed and c not in chosen:
                chosen.append(c)

    if not chosen:
        return RouteDecision([], True, "no_channel_available")

    # ordena por "intrusividade" para envio consistente
    order = [Channel.IN_APP, Channel.PUSH, Channel.EMAIL, Channel.TELEGRAM,
             Channel.SLACK, Channel.DISCORD, Channel.WHATSAPP, Channel.WEBHOOK]
    chosen.sort(key=lambda c: order.index(c) if c in order else 99)
    return RouteDecision(chosen, False, "ok")


def _in_quiet(hour: int, start: int, end: int) -> bool:
    if start == end:
        return False
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end     # janela cruzando meia-noite


# Mapeamento canal -> projeto OSS (adapter)
CHANNEL_BACKEND = {
    Channel.IN_APP: "novu",
    Channel.EMAIL: "postal",           # Postal (self-host) via adapter
    Channel.SMS: "sms",                  # SMPP gateway OSS ou Apprise
    Channel.PUSH: "mobile",             # ntfy/Gotify/FCM/APNs
    Channel.SLACK: "apprise",
    Channel.DISCORD: "apprise",
    Channel.TELEGRAM: "apprise",
    Channel.WHATSAPP: "apprise",
    Channel.WEBHOOK: "native",
}


if __name__ == "__main__":
    prefs = NotificationPrefs(
        enabled_channels={Channel.IN_APP, Channel.EMAIL, Channel.SLACK,
                          Channel.TELEGRAM, Channel.PUSH},
        quiet_hours=(22, 7),
    )
    n = Notification("evt_1", "offer.scaling", "Oferta escalando!",
                     "Keto BR ativa há 30d", Priority.HIGH)

    print("PRO @ 14h:", resolve_channels("pro", prefs, n, 14, 0))
    print("FREE @ 14h:", resolve_channels("free", prefs, n, 14, 0))
    print("PRO @ 23h (quiet):", resolve_channels("pro", prefs, n, 23, 0))
    urgent = Notification("evt_2", "billing.failed", "Pagamento falhou",
                          "Atualize seu cartão", Priority.URGENT)
    print("PRO @ 23h URGENT:", resolve_channels("pro", prefs, urgent, 23, 0))
    print("PRO limite atingido:", resolve_channels("pro", prefs, n, 14, 2000))
    print("dedup:", resolve_channels("pro", prefs, n, 14, 0, seen_event=True))
