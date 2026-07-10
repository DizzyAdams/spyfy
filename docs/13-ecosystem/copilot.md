# 🧙 SpyFy Copilot — Agente Conversacional do Ecossistema

O **Copilot** é um agente LangGraph que opera **toda a plataforma** por linguagem natural. É o "Jarvis do media buyer".

## O que ele faz

```
Usuário: "Ache ofertas de keto escalando no BR nos últimos 30 dias,
          resuma as VSLs das 3 melhores e clone a #1 em tempo real."

Copilot: [Scout] encontrei 42 ofertas ativas > 30d...
         [Analyst] 3 escalando: A (score 91), B (88), C (85)
         [Enricher] resumindo VSLs... A: gancho "sem dieta"; ...
         [Cloner] clonando A ao vivo → LP ✓ assets ✓ funil (5 steps) ✓
         Pronto! Bundle: spyfy.io/clones/cl_991  — salvei em "Keto BR".
```

## Arquitetura (LangGraph)

Reutiliza os subgraphs do Core (ver [langgraph-agents.md](../07-ai/langgraph-agents.md)) e adiciona uma camada conversacional com **memória de longo prazo** e **tools de plataforma**.

```
┌────────────────────────────────────────────┐
│              Copilot Graph                   │
│  ┌──────────┐   ┌───────────────────────┐   │
│  │ Planner  │──▶│ Supervisor (Core)     │   │
│  │ (intent) │   │ scout/enrich/clone... │   │
│  └──────────┘   └───────────────────────┘   │
│        │                                     │
│  ┌──────────┐   ┌───────────────────────┐   │
│  │ Memory   │   │ Platform Tools        │   │
│  │ (vetorial│   │ save/alert/export/... │   │
│  │  + thread│   └───────────────────────┘   │
│  └──────────┘                                │
└────────────────────────────────────────────┘
```

## Platform Tools (LangChain)

```python
@tool
async def search_offers(query: str, filters: dict) -> list: ...
@tool
async def clone_offer(offer_id: str) -> dict: ...          # dispara realtime
@tool
async def save_to_collection(offer_id: str, name: str) -> None: ...
@tool
async def create_alert(spec: dict) -> str: ...
@tool
async def export_report(niche: str, fmt: str) -> str: ...
@tool
async def compare_offers(ids: list[str]) -> dict: ...
@tool
async def get_trends(niche: str, days: int) -> dict: ...
```

## Memória

- **Curto prazo:** histórico do thread (checkpointer Postgres).
- **Longo prazo:** preferências do usuário e ofertas relevantes (pgvector).
  - "Você costuma focar em nutra BR com VSL longa" → personaliza respostas.
- **Semântica de workspace:** o Copilot conhece as coleções/alertas do time.

## Streaming conversacional

```python
async for token in copilot.astream(
    {"messages": [("user", prompt)]},
    config, stream_mode="messages"
):
    yield token   # UI mostra a resposta + ações sendo executadas ao vivo
```

- Respostas em streaming (tokens).
- Ações intercaladas ("clonando..." com progresso em tempo real).
- Cards ricos: ofertas, funis, gráficos embutidos no chat.

## Modos do Copilot

| Modo | Descrição |
|------|-----------|
| **Ask** | Perguntas ("qual nicho está saturando?"). |
| **Do** | Ações ("clone X", "crie alerta Y"). |
| **Auto** | Rotinas agendadas ("todo dia às 8h, me mande as novas ofertas escalando"). |
| **Briefing** | Gera briefs de criativo/copy a partir de ofertas. |

## Rotinas autônomas (Auto)

```yaml
routine: daily_winners
schedule: "0 8 * * *"
prompt: >
  Encontre novas ofertas escalando em nutra/keto BR nas últimas 24h,
  resuma e me envie no Slack. Clone automaticamente as com score > 90.
guardrails:
  max_clones_per_run: 3
  require_approval_if_confidence_below: 0.7
```

## Guardrails

- Confirmação para ações caras/irreversíveis (human-in-the-loop).
- Limite de gasto de créditos por sessão.
- Escopo por permissão do workspace (RBAC).
- Filtro de conteúdo e respeito a ToS/compliance.

## Interfaces

- Chat no web app (painel lateral onipresente ⌘K).
- Slack bot (`/spyfy`).
- API (`POST /v1/copilot/messages` com streaming).
- Voz (roadmap) — ditar comandos.

## Observabilidade & evals

- Trace por conversa (LangSmith).
- Evals de intenção (o Copilot chamou a tool certa?).
- Satisfação (thumbs up/down) alimenta fine-tuning de prompts.
- Métrica: **tarefas completadas por conversa** e **tempo economizado**.

## Por que é fora do comum

Nenhum concorrente tem um agente que **descobre + analisa + clona + organiza** por conversa, em tempo real, operando toda a plataforma. É a interface do futuro para performance marketing.
