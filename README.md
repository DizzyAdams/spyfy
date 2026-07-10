# 🕵️ SpyFy — Ad Intelligence & Offer Cloning Platform

> **A biblioteca definitiva para encontrar, analisar e clonar ofertas vencedoras de anúncios (ads).**
> Descubra o que está escalando agora, engenharia reversa de funis, e replique ofertas de alto desempenho em minutos.

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)]()
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue)]()
[![License](https://img.shields.io/badge/license-Proprietary-red)]()
[![Docs](https://img.shields.io/badge/docs-5k%2B%20linhas-green)]()

---

## 📌 O que é o SpyFy?

O **SpyFy** é uma plataforma de *ad intelligence* e *offer cloning* que combina:

- 🔎 **Descoberta de ofertas** — motor de busca sobre milhões de anúncios ativos (Meta Ads Library, TikTok Creative Center, Google Ads Transparency, YouTube, native ads).
- 🧬 **Clonagem de ofertas** — engenharia reversa de landing pages, VSLs, funis, upsells e criativos.
- 📊 **Analytics de mercado** — detecção de ofertas em escala, tendências de nicho, longevidade de campanhas.
- 🤖 **Sub-agents de IA** — agentes especializados que raspam, classificam, transcrevem e reconstroem ofertas automaticamente.
- 🗂️ **Biblioteca colaborativa** — swipe file compartilhado, coleções, tags e alertas.

O objetivo: transformar **dias de pesquisa manual** em **minutos de inteligência acionável**.

---

## 🎯 Para quem é

| Persona | Dor | Como o SpyFy resolve |
|---------|-----|----------------------|
| Media Buyer | Não sabe qual criativo/oferta escalar | Ranking de ofertas por longevidade e volume estimado |
| Copywriter | Precisa de referências de ângulos | Swipe file com transcrições de VSLs e headlines |
| Afiliado | Quer clonar funil validado | Cloner de landing page + estrutura de funil |
| Agência | Precisa provar ROI ao cliente | Relatórios de concorrência e benchmarks de nicho |
| Infoprodutor | Quer validar oferta antes de lançar | Análise de saturação de nicho |

---

## 🧭 Índice da Documentação

### 00 — Visão Geral
- [Visão & Missão](docs/00-overview/vision.md)
- [Visão de Produto](docs/00-overview/product-overview.md)
- [Personas & Casos de Uso](docs/00-overview/personas.md)
- [Glossário](docs/00-overview/glossary.md)

### 01 — Arquitetura
- [Arquitetura de Sistema](docs/01-architecture/system-architecture.md)
- [Event Bus & A13 Notify Agent](docs/01-architecture/event-bus.md)
- [Tech Stack Completa](docs/01-architecture/tech-stack.md)
- [Modelo de Dados](docs/01-architecture/data-model.md)
- [Infraestrutura](docs/01-architecture/infrastructure.md)

### 02 — Time
- [Estrutura do Time](docs/02-team/team-structure.md)
- [Engenheiros Sênior por Spec](docs/02-team/senior-engineers.md)
- [Sub-Agents de IA](docs/02-team/sub-agents.md)

### 03 — Features
- [Offer Discovery Engine](docs/03-features/offer-discovery.md)
- [Offer Cloner](docs/03-features/offer-cloner.md)
- [Ad Library](docs/03-features/ad-library.md)
- [Analytics & Insights](docs/03-features/analytics.md)

### 04 — Backend
- [API Design](docs/04-backend/api-design.md)
- [Scraping Engine](docs/04-backend/scraping-engine.md)
- [Banco de Dados](docs/04-backend/database.md)
- [Autenticação & Billing](docs/04-backend/auth-billing.md)

### 05 — Frontend
- [UI/UX & Design System](docs/05-frontend/ui-ux.md)
- [Design System Pro (tokens/a11y)](docs/05-frontend/design-system-pro.md)
- [Motion & Interações (Framer Motion)](docs/05-frontend/motion.md)
- [Componentes](docs/05-frontend/components.md)

### 06 — Data Pipeline
- [Ingestão](docs/06-data-pipeline/ingestion.md)
- [Enrichment & Normalização](docs/06-data-pipeline/enrichment.md)

### 07 — Inteligência Artificial (LangGraph/LangChain)
- [Agentes de IA](docs/07-ai/ai-agents.md)
- [Modelos de ML](docs/07-ai/ml-models.md)
- [Arquitetura LangGraph/LangChain](docs/07-ai/langgraph-architecture.md)
- [Subgraphs & Agents (código)](docs/07-ai/langgraph-agents.md)
- [Real-Time Cloning Engine](docs/07-ai/realtime-cloning.md)

### 08 — DevOps
- [CI/CD](docs/08-devops/ci-cd.md)
- [Deploy & Infra as Code](docs/08-devops/deployment.md)
- [🚀 Deploy Guide (API deploy-ready)](docs/08-devops/deploy-guide.md)
- [Observabilidade](docs/08-devops/observability.md)
- [Runbooks](docs/08-devops/runbooks.md)
- [🔍 Auditoria Completa](docs/AUDIT.md)

### 09 — Segurança & Compliance
- [Segurança](docs/09-security/security.md)
- [Compliance & Legal](docs/09-security/compliance.md)

### 10 — Roadmap
- [Roadmap & Milestones](docs/10-roadmap/roadmap.md)
- [OKRs](docs/10-roadmap/okrs.md)

### 11 — Qualidade
- [Estratégia de Testes](docs/11-quality/testing-strategy.md)

### 12 — Mercado
- [Análise de Concorrentes](docs/12-market/competitors.md)

### 13 — 🌐 Ecossistema (fora do comum)
- [Visão do Ecossistema](docs/13-ecosystem/overview.md)
- [SpyFy Copilot (agente conversacional)](docs/13-ecosystem/copilot.md)
- [Marketplace de Ofertas](docs/13-ecosystem/marketplace.md)
- [Plugins & Apps Platform](docs/13-ecosystem/plugins-platform.md)
- [Community & Creator Economy](docs/13-ecosystem/community.md)
- [Monorepo Scaffold (executável)](docs/13-ecosystem/monorepo-scaffold.md)

### 14 — ⛏️ Mineração & Time de 14 Agents (tempo real)
- [Time de 14 Agents Especializados](docs/14-mining/team-14-agents.md)
- [Browser Mining Engine (Playwright)](docs/14-mining/browser-mining.md)
- [Library Mining Engine (API/libs)](docs/14-mining/library-mining.md)
- [Scale & ROI Engine (código validado)](docs/14-mining/scale-roi-engine.md)
- Código: `apps/workers-py/spyfy/roi.py` · Testes: `apps/workers-py/tests/test_roi.py` (8/8 ✅)

### 15 — 🔗 Integrations API (webhooks)
- [Visão Geral da Integrations API](docs/15-integrations/overview.md)
- [NexusTracker (tracking/atribuição)](docs/15-integrations/nexustracker.md)
- [DarkfyCheckout (checkout/funil)](docs/15-integrations/darkfycheckout.md)
- [Webhooks (HMAC, eventos, retries)](docs/15-integrations/webhooks.md)
- Código: `apps/workers-py/spyfy/webhooks.py` · Testes: `tests/test_webhooks.py` (8/8 ✅)

### 16 — 🔔 Notificações (open-source)
- [Notification Stack Open-Source (Novu/Apprise/ntfy/Gotify)](docs/16-notifications/open-source-stack.md)
- [Visão Geral](docs/16-notifications/overview.md)
- [Entitlements por Plano](docs/16-notifications/plans-matrix.md)
- [Canais](docs/16-notifications/channels.md)
- [Email · SMS · Mobile Push (Loop 6)](docs/16-notifications/email-sms-mobile.md)
- Código: `apps/workers-py/spyfy/{notifications,channels}.py` · Testes: `tests/test_notifications.py` + `tests/test_channels.py` (16/16 ✅)


### 17 — Engagement & Retention (5 Loops)
- [Loops (Personalizacao/Gamificacao/Radar/Retention/Digest)](docs/17-engagement/loops.md)
- [Personalization & Engagement API](docs/17-engagement/personalization-api.md)
- [Retention Playbook](docs/17-engagement/retention-playbook.md)
- Codigo: `spyfy/{personalization,retention,gamification,digest,radar}.py` · Testes: `tests/test_features.py` (17/17 OK)

### 18 — Proxies · CRM · Cart/Page+Garantia (Loops 7/8/9)
- [Visao (Proxy Pool/CRM/Cart+Page+Garantia)](docs/18-proxies-crm-cart/loops-7-8-9.md)
- [Proxy Pool Guide (anti-Cloudflare)](docs/18-proxies-crm-cart/proxy-guide.md)
- [CRM Integrado Guide](docs/18-proxies-crm-cart/crm-guide.md)
- [Cart + Page Builder + Garantia 24h](docs/18-proxies-crm-cart/cart-garantia.md)
- Codigo: `spyfy/{proxy_pool,crm,cart}.py` · Testes: `tests/test_proxies_crm_cart.py` (12/12 OK)


### Scrapers por rede
- [Meta Ad Library](docs/04-backend/scrapers/meta.md)
- [TikTok](docs/04-backend/scrapers/tiktok.md)
- [Google Ads Transparency](docs/04-backend/scrapers/google.md)

### Extras
- [Guia de Contribuição](docs/CONTRIBUTING.md)
- [Extensão Chrome](docs/03-features/extension.md)
- [SDK & CLI](docs/04-backend/sdk-reference.md)
- [OpenAPI Spec](docs/04-backend/openapi.yaml)
- [ADRs](docs/01-architecture/adr.md)

---

## ⚡ Quick Start (Dev)

```bash
# Clonar
git clone https://github.com/spyfy/spyfy.git && cd spyfy

# Subir stack local
docker compose up -d

# Backend
cd apps/api && pnpm install && pnpm dev

# Frontend
cd apps/web && pnpm install && pnpm dev

# Workers de scraping
cd apps/workers && python -m spyfy.workers
```

Acesse `http://localhost:3000`.

---

## 🏗️ Tech Stack (resumo)

| Camada | Tecnologias |
|--------|-------------|
| Frontend | Next.js 15, React 19, TypeScript, TailwindCSS, shadcn/ui, TanStack Query, Zustand |
| Backend | Node.js (NestJS), Python (FastAPI), tRPC, GraphQL |
| Scraping | Playwright, Crawlee, Scrapy, Puppeteer, proxy rotation |
| IA | OpenAI, Anthropic Claude, Whisper, embeddings, LangGraph |
| Dados | PostgreSQL, Redis, ClickHouse, Elasticsearch, S3/R2 |
| Fila | BullMQ, RabbitMQ, Temporal |
| Infra | Kubernetes, Terraform, AWS/Cloudflare, Docker |
| Observabilidade | Grafana, Prometheus, Loki, Sentry, OpenTelemetry |

Ver detalhes em [tech-stack.md](docs/01-architecture/tech-stack.md).

---

## 🚀 Deploy & Cloud Tunnel (automático)

O stack sobe com `docker compose` e pode ser exposto publicamente via túnel
(ngrok ou Cloudflare Tunnel) com **basic auth na frente** (Caddy), para não
deixar a API sem autenticação exposta na internet.

```bash
cp .env.example .env          # preencha WEBHOOK_SECRET, BASIC_AUTH_PASSWORD, tokens
bash scripts/deploy.sh deploy # sobe stack + Caddy + Cloudflare Tunnel
```

- O **domínio** do túnel é impresso pelo próprio ngrok/cloudflared ao subir
  (ex.: `https://<random>.ngrok-free.app` ou seu domínio fixo na Cloudflare).
- A **senha (PS)** é a `BASIC_AUTH_PASSWORD` que você definiu no `.env` — ela
  **não é enviada por chat**; fica só no seu `.env` (ou secret do CI).
- A `api` (:8000) fica **interna**; só o `web` (:8080 via Caddy) é tunelado.
- CI automatizado em `.github/workflows/deploy.yml` (build → push registry →
  SSH deploy). Configure os secrets do repo para ativar.

> ⚠️ Nunca rode com `WEBHOOK_SECRET=dev` em produção e não exponha a API sem
> autenticação.

## 📄 Licença

Proprietary © 2026 SpyFy. Todos os direitos reservados.
