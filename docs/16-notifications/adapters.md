# 🔌 Delivery Adapters & Dispatcher — SpyFy

Camada de **entrega real** das notificações: adapters concretos para os backends open-source + um Dispatcher que orquestra roteamento → entrega → retry. Código em `apps/workers-py/spyfy/notifiers.py` (7 testes ✅).

## Arquitetura

```
Notification + recipient + plan/prefs
        │
        ▼
NotificationDispatcher.dispatch()
        │  1. resolve_channels()  (plano/prefs/quiet/limite/dedup)
        ▼
  para cada canal escolhido:
        │  CHANNEL_BACKEND[canal] -> backend
        ▼
   Adapter.send()  (com retry)
        │
        ▼
   DispatchReport (delivered / failed / all_ok)
```

## Interface comum (Protocol)

```python
class Notifier(Protocol):
    name: str
    def send(self, channel: Channel, recipient: dict, notif: Notification) -> bool: ...
```

Qualquer backend novo só precisa implementar `send()` → plugável no Dispatcher (e fácil de mockar em teste, via injeção).

## Adapters implementados

| Adapter | Backend OSS | Canais | Como envia |
|---------|-------------|--------|------------|
| `NovuAdapter` | Novu | in-app, email | `POST /v1/events/trigger` (workflow) |
| `AppriseAdapter` | Apprise | slack, discord, telegram, whatsapp | `apprise.notify()` por URL do destinatário |
| `NtfyAdapter` | ntfy.sh | push | `POST /{topic}` com headers Title/Priority |
| `WebhookAdapter` | nativo | webhook | JSON **assinado (HMAC)** via `sign_payload` |

## Dispatcher — uso

```python
from spyfy.notifiers import (NotificationDispatcher, NovuAdapter,
                             AppriseAdapter, NtfyAdapter, WebhookAdapter)

dispatcher = NotificationDispatcher({
    "novu": NovuAdapter(api_key=NOVU_KEY),
    "apprise": AppriseAdapter(),
    "ntfy": NtfyAdapter(base_url="https://ntfy.spyfy.io"),
    "native": WebhookAdapter(secret=WEBHOOK_SECRET),
}, max_retries=2)

report = dispatcher.dispatch(
    plan="pro", prefs=user_prefs, notif=notif, recipient=recipient,
    hour_local=14, sent_today=count_today,
)

if report.route.suppressed:
    log.info("suprimida: %s", report.route.reason)
else:
    log.info("entregue: %s | falhou: %s", report.delivered, report.failed)
```

## Recipient (dados de entrega)

```python
recipient = {
    "user_id": "u1",
    "email": "user@example.com",
    "apprise_urls": {                # resolvidos das prefs/integrações
        "slack": "slack://TOKEN/CHANNEL",
        "telegram": "tgram://BOT/CHAT",
        "discord": "discord://ID/TOKEN",
    },
    "ntfy_topic": "user-u1",
    "webhook_url": "https://partner.example.com/hooks/spyfy",
}
```

## Retry & resultado

- Cada canal tenta até `max_retries + 1` vezes.
- `DeliveryResult{channel, ok, backend, attempts, error}` por canal.
- `DispatchReport.all_ok` só é `True` se todos os canais entregaram.
- Em prod: backoff exponencial + fila (aqui o retry é síncrono para teste).

## Segurança

- Webhook sempre **assinado** (HMAC + timestamp) — ver [webhooks.md](../15-integrations/webhooks.md).
- Segredos (Novu API key, webhook secret) via Vault.
- `_client` injetável (httpx) → testes sem rede.

## Extensibilidade

Adicionar um canal novo (ex.: SMS via open-source):
1. Criar `SmsAdapter(Notifier)`.
2. Registrar em `CHANNEL_BACKEND` (`Channel.SMS -> "sms"`).
3. Injetar no Dispatcher.
Nenhuma mudança na lógica de roteamento.

## Cobertura de testes (7 casos)

| Teste | Verifica |
|-------|----------|
| delivers_to_all_routed_channels | entrega em todos os canais do plano |
| suppressed_route_no_delivery | rota suprimida não entrega |
| missing_adapter_marks_failure | canal sem adapter → `no_adapter` |
| retry_then_success | falha 1x, sucede na 2ª tentativa |
| retry_exhausted_fails | esgota tentativas → falha |
| webhook_adapter_signs | webhook sai assinado (HMAC) |
| free_plan_limits_delivery | Free só in-app/email |

## Observabilidade

- Cada `DeliveryResult` vira métrica/log (canal, backend, tentativas, erro).
- Dashboards: taxa de entrega por backend, retries, falhas por canal.
- Alerta se um backend cai (falhas em sequência).
