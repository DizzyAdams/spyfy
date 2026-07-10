# 👥 Time de 14 Agents Especializados — SpyFy (tempo real)

Um "digital workforce" de **14 agents LangGraph**, um por spec, coordenados por um Orchestrator, operando **em tempo real** sobre o SpyFy Graph. Cada agent tem tools, guardrails, SLAs e métricas próprias.

## Organograma

```
                        ┌─────────────────────────┐
                        │  A0 · Orchestrator       │
                        │  (planeja/roteia/streama)│
                        └────────────┬────────────┘
   ┌──────────┬──────────┬──────────┼──────────┬──────────┬──────────┐
   ▼          ▼          ▼          ▼          ▼          ▼          ▼
 A1 Scout  A2 Browser A3 Library A4 Enrich  A5 Trans.  A6 Stack   A7 Funnel
 (discover)(headless) (API/libs) (classify) (VSL)     (finger)   (walker)
   ▼          ▼          ▼          ▼          ▼          ▼          ▼
 A8 Copy   A9 Scale/  A10 Dedup  A11 Clone  A12 Guard  A13 Alert  (todos ->
 (extract) ROI        /Graph     (assemble) /QA        /Notify     Graph)
```

## Catálogo dos 14 agents

| # | Agent | Spec | Tools principais | Saída | SLA |
|---|-------|------|------------------|-------|-----|
| A0 | **Orchestrator** | planejamento/roteamento | registry, memory, stream | plano + delegação | <2s/decisão |
| A1 | **Scout** | descoberta de ofertas | scrape_network, search | anúncios brutos | freshness <5min |
| A2 | **Browser Miner** | mineração headless | Playwright, proxy, XHR intercept | DOM/JSON/assets | <8s/página |
| A3 | **Library Miner** | mineração via API/libs | Meta API, TikTok CC, requests | dados estruturados | <2s/call |
| A4 | **Enricher** | nicho/idioma/ângulo | LLM, classifier, embeddings | metadados+vetor | <3s/ad |
| A5 | **Transcriber** | VSL → texto | Whisper, LLM struct | transcrição+resumo | <RTF 0.5 |
| A6 | **Stack Detector** | fingerprint | detect_stack, netlog | checkout/pixels | <1s |
| A7 | **Funnel Walker** | mapear funil | headless sandbox | LP→upsell→TY | <25s |
| A8 | **Copy Extractor** | copy/estrutura | LLM structured output | headline/CTA/bullets | <5s |
| A9 | **Scale/ROI Analyst** | escala e ROI | roi.py engine, ClickHouse | score/ROAS/ROI | <1s |
| A10 | **Dedup/Graph** | dedup + grafo | pgvector, upsert | Graph atualizado | idempotente |
| A11 | **Cloner** | montar bundle | packager, R2 | clone_bundle | <10s |
| A12 | **Guard/QA** | qualidade/fidelidade | visual diff, checks | score+flags | <4s |
| A13 | **Alert/Notify** | alertas em tempo real | webhook, slack, ws | notificações | <1s |

## Coordenação em tempo real

- **Estado compartilhado** `OfferState` + checkpointer Postgres (ver [langgraph-architecture.md](../07-ai/langgraph-architecture.md)).
- **Streaming**: cada agent emite `events` → WebSocket → UI ao vivo.
- **Paralelismo**: A2/A3 (mineração) e A4/A5/A6 (enrichment) rodam via map-reduce (`Send`).
- **Backpressure**: filas por agent (BullMQ/KEDA), escala independente.

## Fluxo end-to-end (tempo real)

```
A0 recebe objetivo → planeja
 ├─ A1 Scout descobre alvos
 ├─ A2 Browser + A3 Library mineram em paralelo
 ├─ A4/A5/A6/A8 enriquecem (paralelo)
 ├─ A9 calcula escala/ROI/score
 ├─ A10 dedup + grava no Graph
 ├─ A7 mapeia funil → A11 clona → A12 QA
 └─ A13 dispara alertas
 A0 streama cada passo para a UI
```

## Spawn dos agents (LangGraph)

```python
AGENTS = {
  "orchestrator": build_orchestrator(),
  "scout": build_scout(),        "browser": build_browser_miner(),
  "library": build_library_miner(),"enricher": build_enricher(),
  "transcriber": build_transcriber(),"stack": build_stack_detector(),
  "funnel": build_funnel_walker(),"copy": build_copy_extractor(),
  "roi": build_roi_analyst(),    "dedup": build_dedup_graph(),
  "cloner": build_cloner(),      "guard": build_guard(),
  "alert": build_alert_agent(),
}
graph = wire_supervisor(AGENTS)      # supervisor + subgraphs
app = graph.compile(checkpointer=PostgresSaver.from_conn_string(DB_URL))
```

## Guardrails por agent

- Timeout + max steps individuais.
- Orçamento de tokens/custo por agent (A4/A5/A8 são os caros).
- Respeito a ToS/robots (A1/A2/A3).
- Sandbox isolada (A2/A7) sem acesso à VPC.
- Human-in-the-loop se `confidence < 0.6` (A12 escala p/ humano).

## Observabilidade

- Trace por agent (LangSmith/OTel): passos, tools, tokens, custo, latência.
- Dashboard "workforce": throughput por agent, fila, taxa de erro, custo.
- Métricas de negócio: ofertas/min, clones/min, ROI médio detectado.

## Escala do time

- Cada agent é um **worker autoescalável** (KEDA por profundidade de fila).
- Redes/nichos são **shards** → o time inteiro roda em paralelo por shard.
- Spot instances para A2/A5 (tolerantes a interrupção).

## Ver também
- [browser-mining.md](browser-mining.md) — engine do A2.
- [library-mining.md](library-mining.md) — engine do A3.
- [scale-roi-engine.md](scale-roi-engine.md) — engine do A9 (código em `apps/workers-py/spyfy/roi.py`).
