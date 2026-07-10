# 🔌 API Design — SpyFy

## Princípios

- **API-first:** tudo que a UI faz, a API expõe.
- **Versionada:** prefixo `/v1`.
- **Consistente:** REST para recursos, tRPC para o web app, GraphQL para consultas ricas, Webhooks para eventos.
- **Segura:** OAuth2/JWT, scopes, rate limit por plano.
- **Documentada:** OpenAPI + exemplos.

## Superfícies

| Superfície | Uso |
|-----------|-----|
| REST `/v1` | Integrações externas, SDK, parceiros. |
| tRPC | Web app (type-safe end-to-end). |
| GraphQL | Consultas agregadas/flexíveis. |
| Webhooks | Notificações (alertas, clone pronto). |

## Autenticação

- **Bearer JWT** (usuários) ou **API Key** (server-to-server).
- Scopes: `offers:read`, `clones:write`, `analytics:read`, `alerts:write`.

```http
Authorization: Bearer sk_live_xxx
```

## Recursos REST principais

### Offers
```
GET    /v1/offers/search        # busca
GET    /v1/offers/{id}          # detalhe
GET    /v1/offers/{id}/snapshots
```

### Clones
```
POST   /v1/clones               # inicia clonagem  { offer_id }
GET    /v1/clones/{id}          # status/resultado
GET    /v1/clones/{id}/download # bundle
```

### Collections
```
GET    /v1/collections
POST   /v1/collections          { name, visibility }
POST   /v1/collections/{id}/items { offer_id, note }
DELETE /v1/collections/{id}/items/{itemId}
```

### Alerts
```
GET    /v1/alerts
POST   /v1/alerts               { type, query, channel }
DELETE /v1/alerts/{id}
```

### Analytics
```
GET    /v1/analytics/niches/{niche}/overview
GET    /v1/analytics/advertisers/{id}/timeline
```

## Padrões de resposta

Sucesso:
```json
{ "data": { ... }, "meta": { "request_id": "req_123" } }
```

Erro:
```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many requests",
    "request_id": "req_123"
  }
}
```

## Paginação

- **Cursor-based** (estável para feeds em tempo real):
```
GET /v1/offers/search?cursor=eyJvZmZzZXQiOjI1fQ&limit=25
```

## Rate limiting

| Plano | Req/min | Burst |
|-------|---------|-------|
| Free | 30 | 10 |
| Pro | 600 | 100 |
| Agency | 3000 | 500 |
| Enterprise | custom | custom |

Headers:
```
X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

## Idempotência

- `POST` de clonagem aceita `Idempotency-Key` para evitar duplicidade.

## Webhooks

Eventos:
```
clone.completed
clone.failed
alert.triggered
offer.scaling_detected
```

Payload:
```json
{
  "event": "clone.completed",
  "data": { "clone_id": "cl_789", "download_url": "https://..." },
  "sent_at": "2026-07-10T12:00:00Z",
  "signature": "sha256=..."
}
```
- Assinatura HMAC no header `X-SpyFy-Signature`.
- Retry com backoff até 24h.

## tRPC (web app)

```ts
const offers = await trpc.offers.search.query({
  q: "keto", network: "meta", country: "BR", minDays: 30
});
```

## GraphQL (exemplo)

```graphql
query {
  offers(niche: "weight_loss", minDays: 30, first: 20) {
    edges { node { id headline winningScore longevityDays } }
    pageInfo { endCursor hasNextPage }
  }
}
```

## Versionamento & deprecação

- Breaking changes → nova versão `/v2`.
- Deprecação anunciada com 6 meses e header `Sunset`.

## OpenAPI

- Spec em `apps/api/openapi.yaml`.
- Portal de docs gerado (Redoc/Scalar).
- SDK TS gerado a partir da spec.
