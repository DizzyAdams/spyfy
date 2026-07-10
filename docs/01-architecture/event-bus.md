# 📨 Event Bus & A13 Notify Agent — SpyFy

O **Event Bus** de domínio conecta, em tempo real, o pipeline (discovery, cloner, integrações) aos consumidores (notificações, analytics). Código testado em `apps/workers-py/spyfy/events.py` + `spyfy/agents/notify_agent.py`.

## Papel no ecossistema

```
Pipeline / Integrações
  (Scout, Cloner, DarkfyCheckout, NexusTracker...)
        │  publish(DomainEvent)
        ▼
   ┌───────────────┐
   │   EventBus     │  pub/sub · dedup · wildcards · middleware · DLQ
   └───────┬───────┘
   ┌───────┼─────────────┬──────────────┐
   ▼       ▼             ▼              ▼
 A13     Analytics     Webhooks       Audit
 Notify  (ClickHouse)  (out)          (log)
```

## DomainEvent

```python
@dataclass
class DomainEvent:
    event_id: str          # idempotência
    type: str              # "offer.scaling", "order.paid", ...
    data: dict
    workspace_id: str | None
    created_at: float
```

## Recursos do EventBus

| Recurso | Descrição |
|---------|-----------|
| **Wildcards** | `subscribe("offer.*", h)` casa `offer.scaling`, `offer.discovered`. |
| **Dedup** | mesmo `event_id` não reprocessa (idempotência). |
| **Middleware** | `use(fn)` roda antes dos handlers (log/metrics). |
| **Dead-letter** | handler que falha vai para `dead_letters`. |
| **Replay** | `replay_dead_letters()` reprocessa após corrigir. |

## Uso

```python
from spyfy.events import EventBus, DomainEvent

bus = EventBus()
bus.use(lambda e: metrics.incr(f"event.{e.type}"))
bus.subscribe("offer.*", on_offer)
bus.subscribe("order.paid", on_order)

bus.publish(DomainEvent("e1", "offer.scaling",
                        {"headline": "Keto BR", "score": 91}))
```

## Catálogo de eventos (`EVENT_TYPES`)

```
offer.discovered · offer.scaling · offer.enriched
advertiser.new_creative
clone.requested · clone.completed · clone.failed
alert.triggered
checkout.created · order.paid · upsell.accepted · refund.created
conversion.tracked · roi.milestone · roi.recalibrated
billing.failed
```

## A13 — Notify Agent

Ponte final **evento → notificação entregue**. Consome eventos, monta `Notification` (título/prioridade/corpo por tipo) e despacha via `NotificationDispatcher`.

```python
from spyfy.agents import NotifyAgent
from spyfy.notifiers import NotificationDispatcher, NovuAdapter, NtfyAdapter, AppriseAdapter, WebhookAdapter

dispatcher = NotificationDispatcher({
    "novu": NovuAdapter(api_key=KEY), "apprise": AppriseAdapter(),
    "ntfy": NtfyAdapter(), "native": WebhookAdapter(secret=SECRET),
})

agent = NotifyAgent(
    dispatcher,
    resolve_recipients=lambda e: recipients_for(e),   # quem recebe
    resolve_context=lambda uid: plan_prefs_sent(uid), # plano, prefs, enviados hoje
)
agent.register(bus)     # inscreve nos tipos mapeados
```

Ao publicar `offer.scaling`, o A13:
1. Monta `Notification("🔥 Oferta escalando", HIGH, "Keto BR — score 91")`.
2. Para cada destinatário, resolve plano/prefs.
3. Dispatcher roteia (plano ∩ prefs, quiet hours, limite, dedup) e entrega.

## Mapa evento → notificação (`EVENT_MAP`)

| Evento | Título | Prioridade |
|--------|--------|-----------|
| offer.scaling | 🔥 Oferta escalando | HIGH |
| advertiser.new_creative | Novo criativo do concorrente | NORMAL |
| clone.completed | Clone pronto ✅ | NORMAL |
| clone.failed | Clonagem falhou | HIGH |
| order.paid | 💰 Venda! | NORMAL |
| roi.milestone | 🚀 Meta de ROI atingida | HIGH |
| billing.failed | ⚠️ Pagamento falhou | URGENT |
| alert.triggered | Alerta disparado | NORMAL |

## Transporte em produção

- Core in-process (testável) + adapters para **RabbitMQ/Redis** (mesmo contrato).
- At-least-once + dedup por `event_id` → idempotência ponta a ponta.
- Ordenação por `created_at` quando necessário.

## Testes (19 no total desta camada)

- `test_events.py` — wildcards, dedup, middleware, dead-letter, replay, count (7).
- `test_notify_agent.py` — E2E EventBus→A13→Dispatcher: offer.scaling, urgente fura quiet hours, free limitado, evento não mapeado ignorado, dedup (5).
- (+ dispatcher/notifications/webhooks/roi anteriores).

## Observabilidade

- Middleware de métricas por tipo de evento.
- Tamanho da DLQ como alerta.
- Trace: evento → handlers → entregas.
