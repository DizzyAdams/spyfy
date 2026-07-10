# 🤖 Sub-Agents de IA — SpyFy

Os **sub-agents** são agentes de IA autônomos e especializados que executam o trabalho pesado da plataforma 24/7. São orquestrados via **LangGraph** e coordenados por um **Orchestrator Agent**.

## Arquitetura de orquestração

```
                ┌────────────────────────┐
                │   Orchestrator Agent    │
                │  (planeja e roteia)     │
                └───────────┬────────────┘
      ┌──────────┬──────────┼──────────┬───────────┬──────────┐
      ▼          ▼          ▼          ▼           ▼          ▼
 ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
 │Scraper │ │Classify│ │Transcr.│ │ Cloner │ │Analyst │ │  QA    │
 │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
 └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

## Catálogo de sub-agents

### 1. Orchestrator Agent
- **Papel:** recebe objetivos ("descobrir ofertas keto BR ativas > 30d"), decompõe em tarefas e roteia.
- **Modelo:** Claude / GPT (raciocínio).
- **Ferramentas:** fila de jobs, registro de agents, memória.
- **Output:** plano de execução + delegação.

### 2. Scraper Agent
- **Papel:** coletar anúncios de redes-alvo.
- **Ferramentas:** Playwright, Crawlee, proxy pool, resolver de captcha.
- **Entrada:** rede, nicho, filtros.
- **Saída:** anúncios brutos + assets → evento `AdDiscovered`.
- **Guardrails:** respeita robots/ToS configurados, rate limit por domínio.

### 3. Classifier Agent (Enrichment)
- **Papel:** classificar nicho, idioma, país, formato, ângulo.
- **Modelo:** LLM + classificador fine-tuned + embeddings.
- **Saída:** metadados normalizados + embedding.

### 4. Transcribe Agent
- **Papel:** transcrever e resumir VSLs.
- **Ferramentas:** Whisper (transcrição) + LLM (estruturação).
- **Saída:** transcrição + resumo com marcação (hook/problema/solução/oferta/CTA).

### 5. Cloner Agent
- **Papel:** reconstruir LP e mapear funil.
- **Ferramentas:** headless browser, extrator de DOM, detector de stack, LLM.
- **Saída:** bundle HTML + manifest de funil + copy extraída.
- **Sub-tarefas:** capturar assets, seguir CTAs, detectar upsells/checkout.

### 6. Analyst Agent
- **Papel:** detectar tendências e ofertas escalando.
- **Ferramentas:** consultas ClickHouse, séries temporais, LLM p/ narrativa.
- **Saída:** insights + alertas.

### 7. QA/Guard Agent
- **Papel:** validar qualidade dos dados e clones (deduplicação, fidelidade).
- **Ferramentas:** diff visual, checks de schema, detecção de anomalias.
- **Saída:** score de qualidade + flags para revisão humana.

## Especificação de um agent (template)

```yaml
agent: cloner
description: Reconstrói landing pages e mapeia funis.
model: claude-sonnet
memory: workspace-scoped
tools:
  - headless_fetch
  - asset_downloader
  - dom_extractor
  - stack_detector
  - llm_copy_extractor
inputs:
  - offer_id
  - landing_url
outputs:
  - clone_bundle_url
  - funnel_manifest
guardrails:
  - max_pages: 20
  - respect_robots: true
  - timeout_s: 120
retries:
  strategy: exponential_backoff
  max: 3
```

## Padrões de agentes

- **ReAct**: raciocínio + ação intercalados.
- **Plan-and-Execute**: Orchestrator planeja, workers executam.
- **Reflection**: QA Agent revisa saída antes de persistir.
- **Human-in-the-loop**: casos de baixa confiança vão para fila de revisão.

## Memória

- **Curto prazo:** contexto do job atual (Redis).
- **Longo prazo:** vetores de ofertas conhecidas (pgvector) para deduplicação e "ofertas similares".

## Observabilidade de agents

- Trace por job (OpenTelemetry).
- Custo por agent/token logado.
- Taxa de sucesso, latência, taxa de escalonamento p/ humano.

## Ver também
- [ai-agents.md](../07-ai/ai-agents.md) — detalhes de implementação.
- [scraping-engine.md](../04-backend/scraping-engine.md) — engine que os agents usam.
