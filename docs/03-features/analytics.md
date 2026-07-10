# 📊 Analytics & Insights — SpyFy

## Objetivo

Transformar o volume bruto de anúncios em **inteligência de mercado acionável**: o que está escalando, tendências por nicho, saturação e concorrência.

## Dashboards

### 1. Market Overview (por nicho)
- Nº de ofertas ativas.
- Novas ofertas nos últimos 7/30 dias.
- Distribuição por rede, país, formato.
- Top anunciantes.

### 2. Winning Offers
- Ranking de ofertas por winning_score.
- Ofertas "em ascensão" (score subindo).
- Longevidade média do nicho.

### 3. Trend Radar
- Ângulos/temas emergentes (via clustering de embeddings).
- Sazonalidade.
- Comparação período vs período.

### 4. Competitor Watch
- Timeline de anúncios de um anunciante.
- Novos criativos, frequência de lançamento.
- Estimativa de investimento relativo.

### 5. Saturation Index
- Quão saturado está um nicho/ângulo.
- Nº de anunciantes rodando ofertas similares.

## Métricas & definições

| Métrica | Definição |
|---------|-----------|
| Active Offers | ofertas com anúncio ativo no período. |
| New Offers | primeira aparição no período. |
| Longevity | dias entre first_seen e last_seen. |
| Est. Impressions | estimativa via faixas públicas + modelo. |
| Winning Score | score composto (ver data-model). |
| Saturation | nº de anunciantes / similaridade de ofertas. |
| Scaling Signal | derivada positiva de criativos+longevidade. |

## Fonte de dados

- **ClickHouse** para agregações OLAP.
- Materialized views para dashboards rápidos.
- Refresh incremental (near real-time).

## Exemplo de query (ClickHouse)

```sql
SELECT niche,
       count() AS active_offers,
       avg(longevity_days) AS avg_longevity
FROM offer_daily
WHERE observed_date >= today() - 30
  AND active = 1
GROUP BY niche
ORDER BY active_offers DESC
LIMIT 20;
```

## Detecção de "escalando"

```
Para cada oferta:
  slope = regressão linear (creative_count + longevity) nos últimos 14d
  se slope > threshold e longevity >= 7d:
     marcar como "scaling" → disparar alerta
```

## Relatórios

- **Relatório de nicho** (PDF/white-label): overview + top ofertas + tendências.
- **Relatório de concorrente**: timeline + criativos + estimativas.
- **Export**: CSV/JSON via API.

## Alertas inteligentes

- Baseados em thresholds + anomalia (detecção estatística).
- Deduplicados e priorizados (não spammar).

## Métricas de sucesso do módulo

- Adoção de dashboards (WAU).
- Relatórios gerados/exportados.
- Precisão dos sinais de "escalando" (validação amostral).
- Taxa de ação sobre insights.

## Privacidade & estimativas

- Todas as estimativas são claramente rotuladas como tal.
- Dados agregados; sem PII de usuários finais dos anúncios.
- Ver [compliance.md](../09-security/compliance.md).
