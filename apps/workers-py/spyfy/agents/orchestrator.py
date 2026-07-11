"""
SpyFy — Orchestrator autônomo (LangGraph "digital workforce")
==============================================================
Implementa o grafo de estado do time de 14 agents (docs/14-mining/
team-14-agents.md) para o pipeline **descobrir -> enriquecer -> extrair
copy -> analisar ROI -> dedup(RAG) -> QA -> alertar**.

Topologia (Supervisor + sub-agents), conforme docs/07-ai/langgraph-
architecture.md:
    START -> supervisor --(route)--> scout -> enricher -> copy -> roi
             -> dedup -> guard -> alert -> supervisor ... até FINISH

Projeto para rodar **100% offline e determinístico** (sem chamar LLM) usando
os engines reais do pacote (`scraper_bridge.mine`, `roi.estimate_offer`,
`radar.win_probability`) como "tools". Quando um `llm` (langchain
BaseChatModel) é injetado, os nós de enriquecimento/copy o utilizam; caso
contrário caem em heurísticas. Isso garante degradação graciosa e testes
sem rede/API key.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..events import DomainEvent
from ..radar import RadarOffer, early_mover_bonus, win_probability
from ..roi import AdSignals, NicheEconomics, estimate_offer
from ..scraper_bridge import mine
from .memory import OfferMemory
from .state import OfferState

MEMBERS = ["scout", "enricher", "copy", "roi", "dedup", "guard", "alert"]
REQUIRED_STEPS = {"scout", "enricher", "copy", "roi", "dedup"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_radar(o: dict[str, Any]) -> RadarOffer:
    return RadarOffer(
        offer_id=o.get("id") or o.get("offer_id") or "x",
        niche=o.get("niche") or "Geral",
        network=o.get("network") or "meta",
        country=o.get("country") or "BR",
        winning_score=float(o.get("winningScore") or 0.0),
        longevity_days=int(o.get("longevityDays") or 0),
        creative_variants=len(o.get("funnel", []) or []) or 1,
        scaling_signal=o.get("scaling_signal") or "warming",
        first_seen_rank=0.5,
    )


def _estimate(o: dict[str, Any]) -> Any:
    long_days = int(o.get("longevityDays") or 0)
    last = datetime.now(timezone.utc)
    first = last - timedelta(days=long_days)
    sig = AdSignals(
        first_seen=first,
        last_seen=last,
        creative_variants=len(o.get("funnel", []) or []) or 1,
        est_impressions_low=int((o.get("estImpressions") or 0) * 0.8),
        est_impressions_high=int((o.get("estImpressions") or 0) * 1.2),
        networks=1,
        countries=1,
    )
    return estimate_offer(sig, NicheEconomics())


def _classify(o: dict[str, Any], llm: Any = None) -> dict[str, Any]:
    text = f"{o.get('headline', '')} {' '.join(o.get('bullets', []) or [])}".lower()
    niche = o.get("niche") or "Geral"
    angle = "beneficio"
    if any(w in text for w in ["emagrec", "gordura", "peso", "keto",
                                "vidro", "cilios", "pele"]):
        angle = "transformacao"
    elif any(w in text for w in ["renda", "divida", "invest", "fatura r$",
                                 "trafego pago"]):
        angle = "liberdade_financeira"
    lang = "pt-BR" if any(w in text for w in ["voc", "para", "com", "sem",
                                              "que"]) else "en"
    conf = 0.7
    if llm is not None:  # hook opcional de LLM (best-effort)
        try:
            out = llm.invoke(f"Classifique nicho/angulo: {o.get('headline')}")
            if isinstance(out, dict) and "confidence" in out:
                conf = float(out["confidence"])
        except Exception:  # noqa: BLE001 - mantém heurística
            pass
    return {"offer_id": o.get("id"), "niche": niche, "angle": angle,
            "language": lang, "confidence": conf}


def _extract_copy(o: dict[str, Any], llm: Any = None) -> dict[str, Any]:
    return {
        "offer_id": o.get("id"),
        "headline": o.get("headline"),
        "cta": o.get("cta"),
        "bullets": o.get("bullets", []) or [],
        "format": o.get("format"),
        "by": "llm" if llm else "heuristic",
    }
# --------------------------------------------------------------------------
# Node builders (closures capturam dependências injetáveis: llm/memory/bus)
# --------------------------------------------------------------------------

def _make_scout(simulate: bool, count: int, token: str):
    def scout(state: OfferState) -> dict[str, Any]:
        niche = state.get("niche") or "keto"
        network = state.get("network") or "meta"
        country = state.get("country") or "BR"
        offers = mine(niche, network, count=count, simulate=simulate,
                      token=token, country=country)
        for i, o in enumerate(offers):
            o.setdefault("id", o.get("offer_id")
                         or f"scrape_{niche}_{network}_{i}")
        events = [{"type": "offer.discovered",
                   "data": {"count": len(offers), "niche": niche,
                            "network": network}, "at": _now()}]
        return {"discovered_ads": offers, "done_steps": ["scout"],
                "events": events, "confidence": 0.5}
    return scout


def _make_enricher(llm: Any = None):
    def enricher(state: OfferState) -> dict[str, Any]:
        ads = state.get("discovered_ads", []) or []
        enriched = [_classify(o, llm) for o in ads]
        conf = (sum(e["confidence"] for e in enriched) / len(enriched)
                if enriched else 0.5)
        enrichment = {"offers": enriched, "by": "llm" if llm else "heuristic",
                      "count": len(enriched)}
        events = [{"type": "offer.enriched",
                   "data": {"count": len(enriched)}, "at": _now()}]
        return {"enrichment": enrichment, "done_steps": ["enricher"],
                "events": events, "confidence": round(conf, 3),
                "messages": [{"role": "system",
                              "content": f"Enriquecidos {len(enriched)} anúncios."}]}
    return enricher


def _make_copy(llm: Any = None):
    def copy(state: OfferState) -> dict[str, Any]:
        ads = state.get("discovered_ads", []) or []
        extracted = [_extract_copy(o, llm) for o in ads]
        events = [{"type": "copy.extracted",
                   "data": {"count": len(extracted)}, "at": _now()}]
        return {"copy": {"offers": extracted, "by": "llm" if llm else "heuristic"},
                "done_steps": ["copy"], "events": events}
    return copy


def _make_roi():
    def roi(state: OfferState) -> dict[str, Any]:
        ads = state.get("discovered_ads", []) or []
        rows: list[dict[str, Any]] = []
        for o in ads:
            est = _estimate(o)
            r = _to_radar(o)
            rows.append({
                "offer_id": o.get("id"),
                "winning_score": est.winning_score,
                "scaling_signal": est.scaling_signal,
                "est_roi_pct": est.est_roi_pct,
                "est_roas": est.est_roas,
                "win_prob": win_probability(r),
                "edge": early_mover_bonus(r),
            })
        best = max(rows, key=lambda r: r["winning_score"]) if rows else None
        events = [{"type": "roi.computed",
                   "data": {"count": len(rows)}, "at": _now()}]
        return {"analytics": {"offers": rows, "best": best},
                "done_steps": ["roi"], "events": events}
    return roi

def _make_dedup(memory: OfferMemory | None):
    def dedup(state: OfferState) -> dict[str, Any]:
        ads = state.get("discovered_ads", []) or []
        similar_all: list[dict[str, Any]] = []
        added = 0
        if memory is not None:
            added = memory.add_offers(ads)
            for o in ads:
                sim = memory.find_similar(o)
                if sim:
                    similar_all.append({"offer_id": o.get("id"),
                                        "similar": sim})
        events = [{"type": "offer.indexed",
                   "data": {"added": added}, "at": _now()}]
        return {"similar_offers": similar_all, "done_steps": ["dedup"],
                "events": events,
                "assets": [{"kind": "rag_index", "count": len(ads)}]}
    return dedup


def _make_guard():
    def guard(state: OfferState) -> dict[str, Any]:
        steps = set(state.get("done_steps", []) or [])
        completeness = len(REQUIRED_STEPS & steps) / len(REQUIRED_STEPS)
        prior = state.get("confidence", 0.5) or 0.5
        confidence = round(0.6 * completeness + 0.4 * prior, 3)
        needs_human = confidence < 0.6
        flags = ["pipeline_incompleto"] if completeness < 1.0 else []
        events = [{"type": "guard.qa",
                   "data": {"confidence": confidence,
                            "needs_human": needs_human}, "at": _now()}]
        return {"confidence": confidence, "needs_human": needs_human,
                "done_steps": ["guard"], "events": events,
                "stack": {"qa_flags": flags}}
    return guard


def _make_alert(bus: Any = None, notify: Any = None):
    def alert(state: OfferState) -> dict[str, Any]:
        analytics = state.get("analytics") or {}
        best = analytics.get("best")
        alerts: list[dict[str, Any]] = []
        if best:
            alerts.append({"level": "hot", "offer_id": best.get("offer_id"),
                           "win_prob": best.get("win_prob"), "at": _now()})
            if bus is not None:
                ts = int(datetime.now(timezone.utc).timestamp())
                bus.publish(DomainEvent(
                    event_id=f"alert_{best.get('offer_id')}_{ts}",
                    type="alert.triggered",
                    data={"offer_id": best.get("offer_id"),
                          "win_prob": best.get("win_prob"),
                          "winning_score": best.get("winning_score")}))
        if notify is not None and best:
            notify(best)
        events = [{"type": "alert.triggered",
                   "data": {"count": len(alerts)}, "at": _now()}]
        return {"alerts": alerts, "done_steps": ["alert"], "events": events}
    return alert


def _supervisor(state: OfferState) -> dict[str, Any]:
    done = set(state.get("done_steps", []) or [])
    for m in MEMBERS:
        if m not in done:
            return {"next": m}
    return {"next": "FINISH"}


def _route(state: OfferState) -> str:
    return END if state.get("next") == "FINISH" else state.get("next") or END

def build_offer_graph(
    llm: Any = None,
    memory: OfferMemory | None = None,
    bus: Any = None,
    notify: Any = None,
    simulate: bool = True,
    count: int = 3,
    token: str = "",
):
    """Monta e compila o grafo autônomo de mineração -> enriquecimento.

    Retorna ``(graph, checkpointer)``. O ``checkpointer`` (MemorySaver) dá
    retomada durável por ``thread_id`` — exatamente o padrão de
    human-in-the-loop/resume da arquitetura LangGraph.
    """
    builder = StateGraph(OfferState)
    builder.add_node("supervisor", _supervisor)
    builder.add_node("scout", _make_scout(simulate, count, token))
    builder.add_node("enricher", _make_enricher(llm))
    builder.add_node("copy", _make_copy(llm))
    builder.add_node("roi", _make_roi())
    builder.add_node("dedup", _make_dedup(memory))
    builder.add_node("guard", _make_guard())
    builder.add_node("alert", _make_alert(bus, notify))

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", _route, [*MEMBERS, END])
    for m in MEMBERS:
        builder.add_edge(m, "supervisor")

    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph, checkpointer


async def run_offer_pipeline(
    objective: str,
    *,
    niche: str | None = None,
    network: str | None = None,
    country: str | None = None,
    min_score: float = 0.0,
    llm: Any = None,
    memory: OfferMemory | None = None,
    bus: Any = None,
    notify: Any = None,
    simulate: bool = True,
    count: int = 3,
    token: str = "",
    thread_id: str | None = None,
    recursion_limit: int = 32,
) -> dict[str, Any]:
    """Executa o pipeline autônomo de ponta a ponta (async).

    Útil para streaming pela UI (``graph.astream``) ou execução direta.
    Retorna o estado final do grafo (``OfferState`` mesclado).
    """
    graph, _ = build_offer_graph(
        llm=llm, memory=memory, bus=bus, notify=notify,
        simulate=simulate, count=count, token=token,
    )
    tid = thread_id or f"offer-{abs(hash(objective))}"
    config = {"configurable": {"thread_id": tid}, "recursion_limit": recursion_limit}
    init: OfferState = {
        "objective": objective,
        "niche": niche,
        "network": network,
        "country": country,
        "min_score": min_score,
    }
    final = await graph.ainvoke(init, config)
    return dict(final)


def run_offer_pipeline_sync(
    objective: str,
    *,
    niche: str | None = None,
    network: str | None = None,
    country: str | None = None,
    min_score: float = 0.0,
    llm: Any = None,
    memory: OfferMemory | None = None,
    bus: Any = None,
    notify: Any = None,
    simulate: bool = True,
    count: int = 3,
    token: str = "",
    thread_id: str | None = None,
    recursion_limit: int = 32,
) -> dict[str, Any]:
    """Versão síncrona de :func:`run_offer_pipeline` (CLI / testes)."""
    graph, _ = build_offer_graph(
        llm=llm, memory=memory, bus=bus, notify=notify,
        simulate=simulate, count=count, token=token,
    )
    tid = thread_id or f"offer-{abs(hash(objective))}"
    config = {"configurable": {"thread_id": tid}, "recursion_limit": recursion_limit}
    init: OfferState = {
        "objective": objective,
        "niche": niche,
        "network": network,
        "country": country,
        "min_score": min_score,
    }
    final = graph.invoke(init, config)
    return dict(final)

