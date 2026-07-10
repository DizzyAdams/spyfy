# 📚 Library Mining Engine (A3) — SpyFy

Mineração via **APIs oficiais e bibliotecas** (sem browser), quando a fonte expõe dados estruturados. Mais barato, estável e rápido que o browser.

## Fontes com API/lib

| Fonte | Acesso | Lib/Client |
|-------|--------|-----------|
| Meta Ad Library | Graph API `ads_archive` | httpx + client próprio |
| TikTok Commercial Content (UE) | API de transparência | httpx |
| Google Ads Transparency | RPC/JSON interno | httpx (headers corretos) |
| RSS/afiliados/redes | feeds/API | feedparser/httpx |
| American Swap* (swipe source) | conector futuro | plugin |

\* Não localizado como ferramenta pública; mantido como *conector opcional* caso o usuário forneça a fonte/credenciais.

## Cliente Meta Ad Library

```python
import httpx

class MetaAdLibrary:
    BASE = "https://graph.facebook.com/v19.0/ads_archive"

    def __init__(self, token: str):
        self.token = token

    async def search(self, terms, countries=("BR",), status="ACTIVE", limit=100):
        params = {
            "search_terms": terms,
            "ad_reached_countries": str(list(countries)),
            "ad_active_status": status,
            "fields": ("id,page_id,page_name,ad_creative_bodies,"
                       "ad_creative_link_titles,ad_delivery_start_time,"
                       "ad_snapshot_url,publisher_platforms"),
            "limit": limit,
            "access_token": self.token,
        }
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(self.BASE, params=params)
            r.raise_for_status()
            return r.json()

    async def paginate(self, terms, **kw):
        page = await self.search(terms, **kw)
        while page.get("data"):
            for ad in page["data"]:
                yield ad
            nxt = page.get("paging", {}).get("next")
            if not nxt:
                break
            async with httpx.AsyncClient(timeout=30) as c:
                page = (await c.get(nxt)).json()
```

## Normalização unificada

Cada fonte mapeia para o schema comum (`ads`, `creatives`, `advertisers`):

```python
def normalize_meta(ad: dict) -> dict:
    return {
        "network": "meta",
        "external_id": ad["id"],
        "advertiser": {"external_id": ad.get("page_id"),
                       "name": ad.get("page_name")},
        "creatives": [{"headline": h, "body_text": b}
                      for h, b in zip(ad.get("ad_creative_link_titles", []),
                                      ad.get("ad_creative_bodies", []))],
        "first_seen": ad.get("ad_delivery_start_time"),
        "snapshot_url": ad.get("ad_snapshot_url"),
        "platforms": ad.get("publisher_platforms", []),
    }
```

## Rate limit & retries

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
async def safe_get(client, url, **kw):
    r = await client.get(url, **kw)
    if r.status_code == 429:
        raise RuntimeError("rate limited")   # dispara retry com backoff
    r.raise_for_status()
    return r
```

- Respeita `X-RateLimit-*` e `Retry-After`.
- Token bucket por fonte.
- Rotação de tokens/apps para volume.

## Vantagens sobre browser

| Critério | Library (A3) | Browser (A2) |
|----------|:------------:|:------------:|
| Custo | 💚 baixo | 🔴 alto (proxy/CPU) |
| Estabilidade | 💚 alta | 🟡 média (layout muda) |
| Cobertura | 🟡 limitada à API | 💚 ampla |
| Velocidade | 💚 rápida | 🟡 render lento |

**Regra:** sempre tentar A3 primeiro; cair para A2 quando a API não cobrir.

## Orquestração híbrida

```python
async def mine(network, niche, country):
    if has_api(network):
        try:
            return await library_mine(network, niche, country)   # A3
        except CoverageGap:
            pass
    return await browser_mine(network, niche, country)           # A2 fallback
```

## Streaming

- Cada página/lote emite `{"type":"batch_mined","source":"meta","n":100}`.
- Alimenta o pipeline de enrichment em tempo real.

## Compliance

- Uso conforme ToS das APIs; tokens legítimos.
- Sem PII de usuários finais.
- Ver [compliance.md](../09-security/compliance.md).
