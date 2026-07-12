# A9 — Scale/ROI Analyst

Agente da squad de mining que **calcula escala e ROI** de ofertas de ads a partir de sinais públicos (longevidade, criativos, impressões, economia do nicho). Toda saída de dinheiro/volume é **estimativa rotulada**, nunca fato.

## Responsabilidades
- Estimar volume diário (impressões, gasto, cliques, vendas, receita, lucro).
- Calcular o **winning_score** (0–100) e o **scaling_signal** (cold→hot).
- Projetar ROAS e ROI% e a probabilidade de a oferta continuar vencedora.

## Mapeamento de código
- **`apps/workers-py/spyfy/roi.py`** — núcleo do motor:
  - `estimate_offer(sig, econ, weights) -> OfferEstimate` — produz todas as estimativas.
  - `AdSignals` — sinais observados de uma oferta (longevidade, variantes, impressões, engajamento).
  - `NicheEconomics` — economia do nicho (ticket, CVR, CTR, CPM, upsell, refund) calibravel.
- **`apps/workers-py/spyfy/agents/orchestrator.py`** — pipeline:
  - `_estimate(o)` — monta `AdSignals` e chama `estimate_offer` com `NicheEconomics()` padrão.
  - `_make_roi()` — nó `roi` do grafo: itera `discovered_ads`, chama `_estimate`, converte via `_to_radar` e monta `analytics.offers`/`best`.
- **`apps/workers-py/spyfy/radar.py`** — `win_probability(o)` (logística sobre longevidade, variantes e sinal) usado pelo pipeline.

## Saídas
- `winning_score` (0–100): força da oferta (`roi.py`).
- `scaling_signal`: `cold | warming | scaling | hot` (`roi.py:_scaling_signal`).
- `est_roas`: receita/gaasto diário estimado.
- `est_roi_pct`: lucro/gaasto × 100.
- `est_daily_profit`: lucro diário estimado.
- `win_probability` (0–1): de `radar.win_probability` via `_make_roi`.

## SLA
Processamento < **1s** por oferta (engine determinístico, sem LLM).
