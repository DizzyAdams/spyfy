# 📐 Architecture Decision Records (ADRs) — SpyFy

Registro imutável das principais decisões técnicas. Formato: contexto → decisão → consequências.

---

## ADR-001 — Monorepo com Turborepo
- **Status:** Aceito
- **Contexto:** múltiplos apps (web, api, workers, extensão) e packages compartilhados (sdk, ui, schemas).
- **Decisão:** monorepo pnpm + Turborepo com cache remoto.
- **Consequências:** compartilhamento fácil de tipos/schemas; builds afetados; único ponto de versionamento (Changesets). Trade-off: tooling de monorepo mais complexo.

## ADR-002 — Postgres (OLTP) + ClickHouse (OLAP)
- **Status:** Aceito
- **Contexto:** carga transacional (usuários/ofertas) e analítica (bilhões de métricas de anúncios) têm perfis opostos.
- **Decisão:** Postgres como fonte da verdade; ClickHouse para analytics derivado.
- **Consequências:** consultas analíticas rápidas; necessidade de sincronização (CDC/eventos idempotentes). ClickHouse é reprocessável.

## ADR-003 — Temporal para workflows de clonagem
- **Status:** Aceito
- **Contexto:** clonagem é multi-etapa, longa, com retries e falhas parciais.
- **Decisão:** Temporal para orquestrar workflows duráveis.
- **Consequências:** retries/estado durável nativos; menos código de orquestração manual. Trade-off: mais um sistema para operar.

## ADR-004 — Playwright como engine de scraping principal
- **Status:** Aceito
- **Contexto:** redes-alvo dependem de JS pesado (TikTok, Google Transparency).
- **Decisão:** Playwright headless + Scrapy para HTML simples.
- **Consequências:** cobertura de SPAs; custo maior de CPU. Mitigado com pool de browsers e spot instances.

## ADR-005 — Busca híbrida: Elasticsearch + pgvector
- **Status:** Aceito
- **Contexto:** usuários buscam por palavra-chave e por conceito/ângulo.
- **Decisão:** BM25 (Elasticsearch) + kNN (pgvector) com Reciprocal Rank Fusion.
- **Consequências:** melhor relevância; dois sistemas de índice para manter sincronizados.

## ADR-006 — tRPC para o web app, REST para externos
- **Status:** Aceito
- **Contexto:** web app quer type-safety end-to-end; integradores querem REST estável.
- **Decisão:** tRPC interno + REST `/v1` versionado externo + GraphQL para consultas ricas.
- **Consequências:** DX excelente no front; superfície de API maior para manter.

## ADR-007 — LangGraph para orquestração de agents
- **Status:** Aceito
- **Contexto:** sub-agents precisam de planejamento, roteamento, reflexão e human-in-the-loop.
- **Decisão:** LangGraph (grafos de estado) sobre LangChain tools.
- **Consequências:** fluxos de agent explícitos e testáveis; curva de aprendizado.

## ADR-008 — Cloudflare R2 para storage de objetos
- **Status:** Aceito
- **Contexto:** grande volume de assets/snapshots/clones; egress caro na AWS.
- **Decisão:** R2 (sem egress fee) para assets.
- **Consequências:** custo de saída reduzido; latência boa via CDN. Trade-off: fora da AWS (integração via S3 API compatível).

## ADR-009 — Autoscaling de workers por fila (KEDA)
- **Status:** Aceito
- **Contexto:** carga de scraping/enrichment é bursty e fila-dependente.
- **Decisão:** KEDA escala workers pela profundidade das filas Redis.
- **Consequências:** custo proporcional à carga; escala a zero em ociosidade.

## ADR-010 — GitOps com ArgoCD
- **Status:** Aceito
- **Contexto:** deploys auditáveis e reproduzíveis.
- **Decisão:** estado desejado no git; ArgoCD sincroniza.
- **Consequências:** rollback trivial, auditoria; disciplina de PRs em infra.

## ADR-011 — Feature flags + trunk-based
- **Status:** Aceito
- **Contexto:** desacoplar deploy de release; reduzir branches longas.
- **Decisão:** trunk-based com flags (ex.: Unleash/LaunchDarkly).
- **Consequências:** entregas frequentes; necessidade de higiene de flags.

## ADR-012 — Idempotência e at-least-once em toda ingestão
- **Status:** Aceito
- **Contexto:** filas garantem at-least-once; duplicatas são inevitáveis.
- **Decisão:** dedup por chave + registro de event_id processado.
- **Consequências:** processamento seguro a reprocessos; leve overhead de estado.

---

## Processo de ADR

1. Propor via PR em `docs/01-architecture/adr.md` (ou arquivo próprio).
2. Discussão assíncrona + review de Staff/Tech Leads.
3. Status: Proposto → Aceito / Rejeitado / Substituído.
4. ADRs aceitos são imutáveis (mudanças = novo ADR que substitui).
