# 📡 Canais de Notificação — Detalhe

Cada canal, seu backend open-source, formato e boas práticas.

## In-app (Novu)

- **Backend:** Novu (inbox + WebSocket).
- **UI:** `@novu/notification-center` (React) — sino com contador, feed, marcar como lido.
- **Uso:** todo evento (baseline). Não intrusivo.
- **Formato:** título + corpo + CTA + ícone por tipo.

## Email (Novu + Postal/Listmonk ou SES)

- **Backend:** Novu orquestra; provedor de envio configurável.
- **Uso:** eventos importantes + digest.
- **Boas práticas:** template responsivo, unsubscribe, links assinados, DKIM/SPF/DMARC.

## Push (ntfy / Gotify)

- **Backend:** ntfy.sh (self-host) ou Gotify.
- **Uso:** tempo real (oferta escalando, clone pronto).
- **Formato:** título curto + prioridade + tags (emoji ntfy) + click action.
- **Mobile:** app ntfy/Gotify ou PWA push.

## Telegram (Apprise)

- **Backend:** Apprise (`tgram://`).
- **Uso:** alertas rápidos; muito popular entre media buyers.
- **Setup:** bot token + chat/grupo.
- **Formato:** Markdown, botões inline (link para oferta/clone).

## Slack (Apprise / Novu)

- **Backend:** Apprise (`slack://`) ou webhook Slack.
- **Uso:** times/agências.
- **Formato:** Block Kit (card com botões "Ver oferta", "Clonar").
- **Slash command:** `/spyfy` para buscar sem sair do Slack (roadmap).

## Discord (Apprise)

- **Backend:** Apprise (`discord://`).
- **Uso:** comunidades/servidores de afiliados.
- **Formato:** embeds ricos (thumbnail do criativo, score, longevidade).

## WhatsApp (Apprise / provider)

- **Backend:** Apprise + provider (WhatsApp Cloud API).
- **Uso:** Agency/Enterprise; alertas urgentes.
- **Compliance:** opt-in explícito, templates aprovados.

## Webhook (nativo)

- **Backend:** nosso sistema de webhooks (HMAC — ver [webhooks.md](../15-integrations/webhooks.md)).
- **Uso:** integrações (NexusTracker, apps de terceiros).
- **Formato:** envelope JSON assinado.

## Formato unificado (payload interno)

```json
{
  "event_id": "evt_1",
  "type": "offer.scaling",
  "title": "Oferta escalando!",
  "body": "Keto BR ativa há 30d — score 91",
  "priority": "high",
  "data": { "offer_id": "ofr_123", "score": 91, "deep_link": "spyfy://offer/ofr_123" }
}
```

Cada backend adapta esse payload ao seu formato (blocks, embeds, markdown).

## Deep links

- `spyfy://offer/{id}`, `spyfy://clone/{id}` — abrem direto no app/web.
- Links de email/webhook assinados com expiração.

## Boas práticas por canal

| Canal | Regra-chave |
|-------|-------------|
| Push | título ≤ 50 chars, ação clara |
| Email | mobile-first, 1 CTA principal |
| Slack/Discord | usar cards/embeds, não texto cru |
| Telegram | botões inline |
| WhatsApp | opt-in + template aprovado |
| Webhook | assinar + idempotência |

## Fallback

- Ordem: in-app → push → email → chat → webhook.
- Se canal preferido falha, tenta o próximo permitido pelo plano.

## Testabilidade

- Modo sandbox: envia para endpoints de teste (Apprise `json://`, Novu test).
- Preview de template antes de disparar.
