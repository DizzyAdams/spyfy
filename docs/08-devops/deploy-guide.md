# 🚀 Deploy Guide (API deploy-ready) — SpyFy

Guia para subir a **SpyFy API** (FastAPI) em produção. A app real está em `apps/workers-py/spyfy/api/app.py` e é 100% testada (56 testes ✅).

## O que a API expõe

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | healthcheck (liveness/readiness) |
| GET | `/v1/version` | versão |
| GET | `/v1/events/types` | catálogo de eventos |
| POST | `/v1/offers/estimate` | ROI/escala/winning score |
| POST | `/v1/notify` | roteia + entrega notificação |
| POST | `/v1/webhooks/{provider}` | recebe webhook assinado (NexusTracker/Darkfy) |

Docs interativas automáticas: `/docs` (Swagger) e `/redoc`.

## Rodar local

```bash
cd apps/workers-py
pip install -r requirements.txt
uvicorn spyfy.api.app:app --reload --port 8000
# http://localhost:8000/docs
```

## Testes

```bash
PYTHONPATH=. pytest -q          # 56 testes
```

## Docker

```bash
cd apps/workers-py
docker build -t spyfy-api .
docker run -p 8000:8000 \
  -e WEBHOOK_SECRET=troque-me \
  -e NOVU_API_KEY=... \
  -e NTFY_URL=https://ntfy.spyfy.io \
  spyfy-api
```

- Imagem `python:3.12-slim`, **usuário não-root**, healthcheck embutido.
- Servidor: **gunicorn + UvicornWorker** (4 workers).

## Variáveis de ambiente

| Var | Uso | Default |
|-----|-----|---------|
| `WEBHOOK_SECRET` | segredo HMAC padrão | `dev` |
| `WEBHOOK_SECRET_NEXUSTRACKER` | segredo do NexusTracker | herda default |
| `WEBHOOK_SECRET_DARKFY` | segredo do DarkfyCheckout | herda default |
| `NOVU_API_KEY` | Novu (in-app/email) | vazio |
| `NTFY_URL` | ntfy self-host | ntfy.spyfy.io |

## Exemplos de chamada

### ROI/escala
```bash
curl -X POST localhost:8000/v1/offers/estimate -H 'content-type: application/json' -d '{
  "first_seen":"2026-05-08T00:00:00+00:00","last_seen":"2026-07-10T00:00:00+00:00",
  "creative_variants":9,"est_impressions_low":1000000,"est_impressions_high":5000000,
  "engagement":8200,"networks":2,"countries":3,
  "avg_ticket":57,"cvr":0.025,"ctr":0.014,"cpm":14 }'
# -> winning_score, scaling_signal:"hot", est_roi_pct, ...
```

### Webhook assinado (inbound)
```bash
# assinar: HMAC_SHA256(secret, "{timestamp}.{body}")
curl -X POST localhost:8000/v1/webhooks/darkfy \
  -H "X-SpyFy-Signature: sha256=..." -H "X-SpyFy-Timestamp: 1780000000" \
  -H "content-type: application/json" \
  -d '{"event_id":"wh_1","type":"order.paid","data":{"amount":96}}'
```

## Kubernetes (resumo)

```yaml
# probes
livenessProbe:  { httpGet: { path: /health, port: 8000 }, periodSeconds: 15 }
readinessProbe: { httpGet: { path: /health, port: 8000 }, periodSeconds: 10 }
resources:
  requests: { cpu: 250m, memory: 256Mi }
  limits:   { cpu: "1",  memory: 512Mi }
```
- HPA por CPU + ingress TLS + secrets via Vault/External Secrets.
- Ver [deployment.md](deployment.md) e [infrastructure.md](../01-architecture/infrastructure.md).

## Checklist deploy-ready

- [x] App importável e testada (56 testes).
- [x] Healthcheck (`/health`).
- [x] Dockerfile não-root + healthcheck.
- [x] Config via env (12-factor).
- [x] Webhooks com verificação HMAC + dedup.
- [x] OpenAPI automática (`/docs`).
- [ ] Segredos reais no Vault (preencher no deploy).
- [ ] Backends OSS (Novu/ntfy) provisionados.
- [ ] Observabilidade (OTel) conectada.

## CI/CD

- Build da imagem no merge → push registry → ArgoCD sync.
- Testes + audit rodam no CI (ver [ci-cd.md](ci-cd.md)).
