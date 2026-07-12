# Deploy SpyFy API no Coolify (free tier self-hosted)

[Coolify](https://coolify.io) é uma PaaS open-source que você hospeda na
própria VM. O backend SpyFy (`apps/workers-py`) já é uma imagem Docker
completa, então o deploy é "aponte o compose e clique em Deploy".

## Pré-requisitos
- Uma VM Linux (Ubuntu 22.04+) — dá pra usar **Oracle Cloud Always Free** (2
  ARM de 4GB, gratuitas) ou Hetzner/VPS barata.
- Docker instalado (o script do Coolify já instala).
- Repo `DizzyAdams/spyfy` clonado na VM (ou conecte o GitHub ao Coolify).

## 1. Instalar o Coolify
```bash
curl -fsSL https://get.coolify.io | bash
```
Abra `http://<ip-da-vm>:8000`, crie a conta admin e o projeto `spyfy`.

## 2. Criar o recurso Docker Compose
- Painel → **New Resource** → **Docker Compose**.
- Em "Compose file / repository", aponte para
  `apps/workers-py/docker-compose.yml` do repo (ou cole o conteúdo do arquivo).
- Coolify detecta o service `spyfy-api` e a porta.

## 3. Variáveis de ambiente (projeto)
| Var | Valor sugerido |
|-----|----------------|
| `PORT` | `8000` (Coolify injeta automaticamente em alguns provedores) |
| `WEB_CONCURRENCY` | `1` (free tier / pouca RAM) |
| `WEBHOOK_SECRET` | segredo forte (NUNCA `dev` em produção) |
| `NTFY_URL` | `https://ntfy.sh/spyfy` |
| `CORS_ORIGINS` | `https://spyfyprod.vercel.app,http://localhost:3000` |

## 4. Deploy e healthcheck
- Clique **Deploy**. O Coolify usa o `healthcheck` de `/health` para marcar o
  container como *Healthy*.
- A URL pública fica em **Domains** (pode usar domínio próprio ou o
  `*.coolify.dev` gratuito).

## 5. Conectar o frontend (Vercel)
No projeto Vercel, defina:
```
NEXT_PUBLIC_API_URL=<url-do-coolify>
```
O frontend degrada graciosamente ("Backend offline") se a API não responder.

## Notas de custo / free tier
- RAM: com 1 worker e RAG em memória, o backend roda bem em **512MB–1GB**.
  chromadb/langgraph são pesados em memória; em VM de 4GB folga.
- O backend roda **100% offline** (embeddings determinísticos, sem GPU/LLM),
  então não há custo de API de LLM.
- Sem cold-start agressivo (diferente do Render free).

## Rollback / atualização
A cada push na `main`, basta **Redeploy** no Coolify (ou automatize com webhook
do GitHub). Imagens são reconstruídas a partir do `Dockerfile`.

## Deploy automatizado via API (sem clicar na UI)

Se preferir disparar o deploy por script (CI/CD, ou sem acesso ao painel):

```powershell
# Requer token Coolify com ability "deploy" (e "read" para descoberta por nome).
$env:COOLIFY_TOKEN = 'seu-token'
.\scripts\deploy-coolify.ps1 `
  -CoolifyHost https://seu.coolify.dev `
  -Token $env:COOLIFY_TOKEN `
  -ApplicationName spyfy-api -Force
```

O script (`scripts/deploy-coolify.ps1`) faz healthcheck da API, resolve o UUID
da aplicação por nome (`GET /api/v1/applications`) e dispara o deploy
(`POST /api/v1/applications/{uuid}/deployments`). A rota de deploy é
sobrescrevível via `-DeployEndpoint` caso sua instância use padrão diferente.
Use `-DryRun` para validar a conexão sem disparar deploy.

