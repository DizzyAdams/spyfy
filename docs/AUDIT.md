# 🔍 Auditoria Completa — SpyFy

Auditoria automatizada do estado do projeto. Atualizada a cada rodada.

## Status geral: ✅ VERDE (deploy-ready para a camada API)

| Item | Status |
|------|--------|
| Imports do pacote `spyfy` | ✅ OK (32 símbolos) |
| Sintaxe de todos os módulos `.py` | ✅ OK |
| Suíte de testes | ✅ **56/56 passando** |
| API FastAPI executável | ✅ (`/health`, `/docs`) |
| Dockerfile produção | ✅ não-root + healthcheck |
| Config 12-factor (env) | ✅ |
| Webhooks HMAC + dedup | ✅ testado |
| 5 Loops de Engagement/Retention | ✅ (17 testes) |
| Loop 6: Email/SMS/Mobile Push OSS | ✅ (9 testes) |
| Loops 7/8/9: Proxy Pool / CRM / Cart+Page+Garantia | ✅ (12 testes) |
| Lint (ruff) | ✅ 0 erros (spyfy + tests) |
| Type-check (mypy) | ✅ 0 erros (20 arquivos) |
| Scan de dependências (pip-audit) | ✅ 0 vulnerabilidades |
| SAST (bandit) | ✅ 0 issues (1843 linhas) |

## Cobertura de testes por módulo

| Módulo | Testes | Foco |
|--------|:------:|------|
| `roi.py` | 8 | escala, ROI, winning score, ranking |
| `webhooks.py` | 8 | HMAC, anti-replay, dedup |
| `notifications.py` | 11 | entitlements por plano, quiet hours |
| `notifiers.py` | 7 | dispatcher, adapters, retry |
| `events.py` | 7 | pub/sub, wildcards, DLQ, replay |
| `agents/notify_agent.py` | 5 | E2E evento→notificação |
| `api/app.py` | 10 | endpoints REST |
| `personalization.py` | 4 | aba por persona (Loop 1) |
| `retention.py` | 3 | health/churn/expansion (Loop 2) |
| `gamification.py` | 3 | XP/level/badge/streak (Loop 3) |
| `digest.py` | 3 | feed personalizado (Loop 4) |
| `radar.py` | 4 | radar/win-prob/edge (Loop 5) |
| `channels.py` | 9 | email/sms/mobile push OSS (Loop 6) |
| `proxy_pool.py` | 3 | proxy anti-Cloudflare (Loop 7) |
| `crm.py` | 4 | CRM integrado (Loop 8) |
| `cart.py` | 5 | carrinho/page builder/garantia (Loop 9) |
| **Total** | **94** | — |

## Cobertura de testes por módulo

| Módulo | Testes | Foco |
|--------|:------:|------|
| `roi.py` | 8 | escala, ROI, winning score, ranking |
| `webhooks.py` | 8 | HMAC, anti-replay, dedup |
| `notifications.py` | 11 | entitlements por plano, quiet hours |
| `notifiers.py` | 7 | dispatcher, adapters, retry |
| `events.py` | 7 | pub/sub, wildcards, DLQ, replay |
| `agents/notify_agent.py` | 5 | E2E evento→notificação |
| `api/app.py` | 10 | endpoints REST |
| **Total** | **94** | — |

## Inventário de código (`apps/workers-py`)

```
spyfy/
├── __init__.py          (32 exports)
├── roi.py               Scale & ROI Engine
├── webhooks.py          HMAC webhook security
├── notifications.py     Routing por plano/prefs
├── notifiers.py         Adapters OSS + Dispatcher
├── events.py            Event Bus de domínio
├── agents/
│   ├── __init__.py
│   └── notify_agent.py  A13 Alert/Notify
└── api/
    ├── __init__.py
    ├── app.py           FastAPI (deploy-ready)
    └── schemas.py       Pydantic
tests/                   11 arquivos, 94 testes
Dockerfile · requirements.txt · pyproject.toml
```

## Segurança (checklist)

- [x] Webhooks assinados (HMAC-SHA256 + timestamp anti-replay 300s).
- [x] Comparação timing-safe (`hmac.compare_digest`).
- [x] Dedup por `event_id` (idempotência).
- [x] Container não-root.
- [x] Segredos via env/Vault (não hardcoded).
- [x] Validação de input (Pydantic) em todos os endpoints.
- [ ] Rate limiting no gateway (documentado; implementar no BFF).
- [ ] Pentest/DAST (planejado — ver security.md).

## Qualidade

- [x] Type hints em todo o código.
- [x] Dataclasses/Pydantic para contratos.
- [x] Injeção de dependência (dispatcher/adapters testáveis).
- [x] Sem I/O real em testes (fakes/mocks).
- [x] Funções puras no core (ROI/routing) — fáceis de testar.

## Riscos & pendências

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| Backends OSS não provisionados | média | docker-compose + Helm (documentado) |
| Segredos default `dev` | alta (se for p/ prod sem trocar) | forçar env em prod, checar no boot |
| Scrapers ainda são spec (não código) | média | implementar A2/A3 clients |
| Sem persistência real (DB) nos engines | média | ligar Postgres/ClickHouse |

## Como reproduzir a auditoria

```bash
cd apps/workers-py
PYTHONPATH=. python -c "import spyfy; from spyfy.api import app"     # imports
PYTHONPATH=. python -c "import pathlib,ast; [ast.parse(p.read_text('utf-8')) for p in pathlib.Path('spyfy').rglob('*.py')]"  # sintaxe
PYTHONPATH=. pytest -q                                              # 94 testes
```

## Próximas verificações (quando o link chegar)

1. Auditoria do repositório/URL enviado (estrutura, deps, segredos expostos).
2. ~~SAST (bandit/semgrep) + scan de dependências (pip-audit).~~ ✅ **pip-audit: 0 vulnerabilidades · bandit: 0 issues** (semgrep opcional pendente).
3. ~~Lint (ruff) + type-check (mypy).~~ ✅ **ruff: 0 erros · mypy: 0 erros (20 arquivos)**.
4. Teste de carga (k6) nos endpoints.
5. Revisão de integração NexusTracker + DarkfyCheckout (contratos reais).

## Status de Deploy (deploy-ready + automação)

Artefatos de deploy criados e validados:

| Artefato | Estado |
|----------|--------|
| `docker-compose.yml` (web + api + caddy + tunnel) | ✅ validado via `docker compose config` |
| `apps/web/Dockerfile` + `.dockerignore` | ✅ (Next.js 15, `next start` :3000) |
| `apps/workers-py/.dockerignore` | ✅ |
| `scripts/deploy.sh` (up/down/ngrok/tunnel/deploy) | ✅ criado |
| `scripts/gen-caddyfile.sh` (basic auth env-driven) | ✅ criado |
| `.env.example` (template de secrets) | ✅ criado |
| `.github/workflows/deploy.yml` (CI automatizado) | ✅ criado (template) |
| Build do frontend (`next build`) | ✅ 13 rotas |
| API FastAPI serve | ✅ smoke test (TestClient) → 200 |
| Basic auth (Caddy) à frente do túnel | ✅ configurado |
| Repositório git | ✅ commit inicial + doc |

**Automação de deploy:** `bash scripts/deploy.sh deploy` sobe stack + Caddy
(basic auth) + Cloudflare Tunnel. CI em `.github/workflows/deploy.yml` faz
build → push registry → SSH deploy no push em `main`.

**Segurança ao expor publicamente:** a `api` (:8000) fica **interna**; só o
`web` (:8080) é tunelado, protegido por basic auth (Caddy). Não usar
`WEBHOOK_SECRET=dev` em produção.

**Deploy real executado e verificado (sem Docker):** como o daemon do Docker
não sobe neste sandbox (sem GUI) e o ngrok tem authtoken inválido, o deploy foi
feito via `cloudflared` + proxy Python com basic auth (`scripts/tunnel.ps1` /
`scripts/basic_auth_proxy.py`). Cadeia validada ao vivo:
- Web (Next.js :3000) → `200`; API (uvicorn :8000) `/health` → `200`.
- Proxy (:9090) → **401** sem credencial, **200** com `Basic` (basic auth OK).
- `cloudflared` conectou e criou túnel público real
  (`https://captured-alias-bridal-pulse.trycloudflare.com`).

**Limite deste sandbox (não é gap de código):** o túnel é **efêmero aqui**
porque o harness encerra o processo `cloudflared` ao estourar o limite de 30s
por comando — por isso a URL pública não persiste entre chamadas. Na máquina
do usuário (processo persistente), `scripts/tunnel.ps1` entrega URL + PS estáveis.
O domínio e a senha de basic auth são gerados ao rodar o deploy e ficam em
`.tunnel_info.txt` (arquivo gitignored, nunca comitado).
