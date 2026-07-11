"""
SpyFy — TikTok Ad Library integration (REAL)
===========================================
Busca de anúncios ativos do TikTok via TikTok Ad Library (fonte pública
oficial de transparência). Dois modos, em ordem de preferência:

1. Ad Library API (ads.tiktok.com/open_api/v1.3/ad_library/get) quando um
   ``access_token`` é informado — estável, legal, barato.
2. Web scrape da Ad Library (ads.tiktok.com/ad-library) como fallback sem
   token, usando httpx + html.parser (stdlib, zero novas deps).

Ambos retornam dicts no formato ``Offer`` consumido pelo Radar
(apps/web/server/realtime.js -> normalizeOffer). Contrato em lib/data.ts.

Espelha a interface de ``spyfy.meta_library.MetaAdLibrary``.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlencode

import httpx

from .realtime_producer import GRADIENTS

AD_LIBRARY_WEB = "https://ads.tiktok.com/ad-library"
AD_LIBRARY_API = "https://ads.tiktok.com/open_api/v1.3/ad_library/get/"

_MEDIA_TO_FORMAT = {
    "VIDEO": "video",
    "IMAGE": "image",
    "CAROUSEL": "carousel",
    "SINGLE_VIDEO": "video",
    "SINGLE_IMAGE": "image",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class TikTokScrapeError(RuntimeError):
    """Levantado quando nem a API nem o web-scrape retornam dados."""


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
        node.get("mediaType") or node.get("ad_format") or node.get("format") or ""
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
        return ["Criativo coletado da TikTok Ad Library"]
    parts = re.split(r"(?<=[\.!?])\s+", body.strip())
    out = [p.strip() for p in parts if p.strip()]
    return out[:n] if out else [body[:120]]


class TikTokAdLibrary:
    """Cliente de busca de anúncios do TikTok Ad Library (API ou web)."""

    def __init__(
        self,
        access_token: str = "",
        country: str = "BR",
        timeout: float = 20.0,
        client: httpx.Client | None = None,
        proxies: str | dict | None = None,
    ) -> None:
        self.access_token = access_token or ""
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
                proxies=self.proxies or None,
            )
        return self._client

    def search(
        self,
        query: str,
        limit: int = 20,
        country: str | None = None,
        media_types: Iterable[str] = ("all",),
    ) -> list[dict]:
        """Retorna até ``limit`` ofertas (formato Offer) para ``query``."""
        country = country or self.country
        media_types = tuple(media_types) or ("all",)

        if self.access_token:
            try:
                return self._search_api(query, limit, country, media_types)
            except TikTokScrapeError:
                raise
            except Exception:  # noqa: BLE001 - fallback explícito p/ web
                pass

        return self._search_web(query, limit, country, media_types)

    def _search_api(
        self,
        query: str,
        limit: int,
        country: str,
        media_types: tuple[str, ...],
    ) -> list[dict]:
        params: dict[str, str] = {
            "query": query,
            "region": country,
            "page_size": str(min(limit, 100)),
            "ad_format": media_types[0] if media_types else "ALL",
        }
        resp = self.client.get(
            AD_LIBRARY_API,
            params=params,
            headers={"Access-Token": self.access_token},
        )
        if resp.status_code != 200:
            raise TikTokScrapeError(
                f"TikTok Ad Library API {resp.status_code}: {resp.text[:200]}"
            )
        payload = resp.json()
        rows = (
            payload.get("data", {}).get("list")
            or payload.get("data", {}).get("ads")
            or []
        )
        offers = []
        seen: set[str] = set()
        for row in rows:
            off = self._api_to_offer(row)
            if off and off["id"] not in seen:
                seen.add(off["id"])
                offers.append(off)
            if len(offers) >= limit:
                break
        if not offers:
            raise TikTokScrapeError(
                f"TikTok Ad Library API sem anúncios para {query!r}"
            )
        return offers[:limit]

    def _search_web(
        self,
        query: str,
        limit: int,
        country: str,
        media_types: tuple[str, ...],
    ) -> list[dict]:
        params = {
            "q": query,
            "region": country.lower(),
            "media_type": media_types[0] if media_types else "all",
        }
        url = f"{AD_LIBRARY_WEB}?{urlencode(params)}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise TikTokScrapeError(
                f"TikTok Ad Library web {resp.status_code} para {query!r}"
            )
        offers = self.parse_html(resp.text, limit=limit)
        if not offers:
            raise TikTokScrapeError(
                f"TikTok Ad Library web sem cards extraídos para {query!r} "
                f"(possível login wall / bloqueio de região)"
            )
        return offers



    def parse_html(self, html_text: str, limit: int = 20) -> list[dict]:
        """Extrai ofertas do HTML da TikTok Ad Library (JSON + fallback)."""
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
            for m in re.finditer(r'"(?:adId|ad_id)"\s*:\s*"([^"]+)"', html_text):
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
            if "adId" in node and isinstance(node.get("adId"), str):
                yield node
            elif "ad_id" in node and isinstance(node.get("ad_id"), str):
                yield node
            for v in node.values():
                yield from self._iter_ad_nodes(v)
        elif isinstance(node, list):
            for v in node:
                yield from self._iter_ad_nodes(v)

    def _regex_node(self, html_text: str, aid: str) -> dict:
        idx = html_text.find(aid)
        window = html_text[max(0, idx - 600) : idx + 600]
        node: dict[str, Any] = {"adId": aid}
        for key in (
            "advertiserName",
            "adText",
            "landingPageUrl",
            "startDate",
            "mediaType",
        ):
            m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', window)
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
        aid = str(d.get("adId") or d.get("ad_id") or d.get("id") or "")
        if not aid:
            return None
        page = (
            d.get("advertiserName")
            or d.get("brandName")
            or d.get("pageName")
            or "Anunciante"
        )
        body = d.get("adText") or d.get("body") or d.get("caption") or ""
        if isinstance(body, list):
            body = " ".join(x for x in body if isinstance(x, str))
        titles = d.get("adTitle") or d.get("headline") or ""
        headline = (titles or (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(d.get("startDate") or d.get("createTime"))
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
            or d.get("adUrl")
            or d.get("url")
            or "",
        )



    def _api_to_offer(self, d: dict[str, Any]) -> dict | None:
        aid = str(d.get("ad_id") or d.get("adId") or d.get("id") or "")
        if not aid:
            return None
        page = d.get("advertiser_name") or d.get("advertiserName") or "Anunciante"
        body = d.get("ad_text") or d.get("adText") or d.get("body") or ""
        if isinstance(body, list):
            body = " ".join(x for x in body if isinstance(x, str))
        titles = d.get("ad_title") or d.get("headline") or ""
        headline = (titles or (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(d.get("start_date") or d.get("startDate"))
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
            snapshot=d.get("ad_url") or d.get("landingPageUrl") or d.get("url") or "",
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
    ) -> dict:
        longevity = max(1, (_now() - start).days) if start else 1
        has_video = fmt == "video"
        score = _compute_score(longevity, impr, has_video)
        if impr <= 0:
            impr = int(200_000 + score * 60_000)
        bullets = _bullets_from_body(body)
        cta = "Ver anúncio" if snapshot else "Ver oferta"
        return {
            "id": f"tiktok_{uid}",
            "headline": headline.strip()[:160] or "Oferta da TikTok Ad Library",
            "advertiser": str(advertiser)[:60],
            "network": "tiktok",
            "format": fmt,
            "niche": "",
            "longevityDays": longevity,
            "winningScore": score,
            "estImpressions": impr,
            "country": country,
            "thumbnailHue": _hue_from_id(uid),
            "gradient": GRADIENTS[hash(uid) % len(GRADIENTS)],
            "bullets": bullets or ["Criativo coletado da TikTok Ad Library"],
            "cta": cta,
            "funnel": [
                {"type": "lp", "label": "Landing Page"},
                {"type": "checkout", "label": "Checkout"},
            ],
            "vslSeconds": 0,
            "transcript": [],
            "snapshotUrl": snapshot,
            "source": "tiktok_ad_library",
        }


__all__ = ["TikTokAdLibrary", "TikTokScrapeError"]

