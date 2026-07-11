# 📘 Scraper — Meta Ad Library

Coleta de anúncios ativos do Facebook/Instagram via **Meta Ad Library** (fonte pública oficial).

## Fontes

- **Ad Library API** (oficial) — para anúncios sociais/políticos e, com limites, comerciais por país.
- **Ad Library web** (scraping headless) — cobertura ampla de anúncios comerciais.

## Status: IMPLEMENTADO (real)

A integração vive em `apps/workers-py/spyfy/meta_library.py` (`MetaAdLibrary`)
e está coberta por `tests/test_meta_library.py` (100% da suíte verde). Sem
novas dependências — usa `httpx` (já presente) + `html.parser` (stdlib).

```python
from spyfy.meta_library import MetaAdLibrary

# Modo web-scrape (sem token) — fallback p/ Ad Library API
lib = MetaAdLibrary(country="BR")
offers = lib.search("emagrecimento", limit=20)

# Modo Ad Library API oficial (quando houver access_token)
lib = MetaAdLibrary(access_token="<META_TOKEN>", country="BR")
offers = lib.search("keto", limit=20)
```

Ambos retornam dicts no formato `Offer` (consumido pelo Radar em
`apps/web/server/realtime.js` → `normalizeOffer`). O `scraper_bridge`
(`python -m spyfy.scraper_bridge --network meta`) já usa `MetaAdLibrary`
quando `--simulate` não está setado, com fallback automático para o gerador
estruturado em caso de bloqueio/erro.

> **Requisito de ambiente p/ dados ao vivo:** a Ad Library web exige sessão de
> navegador/cookies (requisições server-side recebem 403). Em produção, use um
> token válido da **Ad Library API** ou proxy residencial + cookies. Sem isso,
> o módulo levanta `MetaScrapeError` e o chamador cai no fallback.

## Estratégia

```
1. Preferir API oficial quando disponível (estável, legal, barato).
2. Fallback web-scrape (httpx + html.parser) para cobertura comercial ampla.
3. Combinar e deduplicar por ad_archive_id.
```

## Endpoint (API oficial)

```
GET https://graph.facebook.com/v19.0/ads_archive
  ?search_terms=keto
  &ad_reached_countries=['BR']
  &ad_active_status=ACTIVE
  &fields=id,ad_creative_bodies,ad_delivery_start_time,page_name,...
  &access_token=<token>
```

## Campos coletados

| Campo | Mapeia para |
|-------|-------------|
| `id` / `ad_archive_id` | `ads.external_id` |
| `page_name` / `page_id` | `advertisers.name/external_id` |
| `ad_creative_bodies` | `creatives.body_text` |
| `ad_creative_link_titles` | `creatives.headline` |
| `ad_delivery_start_time` | `ads.first_seen_at` (longevidade) |
| `snapshot_url` | link do criativo |
| `publisher_platforms` | fb/ig/messenger/audience |

## Scraping headless (fallback)

```python
async def scrape_meta_web(niche, country):
    url = f"https://www.facebook.com/ads/library/?q={niche}&country={country}&active_status=active"
    async with browser_pool.acquire(fingerprint=random_fp(geo=country)) as page:
        await page.goto(url)
        await page.wait_for_selector("[role='article']")
        await autoscroll(page)                 # lazy load
        cards = await page.query_selector_all("[role='article']")
        return [await parse_card(c) for c in cards]
```

## Longevidade (sinal-chave)

- `first_seen = ad_delivery_start_time`.
- `longevity_days = now - first_seen`.
- Anúncio some da library → marcar `status=inactive`, mas manter snapshots.

## Detecção de variantes de criativo

- Um mesmo anunciante roda N criativos → agrupar por `page_id` + similaridade → `creative_variants` (entra no winning_score).

## Anti-bloqueio específico

- Proxy residencial no país do anúncio (geo-consistente).
- Autoscroll com jitter humano.
- Respeitar rate; sessões reutilizáveis.
- Detectar checkpoint/login wall → trocar proxy/fingerprint.

## Paginação

- Web: scroll infinito (cursor por posição).
- API: `after` cursor.

## Agendamento

- Nichos quentes: a cada 1–3h.
- Anunciantes monitorados (alertas): prioridade alta.
- Backfill histórico: baixa prioridade.

## Qualidade

- Dedup por `ad_archive_id`.
- Validar campos mínimos (criativo + página).
- Detectar mudança → novo snapshot.

## Compliance

- Dados públicos da biblioteca de transparência.
- Sem coleta de PII de usuários finais.
- Respeitar ToS da Meta e limites de API.
- Ver [compliance.md](../../09-security/compliance.md).
