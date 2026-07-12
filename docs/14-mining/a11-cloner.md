# A11 — Cloner (engenharia reversa de LP/funil)

Agente da squad de mining que **clona uma landing page / oferta**: extrai o
copy, detecta o stack e mapeia o funil, montando um *clone bundle* estruturado
+ um HTML reconstruído pronto para exportar. **Implementado** em
`apps/workers-py/spyfy/clone.py`.

## Por que é leve (free tier)
Usa apenas `httpx` + `html.parser` (stdlib). **Sem Playwright / bs4**, então
cabe no free tier e roda 100% offline. O fetch de LP é opcional: se não houver
URL ou a rede falhar, reconstrói a partir do `offer` (fallback gracioso).

## Mapeamento de código (`spyfy/clone.py`)
- `clone_offer(url=None, offer=None, niche=None, country="BR")` — entrypoint.
  - Com `url`: faz `_fetch` (httpx, UA de browser, timeout 12s) e extrai.
  - Sem `url` (ou em falha): `_fallback_clone` reconstrói a partir do `offer`.
- `_PageExtractor` (subclasse de `HTMLParser`) — coleta título, `h1/h2`,
  parágrafos, `li` bullets, `a.btn` CTAs, `img`, links.
- `detect_stack(page_html)` — detecta plataformas por assinatura
  (Hotmart, Kiwify, Cartpanda, Stripe, Eduzz, Monetizze, pixels Meta/TikTok,
  GTM, Vimeo/YouTube/Wistia…).
- `detect_funnel(links)` — mapeia links em etapas
  (Landing Page → VSL → Checkout → Upsell → Thank You).
- `_build_html(bundle)` — gera um HTML standalone reconstruindo o funil.

## Exposição via API
- `POST /v1/clone` — corpo `{ "offer_id": "...", "url": "...", "niche": "..." }`.
  - Informe `offer_id` (busca o offer ranqueado) **ou** `url` (fetch real).
  - Retorna `{ clone_id, source, headline, bullets, ctas, funnel,
    detected_stack, images, html, exported_at }`.

## SLA / propriedades
- `< 10s` por clone (rede permitindo).
- Nunca quebra o pipeline: qualquer erro de fetch vira fallback template.
- Uso ético: ferramenta de **estudo/referência** (ver `docs/09-security/compliance.md`).
