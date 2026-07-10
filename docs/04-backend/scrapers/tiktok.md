# 🎵 Scraper — TikTok

Coleta de anúncios do **TikTok Creative Center** (Top Ads) e biblioteca de anúncios comerciais.

## Fontes

- **TikTok Creative Center** — "Top Ads", tendências, por país/indústria.
- **Commercial Content Library** (UE) — transparência regulatória.

## Desafios

- SPA pesada (muito JS) → exige headless com espera de network idle.
- Vídeos: coletar URL do criativo + thumbnail + métricas visíveis.
- Rate/anti-bot agressivo.

## Scraping (headless)

```python
async def scrape_tiktok(niche, country):
    url = ("https://ads.tiktok.com/business/creativecenter/topads/"
           f"?region={country}&industry={map_niche(niche)}")
    async with browser_pool.acquire(fingerprint=random_fp(geo=country)) as page:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await dismiss_cookie_banner(page)
        await autoscroll(page)
        # muitas vezes os dados vêm de XHR JSON — interceptar é mais robusto
        return await intercept_json(page, pattern="/creative_radar_api/")
```

## Interceptação de XHR (preferível)

- Em vez de raspar DOM, interceptar respostas JSON da API interna do Creative Center.
- Mais estável a mudanças de layout.

```python
page.on("response", lambda r: capture(r) if "topads" in r.url else None)
```

## Campos coletados

| Campo | Mapeia para |
|-------|-------------|
| ad id | `ads.external_id` |
| advertiser/brand | `advertisers` |
| video_url / cover | `creatives.url/thumbnail` |
| duration | `creatives.duration` |
| CTR/likes (quando expostos) | métricas/engagement |
| first_seen (estimado) | longevidade |
| industry/region | `offers.niche/country` |

## Métricas

- Creative Center expõe CTR, likes, tempo de exibição (relativos).
- Usar como sinal de engagement no winning_score.

## Transcrição de VSL/vídeo

- Vídeos vão para o Transcribe Agent (Whisper) → transcrição + resumo.

## Anti-bloqueio

- Proxy residencial no país.
- Fingerprint mobile quando necessário (TikTok é mobile-first).
- Espera de network idle + jitter.
- Rotação ao detectar captcha/slider.

## Agendamento

- Top Ads atualizados diariamente.
- Nichos e-com/dropshipping: alta frequência.

## Qualidade & compliance

- Dedup por ad id.
- Baixar vídeo apenas 1x (cache).
- Dados públicos/transparência; respeitar ToS.
- Ver [compliance.md](../../09-security/compliance.md).
