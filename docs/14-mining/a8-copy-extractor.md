# A8 — Copy Extractor (Extrator de Copy)

**Papel:** extrai *headline*, *CTA*, *bullets* e a *estrutura* (títulos/seções)
de ofertas e landing pages para alimentar enriquecimento, ROI e clonagem.

## Implementação 1 — Heurística + LLM opcional (`agents/orchestrator.py`)

- `_extract_copy(o, llm)`: extração puramente heurística — lê os campos
  `headline`, `cta`, `bullets`, `format` já presentes no dict do offer.
  Marca `by: "llm" if llm else "heuristic"`.
- `_make_copy(llm)`: builder do nó LangGraph `copy`. Mapeia `discovered_ads`,
  chama `_extract_copy` por oferta e emite o evento `copy.extracted`.
  O `llm` (BaseChatModel) é hook *best-effort*: se ausente, cai em heurística
  (grafo 100% offline e determinístico, sem rede/API key).

## Implementação 2 — Extração real de HTML (`clone.py`, novo)

- `_PageExtractor(HTMLParser)`: parser da stdlib `html.parser`
  (`convert_charrefs=True`) que coleta:
  - `title` (tag `<title>`)
  - `h1` / `h2` (headings)
  - `<p>` (parágrafos)
  - `<li>` (bullets)
  - `<a class=…>` contendo `btn`/`cta`/`button`/`comprar`/`buy` → **CTAs**
  - `<img>` (imagens, com `src`/`data-src`/`srcset`)
  - ignora `script`/`style`/`noscript` (`_skip`).
- `_extract(page_html, base_url)`: roda o parser, normaliza `href`/imagens
  via `urljoin` e limita listas (h1≤5, h2≤8, paras≤10, bullets≤15, ctas≤10, imgs≤24).
- Consumido por `clone_offer()` para montar `headline` (h1[0]), `subheadline`
  (h2[0] ou para[0]), `bullets`, `ctas` e `images` do clone bundle.

## SLA

- **Tempo de extração < 5 s** por oferta/URL (fetch + parse stdlib, sem
  browser/bs4 — adequado a free tier e execução offline).
