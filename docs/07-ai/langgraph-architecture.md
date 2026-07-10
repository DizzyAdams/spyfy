# 🕸️ Arquitetura LangGraph/LangChain — SpyFy

Arquitetura **multi-agente stateful** para descobrir, enriquecer e **clonar ofertas em tempo real**, construída com **LangGraph** (grafos de estado) + **LangChain** (tools) + **LangSmith** (observabilidade).

## Por que LangGraph

- **Estado explícito e durável** (checkpointers) → clonagem longa sobrevive a falhas.
- **Ciclos e branches** → retries, reflexão, roteamento condicional.
- **Human-in-the-loop** (interrupts) → revisão de baixa confiança.
- **Streaming nativo** → progresso em tempo real para a UI.
- **Subgraphs** → cada domínio (scrape/enrich/clone) é um grafo componível.

## Topologia (Supervisor + Subgraphs)

```
                    ┌──────────────────────┐
                    │  Supervisor (router)  │
                    │  planeja e delega     │
                    └───────────┬──────────┘
        ┌───────────┬───────────┼───────────┬────────────┐
        ▼           ▼           ▼           ▼            ▼
  ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌───────────┐
  │ Scout    ││ Enricher ││ Cloner   ││ Analyst  ││ Guard/QA  │
  │ subgraph ││ subgraph ││ subgraph ││ subgraph ││ subgraph  │
  └──────────┘└──────────┘└──────────┘└──────────┘└───────────┘
        │           │           │           │            │
        └───────────┴─ shared state + checkpointer ──────┘
```

## Estado global (State Schema)

```python
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph.message import add_messages

class OfferState(TypedDict):
    objective: str
    offer_id: str | None
    landing_url: str | None
    messages: Annotated[list, add_messages]
    discovered_ads: Annotated[list, add]
    assets: Annotated[list, add]
    funnel_steps: Annotated[list, add]
    events: Annotated[list, add]          # progresso p/ streaming
    stack: dict | None
    copy: dict | None
    transcript: dict | None
    clone_bundle_url: str | None
    next: str | None
    confidence: float
    needs_human: bool
```

## Supervisor (roteador)

```python
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END

MEMBERS = ["scout", "enricher", "cloner", "analyst", "guard"]

supervisor_llm = ChatAnthropic(
    model="claude-sonnet-4"
).with_structured_output(Route)   # {"next": Literal[*MEMBERS, "FINISH"]}

SUPERVISOR_PROMPT = """Você é o supervisor do SpyFy.
Dado o objetivo e o estado atual, escolha o próximo agente:
- scout: descobrir/coletar anúncios
- enricher: nicho/idioma/ângulo, transcrição, embeddings
- cloner: reconstruir LP + mapear funil
- analyst: métricas, longevidade, sinal de escala
- guard: validar qualidade/fidelidade
Responda com o próximo passo ou FINISH quando completo."""

def supervisor(state: OfferState) -> dict:
    decision = supervisor_llm.invoke(
        [{"role": "system", "content": SUPERVISOR_PROMPT}, *state["messages"]]
    )
    return {"next": decision.next}

def route(state: OfferState) -> str:
    return END if state["next"] == "FINISH" else state["next"]
```

## Montagem do grafo principal

```python
from langgraph.checkpoint.postgres import PostgresSaver

## Streaming em tempo real (para a UI)

```python
config = {"configurable": {"thread_id": f"clone-{offer_id}"}}

async for event in graph.astream(
    {"objective": objective, "offer_id": offer_id,
     "messages": [("user", objective)]},
    config,
    stream_mode="updates",   # deltas de estado por nó
):
    for node, update in event.items():
        await ws.send_json({
            "node": node,
            "events": update.get("events", []),
        })
```

Modos de streaming:
- `updates` → deltas por nó (timeline de progresso).
- `messages` → tokens do LLM ao vivo (transcrição/copy em streaming).
- `custom` → eventos de negócio (`asset_downloaded`, `step_detected`).

## Persistência & retomada

- **PostgresSaver** salva checkpoints por `thread_id`.
- Falha no meio da clonagem → `await graph.ainvoke(None, config)` retoma do último checkpoint.
- Cada oferta = um thread durável, auditável e reexecutável.

## Human-in-the-loop

```python
state = graph.get_state(config)
if state.values["confidence"] < 0.6:
    # UI solicita aprovação humana; após aprovar:
    graph.update_state(config, {"needs_human": False})
    await graph.ainvoke(None, config)   # retoma execução
```

## Observabilidade (LangSmith)

- Trace por thread: nós, tools, tokens, custo, latência.
- Tags: `network`, `niche`, `offer_id`.
- Evals automáticos de extração/classificação (ver [ml-models.md](ml-models.md)).

## Controle de custo & confiabilidade

- Roteamento de modelo por complexidade (Haiku/mini para tarefas simples).
- Cache de prompts determinísticos (LangChain cache).
- `recursion_limit` no `compile`/config para evitar loops infinitos.
- Fallback entre provedores (Claude ↔ GPT) via `.with_fallbacks([...])`.

## Próximos documentos

- [langgraph-agents.md](langgraph-agents.md) — implementação de cada subgraph com tools.
- [realtime-cloning.md](realtime-cloning.md) — engine de clonagem em tempo real (pipeline, streaming, infra).


builder = StateGraph(OfferState)
builder.add_node("supervisor", supervisor)
builder.add_node("scout", scout_subgraph)
builder.add_node("enricher", enricher_subgraph)
builder.add_node("cloner", cloner_subgraph)
builder.add_node("analyst", analyst_subgraph)
builder.add_node("guard", guard_subgraph)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route, MEMBERS + [END])
for m in MEMBERS:
    builder.add_edge(m, "supervisor")   # volta ao supervisor

checkpointer = PostgresSaver.from_conn_string(DB_URL)
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["cloner"],        # aprovação opcional antes de clonar
)
```
