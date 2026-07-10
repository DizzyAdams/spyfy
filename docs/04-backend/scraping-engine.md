# 🕸️ Scraping Engine — SpyFy

## Objetivo

Coletar, de forma **resiliente, escalável e ética**, anúncios de múltiplas redes, mantendo dados frescos e completos.

## Fontes suportadas

| Fonte | Método | Notas |
|-------|--------|-------|
| Meta Ad Library | API pública + scraping HTML | Principal fonte. |
| TikTok Creative Center | Scraping headless | JS pesado. |
| Google Ads Transparency | Scraping headless | Paginação complexa. |
| YouTube Ads | Scraping | Via transparency. |
| Native (Taboola/Outbrain) | Scraping | Rotativo. |

## Arquitetura

```
Scheduler (cron/Temporal)
   │  dispara jobs por (rede × nicho × país)
   ▼
Job Queue (BullMQ)
   │
   ▼
Scraper Workers (Playwright / Scrapy / Crawlee)
   │  coletam anúncios + assets
   ▼
Normalizer → evento AdDiscovered
   │
   ▼
Pipeline de enrichment (ver 06)
```

## Estratégia anti-bloqueio

| Técnica | Descrição |
|---------|-----------|
| Proxy residencial rotativo | Bright Data / Oxylabs; rotação por request. |
| Fingerprint randomization | User-agent, viewport, timezone, WebGL. |
| Stealth plugins | Ocultar sinais de automação. |
| Rate limiting por domínio | Respeitar limites, evitar padrões. |
| Captcha solving | Serviço externo quando necessário. |
| Retry inteligente | Backoff + troca de proxy/fingerprint. |

## Worker (pseudo-código)

```python
async def scrape_meta(job):
    async with browser_pool.acquire(fingerprint=random_fp()) as page:
        await page.goto(build_url(job.niche, job.country))
        await page.wait_for_load_state("networkidle")
        ads = await extract_ads(page)
        for ad in ads:
            await download_assets(ad)
            emit_event("AdDiscovered", normalize(ad))
```

## Normalização

- Mapear campos de cada rede → schema unificado (`ads`, `creatives`).
- Deduplicar por `(network, external_id)`.
- Detectar mudanças → novo `ad_snapshot`.

## Agendamento & priorização

- Nichos "quentes" scrapeados com mais frequência.
- Anunciantes monitorados (alertas) têm prioridade.
- Backfill histórico em lotes de baixa prioridade.

## Escalabilidade

- Workers stateless, autoscale por profundidade de fila (KEDA).
- Spot instances para reduzir custo.
- Sharding por rede/região.
- Pool de browsers reutilizáveis.

## Resiliência

- DLQ para jobs que falham após N retries.
- Circuit breaker por fonte (se rede bloqueia, pausar e alertar).
- Idempotência por chave de dedup.
- Health checks e auto-restart.

## Qualidade dos dados

- Validação de schema na ingestão.
- Detecção de anomalia (queda súbita de volume → alerta).
- QA Agent amostra e valida.

## Ética & compliance

- Coletamos apenas de **bibliotecas públicas de transparência**.
- Respeitamos ToS e robots configuráveis por fonte.
- Sem coleta de PII de usuários finais.
- Ver [compliance.md](../09-security/compliance.md).

## Observabilidade

- Métricas: anúncios/min, taxa de sucesso, taxa de bloqueio, custo de proxy.
- Traces por job.
- Dashboards por fonte.

## Custos

- Proxy é o maior custo variável → otimizar reuso de sessão e cache.
- Priorizar API pública onde disponível (mais barato/estável).
