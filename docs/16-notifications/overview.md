# 🔔 Notifications — Visão Geral

Sistema de notificações multicanal, orientado a eventos, com **entitlements por plano**, quiet hours, digest, deduplicação e retries — sobre stack open-source (ver [open-source-stack.md](open-source-stack.md)).

## Objetivo

Avisar o usuário **no momento certo, pelo canal certo**, sobre o que importa: ofertas escalando, novos criativos de concorrentes, clones prontos, alertas de conta.

## Arquitetura orientada a eventos

```
Evento de domínio (offer.scaling, clone.completed, order.paid...)
   │
   ▼
Notification Engine (spyfy/notifications.py)
   ├─ resolve destinatários (workspace/usuários)
   ├─ aplica plano ∩ preferências
   ├─ quiet hours / prioridade / limite diário / dedup
   ▼
Fan-out para backends OSS (Novu / Apprise / ntfy / Gotify)
   ▼
Entrega + tracking (aberto, clicado, falhou) → retry/DLQ
```

## Tipos de notificação

| Tipo | Gatilho | Prioridade padrão |
|------|---------|-------------------|
| `offer.scaling` | oferta cruzou threshold de escala | HIGH |
| `advertiser.new_creative` | concorrente lançou criativo | NORMAL |
| `clone.completed` | clonagem terminou | NORMAL |
| `clone.failed` | clonagem falhou | HIGH |
| `alert.triggered` | alerta custom disparou | conforme alerta |
| `order.paid` (via DarkfyCheckout) | venda em oferta clonada | NORMAL |
| `roi.milestone` | oferta atingiu ROI-alvo | HIGH |
| `billing.failed` | pagamento falhou | URGENT |
| `digest.daily` | resumo diário | LOW |

## Roteamento (o coração)

Implementado e **testado** em `resolve_channels(...)`:

1. **Dedup** por `event_id`.
2. **Muted types** (usuário silenciou).
3. **Limite diário** por plano (urgentes furam).
4. **Quiet hours** (urgentes furam; senão cai para in-app).
5. **Interseção** plano ∩ preferências do usuário.
6. **Urgentes** garantem push/email/in-app.
7. **Ordena** por intrusividade.

Ver matriz em [plans-matrix.md](plans-matrix.md).

## Digest & agrupamento

- Eventos de baixa prioridade agrupados em **digest** (diário/horário) via Novu.
- Evita fadiga: "12 novas ofertas no seu nicho" em vez de 12 pushes.

## Preferências do usuário

```json
{
  "enabled_channels": ["in_app", "email", "slack", "telegram"],
  "quiet_hours": [22, 7],
  "muted_types": ["digest.daily"],
  "digest": "daily"
}
```

## Confiabilidade

- Idempotência por `event_id` (dedup).
- Retry com backoff + DLQ (falha de entrega).
- Tracking de entrega (Novu) — aberto/clicado.
- Fallback de canal (se push falha, email).

## Segurança & compliance

- Sem PII sensível no corpo; links assinados.
- Unsubscribe/opt-out (LGPD/GDPR).
- Segredos dos backends no Vault.
- Rate limit por usuário/plano (anti-spam).

## Sub-agent de notificação (A13)

O **Alert/Notify Agent** (ver [team-14-agents.md](../14-mining/team-14-agents.md)) consome eventos em tempo real, chama o Engine e dispara os backends OSS, emitindo eventos de progresso para observabilidade.

## Métricas

- Taxa de entrega por canal.
- Open/click rate (email/in-app).
- Taxa de opt-out.
- Notificações → ações (proxy de valor / WWOA).
