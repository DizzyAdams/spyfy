"""
SpyFy — OfferState (schema de estado do grafo LangGraph)
=========================================================
Estado compartilhado e durável do "digital workforce" de agentes autônomos
(docs/14-mining/team-14-agents.md). Cada agente lê o estado, executa sua
função e devolve apenas os deltas; os redutores (``add``/``add_messages``)
mesclam com o estado anterior — exatamente como prevê a arquitetura
LangGraph (docs/07-ai/langgraph-architecture.md).
"""
from __future__ import annotations

from operator import add
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class OfferState(TypedDict, total=False):
    """Estado global do pipeline autônomo de mineração -> enriquecimento.

    Campos com ``Annotated[..., add]`` são **acumulativos** (cada agente
    anexa, sem sobrescrever o que veio antes).
    """

    # ---- Objetivo (entrada do A0 Orchestrator) ----
    objective: str
    niche: str | None
    network: str | None
    country: str | None
    min_score: float

    # ---- Roteamento ----
    next: str | None
    done_steps: Annotated[list[str], add]
    needs_human: bool
    confidence: float

    # ---- Saídas acumuladas ----
    offer_id: str | None
    landing_url: str | None
    discovered_ads: Annotated[list[dict], add]
    assets: Annotated[list[dict], add]
    funnel_steps: Annotated[list[dict], add]
    events: Annotated[list[dict], add]
    alerts: Annotated[list[dict], add]
    messages: Annotated[list, add_messages]

    # ---- Resultados por agente ----
    enrichment: dict | None
    copy: dict | None
    transcript: dict | None
    stack: dict | None
    analytics: dict | None
    similar_offers: Annotated[list[dict], add]
    clone_bundle_url: str | None
