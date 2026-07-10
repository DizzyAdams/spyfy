# 🔍 Scraper — Google Ads Transparency

Coleta via **Google Ads Transparency Center** (anúncios de Search, Display, YouTube, Shopping por anunciante/país).

## Fonte

- `https://adstransparency.google.com/` — busca por anunciante ou domínio, filtro por país/formato/período.

## Estratégia

```
1. Descobrir anunciantes por domínio/nicho.
2. Para cada anunciante, listar anúncios ativos.
3. Coletar criativos (texto, imagem, vídeo/YouTube) + período de veiculação.
```

## Scraping (headless + XHR)

```python
async def scrape_google(advertiser_or_domain, country):
    url = f"https://adstransparency.google.com/?region={country}&domain={advertiser_or_domain}"
    async with browser_pool.acquire(fingerprint=random_fp(geo=country)) as page:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        # dados vêm de RPC/JSON internos — interceptar é mais robusto
        return await intercept_json(page, pattern="SearchService")
```

## Campos coletados

| Campo | Mapeia para |
|-------|-------------|
| creative id | `ads.external_id` |
| advertiser (verificado) | `advertisers` |
| formato (text/image/video) | `creatives.type` |
| first/last shown | longevidade |
| regiões | país |
| destino/domínio | `ads.landing_url` |

## Formatos

- **Search:** headline + descrições.
- **Display:** imagem/responsivo.
- **YouTube:** vídeo → Transcribe Agent.
- **Shopping:** produto + preço.

## Longevidade

- Google mostra período de exibição → excelente sinal de longevidade.

## Anti-bloqueio

- Proxy no país; fingerprint desktop.
- Interceptar JSON interno (menos frágil que DOM).
- Backoff ao detectar rate limit.

## Descoberta de anunciantes

- A partir de domínios de LPs já conhecidas (cross-network).
- A partir de nichos (seed de domínios).
- Enriquecer o Graph ligando anunciante ↔ redes.

## Cross-network linking

- Mesmo anunciante em Meta + TikTok + Google → unificar no `advertisers` (heurística por domínio/nome).
- Visão 360° do concorrente (Competitor Watch).

## Qualidade & compliance

- Dedup por creative id.
- Dados públicos de transparência; respeitar ToS.
- Ver [compliance.md](../../09-security/compliance.md).

## Roadmap de redes

Após Meta/TikTok/Google: **YouTube (via Google), Pinterest, LinkedIn, X, native (Taboola/Outbrain), Kwai**.
