# 🎯 OKRs & Métricas — SpyFy

## North Star Metric

**WWOA — Weekly Winning Offers Actioned:** ofertas vencedoras que o usuário salva, clona ou exporta por semana.

## OKRs por trimestre (exemplo Q1)

### Objetivo 1 — Entregar valor rápido ao usuário
- **KR1:** TTFI (time-to-first-insight) < 5 min para 80% dos novos usuários.
- **KR2:** 60% dos novos usuários salvam ≥ 1 oferta em 24h (activation).
- **KR3:** WWOA médio ≥ 5 por usuário ativo.

### Objetivo 2 — Dados frescos e abrangentes
- **KR1:** freshness < 5 min de lag para 95% dos anúncios.
- **KR2:** cobertura de 3 redes (Meta, TikTok, Google).
- **KR3:** > 5M anúncios ativos indexados.

### Objetivo 3 — Cloner confiável
- **KR1:** clone success rate > 95%.
- **KR2:** tempo médio de clonagem < 60s.
- **KR3:** fidelidade visual média > 95%.

### Objetivo 4 — Negócio sustentável
- **KR1:** 1.000 usuários pagantes.
- **KR2:** churn mensal < 6%.
- **KR3:** conversão Free→Pro > 8% em 14 dias.

## Métricas por área

### Produto
| Métrica | Meta |
|---------|------|
| Activation (save em 24h) | > 60% |
| Retention D30 | > 45% |
| WWOA | ≥ 5 |
| NPS | > 40 |

### Discovery
| Métrica | Meta |
|---------|------|
| Busca p95 | < 300ms |
| Zero-result rate | < 5% |
| NDCG (relevância) | > 0.75 |

### Cloner
| Métrica | Meta |
|---------|------|
| Success rate | > 95% |
| Tempo médio | < 60s |
| Fidelidade | > 95% |

### Dados/IA
| Métrica | Meta |
|---------|------|
| Freshness lag | < 5 min |
| Precisão de nicho | > 90% |
| Custo IA / oferta | < $0.05 |

### Infra/SRE
| Métrica | Meta |
|---------|------|
| Uptime | 99.9% |
| MTTR | < 1h |
| Deploy frequency | diário |
| Change failure rate | < 15% |

### Negócio
| Métrica | Meta |
|---------|------|
| MRR growth | +15% m/m |
| Churn | < 6% |
| CAC payback | < 6 meses |
| LTV/CAC | > 3 |

## Instrumentação

- Eventos-chave (PostHog): `signup`, `first_search`, `first_save`, `first_clone`, `upgrade`, `alert_created`.
- Dashboards de negócio e produto.
- Revisão semanal de métricas; OKRs revisados trimestralmente.

## Governança

- OKRs definidos por liderança + squads.
- Check-in quinzenal (confidence score 0–1).
- Retrospectiva de OKRs no fim do trimestre.
