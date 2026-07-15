"""
Testes do spyfy.google_library — integração REAL com o Google Ads Transparency.

Cobrem o parser HTML (JSON embarcado + fallback regex) e o contrato de dados
(formato Offer). Tudo sem rede: o transporte HTTP é mockado com httpx.MockTransport.
"""
from __future__ import annotations

import httpx
import pytest

from spyfy.google_library import GoogleAdsTransparency, GoogleTransparencyError

# --- fixtures ----------------------------------------------------------------
FIXTURE_HTML = """
<html><body>
<script type="application/json">{"ads":[
  {"creativeId":"G123456789","advertiserName":"GoogleFit",
   "adText":"Comece a treinar hoje mesmo. Resultados rápidos.",
   "startDate":"2024-02-10",
   "impressions":{"lower_bound":"20000","upper_bound":"80000"},
   "landingPage":"https://exemplo.com/lp",
   "format":"IMAGE"},
  {"creativeId":"G987654321","advertiserName":"GlowGoogle",
   "adText":"Pele perfeita sem manchas.",
   "startDate":"2024-03-05",
   "impressions":{"lower_bound":"5000","upper_bound":"15000"},
   "landingPage":"https://exemplo.com/g",
   "format":"VIDEO"}
]}</script>
</body></html>
"""

FIXTURE_REGEX_HTML = """
<div class="ad">
  "creativeId":"G555111222"
  some text "advertiserName":"BeautyGoogle"
  more "adText":"Cílios volumosos em poucos dias."
  end "landingPage":"https://exemplo.com/b"
</div>
"""


def _client(text: str | None = None, json_body: dict | None = None):
    def handler(req):
        if json_body is not None:
            return httpx.Response(200, json=json_body)
        return httpx.Response(200, text=text or "")

    return httpx.Client(transport=httpx.MockTransport(handler))


# --- parser HTML (JSON embarcado) --------------------------------------------
def test_parse_html_json_blob():
    lib = GoogleAdsTransparency()
    offers = lib.parse_html(FIXTURE_HTML, limit=10)
    assert len(offers) == 2

    ids = {o["id"] for o in offers}
    assert "google_G123456789" in ids
    assert "google_G987654321" in ids

    o1 = next(o for o in offers if o["id"] == "google_G123456789")
    assert o1["advertiser"] == "GoogleFit"
    assert o1["network"] == "google"
    assert o1["format"] == "image"
    assert o1["estImpressions"] == 50000  # (20000+80000)/2
    assert o1["snapshotUrl"].endswith("lp")
    assert o1["cta"] == "Ver anúncio"
    assert o1["longevityDays"] >= 1
    assert 40.0 <= o1["winningScore"] <= 99.0
    assert o1["bullets"]
    assert o1["source"] == "google_ads_transparency"


def test_parse_html_regex_fallback():
    lib = GoogleAdsTransparency()
    offers = lib.parse_html(FIXTURE_REGEX_HTML, limit=5)
    assert len(offers) == 1
    o = offers[0]
    assert o["id"] == "google_G555111222"
    assert o["advertiser"] == "BeautyGoogle"
    assert "Cílios volumosos" in o["headline"]


# --- web-scrape end-to-end (HTTP mockado) ------------------------------------
def test_search_web_path():
    lib = GoogleAdsTransparency(client=_client(text=FIXTURE_HTML), country="BR")
    offers = lib.search("emagrecimento", limit=10)
    assert len(offers) == 2
    assert all(o["network"] == "google" for o in offers)


def test_search_web_empty_raises():
    lib = GoogleAdsTransparency(client=_client(text="<html><body>login required</body></html>"))
    with pytest.raises(GoogleTransparencyError):
        lib.search("x")


# --- Scrapling adapter (transporte REAL substituto do httpx) -----------------
def test_scrapling_adapter_importable():
    # Garante que o adapter existe e expõe a interface mínima esperada.
    from spyfy.scrapling_adapter import (
        SCRAPLING_AVAILABLE,
        ScraplingClient,
        fetch_html,
    )
    assert callable(ScraplingClient)
    assert callable(fetch_html)
    # SCRAPLING_AVAILABLE reflete o ambiente (True se todas as deps instaladas).
    assert isinstance(SCRAPLING_AVAILABLE, bool)


def test_scrapling_client_drops_into_search():
    """ScraplingClient é drop-in do httpx.Client: search() consome .status_code/.text."""
    from spyfy.scrapling_adapter import ScraplingClient

    class _StubScrapling(ScraplingClient):
        def get(self, url, *, params=None, headers=None, timeout=None):
            from spyfy.scrapling_adapter import _ScraplingResponse

            return _ScraplingResponse(200, FIXTURE_HTML, url)

    lib = GoogleAdsTransparency(client=_StubScrapling(), country="BR")
    offers = lib.search("emagrecimento", limit=10)
    assert len(offers) == 2
    assert all(o["network"] == "google" for o in offers)

