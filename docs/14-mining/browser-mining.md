# 🌐 Browser Mining Engine (A2) — SpyFy

Mineração via **browser automatizado** (Playwright) para redes que exigem render de JS, com anti-bloqueio, interceptação de XHR e captura de assets — tudo em tempo real.

## Quando usar browser vs library

| Situação | Engine |
|----------|--------|
| API pública disponível | **A3 Library** (mais barato/estável) |
| SPA pesada / sem API (TikTok CC, Google Transparency) | **A2 Browser** |
| Captura de LP para clonagem | **A2 Browser** (render completo) |

## Arquitetura

```
Job (rede, nicho, país)
   ▼
Browser Pool (Playwright, N contextos)
   ├─ fingerprint aleatório (UA, viewport, tz, locale, WebGL)
   ├─ proxy residencial (geo do alvo)
   ├─ stealth (oculta sinais de automação)
   ▼
Render + interações humanas (scroll/jitter)
   ├─ intercepta respostas XHR/JSON  ← preferível ao DOM
   ├─ extrai cards (fallback DOM)
   └─ baixa assets (img/vídeo/css/fontes)
   ▼
Normaliza → evento AdDiscovered (stream)
```

## Pool de browsers

```python
class BrowserPool:
    def __init__(self, size=20):
        self._sem = asyncio.Semaphore(size)

    @asynccontextmanager
    async def acquire(self, geo="BR"):
        async with self._sem:
            pw = await async_playwright().start()
            browser = await pw.chromium.launch(args=STEALTH_ARGS, headless=True)
            ctx = await browser.new_context(
                proxy={"server": proxy_for(geo)},
                user_agent=random_ua(),
                viewport=random_viewport(),
                locale=locale_for(geo), timezone_id=tz_for(geo),
            )
            await apply_stealth(ctx)      # remove navigator.webdriver etc.
            try:
                yield ctx
            finally:
                await browser.close(); await pw.stop()
```

## Interceptação de XHR (robusto)

Preferimos capturar o **JSON da API interna** em vez de raspar o DOM (menos frágil).

```python
async def mine_with_intercept(ctx, url, pattern):
    page = await ctx.new_page()
    captured = []
    page.on("response", lambda r: captured.append(r) if pattern in r.url else None)
    await page.goto(url, wait_until="networkidle")
    await human_scroll(page)
    data = []
    for r in captured:
        try:
            data.append(await r.json())
        except Exception:
            pass
    return normalize(data)
```

## Comportamento humano (anti-bot)

```python
async def human_scroll(page, steps=8):
    for _ in range(steps):
        await page.mouse.wheel(0, random.randint(600, 1200))
        await page.wait_for_timeout(random.randint(400, 1400))  # jitter
```

- UA/viewport/timezone coerentes com o proxy (geo-consistência).
- Movimentos de mouse e delays aleatórios.
- Resolver de captcha sob demanda (serviço externo).
- Detectar login/checkpoint wall → trocar proxy+fingerprint e re-tentar.

## Captura de assets (para clonagem)

```python
async def capture_assets(page, base_url):
    urls = await page.eval_on_selector_all(
        "img,source,link[rel=stylesheet],script[src]",
        "els => els.map(e => e.src || e.href).filter(Boolean)")
    saved = await asyncio.gather(*(download_to_r2(u) for u in set(urls)))
    return saved
```

## Streaming de progresso

Cada etapa emite evento p/ o Orchestrator → UI:
```
{"type":"page_rendered"} {"type":"xhr_captured","n":42}
{"type":"assets_saved","n":31} {"type":"ads_extracted","n":57}
```

## Resiliência

- Retry com backoff + troca de proxy/fingerprint.
- Circuit breaker por fonte (se bloqueia, pausa e alerta A13).
- Timeout por página; DLQ para falhas persistentes.
- Idempotência por `(network, external_id)`.

## Escala

- Pool horizontal (KEDA por profundidade de fila).
- Spot instances (workers efêmeros).
- Sharding por rede/nicho/país.
- Reuso de contexto/sessão para reduzir custo de proxy.

## Custo

- Proxy residencial é o maior custo → interceptar XHR reduz páginas necessárias.
- Cache de assets (não baixar 2x).
- Meta: < $0.004 por anúncio minerado.

## Ética & compliance

- Somente bibliotecas públicas de transparência e páginas públicas.
- Sem burlar autenticação/paywalls.
- Respeitar rate/ToS configurável por fonte.
- Ver [compliance.md](../09-security/compliance.md).
