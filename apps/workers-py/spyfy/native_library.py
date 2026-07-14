"""
SpyFy — Native Ad Library integration (REAL)
============================================
Busca de anúncios nativos (native ads: Taboola, Outbrain, MGID, Revcontent,
Yahoo Gemini, AdNow, etc.) via fontes públicas de transparência/showcase.

Ao contrário de Meta/TikTok/Google, não existe uma *Ad Library* oficial e
gratuita e estável para native. Esta classe segue o mesmo contrato das demais
bibliotecas (``spyfy.meta_library.MetaAdLibrary``) e oferece dois modos, em
ordem de preferência:

1. API de um provedor de native ads (ex.: Anstrex/AdPlexity-style) quando um
   ``api_token`` (e opcionalmente ``api_url``) é informado — estável e legal.
2. Web-scrape de um showcase público de native ads (``base_url`` configurável),
   usando httpx + html.parser (stdlib, zero novas deps).

Ambos retornam dicts no formato ``Offer`` consumido pelo Radar
(apps/web/server/realtime.js -> normalizeOffer). Contrato em lib/data.ts.

Espelha a interface das outras bibliotecas: quando o scrape não encontra
cards (página client-rendered / bloqueio / fonte indisponível), levanta
``NativeAdsError`` e o caller (``spyfy.scraper_bridge.mine``) faz fallback
para o gerador estruturado (simulador) — 100% offline-safe, nunca quebra.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from .realtime_producer import (
    GRADIENTS,
    cover_image,
    looks_like_image,
    looks_like_video,
)

# Showcase público de native ads usado como fonte de web-scrape por padrão.
# Pode ser sobrescrito por ``base_url`` (ex.: um portal interno de transparência).
NATIVE_AD_LIBRARY_WEB = "https://nativeads.com/"

_MEDIA_TO_FORMAT = {
    "VIDEO": "video",
    "IMAGE": "image",
    "CAROUSEL": "carousel",
    "SINGLE_IMAGE": "image",
    "SINGLE_VIDEO": "video",
    "NATIVE": "image",
    "DISPLAY": "image",
    "CONTENT": "image",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class NativeAdsError(RuntimeError):
    """Levantado quando nem a API nem o web-scrape retornam dados de native."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    s = str(value).strip()
    cands = [s[:19].replace("Z", "")] if "T" in s else [s[:10]]
    for c in cands:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(c, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = re.sub(r"[^\d]", "", str(value))
    return int(s) if s else 0


def _parse_impressions(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, dict):
        lo = _to_int(value.get("lower_bound") or value.get("min"))
        hi = _to_int(value.get("upper_bound") or value.get("max"))
        if lo and hi:
            return (lo + hi) // 2
        return lo or hi or 0
    return _to_int(value)


def _hue_from_id(uid: str) -> int:
    return (hash(uid) % 360 + 360) % 360


def _infer_format(node: dict[str, Any]) -> str:
    mt = str(
        node.get("mediaType")
        or node.get("media_type")
        or node.get("format")
        or node.get("adFormat")
        or ""
    ).upper()
    if mt in _MEDIA_TO_FORMAT:
        return _MEDIA_TO_FORMAT[mt]
    if any("video" in k.lower() for k in node):
        return "video"
    return "image"


def _compute_score(longevity_days: int, impressions: int, has_video: bool) -> float:
    s = 50.0
    s += min(longevity_days, 120) * 0.18
    s += min(impressions, 50_000_000) / 10_000_000 * 12.0
    if has_video:
        s += 6.0
    return round(min(99.0, max(40.0, s)), 1)


def _bullets_from_body(body: str, n: int = 3) -> list[str]:
    if not body:
        return ["Criativo coletado da Native Ad Library"]
    parts = re.split(r"(?<=[.!?])\s+", body.strip())
    out = [p.strip() for p in parts if p.strip()]
    return out[:n] if out else [body[:120]]


class NativeAdsLibrary:
    """Cliente de busca de anúncios nativos (API opcional + web-scrape)."""

    def __init__(
        self,
        *,
        api_token: str = "",
        api_url: str = "",
        base_url: str = NATIVE_AD_LIBRARY_WEB,
        country: str = "BR",
        timeout: float = 20.0,
        client: httpx.Client | None = None,
        proxies: str | None = None,
    ) -> None:
        self.api_token = api_token or ""
        self.api_url = api_url or ""
        self.base_url = base_url
        self.country = country
        self.timeout = timeout
        self._client = client
        self.proxies = proxies

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers=_HEADERS,
                timeout=self.timeout,
                follow_redirects=True,
                proxy=self.proxies or None,
            )
        return self._client

    def search(
        self,
        query: str,
        limit: int = 20,
        country: str | None = None,
    ) -> list[dict]:
        """Retorna até ``limit`` ofertas (formato Offer) para ``query``.

        Tenta a API (se ``api_token`` presente) e, na ausência, o web-scrape.
        Qualquer falha/ausência de dados levanta ``NativeAdsError`` para que
        o caller faça fallback ao simulador.
        """
        country = country or self.country
        if self.api_token:
            return self._search_api(query, limit, country)
        return self._search_web(query, limit, country)

    # ----- API path (provedor de native ads) ---------------------------------
    def _search_api(
        self, query: str, limit: int, country: str
    ) -> list[dict]:
        if not self.api_url:
            raise NativeAdsError(
                "NativeAdsLibrary: api_token informado sem api_url"
            )
        params = {"q": query, "limit": limit, "country": country.upper()}
        sep = "&" if "?" in self.api_url else "?"
        url = f"{self.api_url}{sep}{urlencode(params)}"
        resp = self.client.get(
            url,
            headers={"Authorization": f"Bearer {self.api_token}"},
        )
        if resp.status_code != 200:
            raise NativeAdsError(
                f"Native ads API {resp.status_code} para {query!r}"
            )
        try:
            data = resp.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise NativeAdsError(f"Native ads API JSON inválido: {exc}") from exc
        offers = self._api_offers(data, limit)
        if not offers:
            raise NativeAdsError(
                f"Native ads API sem anúncios para {query!r}"
            )
        return offers[:limit]

    def _api_offers(self, data: Any, limit: int) -> list[dict]:
        nodes: list[Any] = []
        if isinstance(data, dict):
            for key in ("ads", "data", "results", "items"):
                v = data.get(key)
                if isinstance(v, list):
                    nodes = v
                    break
            if not nodes and "list" in data and isinstance(data["list"], list):
                nodes = data["list"]
        elif isinstance(data, list):
            nodes = data
        offers: list[dict] = []
        for node in nodes:
            off = self._api_node_to_offer(node)
            if off:
                offers.append(off)
            if len(offers) >= limit:
                break
        return offers

    def _api_node_to_offer(self, d: dict[str, Any]) -> dict | None:
        if not isinstance(d, dict):
            return None
        aid = str(
            d.get("adId")
            or d.get("ad_id")
            or d.get("id")
            or d.get("creativeId")
            or ""
        )
        if not aid:
            return None
        page = (
            d.get("advertiserName")
            or d.get("advertiser_name")
            or d.get("brand")
            or d.get("sponsor")
            or "Anunciante"
        )
        body = d.get("adText") or d.get("ad_text") or d.get("body") or ""
        if isinstance(body, list):
            body = " ".join(x for x in body if isinstance(x, str))
        titles = (
            d.get("adTitle")
            or d.get("ad_title")
            or d.get("headline")
            or d.get("title")
            or ""
        )
        headline = (titles or (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(
            d.get("startDate") or d.get("start_date") or d.get("firstShown")
        )
        impr = _parse_impressions(d.get("impressions"))
        country = str(d.get("region") or d.get("country") or self.country or "BR")
        fmt = _infer_format(d)
        return self._finalize(
            uid=aid,
            headline=headline,
            advertiser=page,
            country=country,
            body=str(body),
            fmt=fmt,
            start=start,
            impr=impr,
            snapshot=d.get("landingPageUrl")
            or d.get("url")
            or d.get("adUrl")
            or "",
            image=d.get("landingPageUrl")
            or d.get("imageUrl")
            or d.get("image")
            or d.get("url")
            or "",
            video="",
        )



    # ----- Web-scrape path ----------------------------------------------------
    def _search_web(
        self, query: str, limit: int, country: str
    ) -> list[dict]:
        params = {"q": query, "country": country.upper(), "type": "native"}
        url = f"{self.base_url.rstrip('/')}/?{urlencode(params)}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise NativeAdsError(
                f"Native ads web {resp.status_code} para {query!r}"
            )
        offers = self.parse_html(resp.text, limit=limit)
        if not offers:
            raise NativeAdsError(
                f"Native ads web sem cards extraídos para {query!r} "
                f"(página client-rendered / bloqueio de região)"
            )
        return offers

    def parse_html(self, html_text: str, limit: int = 20) -> list[dict]:
        """Extrai ofertas do HTML do showcase de native ads (JSON + fallback)."""
        offers: list[dict] = []
        seen: set[str] = set()

        for blob in re.findall(
            r"<script[^>]*type=[\"']application/json[\"'][^>]*>(.*?)</script>",
            html_text,
            re.S | re.I,
        ):
            try:
                data = json.loads(blob)
            except (ValueError, json.JSONDecodeError):
                continue
            for node in self._iter_ad_nodes(data):
                off = self._web_node_to_offer(node)
                if off and off["id"] not in seen:
                    seen.add(off["id"])
                    offers.append(off)
                if len(offers) >= limit:
                    return offers[:limit]

        if not offers:
            for m in re.finditer(
                r'"(?:creativeId|adId)"\s*:\s*"([^"]+)"', html_text
            ):
                aid = m.group(1)
                if aid in seen:
                    continue
                seen.add(aid)
                node = self._regex_node(html_text, aid)
                off = self._web_node_to_offer(node)
                if off:
                    offers.append(off)
                if len(offers) >= limit:
                    break

        return offers[:limit]

    def _iter_ad_nodes(self, node: Any):
        if isinstance(node, dict):
            if "creativeId" in node and isinstance(node.get("creativeId"), str):
                yield node
            elif "adId" in node and isinstance(node.get("adId"), str):
                yield node
            for v in node.values():
                yield from self._iter_ad_nodes(v)
        elif isinstance(node, list):
            for v in node:
                yield from self._iter_ad_nodes(v)

    def _regex_node(self, html_text: str, aid: str) -> dict:
        idx = html_text.find(aid)
        window = html_text[max(0, idx - 600): idx + 600]
        node: dict[str, Any] = {"creativeId": aid}
        for key in (
            "advertiserName",
            "adText",
            "landingPageUrl",
            "startDate",
            "mediaType",
        ):
            pattern = '"' + re.escape(key) + r'"\s*:\s*"([^"]*)"'
            m = re.search(pattern, window)
            if m:
                raw = m.group(1)
                try:
                    decoded = json.loads(f'"{raw}"')
                except (json.JSONDecodeError, ValueError):
                    decoded = raw
                node[key] = html.unescape(decoded)
        return node



    def _web_node_to_offer(self, d: dict[str, Any]) -> dict | None:
        if not isinstance(d, dict):
            return None
        aid = str(
            d.get("creativeId")
            or d.get("adId")
            or d.get("id")
            or ""
        )
        if not aid:
            return None
        page = (
            d.get("advertiserName")
            or d.get("advertiser_name")
            or d.get("brand")
            or d.get("sponsor")
            or "Anunciante"
        )
        body = d.get("adText") or d.get("body") or d.get("headline") or ""
        if isinstance(body, list):
            body = " ".join(x for x in body if isinstance(x, str))
        titles = d.get("adTitle") or d.get("headline") or ""
        headline = (titles or (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(d.get("startDate") or d.get("firstShown"))
        impr = _parse_impressions(d.get("impressions"))
        country = str(d.get("region") or d.get("country") or self.country or "BR")
        fmt = _infer_format(d)
        return self._finalize(
            uid=aid,
            headline=headline,
            advertiser=page,
            country=country,
            body=str(body),
            fmt=fmt,
            start=start,
            impr=impr,
            snapshot=d.get("landingPageUrl")
            or d.get("url")
            or d.get("adUrl")
            or "",
            image=d.get("landingPageUrl")
            or d.get("imageUrl")
            or d.get("image")
            or d.get("url")
            or "",
            video="",
        )

    def _finalize(
        self,
        *,
        uid: str,
        headline: str,
        advertiser: str,
        country: str,
        body: str,
        fmt: str,
        start: datetime | None,
        impr: int,
        snapshot: str,
        image: str = "",
        video: str = "",
    ) -> dict:
        longevity = max(1, (_now() - start).days) if start else 1
        has_video = fmt == "video"
        score = _compute_score(longevity, impr, has_video)
        if impr <= 0:
            impr = int(200_000 + score * 60_000)
        bullets = _bullets_from_body(body)
        cta = "Ver anúncio" if snapshot else "Ver oferta"
        return {
            "id": f"native_{uid}",
            "headline": headline.strip()[:160] or "Oferta da Native Ad Library",
            "advertiser": str(advertiser)[:60],
            "network": "native",
            "format": fmt,
            "niche": "",
            "longevityDays": longevity,
            "winningScore": score,
            "estImpressions": impr,
            "country": country,
            "thumbnailHue": _hue_from_id(uid),
            "gradient": GRADIENTS[hash(uid) % len(GRADIENTS)],
            "image": image if looks_like_image(image) else cover_image(uid, "native"),
            "thumb": image if looks_like_image(image) else cover_image(uid, "native"),
            "videoUrl": video if looks_like_video(video) else "",
            "bullets": bullets or ["Criativo coletado da Native Ad Library"],
            "cta": cta,
            "funnel": [
                {"type": "lp", "label": "Landing Page"},
                {"type": "checkout", "label": "Checkout"},
            ],
            "vslSeconds": 0,
            "transcript": [],
            "snapshotUrl": snapshot,
            "source": "native_ad_library",
        }


__all__ = ["NativeAdsLibrary", "NativeAdsError"]

