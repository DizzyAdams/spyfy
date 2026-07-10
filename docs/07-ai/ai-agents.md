# 🧠 Agentes de IA — Implementação — SpyFy

Detalhes de implementação dos sub-agents descritos em [02-team/sub-agents.md](../02-team/sub-agents.md).

## Framework

- **LangGraph** para grafos de estado (planejamento + execução).
- **LangChain** para tools e integrações.
- Modelos: **Claude** (raciocínio/estrutura longa), **GPT** (extração/classificação), **Whisper** (áudio).

## Grafo do Orchestrator

```
       ┌─────────┐
       │  START  │
       └────┬────┘
            ▼
      ┌───────────┐
      │  Planner  │ (decompõe objetivo em tarefas)
      └────┬──────┘
           ▼
     ┌───────────┐   loop
     │  Router   │──────────┐
     └────┬──────┘          │
          ▼                 │
   ┌─────────────┐          │
   │ Tool/Agent  │          │
   │ Execution   │──────────┘
   └────┬────────┘
        ▼
   ┌───────────┐
   │ Reflect/QA│
   └────┬──────┘
        ▼
   ┌─────────┐
   │  END    │
   └─────────┘
```

## Definição de tools

```python
@tool
def headless_fetch(url: str) -> str:
    """Renderiza uma página e retorna o HTML final."""
    ...

@tool
def stack_detector(html: str) -> dict:
    """Detecta checkout, builder e pixels."""
    ...

@tool
def transcribe(video_url: str) -> str:
    """Transcreve VSL com Whisper."""
    ...
```

## Prompts (padrões)

- **System prompt** por agent, versionado em `packages/prompts`.
- Few-shot para classificação de nicho/ângulo.
- Structured output (JSON schema) para extração.

Exemplo (extração de copy):
```
Você é um especialista em copy de resposta direta.
Extraia da landing page: headline, subheadline, bullets,
CTA principal, garantia, provas sociais.
Responda em JSON seguindo o schema fornecido.
```

## Structured output

- Usa function calling / JSON mode.
- Validação com Pydantic/Zod; retry se inválido.

## Memória

- **Curto prazo:** estado do grafo (checkpoints).
- **Longo prazo:** pgvector (ofertas conhecidas, dedup, "similares").

## Human-in-the-loop

- Confiança < threshold → cria tarefa de revisão.
- Interrupção do grafo (LangGraph interrupt) até aprovação.

## Avaliação (Evals)

- Dataset rotulado por tarefa (classificação, extração).
- Métricas: accuracy, F1, fidelidade de extração.
- Regressão de prompts em CI (evals rodam antes de merge).
- Tracing com LangSmith/OpenTelemetry.

## Controle de custo

- Roteamento de modelo por complexidade (modelo barato p/ tarefas simples).
- Cache de prompts/respostas determinísticas.
- Orçamento de tokens por job; alerta ao estourar.

## Guardrails

- Timeout e max steps por agent.
- Respeito a ToS/robots no scraping.
- Filtro de conteúdo (sem gerar conteúdo enganoso/ilegal).
- Red-teaming periódico.

## Confiabilidade

- Retries com backoff.
- Idempotência (mesmo input → mesmo output persistido).
- Fallback entre provedores (Claude ↔ GPT).

## Observabilidade

- Trace por job: passos, tools, tokens, custo, latência.
- Taxa de sucesso e de escalonamento humano.
- Dashboards por agent.
