# 💰 Scale & ROI Engine (A9) — SpyFy

Motor que **estima escala (volume/investimento), ROI, ROAS e winning score** de cada oferta a partir de sinais públicos. Código real e testado em `apps/workers-py/spyfy/roi.py`.

> ⚠️ Todas as saídas monetárias/volume são **estimativas** (rotuladas), derivadas de dados públicos + economia do nicho. Não são números oficiais do anunciante.

## Sinais de entrada (`AdSignals`)

| Sinal | Fonte | Uso |
|-------|-------|-----|
| `first_seen` / `last_seen` | Ad Library | longevidade |
| `creative_variants` | agrupamento por anunciante | intensidade de teste |
| `est_impressions_low/high` | faixa da Ad Library | volume |
| `engagement` | likes/comments/shares | tração |
| `networks` / `countries` | cross-network linking | spread/escala |

## Economia do nicho (`NicheEconomics`)

Calibrável por dados históricos (ticket, CVR, CTR, CPM, upsell, refund). Ex.: keto BR = ticket $57, CVR 2.5%, CTR 1.4%, CPM $14.

## Fórmulas

```
longevity_days   = last_seen - first_seen
impressions(est) = média_geométrica(low, high)   # ou proxy por longevidade×variantes
daily_impr       = impressions / longevity_days

daily_spend   = daily_impr / 1000 * CPM
daily_clicks  = daily_impr * CTR
daily_sales   = daily_clicks * CVR

front_rev   = daily_sales * ticket
upsell_rev  = daily_sales * upsell_take * upsell_ticket
gross_rev   = (front_rev + upsell_rev) * (1 - refund_rate)

daily_profit = gross_rev - daily_spend
ROAS         = gross_rev / daily_spend
ROI%         = daily_profit / daily_spend * 100
```

### Winning Score (0–100)

```
score = Σ (peso_i × norm(sinal_i))  /  Σ pesos
norm(x) = tanh(x / escala)          # saturação suave
```
Pesos default: longevidade 1.0 · volume 2.0 · variantes 0.6 · engajamento 0.8 · spread 0.5. **Calibráveis via A/B.**

### Sinal de escala

```
heat = (dias≥7) + (dias≥30) + (variantes≥5) + (impr/dia≥50k)
sinal = [cold, warming, scaling, hot, hot][min(heat,4)]
```

## Uso (Python)

```python
from datetime import datetime, timedelta, timezone
from spyfy.roi import AdSignals, NicheEconomics, estimate_offer

now = datetime.now(timezone.utc)
sig = AdSignals(first_seen=now - timedelta(days=63), last_seen=now,
                creative_variants=9, est_impressions_low=1_000_000,
                est_impressions_high=5_000_000, engagement=8200,
                networks=2, countries=3)
econ = NicheEconomics(avg_ticket=57, cvr=0.025, ctr=0.014, cpm=14,
                      upsell_take=0.4, upsell_ticket=39, refund_rate=0.09)

est = estimate_offer(sig, econ)
print(est.winning_score, est.scaling_signal, est.est_roi_pct)
```

## Resultado validado (exemplo real da execução)

```
=== WINNER ===
longevidade: 63d | score: 82.9 | sinal: hot | conf: 0.95
impressoes(est): 2,236,067 | gasto/dia: $497 | receita/dia: $821
lucro/dia(est): $324 | ROAS: 1.65 | ROI: 65.2%

=== LOSER ===
longevidade: 3d | score: 29.3 | sinal: cold | conf: 0.55
impressoes(est): 15,000 | gasto/dia: $70 | receita/dia: $116
```

## Ranking de ofertas (feed)

```python
from spyfy.roi import rank_offers
ranked = rank_offers([("a", sig_a), ("b", sig_b)], econ)
# [{offer_id, score, roi_pct, signal, daily_profit}, ...] desc por score
```

## Confiança da estimativa

- Base 0.4; +0.35 com faixa de impressões real; +0.15 com engajamento; +0.10 se ≥14 dias.
- Máx. 0.95. Estimativas de baixa confiança são rotuladas na UI.

## Calibração (data-driven)

- `NicheEconomics` por nicho/país mantido em tabela e atualizado com dados reais (quando usuários reportam performance ou via benchmarks).
- Pesos do score ajustados por experimentos de relevância (NDCG).
- Backtesting: comparar previsão de "escalando" vs longevidade futura observada.

## Integração no pipeline

```
A4 Enricher → A9 Scale/ROI → grava offers.winning_score + métricas
                              → ClickHouse (analytics) → dashboards/alertas
```
- A9 roda em <1s por oferta (sem LLM — puramente numérico).
- Recalcula quando novos snapshots chegam (longevidade/variantes mudam).

## Testes

`apps/workers-py/tests/test_roi.py` — 8 testes (winner>loser, longevidade, sinais, confiança, média geométrica, ROI positivo, ranking, bounds). **Todos passando.**

## Métricas do engine

- Cobertura: % de ofertas com estimativa de ROI.
- Acurácia do sinal "escalando" (validação temporal).
- Distribuição de winning_score por nicho.
