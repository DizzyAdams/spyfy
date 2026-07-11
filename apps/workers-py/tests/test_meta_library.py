"""
Testes do spyfy.meta_library — integração REAL com o Meta Ad Library.

Cobrem o parser HTML (JSON embarcado + fallback regex), o mapeamento da
Ad Library API e o contrato de dados (formato Offer). Tudo sem rede: o
transporte HTTP é mockado com httpx.MockTransport.
"""
from __future__ import annotations

import httpx
import pytest

from spyfy.meta_library import MetaAdLibrary, MetaScrapeError

# --- fixtures ----------------------------------------------------------------
# HTML da Ad Library com o JSON de anúncios embarcado em <script>.
FIXTURE_HTML = """
<html><body>
<script type="application/json">{"ads":[
  {"adArchiveId":"123456789","pageName":"HealthBR",
   "body":"Emagreça 7kg em 21 dias. Sem dietas malucas. Resultado na primeira semana.",
   "startDate":"2024-01-15",
   "impressions":{"lower_bound":"10000","upper_bound":"50000"},
   "snapshotUrl":"https://www.facebook.com/ads/library/?id=123456789",
   "mediaType":"VIDEO"},
  {"adArchiveId":"987654321","pageName":"GlowLab",
   "body":"Pele de vidro em 14 dias sem laser.",
   "startDate":"2024-03-01",
   "impressions":{"lower_bound":"5000","upper_bound":"20000"},
   "snapshotUrl":"https://www.facebook.com/ads/library/?id=987654321",
   "mediaType":"IMAGE"}
]}</script>
</body></html>
"""

# HTML sem JSON parseável, mas com adArchiveId + campos vizinhos (fallback regex).
FIXTURE_REGEX_HTML = """
<div class="ad">
  "adArchiveId":"555111222"
  some text "pageName":"FitCorp"
  more "body":"Treine em casa e ganhe massa muscular."
  end "snapshotUrl":"https://www.facebook.com/ads/library/?id=555111222"
</div>
"""

API_JSON = {
    "data": [
        {
            "ad_archive_id": "111222333",
            "page_name": "AdvPro",
            "ad_creative_bodies": ["Compre agora e transforme sua rotina."],
            "ad_creative_link_titles": ["Oferta imperdível"],
            "ad_delivery_start_time": "2024-02-01T00:00:00Z",
            "ad_delivery_country": "BR",
            "impressions": {"lower_bound": "100000", "upper_bound": "500000"},
            "snapshot_url": "https://www.facebook.com/ads/library/?id=111222333",
        }
    ],
    "paging": {},
}


def _client(text: str | None = None, json_body: dict | None = None):
    def handler(req):
        if json_body is not None:
            return httpx.Response(200, json=json_body)
        return httpx.Response(200, text=text or "")

    return httpx.Client(transport=httpx.MockTransport(handler))


# --- parser HTML (JSON embarcado) ------------------------------------------
def test_parse_html_json_blob():
    lib = MetaAdLibrary()
    offers = lib.parse_html(FIXTURE_HTML, limit=10)
    assert len(offers) == 2

    ids = {o["id"] for o in offers}
    assert "meta_123456789" in ids
    assert "meta_987654321" in ids

    o1 = next(o for o in offers if o["id"] == "meta_123456789")
    assert o1["advertiser"] == "HealthBR"
    assert o1["network"] == "meta"
    assert o1["format"] == "video"
    assert o1["estImpressions"] == 30000  # (10000+50000)/2
    assert o1["snapshotUrl"].endswith("123456789")
    assert o1["cta"] == "Ver anúncio"
    assert o1["longevityDays"] >= 1
    assert 40.0 <= o1["winningScore"] <= 99.0
    assert o1["bullets"]  # derivado do body


def test_parse_html_regex_fallback():
    lib = MetaAdLibrary()
    offers = lib.parse_html(FIXTURE_REGEX_HTML, limit=5)
    assert len(offers) == 1
    o = offers[0]
    assert o["id"] == "meta_555111222"
    assert o["advertiser"] == "FitCorp"
    assert "Treine em casa" in o["headline"]


# --- web-scrape end-to-end (HTTP mockado) ---------------------------------
def test_search_web_path():
    lib = MetaAdLibrary(client=_client(text=FIXTURE_HTML), country="BR")
    offers = lib.search("emagrecimento", limit=10)
    assert len(offers) == 2
    assert all(o["network"] == "meta" for o in offers)


def test_search_web_empty_raises():
    lib = MetaAdLibrary(client=_client(text="<html><body>login required</body></html>"))
    with pytest.raises(MetaScrapeError):
        lib.search("x")


# --- API path (HTTP mockado) ----------------------------------------------
def test_search_api_path():
    lib = MetaAdLibrary(access_token="SECRET", client=_client(json_body=API_JSON))
    offers = lib.search("keto", limit=5)
    assert len(offers) == 1
    o = offers[0]
    assert o["id"] == "meta_111222333"
    assert o["advertiser"] == "AdvPro"
    assert o["estImpressions"] == 300000  # (100000+500000)/2
    assert o["headline"] == "Oferta imperdível"
    assert o["network"] == "meta"


def test_api_to_offer_mapping():
    lib = MetaAdLibrary()
    o = lib._api_to_offer(API_JSON["data"][0])
    assert o is not None
    assert o["country"] == "BR"
    assert o["format"] in ("video", "image", "carousel")
    assert "funnel" in o and isinstance(o["funnel"], list)
    assert o["source"] == "meta_ad_library"
