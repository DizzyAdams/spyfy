# 📒 Retention Playbook (operacional)

Como o time opera retenção usando o Retention Engine (Loop 2) + demais loops. Objetivo: **LTV máximo, churn mínimo**.

## Monitoramento (diário)

| Sinal | Fonte | Ação se ruim |
|--------|-------|----------------|
| % usuários `critical`/`churned` | `health_score` | campanha de winback |
| % sem `first_clone` em 7d | `UsageSnapshot` | guiar a 1ª clonagem |
| streak médio | `gamification` | lembrete diário + XP bônus |
| abertura de digest | `digest` | trocar horário/`optimal_send_hour` |
| alertas de radar ignorados | `radar` | reafinar `RadarQuery` |

## Playbook por risco

### Healthy (score ≥ 70)
- **Upsell**: `expansion_ready()` → oferecer plano superior / seats.
- **Advocacy**: pedir review / indicação (afiliado).

### At risk (45–69)
- Digest personalizado no horário ótimo.
- Destacar 1 oferta escalando no nicho dele.

### Critical (45–)
- **Winback**: email + **crédito de clonagem grátis**.
- Onboarding assistido / call (se LTV alto).

### Churned (idle ≥ 45d)
- Desconto de reativação.
- Pesquisa de cancelamento (aprender motivo).

## Gatilhos ligados ao A13 (automáticos)

```
health_score critical  ─▶ evento "winback.trigger"  ─▶ A13 ─▶ email+crédito
first_clone == 0  (>7d) ─▶ "onboarding.nudge"  ─▶ A13 ─▶ guião
expansion_ready       ─▶ "upsell.trigger"     ─▶ A13 ─▶ offer upgrade
level_up             ─▶ "level.up"            ─▶ A13 ─▶ notificação
radar new hit       ─▶ "offer.scaling"       ─▶ A13 ─▶ alerta
```

## Anti-churn product

- **Onboarding de aha**: levar a **1ª clonagem** em < 48h (maior preditor de retenção).
- **Streak**: login diário mantém o hábito (gamification).
- **Radar**: sensação de "não perco nada" (moat).

## Metas

| Métrica | Meta |
|---------|------|
| Churn 30d | < 4% |
| Ativação (1ª clone em 7d) | > 60% |
| Retorno de winback | > 15% |
| NPS | > 50 |

## Por que bate a concorrência

AdSpy/BigSpy/Minea entregam **dados**, não **retenção**. O SpyFy entrega **hábito + moat pessoal** (aba única, gamification, radar early-mover). Isso é o que mantém o cliente pagando mês após mês.
