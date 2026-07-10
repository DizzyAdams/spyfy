# 🐘 Banco de Dados — SpyFy

## Estratégia poliglota

| Banco | Papel | Por quê |
|-------|-------|---------|
| **PostgreSQL** | OLTP (usuários, ofertas, coleções, funis) | Consistência, relacional, pgvector. |
| **ClickHouse** | OLAP (métricas de anúncios, tendências) | Agregações rápidas em bilhões de linhas. |
| **Elasticsearch** | Busca full-text | Relevância, facetas. |
| **Redis** | Cache, filas, sessões, rate limit | Baixa latência. |
| **pgvector** | Embeddings/busca semântica | Integrado ao Postgres. |
| **R2/S3** | Assets, snapshots, clones | Objeto barato. |

## PostgreSQL

- Aurora Postgres, Multi-AZ, read replicas.
- Extensões: `pgvector`, `pg_trgm`, `citext`, `uuid-ossp`.
- Row-Level Security por `workspace_id`.
- Particionamento de `ad_snapshots` por mês.

### Estratégia de índices
- B-tree em FKs e colunas de filtro.
- GIN (`pg_trgm`) para busca fuzzy leve.
- HNSW (`pgvector`) para kNN.
- Índices parciais para `status = 'active'`.

### Migrations
- **Drizzle Kit** (ou Prisma Migrate).
- Migrations versionadas, aplicadas no deploy via job.
- Expand/contract para mudanças sem downtime.

## ClickHouse

- Tabelas `MergeTree` particionadas por mês.
- Materialized views para dashboards.
- TTL para dados brutos antigos (mover p/ agregados).

```sql
CREATE MATERIALIZED VIEW niche_daily_mv
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(observed_date)
ORDER BY (niche, observed_date)
AS SELECT niche, observed_date, count() AS active
   FROM ad_metrics WHERE active = 1
   GROUP BY niche, observed_date;
```

## Redis

- Namespaces: `cache:`, `queue:`, `session:`, `ratelimit:`.
- Cluster mode em produção.
- Eviction `allkeys-lru` para cache.

## Elasticsearch

- Índice `ads` com analyzers por idioma.
- Alias para reindexação sem downtime.
- ILM (index lifecycle) para dados antigos.

## Backups & retenção

| Dado | Backup | Retenção |
|------|--------|----------|
| Postgres | contínuo (PITR) | 30d |
| ClickHouse | snapshot diário | 90d agregado |
| R2 | versionamento | 1 ano (lifecycle) |
| Elasticsearch | snapshot diário | 30d |

## Consistência

- Fonte da verdade: **Postgres**.
- ClickHouse e Elasticsearch são **derivados** (reprocessáveis).
- Sincronização via CDC/eventos (idempotente).

## Performance

- Connection pooling (PgBouncer).
- Queries N+1 evitadas (dataloader no GraphQL).
- Cache de leitura em Redis com invalidação por evento.

## Segurança de dados

- Criptografia em repouso (KMS) e em trânsito (TLS).
- Segredos no Vault.
- Acesso via IAM + least privilege.
- Ver [security.md](../09-security/security.md).
