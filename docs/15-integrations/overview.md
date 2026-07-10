# 🔗 SpyFy Integrations API — Visão Geral

API dedicada para integrar o SpyFy com projetos externos. Primeiros parceiros: **NexusTracker** (tracker de campanhas/atribuição) e **DarkfyCheckout** (plataforma de checkout). Arquitetura extensível para futuros parceiros.

## Objetivo

Fechar o loop **espionar → clonar → rodar → medir → otimizar**:

```
SpyFy (oferta/clone) ──▶ DarkfyCheckout (funil live/checkout)
       ▲                          │
       │ ROI real de volta        ▼
NexusTracker (cliques/vendas/atribuição) ──▶ SpyFy (recalibra Scale/ROI)
```

- SpyFy manda ofertas clonadas para o **DarkfyCheckout** publicar.
- **NexusTracker** devolve performance real (cliques, vendas, CPA).
- SpyFy usa esse retorno para **calibrar o Scale/ROI Engine** (estimativas viram dados reais).

## Superfícies da Integrations API

| Superfície | Uso |
|-----------|-----|
| **REST `/v1/integrations`** | CRUD de conexões, push/pull de dados |
| **Webhooks (out)** | SpyFy notifica parceiros (clone pronto, oferta escalando) |
| **Webhooks (in)** | Parceiros notificam SpyFy (venda, clique, checkout criado) |
| **OAuth2** | Autorização entre plataformas |
| **SDK** | `@spyfy/integrations` (TS) |

## Autenticação entre plataformas

- **API Keys por integração** (`sk_int_...`) com scopes.
- **OAuth2** quando ação em nome do usuário.
- **HMAC** em todos os webhooks (assinatura + timestamp anti-replay).
- Ver [webhooks.md](webhooks.md).

## Modelo de conexão

```sql
integrations (
  id, workspace_id, provider,        -- 'nexustracker' | 'darkfycheckout'
  status,                            -- connected | error | revoked
  credentials_ref,                   -- ponteiro p/ Vault (nunca em claro)
  config jsonb, created_at
)
integration_events (
  id, integration_id, direction,     -- inbound | outbound
  event_type, payload jsonb, status, created_at
)
```

## Endpoints núcleo

```
GET    /v1/integrations                    # lista conexões
POST   /v1/integrations                    # cria conexão { provider, config }
DELETE /v1/integrations/{id}               # revoga
POST   /v1/integrations/{id}/test          # testa conexão
GET    /v1/integrations/{id}/events        # auditoria
POST   /v1/webhooks/{provider}             # recebe webhooks inbound
```

## Fluxos suportados

| Fluxo | Origem → Destino | Evento |
|-------|------------------|--------|
| Publicar clone | SpyFy → DarkfyCheckout | `clone.publish` |
| Checkout criado | DarkfyCheckout → SpyFy | `checkout.created` |
| Venda realizada | DarkfyCheckout → SpyFy | `order.paid` |
| Tráfego atribuído | NexusTracker → SpyFy | `conversion.tracked` |
| Oferta escalando | SpyFy → NexusTracker | `offer.scaling` |
| Recalibrar ROI | (interno) | `roi.recalibrated` |

## Idempotência & confiabilidade

- `Idempotency-Key` em toda escrita.
- Webhooks: at-least-once + dedup por `event_id`.
- Retry com backoff (até 24h) + DLQ.
- Reconciliação periódica entre plataformas.

## Segurança

- Credenciais no Vault (nunca em claro/logs).
- HMAC + timestamp (janela de 5 min) contra replay.
- Scopes mínimos por integração.
- Allowlist de IP opcional para parceiros enterprise.
- Ver [security.md](../09-security/security.md).

## Observabilidade

- Log de todo evento (auditoria em `integration_events`).
- Métricas: taxa de entrega de webhook, latência, falhas por provider.
- Alertas quando integração entra em `error`.

## Documentos
- [nexustracker.md](nexustracker.md) — integração de tracking/atribuição.
- [darkfycheckout.md](darkfycheckout.md) — integração de checkout.
- [webhooks.md](webhooks.md) — sistema de webhooks (HMAC, eventos, retries).
