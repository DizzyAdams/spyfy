# 🗄️ Modelo de Dados — SpyFy

## Entidades principais

```
Workspace 1───* User
Workspace 1───* Collection
Advertiser 1───* Ad
Ad 1───* Creative
Ad *───1 Offer
Offer 1───1 Funnel
Funnel 1───* FunnelStep
Ad 1───* AdSnapshot
Offer *───* Collection (via CollectionItem)
User 1───* Alert
```

## Diagrama ER (Postgres — OLTP)

```
workspaces (id, name, plan, created_at)
   └─* users (id, workspace_id, email, role)
   └─* collections (id, workspace_id, name, owner_id)
        └─* collection_items (collection_id, offer_id, note)

advertisers (id, network, external_id, name, page_url)
   └─* ads (id, advertiser_id, offer_id, network, external_id,
            first_seen_at, last_seen_at, status, landing_url)
        └─* creatives (id, ad_id, type, url, thumbnail, duration)
        └─* ad_snapshots (id, ad_id, captured_at, raw_payload)

offers (id, niche, language, country, winning_score, funnel_id, embedding)
   └─1 funnels (id, offer_id, checkout_stack)
        └─* funnel_steps (id, funnel_id, step_order, type, url, snapshot_url)

alerts (id, user_id, query_json, channel, last_fired_at)
```

## Tabelas (DDL resumido)

### workspaces
```sql
CREATE TABLE workspaces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  plan        TEXT NOT NULL DEFAULT 'free',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### users
```sql
CREATE TABLE users (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  email        CITEXT UNIQUE NOT NULL,
  role         TEXT NOT NULL DEFAULT 'member',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### advertisers
```sql
CREATE TABLE advertisers (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT NOT NULL,
  network     TEXT NOT NULL,
  name        TEXT,
  page_url    TEXT,
  UNIQUE (network, external_id)
);
```

### ads
```sql
CREATE TABLE ads (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  advertiser_id UUID REFERENCES advertisers(id),
  offer_id      UUID REFERENCES offers(id),
  network       TEXT NOT NULL,
  external_id   TEXT NOT NULL,
  first_seen_at TIMESTAMPTZ,
  last_seen_at  TIMESTAMPTZ,
  status        TEXT DEFAULT 'active',
  landing_url   TEXT,
  UNIQUE (network, external_id)
);
CREATE INDEX idx_ads_last_seen ON ads (last_seen_at DESC);
CREATE INDEX idx_ads_offer ON ads (offer_id);
```

### creatives
```sql
CREATE TABLE creatives (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ad_id     UUID REFERENCES ads(id),
  type      TEXT NOT NULL,   -- image | video | carousel
  url       TEXT,
  thumbnail TEXT,
  duration  INT,
  body_text TEXT,
  headline  TEXT
);
```


### offers
```sql
CREATE TABLE offers (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  niche         TEXT,
  language      TEXT,
  country       TEXT,
  winning_score NUMERIC(6,2) DEFAULT 0,
  funnel_id     UUID,
  embedding     vector(1536),
  created_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_offers_score ON offers (winning_score DESC);
CREATE INDEX idx_offers_embedding ON offers USING hnsw (embedding vector_cosine_ops);
```

### funnels / funnel_steps
```sql
CREATE TABLE funnels (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  offer_id       UUID REFERENCES offers(id),
  checkout_stack TEXT
);
CREATE TABLE funnel_steps (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  funnel_id    UUID REFERENCES funnels(id),
  step_order   INT,
  type         TEXT,
  url          TEXT,
  snapshot_url TEXT
);
```

### ad_snapshots (histórico imutável)
```sql
CREATE TABLE ad_snapshots (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ad_id       UUID REFERENCES ads(id),
  captured_at TIMESTAMPTZ DEFAULT now(),
  raw_payload JSONB
);
```

## Cálculo de `winning_score`

```
winning_score =
    (longevity_days * W_LONG)
  + (log(estimated_impressions + 1) * W_VOL)
  + (creative_variants * W_VAR)
  + (recency_boost)
```
Pesos configuráveis (default: W_LONG=1.0, W_VOL=2.0, W_VAR=0.5).

## Modelo analítico (ClickHouse)

```sql
CREATE TABLE ad_metrics
(
  ad_id           UUID,
  network         LowCardinality(String),
  niche           LowCardinality(String),
  country         LowCardinality(String),
  observed_date   Date,
  active          UInt8,
  est_impressions UInt64,
  creative_count  UInt16
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_date)
ORDER BY (niche, network, observed_date);
```

## Índices de busca (Elasticsearch)

```json
{
  "mappings": {
    "properties": {
      "ad_id":     { "type": "keyword" },
      "headline":  { "type": "text" },
      "body_text": { "type": "text" },
      "niche":     { "type": "keyword" },
      "network":   { "type": "keyword" },
      "longevity_days": { "type": "integer" },
      "winning_score":  { "type": "float" }
    }
  }
}
```

## Convenções

- UUID v4 para PKs.
- `created_at`/`updated_at` em toda tabela.
- Soft delete via `deleted_at` onde aplicável.
- Row-Level Security por `workspace_id`.
- Snapshots nunca são atualizados (append-only).
