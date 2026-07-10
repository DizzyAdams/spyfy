# 📊 Notification Entitlements por Plano — SpyFy

Canais, limites e recursos de notificação por plano. Implementado e testado em `PLAN_CHANNELS` / `PLAN_DAILY_LIMIT` (`spyfy/notifications.py`).

## Canais por plano

| Canal | Free | Starter | Pro | Agency | Enterprise |
|-------|:----:|:-------:|:---:|:------:|:----------:|
| In-app (Novu) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Email | ✅ | ✅ | ✅ | ✅ | ✅ |
| Push (ntfy/Gotify) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Telegram | ❌ | ✅ | ✅ | ✅ | ✅ |
| Slack | ❌ | ❌ | ✅ | ✅ | ✅ |
| Discord | ❌ | ❌ | ✅ | ✅ | ✅ |
| Webhook | ❌ | ❌ | ✅ | ✅ | ✅ |
| WhatsApp | ❌ | ❌ | ❌ | ✅ | ✅ |

## Limites diários

| Plano | Notificações/dia | Digest | Real-time |
|-------|------------------|--------|-----------|
| Free | 20 | diário | ❌ |
| Starter | 200 | diário/horário | ✅ |
| Pro | 2.000 | configurável | ✅ |
| Agency | 20.000 | configurável | ✅ |
| Enterprise | ilimitado | custom | ✅ + SLA |

## Recursos por plano

| Recurso | Free | Starter | Pro | Agency | Enterprise |
|---------|:----:|:-------:|:---:|:------:|:----------:|
| Quiet hours | ✅ | ✅ | ✅ | ✅ | ✅ |
| Prioridade urgente (fura silêncio) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Alertas custom | 1 | 5 | 50 | 500 | ilimitado |
| Webhooks de saída | ❌ | ❌ | ✅ | ✅ | ✅ |
| Multi-workspace routing | ❌ | ❌ | ❌ | ✅ | ✅ |
| White-label (email/inbox) | ❌ | ❌ | ❌ | ✅ | ✅ |
| SLA de entrega | ❌ | ❌ | ❌ | ❌ | ✅ |

## Regras (validadas por teste)

- **Interseção:** o usuário só recebe em `plano ∩ preferências`. Ex.: quer WhatsApp no Pro → não entra (Pro não tem WhatsApp).
- **Urgente:** `billing.failed` fura quiet hours e limite diário, garantindo push/email/in-app.
- **Quiet hours:** notificações não-urgentes caem para in-app (não intrusivo) ou são suprimidas.
- **Limite diário:** ao atingir, suprime não-urgentes (upsell de plano).
- **Dedup:** mesmo `event_id` não reenvia.

## Upsell embutido

Quando um canal/recurso é bloqueado por plano:
```json
{
  "notification": "in_app",
  "cta": "Desbloqueie alertas no Slack e Telegram",
  "upgrade_url": "https://app.spyfy.io/billing?highlight=notifications"
}
```

## Exemplos (saída real do engine)

```
PRO @14h  -> [in_app, push, email, telegram, slack]
FREE @14h -> [in_app, email]
PRO @23h  -> [in_app]              (quiet hours)
PRO @23h URGENT -> [in_app, push, email, telegram, slack]
PRO limite atingido -> [] (suppressed: daily_limit_reached)
```

## Governança

- Entitlements centralizados (fonte única em código + tabela).
- Mudança de plano → recalcula canais em tempo real.
- Auditoria de entregas por workspace.
