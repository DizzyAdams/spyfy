# 📦 SDK & CLI Reference — SpyFy

## Pacotes

| Pacote | Linguagem | Descrição |
|--------|-----------|-----------|
| `@spyfy/sdk` | TypeScript | Cliente oficial TS/JS. |
| `spyfy` (PyPI) | Python | Cliente oficial Python. |
| `@spyfy/cli` | Node | CLI para terminal. |

## SDK TypeScript

### Instalação
```bash
pnpm add @spyfy/sdk
```

### Inicialização
```ts
import { SpyFy } from "@spyfy/sdk";

const spyfy = new SpyFy({ apiKey: process.env.SPYFY_API_KEY! });
```

### Buscar ofertas
```ts
const { results, nextCursor } = await spyfy.offers.search({
  q: "keto",
  network: "meta",
  country: "BR",
  minDays: 30,
  sort: "score",
});
```

### Clonar oferta
```ts
const clone = await spyfy.clones.create({ offerId: "ofr_123" });
await spyfy.clones.waitUntilReady(clone.id); // polling helper
const bundle = await spyfy.clones.download(clone.id);
```

### Coleções
```ts
const col = await spyfy.collections.create({ name: "Keto BR" });
await spyfy.collections.addItem(col.id, { offerId: "ofr_123", note: "hook forte" });
```

### Alertas
```ts
await spyfy.alerts.create({
  type: "new_creative",
  advertiserId: "adv_55",
  channel: ["email", "slack"],
});
```

### Tratamento de erros
```ts
import { SpyFyError } from "@spyfy/sdk";

try {
  await spyfy.clones.create({ offerId: "x" });
} catch (e) {
  if (e instanceof SpyFyError && e.code === "quota_exceeded") {
    console.log("Faça upgrade:", e.upgradeUrl);
  }
}
```

## SDK Python

```bash
pip install spyfy
```

```python
from spyfy import SpyFy

client = SpyFy(api_key=os.environ["SPYFY_API_KEY"])

results = client.offers.search(q="keto", network="meta", country="BR", min_days=30)
for offer in results.items:
    print(offer.headline, offer.winning_score)

clone = client.clones.create(offer_id="ofr_123")
clone = client.clones.wait_until_ready(clone.id)
client.clones.download(clone.id, path="./clone.zip")
```

## CLI

### Instalação
```bash
pnpm add -g @spyfy/cli
spyfy login   # abre browser / cola API key
```

### Comandos
```bash
# Buscar
spyfy search "keto" --network meta --country BR --min-days 30

# Detalhe
spyfy offer ofr_123

# Clonar
spyfy clone ofr_123 --out ./clone.zip

# Coleções
spyfy collections list
spyfy collections add "Keto BR" ofr_123

# Alertas
spyfy alerts create --type new_creative --advertiser adv_55 --channel email
```

### Saída em JSON (para scripts)
```bash
spyfy search "keto" --json | jq '.results[].headline'
```

## Autenticação

- Variável `SPYFY_API_KEY` ou `spyfy login`.
- Chaves `sk_live_` (prod) e `sk_test_` (sandbox).

## Rate limits & retries

- SDK faz retry automático com backoff em 429/5xx.
- Respeita headers `X-RateLimit-*`.

## Webhooks (verificação)

```ts
import { verifyWebhook } from "@spyfy/sdk";

const event = verifyWebhook(rawBody, signatureHeader, webhookSecret);
if (event.type === "clone.completed") { /* ... */ }
```

## Geração do SDK

- Gerado a partir da spec OpenAPI (`apps/api/openapi.yaml`).
- Publicado via Changesets no merge em `main`.
- Versionamento SemVer.

## Suporte

- Tipos TS completos (autocomplete).
- Docstrings/typing no Python.
- Exemplos em `examples/`.
