# Deploy do Backend SpyFy (FastAPI) em plataforma FREE

O backend (`apps/workers-py`) é uma FastAPI 100% funcional e validada
(125 testes + 12 endpoints vivos, incluindo o pipeline LangGraph autônomo e a
memória RAG offline). Este doc descreve como hospedá-lo **de graça** em uma
plataforma open-source/SaaS, com automação completa.

> ⚠️ O `requirements.txt` de produção foi corrigido para incluir `chromadb` e
> `langgraph` (importados na subida da app). O app roda **100% offline** por
> padrão (embeddings determinísticos), então NENHUM token de LLM é necessário.

---

## Opção A — Render (recomendado, free tier, mais simples)

1. Crie conta free em https://render.com (sem cartão).
2. Dashboard → **New** → **Web Service** → conecte o repo GitHub `DizzyAdams/spyfy`.
3. O `render.yaml` (na raiz) é detectado automaticamente:
   - `runtime: docker`, usa `apps/workers-py/Dockerfile`
   - `healthCheckPath: /health`
   - honra `$PORT` (já tratado no Dockerfile)
4. Defina as env vars (Render não versiona secrets):
   - `WEBHOOK_SECRET` → segredo forte (**nunca** `dev`)
   - `NTFY_URL` → `https://ntfy.sh/spyfy` (ou seu domínio)
   - `CORS_ORIGINS` → inclua `https://spyfyprod.vercel.app`
5. Deploy automático a cada push na `main`. URL: `https://spyfy-api.onrender.com`

Limites do free tier: 512MB RAM (1 worker, já configurado), dorme após 15min
ocioso (cold start ~30–60s), RAG em memória zera no restart. Para produção,
use o plan pago ou a Opção B.

Deploy via CLI (opcional):
```powershell
$env:RENDER_API_KEY='rnd_xxx'
pwsh scripts/deploy-backend.ps1 -Platform render
```

## Opção B — Hugging Face Spaces (open-source, Docker, 16GB RAM free)

1. Crie um **Space** do tipo **Docker**.
2. O backend usa o `Dockerfile` de `apps/workers-py` (que já honra `$PORT`).
3. Defina `WEBHOOK_SECRET` nos Secrets do Space.
4. O frontend consome `NEXT_PUBLIC_API_URL=<url-do-space>`.

Vantagem: 16GB RAM (chromadb/langgraph folgam), sem cold-start agressivo.

## Opção C — Coolify (self-hosted, Docker, free tier)

[Coolify](https://coolify.io) é uma PaaS open-source auto-hospedada (você
fornece a VM barata/gratuita — e.g. Oracle Always Free, Hetzner, VPS). O
backend já roda via Docker, então o deploy é trivial:

1. Instale o Coolify na sua VM (1 comando: `curl -fsSL https://get.coolify.io | bash`).
2. No painel → **New Resource** → **Docker Compose** → aponte para
   `apps/workers-py/docker-compose.yml` (ou cole o conteúdo).
3. Coolify injeta `$PORT`; o `Dockerfile` e o `docker-compose.yml` já a honram.
4. Defina as env vars (Coolify → variáveis do projeto):
   - `WEBHOOK_SECRET` → segredo forte
   - `NTFY_URL` → `https://ntfy.sh/spyfy`
   - `CORS_ORIGINS` → inclua `https://spyfyprod.vercel.app`
5. Deploy. O healthcheck `/health` é usado pelo Coolify para considerar "Healthy".

Vantagem: controle total, sem limite de cold-start agressivo, RAM que você
escolher (chromadb/langgraph folgam em 1–2GB). Free tier efetivo se a VM for
gratuita. Veja `docs/08-devops/coolify.md` para o passo a passo detalhado.

## Opção D — Cloudflare Tunnel (free, sem conta, efêmero)

Para expor um backend rodando localmente sem conta:
```powershell
# 1) sobe a API
cd apps/workers-py; $env:PYTHONPATH='.'; uvicorn spyfy.api.app:app --port 8000
# 2) em outro terminal, tunel via cloudflared (ja instalado)
cloudflared tunnel --url http://localhost:8000
```
A URL `*.trycloudflare.com` é efêmera (muda a cada execução). Bom para demo;
para produção prefira A ou B.

---

## Frontend (Vercel) consumindo o backend

O frontend (`apps/web`) lê `NEXT_PUBLIC_API_URL` em build time e degrada
graciosamente (mostra "Backend offline") se a API não responder. Para apontar
no Vercel:
```powershell
vercel env add NEXT_PUBLIC_API_URL production   # cole a URL do Render/HF
vercel --prod
```
Ou edite `deploy.ps1` para passar `-e NEXT_PUBLIC_API_URL=<url>`.

## CI

`.github/workflows/ci-backend.yml` roda `ruff` + `mypy` + `pytest` + smoke de
import da app em cada push/PR em `apps/workers-py`.
