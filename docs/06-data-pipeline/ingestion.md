# 🚰 Ingestão de Dados — SpyFy

## Objetivo

Trazer anúncios brutos das fontes para dentro do sistema de forma **idempotente, deduplicada e observável**, alimentando busca, analytics e clonagem.

## Fluxo

```
Scraper Workers
   │ AdDiscovered (raw)
   ▼
Ingestion Service
   ├─ validação de schema
   ├─ deduplicação (network+external_id)
   ├─ detecção de mudança → snapshot
   ▼
Postgres (fonte da verdade)
   │ evento OfferUpserted
   ├─────────────► Indexer (Elasticsearch + embeddings)
   └─────────────► Loader (ClickHouse metrics)
```

## Contratos de dados

- Schema de evento versionado (`packages/schemas`, Zod/Avro).
- Rejeição de eventos malformados → DLQ + alerta.

```ts
const AdDiscovered = z.object({
  network: z.enum(["meta","tiktok","google","native"]),
  externalId: z.string(),
  advertiser: z.object({ externalId: z.string(), name: z.string().optional() }),
  creatives: z.array(CreativeSchema),
  landingUrl: z.string().url().optional(),
  observedAt: z.string().datetime(),
});
```

## Deduplicação

- Chave: `(network, external_id)`.
- Upsert: se existe, atualiza `last_seen_at`; se mudou criativo/copy → novo `ad_snapshot`.
- Hash de conteúdo para detectar mudança real.

## Idempotência

- Cada evento tem `event_id`; processamento registra id processado (Redis SET + TTL).
- Reprocessamento seguro (mesmo resultado).

## Detecção de mudança (snapshots)

```
novo_hash = hash(creatives + copy + landing_url)
if novo_hash != ultimo_hash:
    criar ad_snapshot(raw_payload)
    atualizar ad
```

## Orquestração

- **Temporal/Airflow** para pipelines agendados e backfill.
- BullMQ para eventos em fluxo contínuo.
- Backpressure: limitar concorrência por fonte.

## Backfill

- Jobs de baixa prioridade para preencher histórico.
- Idempotente; pode rodar a qualquer momento.

## Qualidade & validação

- Contratos de schema no boundary.
- Métricas de completude (campos faltando).
- Detecção de anomalia de volume (queda súbita → alerta).

## Observabilidade

- Métricas: eventos/s, taxa de dedup, taxa de rejeição, lag.
- Traces por evento.
- Dashboards por fonte.

## Falhas & DLQ

- Após N retries → Dead Letter Queue.
- Ferramenta para inspecionar e reprocessar DLQ.
- Alertas quando DLQ cresce.

## Métricas de sucesso

- Freshness (lag entre observação e disponibilidade < 5 min).
- Taxa de dedup correta.
- Zero perda de eventos (at-least-once + idempotência).
