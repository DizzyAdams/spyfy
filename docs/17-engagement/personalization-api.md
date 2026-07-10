# 🔧 Personalization & Engagement API

Endpoints REST que expõem os 5 loops de retenção. Extensão da SpyFy API (`spyfy/api/app.py`) — especificação (a ligação ao app é o próximo passo de implementação).

## Endpoints (propostos)

```
GET  /v1/home/:user_id
     -> build_home_tab(ctx)  | aba personalizada (Loop 1)

GET  /v1/users/:id/health
     -> health_score(snapshot) | { score, risk, drivers, actions } (Loop 2)

POST /v1/game/action
     body { user_id, action }
     -> apply_action(state) | { xp_gained, level, level_up, unlocked } (Loop 3)

GET  /v1/digest/:user_id?period=daily
     -> build_digest(offers, prefs) | "Daily Winners" (Loop 4)

POST /v1/radar/queries
     body { user_id, niche, network, min_score, min_days }
     -> persist RadarQuery (roda em background) (Loop 5)

POST /v1/radar/run/:query_id
     -> radar_report(query, offers) | top + win_prob + edge (Loop 5)
```

## Exemplo (health)

```bash
curl localhost:8000/v1/users/u1/health
# {"score":17.0,"risk":"critical",
#  "drivers":["sem login ha 30+ dias",...],
#  "actions":["email de winback + credito","guiar a 1a clonagem"]}
```

## Como o A13 consome

- `health_score` crítico → A13 envia webhook/`billing.failed`-like `winback`.
- `level_up` → A13 notifica "Level up!".
- `radar_report` com novidade → A13 `offer.scaling`/`alert.triggered`.

## Persistência (planejado)

| Estado | Onde |
|--------|-------|
| `UserContext` | Postgres (`users`) |
| `GameState` (xp/badges/streak) | Postgres + cache |
| `RadarQuery` | Postgres; execução via worker (Temporal/BullMQ) |
| `UsageSnapshot` | ClickHouse (eventos agregados) |

## Testes

Os módulos já têm **17 testes** em `tests/test_features.py` (todos ✅). Os endpoints seguem os mesmos padrões: Pydantic (validação), injeção de dependência, fakes em teste.

## Segurança

- `user_id` validado + scoping (um usuário só vê o próprio).
- Rate limit em `/v1/game/action` (anti-farm de XP).
- Ver [security.md](../09-security/security.md).
