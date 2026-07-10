# 🏛️ Arquitetura de Sistema — SpyFy

## Visão geral

O SpyFy adota uma arquitetura **modular, orientada a eventos e API-first**, dividida em quatro planos:

1. **Edge/Client** — Web App, extensão, CLI, SDKs.
2. **API Gateway** — autenticação, rate limit, roteamento (REST/GraphQL/tRPC).
3. **Domain Services** — serviços de negócio (Discovery, Cloner, Intelligence, Billing).
4. **Data & Workers** — pipeline de scraping, filas, data lake, IA.

## Diagrama de alto nível

```
                         ┌────────────────────┐
                         │      Clientes       │
                         │ Web · Ext · CLI ·SDK│
                         └─────────┬──────────┘
                                   │ HTTPS
                         ┌─────────▼──────────┐
                         │   API Gateway /     │
                         │   BFF (NestJS)      │
                         │  Auth · RateLimit   │
                         └───┬───────┬────────┘
              ┌──────────────┘       └──────────────┐
     ┌────────▼────────┐   ┌────────▼────────┐   ┌──▼────────────┐
     │ Discovery Svc   │   │  Cloner Svc     │   │ Intelligence  │
     │ (search/rank)   │   │ (reverse eng.)  │   │ Svc (analytics)│
     └───┬─────────────┘   └───┬─────────────┘   └───┬───────────┘
         │                     │                     │
   ┌─────▼─────┐        ┌──────▼──────┐       ┌──────▼──────┐
   │Elasticsrch│        │  Object     │       │ ClickHouse  │
   │  /Vector  │        │  Storage    │       │ (analytics) │
   └───────────┘        │  (S3/R2)    │       └─────────────┘
                        └─────────────┘
                                   ▲
                         ┌─────────┴──────────┐
                         │  Event Bus / Queue  │
                         │ (BullMQ/RabbitMQ)   │
                         └─────────┬──────────┘
              ┌───────────┬────────┴───────┬─────────────┐
     ┌────────▼───┐ ┌─────▼──────┐ ┌───────▼────┐ ┌──────▼──────┐
     │ Scraper    │ │ Enrichment │ │ Transcribe │ │ Clone       │
     │ Workers    │ │ Workers    │ │ Workers    │ │ Workers     │
     └────┬───────┘ └─────┬──────┘ └─────┬──────┘ └──────┬──────┘
          └───────────────┴──────────────┴──────────────┘
                                   │
                         ┌─────────▼──────────┐
                         │   PostgreSQL (OLTP) │
                         │   Redis (cache/fila)│
                         └────────────────────┘
```

## Estilo arquitetural

- **Monorepo** (Turborepo/pnpm) com apps e packages compartilhados.
- **Microserviços de domínio** desacoplados por fila.
- **Event-driven**: eventos de domínio (`AdDiscovered`, `OfferEnriched`, `CloneRequested`).
- **CQRS leve**: escrita no Postgres (OLTP), leitura de analytics no ClickHouse.
- **Hexagonal (Ports & Adapters)** dentro de cada serviço para trocar fontes/scrapers.

## Componentes principais

### API Gateway / BFF
- Framework: **NestJS**.
- Responsável por auth (JWT + sessions), rate limiting (Redis), roteamento e agregação.
- Expõe REST, GraphQL (Apollo) e tRPC (para o web app).

### Discovery Service
- Busca full-text + semântica (Elasticsearch + vetores).
- Ranking por "winning score".
- Cache agressivo em Redis.

### Cloner Service
- Orquestra jobs de clonagem (Temporal para workflows longos).
- Captura LP, mapeia funil, detecta stack.

### Intelligence Service
- Agrega métricas em ClickHouse.
- Gera tendências, alertas e relatórios.

### Workers (Python + Node)
- **Scraper Workers**: Playwright/Scrapy/Crawlee.
- **Enrichment Workers**: classificação de nicho, idioma, stack.
- **Transcribe Workers**: Whisper + LLM.
- **Clone Workers**: reconstrução de LP e funil.

## Comunicação entre serviços

| Padrão | Uso |
|--------|-----|
| Síncrono (HTTP/gRPC) | Consultas do BFF aos serviços de leitura. |
| Assíncrono (fila) | Todo processamento pesado (scrape, enrich, clone). |
| Eventos (pub/sub) | Notificações de domínio, alertas, webhooks. |
| Workflows (Temporal) | Clonagem de funil multi-etapa com retries. |

## Fluxo: descoberta de anúncio

```
1. Scheduler dispara job "scrape Meta Ad Library / nicho keto".
2. Scraper Worker coleta anúncios → publica evento AdDiscovered.
3. Enrichment Worker consome → detecta nicho/idioma/stack → salva no Postgres.
4. Indexer indexa no Elasticsearch + gera embeddings.
5. Intelligence agrega métricas no ClickHouse.
6. Discovery Service passa a retornar o anúncio nas buscas.
```

## Fluxo: clonagem de oferta

```
1. Usuário clica "Clonar" → BFF cria CloneRequested.
2. Temporal inicia workflow de clonagem:
   a. Fetch LP (Playwright headless).
   b. Baixar assets (imagens, fontes, CSS/JS).
   c. Detectar funil (seguir CTAs, checkout, upsells).
   d. Detectar stack/pixels (fingerprint).
   e. Extrair copy/estrutura (LLM).
   f. Empacotar (HTML estático + manifest).
3. Salvar no Object Storage → notificar usuário (webhook/UI).
```

## Escalabilidade

- Workers **stateless** e horizontalmente escaláveis (HPA no K8s).
- Filas com **backpressure** e DLQ (dead letter queue).
- Sharding de scraping por rede/nicho/região.
- Cache multi-camada (CDN → Redis → app).

## Resiliência

- Retries com backoff exponencial + jitter.
- Circuit breakers em integrações externas.
- Idempotência via chaves de deduplicação por anúncio.
- Snapshots imutáveis (nunca sobrescrevem histórico).

## Multi-tenancy

- Isolamento lógico por `workspace_id` (row-level security no Postgres).
- Quotas e rate limits por plano no Gateway.

## Decisões arquiteturais (ADRs)

Ver pasta `docs/adr/` (a criar). Exemplos de ADRs:
- ADR-001: Monorepo com Turborepo.
- ADR-002: Postgres como OLTP + ClickHouse para analytics.
- ADR-003: Temporal para workflows de clonagem.
- ADR-004: Playwright como engine principal de scraping.
- ADR-005: Elasticsearch + pgvector para busca híbrida.
