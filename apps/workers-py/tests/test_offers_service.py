"""Testes dos endpoints /v1/offers e /v1/metrics (descoberta + métricas)."""
import pytest
from fastapi.testclient import TestClient

from spyfy.api import create_app
from spyfy.notifiers import NotificationDispatcher


class _FakeNotifier:
    name = "fake"

    def send(self, channel, recipient, notif):
        return True


@pytest.fixture
def client():
    fake = _FakeNotifier()
    dispatcher = NotificationDispatcher(
        {"novu": fake, "apprise": fake, "ntfy": fake, "native": fake}
    )
    return TestClient(create_app(dispatcher=dispatcher))


def test_list_offers_returns_ranked(client):
    r = client.get("/v1/offers?limit=10&simulate=true")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    offers = data["offers"]
    # ordenado por winningScore desc
    scores = [o["winningScore"] for o in offers]
    assert scores == sorted(scores, reverse=True)
    # cada oferta enriquecida com ROI/escala/win-prob
    first = offers[0]
    assert "scalingSignal" in first
    assert "estRoiPct" in first
    assert "winProb" in first
    assert "estDailyProfit" in first
    # campos obrigatórios do modelo Offer do front presentes
    for k in ("id", "headline", "advertiser", "network", "niche",
              "longevityDays", "thumbnailHue", "gradient", "funnel"):
        assert k in first


def test_list_offers_filter_network(client):
    r = client.get("/v1/offers?network=meta&limit=8&simulate=true")
    assert r.status_code == 200
    offers = r.json()["offers"]
    assert all(o["network"] == "meta" for o in offers)


def test_metrics_aggregates(client):
    r = client.get("/v1/metrics?simulate=true")
    assert r.status_code == 200
    m = r.json()
    assert m["total"] > 0
    assert "byNetwork" in m and "byNiche" in m and "bySignal" in m
    assert "avgWinningScore" in m and "avgRoiPct" in m
    assert "topScaled" in m and len(m["topScaled"]) > 0
    # soma das redes == total
    assert sum(m["byNetwork"].values()) == m["total"]
    # top escalando ordenado por winningScore desc
    top = m["topScaled"]
    assert top == sorted(top, key=lambda x: x["winningScore"], reverse=True)


def test_get_offer_by_id(client):
    # pega um id determinístico do list e busca o detalhe
    r = client.get("/v1/offers?limit=8&network=meta&simulate=true")
    offers = r.json()["offers"]
    assert offers[0]["id"].startswith("ofr_meta_")
    oid = offers[0]["id"]
    d = client.get(f"/v1/offers/{oid}")
    assert d.status_code == 200
    assert d.json()["id"] == oid
    assert "winningScore" in d.json()


def test_get_offer_404(client):
    d = client.get("/v1/offers/ofr_nope_x_0")
    assert d.status_code == 404

