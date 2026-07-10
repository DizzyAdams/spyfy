# 🏗️ Monorepo Scaffold — SpyFy (executável)

Estrutura de repositório real e pronta para começar a codar o ecossistema.

## Árvore completa

```
spyfy/
├── apps/
│   ├── web/                  # Next.js 15 (app web + Copilot UI)
│   ├── api/                  # NestJS BFF (REST/tRPC/GraphQL)
│   ├── realtime/             # FastAPI (WS/SSE + LangGraph runtime)
│   ├── workers-py/           # scraping + IA (Scrapy/Playwright/LangGraph)
│   ├── workers-node/         # Crawlee/BullMQ
│   ├── extension/            # Chrome MV3
│   └── marketplace/          # serviço do marketplace (Stripe Connect)
├── packages/
│   ├── sdk-ts/               # @spyfy/sdk
│   ├── apps-sdk/             # @spyfy/apps (plugins)
│   ├── ui/                   # design system
│   ├── schemas/              # Zod compartilhado
│   ├── prompts/              # prompts versionados
│   └── config/               # eslint/tsconfig/tailwind
├── services/
│   ├── discovery/            # busca/ranking
│   ├── cloner/               # clonagem (Temporal)
│   ├── intelligence/         # analytics
│   └── copilot/              # agente conversacional
├── infra/
│   ├── terraform/
│   ├── helm/
│   └── argocd/
├── docs/                     # esta documentação
├── docker-compose.yml
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
  - "services/*"
```

## turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "dev":   { "cache": false, "persistent": true },
    "test":  { "dependsOn": ["^build"] },
    "lint":  {},
    "typecheck": { "dependsOn": ["^build"] }
  }
}
```

## docker-compose.yml (dev)

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment: { POSTGRES_PASSWORD: spyfy }
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
  clickhouse:
    image: clickhouse/clickhouse-server:24
    ports: ["8123:8123", "9000:9000"]
  opensearch:
    image: opensearchproject/opensearch:2
    environment: { discovery.type: single-node }
    ports: ["9200:9200"]
  temporal:
    image: temporalio/auto-setup:1.24
    ports: ["7233:7233"]
  minio:                     # R2/S3 compatível em dev
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
```

## Realtime app (FastAPI + LangGraph) — esqueleto

```python
# apps/realtime/main.py
from fastapi import FastAPI, WebSocket
from spyfy.graph import build_graph, init_state

app = FastAPI()
graph = build_graph()   # supervisor + subgraphs (ver 07-ai)

@app.websocket("/ws/clones/{offer_id}")
async def ws_clone(ws: WebSocket, offer_id: str):
    await ws.accept()
    config = {"configurable": {"thread_id": f"clone-{offer_id}"}}
    async for chunk in graph.astream(init_state(offer_id), config,
                                     stream_mode=["updates", "custom"]):
        await ws.send_json(chunk)
```

## Copilot service — esqueleto

```python
# services/copilot/app.py
from spyfy.copilot import build_copilot
copilot = build_copilot()   # planner + supervisor + platform tools + memory

async def handle(message, user):
    config = {"configurable": {"thread_id": f"copilot-{user.id}"}}
    async for token in copilot.astream(
        {"messages": [("user", message)]}, config, stream_mode="messages"
    ):
        yield token
```

## SDK de plugins — package.json

```json
{
  "name": "@spyfy/apps",
  "version": "0.1.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "peerDependencies": { "react": ">=18" }
}
```

## Comandos

```bash
pnpm install
docker compose up -d
pnpm db:migrate
pnpm dev                     # web + api + realtime
pnpm --filter workers-py dev # workers de IA/scraping
pnpm test                    # testes afetados (turbo)
```

## Makefile (atalhos)

```make
dev:        ; docker compose up -d && pnpm dev
migrate:    ; pnpm db:migrate
seed:       ; pnpm db:seed
test:       ; pnpm test
lint:       ; pnpm lint && ruff check apps/workers-py
```

## Convenções

- Um `package.json`/`pyproject.toml` por app/package.
- Tipos compartilhados em `packages/schemas` (fonte única de verdade).
- Nada de import cruzado fora dos boundaries definidos.
- Ver [CONTRIBUTING.md](../CONTRIBUTING.md).
