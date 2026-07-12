# SpyFy Orchestrator (A0)

O **Orchestrator (A0)** é o agente supervisor que coordena a mineração de ofertas no SpyFy.

## Mapeamento de código

- **Arquivo:** `apps/workers-py/spyfy/agents/orchestrator.py`
- **Funções principais:**
  - `build_offer_graph()` — constrói o grafo LangGraph.
  - `run_offer_pipeline()` — executa o pipeline de ofertas.

## Arquitetura

O Orchestrator é implementado como um **supervisor LangGraph** que roteia as tarefas entre os membros do time.

### Membros (MEMBERS)

O supervisor distribui o trabalho para os seguintes agentes:

- `scout` — descoberta de ofertas.
- `enricher` — enriquecimento de dados.
- `copy` — geração de texto/copy.
- `roi` — cálculo de retorno sobre investimento.
- `dedup` — deduplicação de ofertas.
- `guard` — validação e conformidade.
- `alert` — disparo de alertas.

## Human-in-the-loop

A execução utiliza um **checkpointer `MemorySaver`**, permitindo a retomada do fluxo com intervenção humana por meio do `thread_id`. Isso possibilita pausar, revisar e continuar o pipeline de forma stateful.
