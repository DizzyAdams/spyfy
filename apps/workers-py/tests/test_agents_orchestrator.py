"""Testes do orquestrador autônomo LangGraph (offline, sem chamar LLM)."""
from spyfy.agents import (MEMBERS, OfferMemory, build_offer_graph,
                          run_offer_pipeline_sync)
from spyfy.events import EventBus


def test_graph_builds_and_compiles():
    graph, _ = build_offer_graph(simulate=True, count=1)
    assert graph is not None
    # grafo compilado expõe invoke/ainvoke
    assert hasattr(graph, "invoke") and hasattr(graph, "ainvoke")


def test_pipeline_runs_end_to_end_offline():
    final = run_offer_pipeline_sync(
        "Encontrar ofertas vencedoras de keto",
        niche="keto", network="meta", country="BR",
        simulate=True, count=3,
    )
    # Scout descobriu ofertas
    assert len(final.get("discovered_ads", [])) == 3
    # Todos os agentes rodaram
    done = set(final.get("done_steps", []))
    assert done == set(MEMBERS), f"faltaram passos: {set(MEMBERS) - done}"
    # Eventos de domínio emitidos
    types = {e["type"] for e in final.get("events", [])}
    assert "offer.discovered" in types
    assert "offer.enriched" in types
    assert "roi.computed" in types
    assert "offer.indexed" in types
    assert "guard.qa" in types
    assert "alert.triggered" in types
    # Guard setou confiança e flag de human-in-the-loop
    assert 0.0 <= final["confidence"] <= 1.0
    assert isinstance(final["needs_human"], bool)
    # Analytics com melhor oferta
    assert final["analytics"]["best"] is not None
    assert "win_prob" in final["analytics"]["best"]


def test_pipeline_persists_to_rag_memory():
    mem = OfferMemory()
    run_offer_pipeline_sync(
        "keto", niche="keto", network="meta", simulate=True, count=2, memory=mem,
    )
    assert mem.count() == 2
    # recuperação semântica funciona
    hits = mem.query("Emagreça 7kg", n=2)
    assert hits


def test_pipeline_publishes_alert_to_eventbus():
    bus = EventBus()
    seen: list[str] = []
    bus.use(lambda e: seen.append(e.type))
    run_offer_pipeline_sync(
        "finance", niche="finance", network="tiktok", simulate=True,
        count=2, bus=bus,
    )
    assert "alert.triggered" in seen


def test_coverage_of_event_types_is_valid():
    # garante que os tipos de evento emitidos pelo pipeline existem no catálogo
    from spyfy.events import EVENT_TYPES
    final = run_offer_pipeline_sync(
        "beauty", niche="beauty", network="meta", simulate=True, count=1,
    )
    for e in final.get("events", []):
        assert e["type"] in EVENT_TYPES, f"tipo não catalogado: {e['type']}"
