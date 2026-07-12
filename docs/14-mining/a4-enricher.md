# A4 — Enricher (Agente de Enriquecimento)

Classifica o **nicho**, **idioma** e **ângulo** de cada anúncio descoberto
pelo scout, produzindo metadados (`niche`, `angle`, `language`, `confidence`)
consumidos pelas etapas seguintes do grafo.

## Implementação

Mapeado em `apps/workers-py/spyfy/agents/orchestrator.py`:

- `_classify(o, llm=None)` — classifica um anúncio individual.
- `_make_enricher(llm=None)` — factory do nó `enricher` (closure); itera
  `state["discovered_ads"]` chamando `_classify` para cada um e agrega
  confiança média + evento `offer.enriched`.

## Heurística (determinística, offline)

1. **Texto**: concatena `headline` + `bullets` em minúsculas.
2. **Ângulo** (default `beneficio`):
   - `transformacao` se houver *emagrec, gordura, peso, keto, vidro, cilios, pele*.
   - `liberdade_financeira` se houver *renda, divida, invest, fatura r$, trafego pago*.
3. **Idioma**: `pt-BR` se houver *voc, para, com, sem, que*; senão `en`.
4. **Confiança fixa**: `0.7`.

## Hook de LLM (opcional, best-effort)

Se `llm` for injetado, tenta `llm.invoke("Classifique nicho/ângulo: ...")`.
Em caso de falha (`except Exception`), **silencia e mantém a heurística**
degradação graciosa, sem rede obrigatória.

## SLA

Tempo de processamento **< 3s por anúncio** (heurística pura é O(n) e offline).
