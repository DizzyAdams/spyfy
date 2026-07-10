# 🧰 Tech Stack Completa — SpyFy

Stack detalhada por camada, com justificativa de escolha e alternativas consideradas.

## Linguagens

| Linguagem | Onde | Por quê |
|-----------|------|---------|
| **TypeScript** | Frontend, BFF, SDK, API | Type safety, ecossistema, DX. |
| **Python** | Workers de scraping, IA/ML, transcrição | Melhor ecossistema de scraping e ML. |
| **Go** | Serviços de alta performance (indexer, proxy manager) | Concorrência, baixa latência. |
| **SQL** | Postgres/ClickHouse | Consultas analíticas e transacionais. |
| **Rust** | (futuro) parser de HTML crítico | Performance + segurança de memória. |

## Frontend

| Categoria | Escolha | Alternativas |
|-----------|---------|--------------|
| Framework | **Next.js 15 (App Router)** | Remix, SvelteKit |
| UI lib | **React 19** | Solid, Svelte |
| Estilo | **TailwindCSS** | CSS Modules, Panda |
| Componentes | **shadcn/ui + Radix** | MUI, Mantine |
| Estado servidor | **TanStack Query** | SWR |
| Estado cliente | **Zustand** | Redux Toolkit, Jotai |
| Forms | **React Hook Form + Zod** | Formik |
| Gráficos | **Recharts / visx** | Chart.js |
| Tabelas | **TanStack Table** | AG Grid |
| Animação | **Framer Motion** | GSAP |
| i18n | **next-intl** | i18next |
| Tipo RPC | **tRPC** | REST puro |

## Backend

| Categoria | Escolha | Alternativas |
|-----------|---------|--------------|
| BFF/API | **NestJS** | Fastify puro, Express |
| API Python | **FastAPI** | Flask, Django REST |
| GraphQL | **Apollo Server** | Yoga, Mercurius |
| RPC | **tRPC / gRPC** | — |
| Validação | **Zod / Pydantic** | class-validator |
| ORM (TS) | **Prisma / Drizzle** | TypeORM |
| ORM (Py) | **SQLAlchemy** | Tortoise |

## Scraping & Automação

| Ferramenta | Uso |
|-----------|-----|
| **Playwright** | Engine principal (headless, multi-browser). |
| **Crawlee** | Orquestração de crawling em Node. |
| **Scrapy** | Crawling em larga escala (Python). |
| **Puppeteer** | Fallback específico Chrome. |
| **Proxy pools** | Bright Data / Oxylabs / proxies residenciais. |
| **Anti-bot** | rotação de fingerprint, stealth plugins, resolvers de captcha. |

## IA / ML

| Ferramenta | Uso |
|-----------|-----|
| **OpenAI GPT** | Extração de copy, classificação, resumos. |
| **Anthropic Claude** | Reconstrução de estrutura de funil, análise longa. |
| **Whisper** | Transcrição de VSLs. |
| **Embeddings (text-embedding-3 / bge)** | Busca semântica. |
| **LangGraph / LangChain** | Orquestração de sub-agents. |
| **pgvector** | Armazenamento de vetores. |
| **Sentence Transformers** | Embeddings self-hosted. |

## Dados

| Sistema | Uso |
|---------|-----|
| **PostgreSQL** | OLTP principal (usuários, ofertas, coleções). |
| **ClickHouse** | Analytics/OLAP (métricas de anúncios, tendências). |
| **Elasticsearch/OpenSearch** | Busca full-text. |
| **Redis** | Cache, sessões, filas, rate limit. |
| **S3 / Cloudflare R2** | Assets, snapshots, clones. |
| **pgvector** | Busca vetorial. |

## Mensageria / Orquestração

| Sistema | Uso |
|---------|-----|
| **BullMQ (Redis)** | Filas de jobs de curta duração. |
| **RabbitMQ** | Pub/sub de eventos de domínio. |
| **Temporal** | Workflows longos (clonagem de funil). |
| **Kafka** (futuro) | Streaming de eventos em alta escala. |

## Infra / DevOps

| Ferramenta | Uso |
|-----------|-----|
| **Docker** | Containerização. |
| **Kubernetes (EKS/GKE)** | Orquestração. |
| **Terraform** | Infra as Code. |
| **Helm** | Deploy de charts. |
| **ArgoCD** | GitOps. |
| **GitHub Actions** | CI/CD. |
| **Cloudflare** | CDN, WAF, R2, Workers. |
| **AWS** | Compute, storage, DB gerenciado. |

## Observabilidade

| Ferramenta | Uso |
|-----------|-----|
| **Prometheus** | Métricas. |
| **Grafana** | Dashboards. |
| **Loki** | Logs. |
| **Tempo / OpenTelemetry** | Tracing distribuído. |
| **Sentry** | Erros (front e back). |
| **PostHog** | Product analytics. |

## Qualidade / Testes

| Ferramenta | Uso |
|-----------|-----|
| **Vitest / Jest** | Unit (TS). |
| **Pytest** | Unit (Python). |
| **Playwright Test** | E2E. |
| **k6** | Load testing. |
| **ESLint + Prettier** | Lint/format TS. |
| **Ruff + Black** | Lint/format Python. |
| **Biome** | (avaliação) all-in-one JS. |

## Segurança

| Ferramenta | Uso |
|-----------|-----|
| **Auth: Clerk / Auth.js** | Autenticação. |
| **Vault** | Secrets. |
| **Snyk / Trivy** | Scan de dependências/imagens. |
| **OWASP ZAP** | Pentest automatizado. |

## Repositório (monorepo)

```
spyfy/
├── apps/
│   ├── web/            # Next.js
│   ├── api/            # NestJS BFF
│   ├── workers-node/   # Crawlee/BullMQ
│   ├── workers-py/     # Scrapy/IA
│   └── extension/      # Chrome MV3
├── packages/
│   ├── sdk-ts/         # @spyfy/sdk
│   ├── ui/             # design system
│   ├── config/         # eslint/tsconfig
│   └── schemas/        # Zod compartilhado
├── infra/
│   ├── terraform/
│   └── helm/
└── docs/
```
