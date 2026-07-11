"""
SpyFy — Domain Event Bus
========================
Barramento de eventos de domínio (pub/sub) que conecta o pipeline
(discovery, cloner, integrações) aos consumidores (notificações, analytics).

- Publish/subscribe assíncrono e síncrono.
- Deduplicação por event_id (idempotência).
- Wildcards por prefixo ("offer.*").
- Middleware (logging/metrics) e dead-letter para handlers que falham.

Em produção o transporte é RabbitMQ/Redis; aqui o core é in-process e
100% testável. Adapters de transporte plugam no mesmo contrato.
"""
from __future__ import annotations

import fnmatch
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class DomainEvent:
    event_id: str
    type: str                       # ex.: "offer.scaling", "order.paid"
    data: dict = field(default_factory=dict)
    workspace_id: str | None = None
    created_at: float = field(default_factory=time.time)


Handler = Callable[[DomainEvent], None]


@dataclass
class DeadLetter:
    event: DomainEvent
    handler: str
    error: str


class EventBus:
    def __init__(self) -> None:
        self._subs: list[tuple[str, Handler]] = []
        self._seen: set[str] = set()
        self._middleware: list[Callable[[DomainEvent], None]] = []
        self.dead_letters: list[DeadLetter] = []
        self.published: int = 0

    # ------------------------------------------------------------------ #
    def subscribe(self, pattern: str, handler: Handler) -> None:
        """Inscreve handler para um padrão ('offer.*', 'order.paid', '*')."""
        self._subs.append((pattern, handler))

    def use(self, middleware: Callable[[DomainEvent], None]) -> None:
        """Middleware executado antes dos handlers (log/metrics)."""
        self._middleware.append(middleware)

    def publish(self, event: DomainEvent) -> int:
        """Publica um evento. Retorna nº de handlers acionados com sucesso."""
        if event.event_id in self._seen:          # idempotência
            return 0
        self._seen.add(event.event_id)
        self.published += 1

        for mw in self._middleware:
            try:
                mw(event)
            except Exception:  # middleware nunca quebra o fluxo
                pass

        delivered = 0
        for pattern, handler in self._subs:
            if _match(pattern, event.type):
                try:
                    handler(event)
                    delivered += 1
                except Exception as e:  # noqa: BLE001
                    self.dead_letters.append(
                        DeadLetter(event, getattr(handler, "__name__", str(handler)),
                                   str(e)))
        return delivered

    def replay_dead_letters(self) -> int:
        """Reprocessa dead-letters (após corrigir o handler)."""
        pending, self.dead_letters = self.dead_letters, []
        ok = 0
        for dl in pending:
            for pattern, handler in self._subs:
                name = getattr(handler, "__name__", str(handler))
                if name == dl.handler and _match(pattern, dl.event.type):
                    try:
                        handler(dl.event)
                        ok += 1
                    except Exception as e:  # noqa: BLE001
                        self.dead_letters.append(DeadLetter(dl.event, name, str(e)))
        return ok


def _match(pattern: str, event_type: str) -> bool:
    return fnmatch.fnmatch(event_type, pattern)


# Catálogo de tipos de evento de domínio (fonte única)
EVENT_TYPES = {
    "offer.discovered", "offer.scaling", "offer.enriched",
    "advertiser.new_creative",
    "copy.extracted",
    "roi.computed",
    "offer.indexed",
    "guard.qa",
    "clone.requested", "clone.completed", "clone.failed",
    "alert.triggered",
    "checkout.created", "order.paid", "upsell.accepted", "refund.created",
    "conversion.tracked", "roi.milestone", "roi.recalibrated",
    "billing.failed",
}


if __name__ == "__main__":
    bus = EventBus()
    log: list[str] = []
    bus.use(lambda e: log.append(f"[mw] {e.type}"))
    bus.subscribe("offer.*", lambda e: log.append(f"offer handler: {e.type}"))
    bus.subscribe("order.paid", lambda e: log.append(f"order handler: {e.data}"))

    bus.publish(DomainEvent("e1", "offer.scaling", {"offer": "keto"}))
    bus.publish(DomainEvent("e2", "order.paid", {"amount": 96}))
    bus.publish(DomainEvent("e1", "offer.scaling", {"dup": True}))  # dedup

    print("\n".join(log))
    print("publicados:", bus.published)
