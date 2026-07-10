# 💳 Integração — DarkfyCheckout

**DarkfyCheckout** = plataforma de checkout/funil. O SpyFy publica ofertas clonadas diretamente como funis live no DarkfyCheckout e recebe de volta eventos de vendas.

## O que a integração faz

- **SpyFy → DarkfyCheckout:** publica o clone (LP + funil + upsells) como funil pronto para vender.
- **DarkfyCheckout → SpyFy:** devolve `checkout.created`, `order.paid`, `upsell.accepted` → alimenta ROI real.
- **Resultado:** do "clonar" ao "vendendo" em minutos, com o loop de dados fechado.

## Fluxo: publicar clone como funil

```
SpyFy clone pronto (cl_991)
   │  POST /funnels (bundle + manifest)
   ▼
DarkfyCheckout cria funil live
   │  retorna funnel_url + checkout_url
   ▼
Usuário aponta o anúncio para funnel_url
```

## Push: publicar funil

```http
POST https://api.darkfycheckout.com/v1/funnels
Authorization: Bearer <darkfy_token>
Content-Type: application/json

{
  "source": "spyfy",
  "clone_id": "cl_991",
  "bundle_url": "https://r2.spyfy.io/clones/cl_991/bundle.zip",
  "funnel": {
    "steps": [
      { "order": 1, "type": "lp",       "html_ref": "lp.html" },
      { "order": 2, "type": "checkout", "product": { "name": "Keto Pro", "price": 57 } },
      { "order": 3, "type": "upsell",   "product": { "name": "Bônus", "price": 39 } },
      { "order": 4, "type": "ty" }
    ]
  }
}
```

Resposta:
```json
{ "funnel_id": "fnl_77", "funnel_url": "https://lp.darkfycheckout.com/keto",
  "checkout_url": "https://pay.darkfycheckout.com/c/fnl_77" }
```

## Inbound webhook: venda paga

```http
POST /v1/webhooks/darkfycheckout
X-Darkfy-Signature: sha256=...
X-Darkfy-Timestamp: 1780000000

{
  "event_id": "evt_xyz",
  "type": "order.paid",
  "data": {
    "spyfy_clone_id": "cl_991",
    "order_id": "ord_555",
    "amount": 96.0,             // front 57 + upsell 39
    "currency": "BRL",
    "upsell_accepted": true,
    "customer_country": "BR",
    "paid_at": "2026-07-10T14:00:00Z"
  }
}
```

## Eventos DarkfyCheckout → SpyFy

| Evento | Uso no SpyFy |
|--------|--------------|
| `checkout.created` | funil publicado com sucesso |
| `order.paid` | receita real → ROI Engine |
| `upsell.accepted` | calibra `upsell_take`/`upsell_ticket` |
| `refund.created` | calibra `refund_rate` |

## Calibração do ROI Engine

```python
def calibrate_from_darkfy(econ, events):
    paid = [e for e in events if e.type == "order.paid"]
    if paid:
        econ.upsell_take = ema(econ.upsell_take,
                               mean(e.data.upsell_accepted for e in paid))
        econ.avg_ticket = ema(econ.avg_ticket, mean(e.data.amount for e in paid))
    refunds = [e for e in events if e.type == "refund.created"]
    econ.refund_rate = ema(econ.refund_rate, len(refunds)/max(len(paid),1))
    return econ
```

## Mapeamento

| DarkfyCheckout | SpyFy |
|----------------|-------|
| funnel.clone_id | `clones.id` |
| order.amount | receita real |
| upsell_accepted | taxa de upsell real |
| refund | taxa de reembolso real |

## SDK

```ts
const { funnelUrl, checkoutUrl } =
  await spyfy.integrations.darkfycheckout.publishClone({ cloneId: "cl_991" });
```

## Segurança

- Token no Vault; webhooks HMAC + timestamp.
- Não trafegamos dados de cartão (PCI fica no DarkfyCheckout).
- Scope: `funnels:write`, `orders:read`.
- Ver [compliance.md](../09-security/compliance.md).

## Métricas

- Tempo do clone → funil live.
- Conversão dos funis publicados via SpyFy.
- Receita atribuída a clones do SpyFy.
- Delta ROI estimado vs real.

## Resiliência

- Idempotência na publicação (`Idempotency-Key = clone_id`).
- Retry/DLQ nos webhooks.
- Reconciliação diária de pedidos.
