# 📕 Runbooks — SpyFy

Guias operacionais para incidentes comuns. Cada runbook: sintoma → diagnóstico → ação → verificação.

---

## RB-01 — API com alta latência / erros

**Sintoma:** alertas de p95 > 1s ou error rate > 2%.

**Diagnóstico:**
1. Grafana → dashboard API (RED).
2. Verificar saturação de pods (CPU/mem).
3. Checar dependências: Postgres (conexões), Redis, Elasticsearch.
4. Traces no Tempo para o endpoint lento.

**Ação:**
- Se saturação → escalar réplicas (HPA já deve; forçar se preciso).
- Se Postgres → checar queries lentas (`pg_stat_activity`), PgBouncer.
- Se dependência externa → ativar circuit breaker / degradar graciosamente.

**Verificação:** p95 e error rate voltam ao SLO por 15 min.

---

## RB-02 — Fila entupida / DLQ crescendo

**Sintoma:** profundidade de fila alta ou DLQ > 100.

**Diagnóstico:**
1. Dashboard de filas: qual fila e idade do job mais antigo.
2. Ver logs dos workers (falhas repetidas?).
3. DLQ: inspecionar amostra de payloads.

**Ação:**
- Workers escalados? KEDA funcionando? Escalar manual se preciso.
- Erro sistemático (ex.: fonte mudou HTML) → hotfix scraper + reprocessar DLQ.
- Backpressure: pausar produtor se necessário.

**Verificação:** fila drenando; DLQ estável/zerando.

---

## RB-03 — Scraping bloqueado por uma fonte

**Sintoma:** taxa de bloqueio > 30% para uma rede.

**Diagnóstico:**
1. Dashboard de scraping por fonte.
2. Logs: captchas, 403/429, mudança de layout.

**Ação:**
- Rotacionar pool de proxies / fingerprints.
- Reduzir rate para a fonte.
- Ativar circuit breaker da fonte + alertar squad Cloner.
- Se mudança de layout → atualizar extrator.

**Verificação:** taxa de sucesso normaliza.

---

## RB-04 — Clonagem falhando

**Sintoma:** clone success rate < 90%.

**Diagnóstico:**
1. Temporal UI: workflows falhos e etapa que falha.
2. Logs do Cloner Worker.

**Ação:**
- Etapa fetch → LP com SPA/anti-bot → ajustar espera/proxy.
- Etapa assets → timeout/CDN → retry.
- Etapa funil → heurística falhando → fallback só metadados.

**Verificação:** success rate > 95%.

---

## RB-05 — Freshness de dados atrasada

**Sintoma:** lag de ingestão > 15 min.

**Diagnóstico:**
1. Dashboard de pipeline: lag por estágio.
2. Ingestion service saudável? Indexer? ClickHouse loader?

**Ação:**
- Escalar workers de ingestão/enrichment.
- Verificar backpressure e conexões de DB.
- Reprocessar backlog.

**Verificação:** lag < 5 min.

---

## RB-06 — Custo de IA disparado

**Sintoma:** alerta de custo diário de IA acima do orçamento.

**Diagnóstico:**
1. Dashboard de custo por agent/modelo.
2. Pico de volume? Retries em loop? Modelo caro sendo usado demais?

**Ação:**
- Ativar roteamento p/ modelo mais barato.
- Verificar cache de embeddings/classificações.
- Cortar reprocessamento desnecessário.

**Verificação:** custo volta à baseline.

---

## RB-07 — Falha de pagamento / billing divergente

**Sintoma:** webhooks Stripe falhando ou saldo de créditos divergente.

**Diagnóstico:**
1. Logs de webhook + dashboard Stripe.
2. Job de reconciliação diária.

**Ação:**
- Reprocessar webhooks (idempotente).
- Rodar reconciliação Stripe ↔ Postgres.
- Dunning para pagamentos falhos.

**Verificação:** reconciliação sem divergência.

---

## RB-08 — Incidente de segurança suspeito

**Sintoma:** acesso anômalo / alerta SIEM.

**Ação (imediata):**
1. Acionar on-call de segurança + declarar severidade.
2. Isolar (revogar credenciais/chaves comprometidas).
3. Preservar evidências (audit logs).
4. Comunicar stakeholders.
5. Post-mortem + disclosure se aplicável.

Ver [security.md](../09-security/security.md).

---

## Escalonamento

| Severidade | Exemplo | Resposta |
|-----------|---------|----------|
| SEV1 | Plataforma fora | Page imediato, war room |
| SEV2 | Feature crítica degradada | Page, correção prioritária |
| SEV3 | Degradação parcial | Horário comercial |
| SEV4 | Cosmético | Backlog |

## Após o incidente

- Post-mortem blameless (template em [observability.md](observability.md)).
- Ações corretivas com owner e prazo.
- Atualizar runbook.
