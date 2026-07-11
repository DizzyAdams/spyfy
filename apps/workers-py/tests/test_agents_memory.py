"""Testes da memória RAG (chromadb) dos agentes autônomos."""
from spyfy.agents.memory import HashEmbedding, OfferMemory, _doc_text


def _offer(headline, niche="keto", network="meta", advertiser="X", bullets=None):
    return {
        "id": f"{niche}_{headline}",
        "headline": headline,
        "niche": niche,
        "network": network,
        "advertiser": advertiser,
        "country": "BR",
        "bullets": bullets or ["Beneficio 1", "Beneficio 2"],
        "cta": "Ver oferta",
        "winningScore": 80.0,
    }


def test_embedding_deterministic():
    ef = HashEmbedding()
    v1 = ef(["emagreca 7kg em 21 dias"])[0]
    v2 = ef(["emagreca 7kg em 21 dias"])[0]
    assert v1 == v2
    # texto diferente -> vetor diferente (quase sempre)
    v3 = ef(["fatura r$10k com trafego pago"])[0]
    assert v1 != v3


def test_add_and_query_returns_inserted():
    mem = OfferMemory()
    o = _offer("Emagreça 7kg em 21 dias")
    assert mem.add_offers([o]) == 1
    hits = mem.query("Emagreça 7kg em 21 dias", n=3)
    assert hits, "deve retornar ao menos 1 oferta similar"
    assert hits[0]["offer_id"] == o["id"]
    assert hits[0]["similarity"] is not None


def test_query_empty_collection_is_safe():
    mem = OfferMemory()
    assert mem.query("qualquer coisa") == []
    assert mem.count() == 0


def test_find_similar_detects_near_duplicate():
    mem = OfferMemory()
    base = _offer("Emagreça 7kg em 21 dias sem dietas")
    mem.add_offers([base])
    dup = _offer("Emagreça 7kg em 21 dias sem dietas")
    dup["id"] = "dup_1"
    sim = mem.find_similar(dup, n=3, threshold=0.7)
    assert any(s["offer_id"] == base["id"] for s in sim)


def test_find_similar_ignores_different_niche():
    mem = OfferMemory()
    base = _offer("Emagreça 7kg em 21 dias", niche="keto")
    mem.add_offers([base])
    other = _offer("Fatura R$10k com tráfego pago", niche="finance")
    other["id"] = "fin_1"
    sim = mem.find_similar(other, n=3, threshold=0.85)
    assert not any(s["offer_id"] == base["id"] for s in sim)


def test_idempotent_upsert():
    mem = OfferMemory()
    o = _offer("Oferta única")
    assert mem.add_offers([o]) == 1
    assert mem.add_offers([o]) == 1  # mesmo id -> upsert, não duplica
    assert mem.count() == 1


def test_doc_text_includes_key_fields():
    text = _doc_text(_offer("Headline X", advertiser="AnuncianteY"))
    assert "Headline X" in text
    assert "AnuncianteY" in text
