# A1 — Agente Scout (SpyFy)

Agente técnico de reconhecimento da squd de mineração do SpyFy.

## Mapeamento de código

- **Módulo:** `apps/workers-py/spyfy/scraper_bridge.py`
- **Função:** `mine()`

## Responsabilidade

Descobre ofertas brutas (raw offers) em múltiplas redes de anúncios:

- `meta`
- `tiktok`
- `google`
- `youtube`
- `native`
- `pinterest`

## Fallback gracioso

O comportamento de `mine()` segue esta ordem:

1. Quando `simulate=True`: usa o gerador estruturado `build_offer`.
2. Quando `simulate=False` e existe token/biblioteca real disponível:
   - chama `MetaAdLibrary`, `TikTokAdLibrary` ou `GoogleAdsTransparency`
   - conforme a rede alvo.
3. Em caso de qualquer erro ( rede, auth, parse), **recua automaticamente**
   para o simulador (`build_offer`).

## SLA de frescor

- **Freshness SLA:** dados com idade inferior a **5 minutos** (`<5min`).

## Resiliência

- Nunca interrompe o pipeline (não quebra a mineração) em falha de rede.
- Falhas são absorvidas e substituídas pelo simulador, garantindo
  continuidade da coleta.
