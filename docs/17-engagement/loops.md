# 🎯 Engagement & Retention Features (5 Loops)

Cinco módulos de **retenção + moat competitivo** — o que a concorrência (AdSpy/BigSpy/Minea) **não tem**: cada usuário vê uma aba personalizada, ganha gamificação, recebe digest no melhor horário e confia no **Offer Radar** para não perder oferta nenhuma. Código em `apps/workers-py/spyfy/` (17 testes ✅).

## Loop 1 — Personalization (aba por persona)
`personalization.py` · `test_features.py`

- **`build_home_tab(ctx)`** monta a home conforme `Persona` (media buyer, copywriter, afiliado, agência, infoprodutor).
- Onboarding aparece no topo até concluir.
- Comportamento boosta widgets ("clona muito" → atalho de clones).
- Nichos favoritos viram atalhos.
- Free **tranca** widgets pro (upsell embutido).
- **`infer_persona()`** deduz persona pelo histórico de ações.

```python
tab = build_home_tab(UserContext("u1", Persona.MEDIA_BUYER, "pro", ...))
# media_buyer vê: Escalando agora > +30d > Concorrentes (pro) > nichos
```

## Loop 2 — Retention Engine (health + churn)
`retention.py`

- **`health_score(u)`** → 0–100 por recência, frequência, ativação (aha = salvar + clonar), alertas.
- **`ChurnRisk`**: healthy / at_risk / critical / churned.
- **Playbook de re-engajamento** por risco (winback + crédito, onboarding assistido).
- **`expansion_ready()`**: sinaliza upsell (saudável + batendo limites).
- POWER (ativo) = 100/healthy · IDLE (sumido) = 17/critical + winback.

## Loop 3 — Gamification
`gamification.py`

- **XP** por ação (clone +25, first_clone +100, marketplace +40).
- **Níveis**: Explorador → Caçador → Analista → Estrategista → Mestre → Lenda.
- **Badges**: first_clone, clone_10/100, trend_hunter, streak_7/30, seller.
- **Streaks** diários (login consecutivo).
- Barra de progresso ao próximo nível.

```python
ev = apply_action(state, "clone")  # first_clone desbloqueia badge
if ev.level_up: notify("Level up!")   # via A13
```

## Loop 4 — Smart Digest & Personalized Feed
`digest.py`

- **`personalized_score()`** não é só winning_score: boosta nicho fav (+20), rede fav (+8), sinal hot (+25), novidade (+12); penaliza já visto (−30).
- **`build_digest()`** monta o "Daily Winners" de cada usuário.
- **`optimal_send_hour()`** envia no pico de login do usuário (menos 1h) → abre mais.

## Loop 5 — Offer Radar & Win Probability (moat)
`radar.py`

- **Saved-searches que rodam sozinhas** em background (`run_radar`).
- **Early-mover bonus**: detecta quem **vê primeiro** (`first_seen_rank`) → "🥇 Você é dos primeiros".
- **`win_probability()`**: logística sobre longevidade + variantes + sinal → P(oferta vencer).
- **`should_alert()`**: ofertas NOVAS no radar → dispara alerta (A13).

## Como se encaixam (fluxo de retenção)

```
Usuário loga
   ├─ Gamification: streak + XP (Loop 3)
   ├─ Personalization: home DIFERENTE por persona (Loop 1)
   ├─ Digest: ranking personalizado no melhor horário (Loop 4)
   ├─ Radar: roda saved-searches, alerta novidades (Loop 5)
   └─ Retention: health score vigia churn; se cair → winback (Loop 2)
```

## Vantagem vs concorrência

| Recurso | SpyFy | AdSpy/BigSpy/Minea |
|---------|:------:|:----------------------:|
| Aba personalizada por persona | ✅ | ❌ |
| Gamification (XP/badges) | ✅ | ❌ |
| Digest no horário ótimo | ✅ | ❌ |
| Offer Radar (early-mover) | ✅ | ❌ |
| Win probability | ✅ | ❌ |
| Health score / churn | ✅ | ❌ |

## Documentos relacionados
- [personalization-api.md](personalization-api.md) — endpoints REST das features.
- [retention-playbook.md](retention-playbook.md) — operação de winback/upsell.
