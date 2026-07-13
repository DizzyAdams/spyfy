"""
Testes do spyfy.native_library — integração REAL com a Native Ad Library.

Cobrem o parser HTML (JSON embarcado + fallback regex) e o contrato de dados
(formato Offer). Tudo sem rede: o transporte HTTP é mockado com
httpx.MockTransport, espelhando os testes das demais bibliotecas.
"""
from __future__ import annotations

import httpx
import pytest

from spyfy.native_library import NativeAdsLibrary, NativeAdsError

# --- fixtures ----------------------------------------------------------------
# HTML do showcase de native ads com o JSON de anúncios embarcado em <script>.
FIXTURE_HTML = """
<html><body>
<script type="application/json">{"ads":[
  {"adId":"N123456789","advertiserName":"TabNative",
   "adText":"Emagreça sem dieta com este chá detox. Resultado em 21 dias.",
   "startDate":"2024-02-10",
   "impressions":{"lower_bound":"20000","upper_bound":"80000"},
   "landingPageUrl":"https://exemplo.com/lp",
   "mediaType":"IMAGE"},
  {"adId":"N987654321","advertiserName":"OutbrainBR",
   "adText":"Pele de vidro sem laser.",
   "startDate":"2024-03-05",
   "impressions":{"lower_bound":"5000","upper_bound":"15000"},
   "landingPageUrl":"https://exemplo.com/g",
   "mediaType":"VIDEO"}
]}</script>
</body></html>
"""

# HTML sem JSON parseável, mas com adId + campos vizinhos (fallback regex).
FIXTURE_REGEX_HTML = """
<div class="ad">
  "adId":"N555111222"
  some text "advertiserName":"MgidNative"
  more "adText":"Cílios 2x mais longos em 3 semanas."
  end "landingPageUrl":"https://exemplo.com/b"
</div>
"""

API_JSON = {
    "ads": [
        {
            "ad_id": "A111222333",
            "advertiser_name": "AdvNative",
            "ad_text": ["Compre agora e transforme sua rotina."],
            "ad_title": "Oferta top native",
            "start_date": "2024-01-20T00:00:00Z",
            "impressions": {"lower_bound": "100000", "upper_bound": "400000"},
            "region": "BR",
            "media_type": "VIDEO",
            "url": "https://exemplo.com/a1",
        }
    ]
}


def _client(text: str | None = None, json_body: dict | None = None):
    def handler(req):
        if json_body is not None:
            return httpx.Response(200, json=json_body)
        return httpx.Response(200, text=text or "")

    return httpx.Client(transport=httpx.MockTransport(handler))


# --- parser HTML (JSON embarcado) --------------------------------------------
def test_parse_html_json_blob():
    lib = NativeAdsLibrary()
    offers = lib.parse_html(FIXTURE_HTML, limit=10)
    assert len(offers) == 2

    ids = {o["id"] for o in offers}
    assert "native_N123456789" in ids
    assert "native_N987654321" in ids

    o1 = next(o for o in offers if o["id"] == "native_N123456789")
    assert o1["advertiser"] == "TabNative"
    assert o1["network"] == "native"
    assert o1["format"] == "image"
    assert o1["estImpressions"] == 50000  # (20000+80000)/2
    assert o1["snapshotUrl"].endswith("lp")
    assert o1["cta"] == "Ver anúncio"
    assert o1["longevityDays"] >= 1
    assert 40.0 <= o1["winningScore"] <= 99.0
    assert o1["bullets"]
    assert o1["source"] == "native_ad_library"


def test_parse_html_regex_fallback():
    lib = NativeAdsLibrary()
    offers = lib.parse_html(FIXTURE_REGEX_HTML, limit=5)
    assert len(offers) == 1
    o = offers[0]
    assert o["id"] == "native_N555111222"
    assert o["advertiser"] == "MgidNative"
    assert "Cílios 2x" in o["headline"]


# --- web-scrape end-to-end (HTTP mockado) ------------------------------------
def test_search_web_path():
    lib = NativeAdsLibrary(client=_client(text=FIXTURE_HTML), country="BR")
    offers = lib.search("emagrecimento", limit=10)
    assert len(offers) == 2
    assert all(o["network"] == "native" for o in offers)


def test_search_web_empty_raises():
    lib = NativeAdsLibrary(
        client=_client(text="<html><body>login required</body></html>")
    )
    with pytest.raises(NativeAdsError):
        lib.search("x")


# --- API path (HTTP mockado) ------------------------------------------------
def test_search_api_path():
    lib = NativeAdsLibrary(
        api_token="SECRET", api_url="https://api.native.example/ads",
        client=_client(json_body=API_JSON),
    )
    offers = lib.search("fitness", limit=5)
    assert len(offers) == 1
    o = offers[0]
    assert o["id"] == "native_A111222333"
    assert o["advertiser"] == "AdvNative"
    assert o["estImpressions"] == 250000  # (100000+400000)/2
    assert o["headline"] == "Oferta top native"
    assert o["network"] == "native"


def test_search_api_without_url_raises():
    lib = NativeAdsLibrary(api_token="SECRET")
    with pytest.raises(NativeAdsError):
        lib.search("x")


def test_api_to_offer_mapping():
    lib = NativeAdsLibrary()
    o = lib._api_node_to_offer(API_JSON["ads"][0])
    assert o is not None
    assert o["country"] == "BR"
    assert o["format"] in ("video", "image", "carousel")
    assert "funnel" in o and isinstance(o["funnel"], list)
    assert o["source"] == "native_ad_library"
