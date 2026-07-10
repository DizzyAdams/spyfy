# 📡 Integração — NexusTracker

**NexusTracker** = tracker de campanhas/atribuição. Fecha o loop devolvendo ao SpyFy a **performance real** das ofertas rodando, para calibrar o Scale/ROI Engine (estimativa → dado real).

## O que a integração faz

- **SpyFy → NexusTracker:** envia ofertas/clones para criar campanhas rastreáveis (com UTMs/subids).
- **NexusTracker → SpyFy:** devolve cliques, conversões, CPA, ROI reais.
- **Resultado:** o winning_score deixa de ser só estimativa e passa a incorporar dados reais do usuário.

## Setup

```
1. Usuário conecta NexusTracker (OAuth2 ou API key).
2. SpyFy registra a integração (credenciais no Vault).
3. Configura mapeamento: nicho SpyFy ↔ campanha NexusTracker.
4. Ativa webhooks bidirecionais.
```

## Push: criar campanha rastreável

```http
POST https://api.nexustracker.io/v1/campaigns
Authorization: Bearer <nexus_token>
Content-Type: application/json

{
  "name": "SpyFy - Keto BR - ofr_123",
  "destination_url": "https://lp.darkfycheckout.com/keto?sub1={click_id}",
  "source": "spyfy",
  "meta": { "spyfy_offer_id": "ofr_123", "clone_id": "cl_991" }
}
```

Resposta → `tracking_url` que o usuário usa no anúncio.

## Inbound webhook: conversão rastreada

```http
POST /v1/webhooks/nexustracker
X-Nexus-Signature: sha256=...
X-Nexus-Timestamp: 1780000000

{
  "event_id": "evt_abc",
  "type": "conversion.tracked",
  "data": {
    "spyfy_offer_id": "ofr_123",
    "clicks": 1450,
    "conversions": 38,
    "revenue": 2166.0,
    "spend": 980.0,
    "cpa": 25.8,
    "roi_pct": 121.0,
    "period": "2026-07-10"
  }
}
```

## Calibração do Scale/ROI Engine

Os dados reais alimentam o `NicheEconomics` (ver `apps/workers-py/spyfy/roi.py`):

```python
def calibrate_from_nexus(econ, tracked):
    # atualiza CVR/CPA/ticket reais por nicho (média móvel exponencial)
    econ.cvr = ema(econ.cvr, tracked.conversions / max(tracked.clicks, 1))
    real_ticket = tracked.revenue / max(tracked.conversions, 1)
    econ.avg_ticket = ema(econ.avg_ticket, real_ticket)
    return econ
```

- Estimativa vira **medição** → confiança sobe para ~0.95.
- Recalcula `winning_score` da oferta com dados reais.

## Mapeamento de dados

| NexusTracker | SpyFy |
|--------------|-------|
| campaign.meta.spyfy_offer_id | `offers.id` |
| clicks/conversions | métricas reais (ClickHouse) |
| revenue/spend | ROI/ROAS reais |
| sub ids | atribuição por criativo/clone |

## SDK

```ts
import { SpyFy } from "@spyfy/integrations";
const spyfy = new SpyFy({ apiKey });

await spyfy.integrations.nexustracker.pushOffer({
  offerId: "ofr_123", cloneId: "cl_991",
});
```

## Segurança

- Token do NexusTracker no Vault.
- Webhooks HMAC + timestamp (ver [webhooks.md](webhooks.md)).
- Scope: `conversions:read`, `campaigns:write`.

## Métricas

- % de ofertas com dados reais de tracking.
- Delta estimativa vs real (acurácia do ROI Engine).
- Latência de ingestão de conversões.

## Erros & resiliência

- Retry com backoff; DLQ para eventos falhos.
- Reconciliação diária (soma de conversões).
- Alerta se integração cair (`status=error`).
