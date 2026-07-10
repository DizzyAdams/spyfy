# 👷 Engenheiros Sênior por Spec — SpyFy

Cada área (spec) do produto tem um **engenheiro sênior owner**, com escopo, responsabilidades, stack e critérios de sucesso claros. Este documento é a "carta de responsabilidade" técnica.

---

## 1. Sr. Backend Engineer — Discovery/Search
- **Owner de:** motor de busca, ranking, feed de ofertas.
- **Stack:** NestJS, Elasticsearch/OpenSearch, pgvector, Redis, TypeScript.
- **Responsabilidades:**
  - Projetar índices e queries de busca híbrida (full-text + semântica).
  - Implementar `winning_score` e ranking.
  - Cache e latência < 300ms p95.
- **Entregáveis:** API de busca, indexer, tuning de relevância.
- **Sucesso:** relevância (NDCG), latência, freshness.
- **Skills:** IR (information retrieval), sistemas distribuídos, tuning de ES.

## 2. Sr. Backend Engineer — Scraping/Cloner
- **Owner de:** engine de scraping e clonagem.
- **Stack:** Python (Scrapy, Playwright), Crawlee (Node), Temporal, proxies.
- **Responsabilidades:**
  - Scrapers resilientes por rede (Meta, TikTok, Google).
  - Anti-bot, rotação de proxy/fingerprint.
  - Workflow de clonagem (LP + funil) com Temporal.
- **Entregáveis:** workers, detectores de stack, pipeline de captura.
- **Sucesso:** taxa de sucesso de scrape/clone, custo por 1k anúncios.
- **Skills:** web automation, engenharia reversa, resiliência.

## 3. Sr. Data Engineer — Pipeline
- **Owner de:** ingestão, normalização, data lake, ClickHouse.
- **Stack:** Python, Kafka/RabbitMQ, ClickHouse, dbt, Airflow/Temporal.
- **Responsabilidades:**
  - Pipeline de ingestão idempotente e deduplicação.
  - Modelagem analítica (OLAP), métricas de anúncios.
  - Qualidade de dados (contratos, validação).
- **Entregáveis:** DAGs, modelos dbt, tabelas ClickHouse.
- **Sucesso:** SLA de freshness, qualidade, custo de storage.
- **Skills:** ETL/ELT, modelagem dimensional, streaming.

## 4. Sr. ML Engineer — IA/Agents
- **Owner de:** sub-agents, embeddings, classificação, transcrição.
- **Stack:** Python, LangGraph, OpenAI/Anthropic, Whisper, pgvector.
- **Responsabilidades:**
  - Orquestração de agents e prompts.
  - Classificadores de nicho/ângulo, embeddings.
  - Avaliação (evals) e controle de custo de tokens.
- **Entregáveis:** agents, pipelines de embedding, evals.
- **Sucesso:** precisão de classificação, custo por job, latência.
- **Skills:** LLMs, RAG, MLOps, avaliação.

## 5. Sr. Frontend Engineer — Web App
- **Owner de:** app web (discovery UI, cloner UI, dashboards).
- **Stack:** Next.js 15, React 19, TanStack Query, Zustand, Tailwind, shadcn/ui.
- **Responsabilidades:**
  - UI performática (feed infinito, filtros, preview de clones).
  - Integração tRPC/GraphQL, estados de loading/erro.
  - Acessibilidade e i18n.
- **Entregáveis:** telas, design system aplicado, componentes.
- **Sucesso:** Core Web Vitals, TTFI, satisfação (SUS).
- **Skills:** React avançado, performance, DX.

## 6. Sr. Frontend Engineer — Extensão & Editor
- **Owner de:** extensão Chrome (MV3) e editor visual de clones.
- **Stack:** TypeScript, Chrome MV3, iframe sandbox, tldraw/GrapesJS.
- **Responsabilidades:**
  - Captura de anúncios direto do FB/TikTok.
  - Editor visual para ajustar clones exportados.
- **Sucesso:** taxa de captura, uso do editor.

## 7. Sr. DevOps/SRE Engineer
- **Owner de:** infra, CI/CD, confiabilidade.
- **Stack:** Kubernetes, Terraform, Helm, ArgoCD, GitHub Actions, Cloudflare/AWS.
- **Responsabilidades:**
  - IaC, autoscaling (KEDA para filas), spot para workers.
  - Observabilidade (Prometheus/Grafana/Loki/Tempo).
  - On-call, runbooks, DR.
- **Sucesso:** uptime 99.9%, DORA metrics, custo.
- **Skills:** SRE, cloud, automação.

## 8. Sr. Security Engineer
- **Owner de:** AppSec, compliance, secrets.
- **Stack:** Vault, Snyk/Trivy, OWASP ZAP, políticas K8s.
- **Responsabilidades:**
  - Threat modeling, pentest, gestão de segredos.
  - LGPD/GDPR, políticas de scraping ético.
- **Sucesso:** zero incidentes críticos, auditorias aprovadas.
- **Skills:** AppSec, cloud security, compliance.

## 9. Sr. QA Engineer
- **Owner de:** estratégia de testes e qualidade.
- **Stack:** Playwright, Vitest, Pytest, k6.
- **Responsabilidades:**
  - Pirâmide de testes, E2E críticos, testes de carga.
  - QA de dados (validação de clones e scrapes).
- **Sucesso:** cobertura, flakiness, defect escape rate.

## 10. Sr. Backend Engineer — Platform/API/Billing
- **Owner de:** gateway, auth, billing, SDK.
- **Stack:** NestJS, tRPC/GraphQL, Stripe, Clerk/Auth.js.
- **Responsabilidades:**
  - Rate limit por plano, quotas, webhooks.
  - Billing (Stripe), gestão de créditos de clonagem.
  - SDK `@spyfy/sdk` e CLI.
- **Sucesso:** confiabilidade de billing, DX do SDK.

---

## Matriz spec → owner → doc

| Spec | Owner | Doc principal |
|------|-------|---------------|
| Discovery/Search | Sr Backend #1 | [offer-discovery.md](../03-features/offer-discovery.md) |
| Scraping/Cloner | Sr Backend #2 | [scraping-engine.md](../04-backend/scraping-engine.md), [offer-cloner.md](../03-features/offer-cloner.md) |
| Data Pipeline | Sr Data Eng | [ingestion.md](../06-data-pipeline/ingestion.md) |
| IA/Agents | Sr ML Eng | [ai-agents.md](../07-ai/ai-agents.md) |
| Web App | Sr Frontend #1 | [ui-ux.md](../05-frontend/ui-ux.md) |
| Extensão/Editor | Sr Frontend #2 | [components.md](../05-frontend/components.md) |
| DevOps/SRE | Sr SRE | [deployment.md](../08-devops/deployment.md) |
| Security | Sr Security | [security.md](../09-security/security.md) |
| QA | Sr QA | [analytics.md](../03-features/analytics.md) |
| Platform/API | Sr Backend #3 | [api-design.md](../04-backend/api-design.md) |

## Interfaces entre owners (contratos)

- Discovery consome dados do Data Pipeline via índices — contrato de schema versionado.
- Cloner emite eventos consumidos por Intelligence.
- Platform expõe auth/quota para todos os serviços.
- IA/Agents fornece enrichment ao Pipeline.

Cada contrato é versionado em `packages/schemas` (Zod) e testado em CI.
