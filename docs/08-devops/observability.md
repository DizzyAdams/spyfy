# 👀 Observabilidade — SpyFy

## Pilares

1. **Métricas** — Prometheus + Grafana.
2. **Logs** — Loki (agregação estruturada).
3. **Traces** — Tempo + OpenTelemetry.
4. **Erros** — Sentry (front e back).
5. **Product analytics** — PostHog.

## Instrumentação

- OpenTelemetry SDK em todos os serviços (traces + métricas).
- Logs estruturados (JSON) com `request_id`, `workspace_id`, `trace_id`.
- Correlação log ↔ trace ↔ métrica.

## Métricas-chave (SLIs)

| Domínio | SLI |
|---------|-----|
| API | latência p95, taxa de erro, RPS |
| Busca | latência de query, zero-result rate |
| Scraping | anúncios/min, taxa de bloqueio, custo/1k |
| Clonagem | tempo médio, success rate |
| Filas | profundidade, idade do job mais antigo, DLQ size |
| IA | tokens/job, custo, taxa de escalonamento |
| Infra | CPU/mem, saturação, pods restart |

## SLOs

| Serviço | SLO |
|---------|-----|
| API disponibilidade | 99.9% |
| Busca p95 | < 300ms |
| Clonagem success | > 95% |
| Freshness de dados | < 5 min lag |
| Error budget | 0.1%/mês |

## Dashboards (Grafana)

- Overview de plataforma (RED: Rate/Errors/Duration).
- Scraping por fonte.
- Filas e workers.
- Custo de IA e proxy.
- Business (WWOA, signups, clones/dia).

## Alertas

- Baseados em SLO (burn rate multi-window).
- Roteados por severidade (PagerDuty/Opsgenie/Slack).
- Runbooks linkados em cada alerta.

Exemplos:
```
- API error rate > 2% por 5 min → page
- DLQ > 100 → page
- Freshness lag > 15 min → page
- Custo diário de IA > $X → warn
- Taxa de bloqueio de scraping > 30% → warn
```

## Tracing distribuído

- Trace atravessa Gateway → Serviço → Fila → Worker.
- Span attributes: `network`, `niche`, `job_id`.
- Amostragem adaptativa (100% em erros).

## Logs

- Retenção: 30d quente, 90d frio.
- PII redigida em logs.
- Busca via Grafana/Loki (LogQL).

## On-call

- Rotação semanal.
- Runbooks por serviço em `docs/runbooks/`.
- Post-mortems blameless para incidentes SEV1/2.

## Post-mortem (template)

```
- Resumo
- Impacto (usuários, duração)
- Timeline
- Causa raiz
- O que funcionou / falhou
- Ações corretivas (com owner e prazo)
```

## Game Days

- Simulações trimestrais (perda de região, fila entupida, fonte bloqueando).
- Validam runbooks e DR.

## Business observability

- PostHog: funil de ativação, retenção, feature usage.
- Eventos-chave: signup, first_search, first_save, first_clone, upgrade.
