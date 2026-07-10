# 🪝 Webhooks — SpyFy Integrations

Sistema de webhooks bidirecional, seguro (HMAC + timestamp), idempotente e resiliente (retry + DLQ). Base das integrações NexusTracker e DarkfyCheckout.

## Direções

- **Outbound:** SpyFy → parceiro (clone pronto, oferta escalando).
- **Inbound:** parceiro → SpyFy (venda, conversão, checkout).

## Segurança — assinatura HMAC

Todo webhook carrega assinatura e timestamp:

```
X-SpyFy-Signature: sha256=<hex hmac>
X-SpyFy-Timestamp: 1780000000
```

Assinatura = `HMAC_SHA256(secret, "{timestamp}.{raw_body}")`.

- **Anti-replay:** rejeitar se `|now - timestamp| > 300s`.
- **Timing-safe compare** (evita timing attacks).
- Segredo por integração, no Vault.

## Verificação (código real — validado)

Ver `packages/integrations/src/webhook.ts` (TS) e
`apps/workers-py/spyfy/webhooks.py` (Python), ambos com testes.

```ts
import crypto from "node:crypto";

export function verifyWebhook(rawBody: string, header: string,
                             timestamp: string, secret: string,
                             toleranceSec = 300): boolean {
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - Number(timestamp)) > toleranceSec) return false;
  const expected = crypto
    .createHmac("sha256", secret)
    .update(`${timestamp}.${rawBody}`)
    .digest("hex");
  const provided = header.replace(/^sha256=/, "");
  const a = Buffer.from(expected), b = Buffer.from(provided);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
```

## Eventos (catálogo)

### Outbound (SpyFy → parceiro)
```
clone.completed
clone.publish            → DarkfyCheckout
offer.scaling_detected   → NexusTracker
alert.triggered
```

### Inbound (parceiro → SpyFy)
```
conversion.tracked       ← NexusTracker
checkout.created         ← DarkfyCheckout
order.paid               ← DarkfyCheckout
upsell.accepted          ← DarkfyCheckout
refund.created           ← DarkfyCheckout
```

## Envelope padrão

```json
{
  "event_id": "evt_abc123",
  "type": "order.paid",
  "created_at": "2026-07-10T14:00:00Z",
  "data": { }
}
```

## Idempotência

- Dedup por `event_id` (Redis SET + TTL 24h).
- Reprocessar o mesmo evento não gera efeito duplicado.

## Entrega & retry (outbound)

- At-least-once.
- Retry com backoff exponencial: 1m, 5m, 30m, 2h, 6h, 24h.
- Após esgotar → DLQ + alerta.
- Endpoint deve responder `2xx` em < 5s (senão retry).

## Recebimento (inbound)

```python
@router.post("/v1/webhooks/{provider}")
async def receive(provider: str, request: Request):
    raw = await request.body()
    sig = request.headers.get(f"X-{provider}-Signature", "")
    ts  = request.headers.get(f"X-{provider}-Timestamp", "0")
    secret = await vault.get(f"integrations/{provider}/webhook_secret")
    if not verify_webhook(raw.decode(), sig, ts, secret):
        raise HTTPException(401, "invalid signature")
    event = json.loads(raw)
    if await seen(event["event_id"]):        # idempotência
        return {"ok": True, "dedup": True}
    await enqueue(provider, event)           # processa async
    return {"ok": True}
```

## Fila & processamento

- Webhook recebido → responde 200 rápido → processa via fila (BullMQ).
- Handlers por tipo de evento; falha → retry/DLQ.

## Assinaturas de webhook (gerenciamento)

```
POST   /v1/webhooks/endpoints      { url, events[] }
GET    /v1/webhooks/endpoints
DELETE /v1/webhooks/endpoints/{id}
POST   /v1/webhooks/endpoints/{id}/rotate-secret
GET    /v1/webhooks/deliveries     # log de entregas
POST   /v1/webhooks/deliveries/{id}/replay
```

## Observabilidade

- Log de toda entrega (status, tentativas, latência).
- Métricas: taxa de sucesso, tamanho da DLQ, p95 de entrega.
- Alertas: falha recorrente por endpoint/provider.

## Boas práticas para o parceiro

- Verificar assinatura SEMPRE.
- Responder 2xx rápido; processar async.
- Tratar duplicatas (idempotência por `event_id`).
- Tolerar reordenação (usar `created_at`).

## Testes

- `packages/integrations` + `apps/workers-py/tests/test_webhooks.py`.
- Casos: assinatura válida/inválida, replay (timestamp velho), corpo adulterado.
