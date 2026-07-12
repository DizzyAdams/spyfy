# A3 — Library Miner

Agente de mineração do esquadrão SpyFy 14. Coleta anúncios reais via **APIs/libs oficiais** das ad libraries, sem scraping genérico, e degrada graciosamente para o simulador quando a fonte falha.

## Responsabilidade

Minerar criativos/ofertas de anúncios ativos das três plataformas suportadas, mapeando cada integração para a lib correspondente em `apps/workers-py/spyfy/`.

## Mapeamento de fontes

| Plataforma | Arquivo | Classe | Credencial |
|------------|---------|--------|------------|
| Meta (FB/IG) | `meta_library.py` | `MetaAdLibrary` | `access_token` |
| TikTok | `tiktok_library.py` | `TikTokAdLibrary` | `token` |
| Google | `google_library.py` | `GoogleAdsTransparency` | nenhuma (web-scrape) |

- **Meta** e **TikTok** usam APIs oficiais e exigem um token de acesso válido.
- **Google** não usa token: faz web-scrape de `adstransparency.google.com` via `httpx` + `html.parser`.

## Tratamento de falha

Cada integração levanta um `*ScrapeError` quando a resposta vem **vazia ou bloqueada**:

- `MetaScrapeError` (`meta_library.py`)
- `TikTokScrapeError` (`tiktok_library.py`)
- `GoogleTransparencyError` (`google_library.py`)

O chamador captura o erro e **cai para o simulador** (dados sintéticos), garantindo que o pipeline de mineração continue operando sem fonte real.

## Contrato

`search(query) -> list[Offer]`; em caso de vazio/bloqueio, lançar `*ScrapeError` para acionar o fallback do simulador.
