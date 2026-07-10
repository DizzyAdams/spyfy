"""
SpyFy — A13 Alert/Notify Agent
==============================
Sub-agent que consome eventos de domínio do EventBus, converte em
Notification e despacha via NotificationDispatcher (backends OSS),
respeitando plano/preferências do destinatário.

É a ponte final: pipeline/integrações → evento → notificação entregue.
"""
from __future__ import annotations

from typing import Callable

from ..events import DomainEvent, EventBus
from ..notifications import Notification, NotificationPrefs, Priority
from ..notifiers import DispatchReport, NotificationDispatcher

# Mapeia tipo de evento -> (título, prioridade, template de corpo)
EVENT_MAP: dict[str, tuple[str, Priority, Callable[[dict], str]]] = {
    "offer.scaling": (
        "🔥 Oferta escalando", Priority.HIGH,
        lambda d: f"{d.get('headline','Oferta')} — score {d.get('score','?')}",
    ),
    "advertiser.new_creative": (
        "Novo criativo do concorrente", Priority.NORMAL,
        lambda d: f"{d.get('advertiser','Anunciante')} lançou um criativo novo",
    ),
    "clone.completed": (
        "Clone pronto ✅", Priority.NORMAL,
        lambda d: f"Seu clone {d.get('clone_id','')} está pronto para download",
    ),
    "clone.failed": (
        "Clonagem falhou", Priority.HIGH,
        lambda d: f"Falha ao clonar {d.get('offer_id','')}. Tente novamente.",
    ),
    "order.paid": (
        "💰 Venda!", Priority.NORMAL,
        lambda d: f"Venda de R${d.get('amount',0)} numa oferta clonada",
    ),
    "roi.milestone": (
        "🚀 Meta de ROI atingida", Priority.HIGH,
        lambda d: f"Oferta atingiu ROI de {d.get('roi_pct','?')}%",
    ),
    "billing.failed": (
        "⚠️ Pagamento falhou", Priority.URGENT,
        lambda d: "Atualize seu método de pagamento para não perder acesso.",
    ),
    "alert.triggered": (
        "Alerta disparado", Priority.NORMAL,
        lambda d: d.get("message", "Um alerta configurado foi disparado"),
    ),
}


class NotifyAgent:
    """A13 — consome eventos e entrega notificações."""

    def __init__(
        self,
        dispatcher: NotificationDispatcher,
        resolve_recipients: Callable[[DomainEvent], list[dict]],
        resolve_context: Callable[[str], tuple[str, NotificationPrefs, int]],
    ):
        """
        resolve_recipients(event) -> lista de dicts de recipient (destinatários).
        resolve_context(user_id)  -> (plano, prefs, enviados_hoje).
        """
        self.dispatcher = dispatcher
        self.resolve_recipients = resolve_recipients
        self.resolve_context = resolve_context
        self.reports: list[DispatchReport] = []

    def register(self, bus: EventBus) -> None:
        """Inscreve o agente nos tipos de evento mapeados."""
        for event_type in EVENT_MAP:
            bus.subscribe(event_type, self.handle)

    def handle(self, event: DomainEvent) -> None:
        spec = EVENT_MAP.get(event.type)
        if not spec:
            return
        title, priority, body_fn = spec
        notif = Notification(
            event_id=event.event_id,
            type=event.type,
            title=title,
            body=body_fn(event.data),
            priority=priority,
            data=event.data,
        )
        for recipient in self.resolve_recipients(event):
            plan, prefs, sent_today = self.resolve_context(recipient["user_id"])
            report = self.dispatcher.dispatch(
                plan=plan, prefs=prefs, notif=notif, recipient=recipient,
                hour_local=recipient.get("hour_local", 12),
                sent_today=sent_today,
            )
            self.reports.append(report)

    @property
    def total_delivered(self) -> int:
        return sum(len(r.delivered) for r in self.reports)
