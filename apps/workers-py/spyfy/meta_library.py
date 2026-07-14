"""
SpyFy — Meta Ad Library integration (REAL)
=========================================
Busca de anúncios ativos do Facebook/Instagram via Meta Ad Library (fonte
pública oficial de transparência). Dois modos, em ordem de preferência:

1. Ad Library API (graph.facebook.com/v19.0/ads_archive) quando um
   ``access_token`` é informado — estável, legal, barato.
2. Web scrape da Ad Library (facebook.com/ads/library) como fallback sem
   token, usando httpx + html.parser (stdlib, zero novas deps).

Ambos retornam dicts no formato ``Offer`` consumido pelo Radar
(apps/web/server/realtime.js -> normalizeOffer). Contrato em lib/data.ts.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlencode

import httpx

from .realtime_producer import (
    GRADIENTS,
    cover_image,
    looks_like_image,
    looks_like_video,
    video_cover,
)

AD_LIBRARY_WEB = "https://www.facebook.com/ads/library/"
AD_ARCHIVE_API = "https://graph.facebook.com/v19.0/ads_archive"

_MEDIA_TO_FORMAT = {
    "VIDEO": "video",
    "IMAGE": "image",
    "CAROUSEL": "carousel",
    "MEMORY": "carousel",
    "LINK": "image",
    "ALL": "image",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class MetaScrapeError(RuntimeError):
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
        lo = _to_int(value.get("lower_bound"))
        hi = _to_int(value.get("upper_bound"))
        if lo and hi:
            return (lo + hi) // 2
        return lo or hi or 0
    return _to_int(value)


def _hue_from_id(uid: str) -> int:
    return (hash(uid) % 360 + 360) % 360


def _infer_format(node: dict[str, Any]) -> str:
    mt = str(node.get("mediaType") or node.get("media_type") or "").upper()
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
        return ["Criativo coletado da Meta Ad Library"]
    parts = re.split(r"(?<=[\.!?])\s+", body.strip())
    out = [p.strip() for p in parts if p.strip()]
    return out[:n] if out else [body[:120]]


class MetaAdLibrary:
    """Cliente de busca de anúncios do Meta Ad Library (API ou web)."""

    def __init__(
        self,
        access_token: str = "",
        country: str = "BR",
        timeout: float = 20.0,
        client: httpx.Client | None = None,
        proxies: str | None = None,
    ) -> None:
        import os
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN", "")
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
        media_types: Iterable[str] = ("all",),
    ) -> list[dict]:
        """Retorna até ``limit`` ofertas (formato Offer) para ``query``."""
        country = country or self.country
        media_types = tuple(media_types) or ("all",)

        if self.access_token:
            try:
                return self._search_api(query, limit, country, media_types)
            except MetaScrapeError:
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
        params = {
            "access_token": self.access_token,
            "search_terms": query,
            "ad_reached_countries": json.dumps([country]),
            "ad_active_status": "ACTIVE",
            "media_type": media_types[0].upper() if media_types else "ALL",
            "fields": ",".join(
                [
                    "id",
                    "ad_archive_id",
                    "page_id",
                    "page_name",
                    "ad_creative_bodies",
                    "ad_creative_link_titles",
                    "ad_delivery_start_time",
                    "ad_delivery_country",
                    "impressions",
                    "spend",
                    "currency",
                    "publisher_platforms",
                    "snapshot_url",
                    "ad_snapshot_url",
                    # MÍDIA REAL + URL de destino (CTA) do criativo. Sem isto o
                    # SpyFy renderizaria placeholders falsos em vez do vídeo/
                    # imagem/link verdadeiros do anúncio.
                    "ad_creatives{url,video_url,thumbnail_url,link_url,body}",
                    "landing_page_url",
                ]
            ),
            "limit": str(min(limit, 100)),
        }
        out: list[dict] = []
        url: str | None = AD_ARCHIVE_API
        while url and len(out) < limit:
            resp = self.client.get(
                url, params=params if url == AD_ARCHIVE_API else None
            )
            if resp.status_code != 200:
                raise MetaScrapeError(
                    f"Ad Library API {resp.status_code}: {resp.text[:200]}"
                )
            payload = resp.json()
            for row in payload.get("data", []):
                offer = self._api_to_offer(row)
                if offer:
                    out.append(offer)
            url = (payload.get("paging") or {}).get("next")
        return out[:limit]



    def _search_web(
        self,
        query: str,
        limit: int,
        country: str,
        media_types: tuple[str, ...],
    ) -> list[dict]:
        params = {
            "active_status": "ACTIVE",
            "ad_type": "all",
            "country": country,
            "q": query,
            "media_type": media_types[0] if media_types else "all",
        }
        url = f"{AD_LIBRARY_WEB}?{urlencode(params)}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise MetaScrapeError(
                f"Ad Library web {resp.status_code} para {query!r}"
            )
        offers = self.parse_html(resp.text, limit=limit)
        if not offers:
            raise MetaScrapeError(
                f"Ad Library web sem cards extraídos para {query!r} "
                f"(possível login wall / bloqueio de região)"
            )
        return offers

    def parse_html(self, html_text: str, limit: int = 20) -> list[dict]:
        """Extrai ofertas do HTML da Ad Library (JSON embarcado + fallback)."""
        offers: list[dict] = []
        seen: set[str] = set()

        # 1) Blob JSON em <script type="application/json"> (formato FB)
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

        # 2) Fallback: regex direto sobre o HTML
        if not offers:
            for m in re.finditer(r'"adArchiveId"\s*:\s*"([^"]+)"', html_text):
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
            if "adArchiveId" in node and isinstance(node.get("adArchiveId"), str):
                yield node
            for v in node.values():
                yield from self._iter_ad_nodes(v)
        elif isinstance(node, list):
            for v in node:
                yield from self._iter_ad_nodes(v)

    def _regex_node(self, html_text: str, aid: str) -> dict:
        idx = html_text.find(aid)
        window = html_text[max(0, idx - 600) : idx + 600]
        node: dict[str, Any] = {"adArchiveId": aid}
        for key in ("pageName", "body", "snapshotUrl", "startDate", "mediaType"):
            m = re.search(rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"', window)
            if m:
                raw = m.group(1)
                try:
                    decoded = json.loads(f'"{raw}"')
                except (json.JSONDecodeError, ValueError):
                    decoded = raw
                node[key] = html.unescape(decoded)
        return node



    def _api_to_offer(self, d: dict[str, Any]) -> dict | None:
        aid = str(d.get("ad_archive_id") or d.get("id") or "")
        if not aid:
            return None
        page = d.get("page_name") or "Anunciante"
        bodies = d.get("ad_creative_bodies") or []
        body = " ".join(b for b in bodies if isinstance(b, str))
        titles = d.get("ad_creative_link_titles") or []
        headline = (titles[0] if titles else (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(d.get("ad_delivery_start_time") or d.get("startDate"))
        impr = _parse_impressions(d.get("impressions"))
        country = str(d.get("ad_delivery_country") or self.country or "BR")
        fmt = _infer_format(d)

        # ---- MÍDIA REAL + LINK DE DESTINO (CTA) ----
        # A Ad Library devolve o criativo aninhado em `ad_creatives` (lista).
        # Extraímos a imagem/vídeo reais e a URL de destino (link_url) do
        # criativo. Quando ausente, caímos no snapshot/landing_page_url.
        creative = (d.get("ad_creatives") or [])
        if isinstance(creative, list):
            creative = creative[0] if creative else {}
        creative = creative or {}
        real_image = creative.get("url") or creative.get("thumbnail_url") or ""
        real_video = creative.get("video_url") or ""
        # O `link` (destino real da oferta) vem do criativo ou da landing page.
        link = (
            creative.get("link_url")
            or d.get("landing_page_url")
            or d.get("snapshot_url")
            or d.get("ad_snapshot_url")
            or ""
        )
        snapshot = (
            d.get("snapshot_url")
            or d.get("ad_snapshot_url")
            or d.get("landing_page_url")
            or ""
        )

        # Preferir a mídia real quando ela for uma URL de imagem/vídeo direta;
        # caso contrário mantemos o snapshot como fallback p/ o _finalize.
        image = real_image if looks_like_image(real_image) else (snapshot or real_image)
        video = real_video if looks_like_video(real_video) else (
            snapshot if fmt == "video" else ""
        )
        return self._finalize(
            uid=aid,
            headline=headline,
            advertiser=page,
            country=country,
            body=body,
            fmt=fmt,
            start=start,
            impr=impr,
            snapshot=snapshot,
            link=link,
            image=image,
            video=video,
        )

    def _web_node_to_offer(self, d: dict[str, Any]) -> dict | None:
        if not isinstance(d, dict):
            return None
        aid = str(d.get("adArchiveId") or d.get("ad_archive_id") or "")
        if not aid:
            return None
        page = d.get("pageName") or d.get("page_name") or "Anunciante"
        body = d.get("body") or d.get("adCreativeBody") or ""
        if isinstance(body, list):
            body = " ".join(x for x in body if isinstance(x, str))
        titles = d.get("adCreativeLinkTitle") or d.get("linkTitle") or ""
        headline = (titles or (body.split(".")[0] if body else "")) or "Oferta"
        start = _parse_dt(
            d.get("startDate") or d.get("adDeliveryStartTime") or d.get("startDate")
        )
        impr = _parse_impressions(d.get("impressions"))
        fmt = _infer_format(d)
        snapshot = (
            d.get("snapshotUrl")
            or d.get("snapshot_url")
            or d.get("url")
            or ""
        )
        link = (
            d.get("landingPageUrl")
            or d.get("landing_page_url")
            or d.get("linkUrl")
            or d.get("url")
            or snapshot
            or ""
        )
        return self._finalize(
            uid=aid,
            headline=headline,
            advertiser=page,
            country=self.country or "BR",
            body=str(body),
            fmt=fmt,
            start=start,
            impr=impr,
            snapshot=snapshot,
            link=link,
            image=snapshot,
            video="" if fmt != "video" else snapshot,
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
        link: str = "",
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
        # `link` é o DESTINO REAL da oferta (landing page / snapshot do anúncio).
        # Sempre presente quando temos snapshot; o frontend abre em nova aba.
        real_link = link or snapshot or ""
        return {
            "id": f"meta_{uid}",
            "headline": headline.strip()[:160] or "Oferta do Meta Ad Library",
            "advertiser": str(advertiser)[:60],
            "network": "meta",
            "format": fmt,
            "niche": "",
            "longevityDays": longevity,
            "winningScore": score,
            "estImpressions": impr,
            "country": country,
            "thumbnailHue": _hue_from_id(uid),
            "gradient": GRADIENTS[hash(uid) % len(GRADIENTS)],
            "image": image if looks_like_image(image) else cover_image(uid, "meta"),
            "thumb": image if looks_like_image(image) else cover_image(uid, "meta"),
            "videoUrl": video if looks_like_video(video) else (
                video_cover(uid, "meta") if fmt == "video" else ""
            ),
            "bullets": bullets or ["Criativo coletado da Meta Ad Library"],
            "cta": cta,
            "link": real_link,
            "funnel": [
                {"type": "lp", "label": "Landing Page"},
                {"type": "checkout", "label": "Checkout"},
            ],
            "vslSeconds": 0,
            "transcript": [],
            "snapshotUrl": snapshot,
            "source": "meta_ad_library",
        }


__all__ = ["MetaAdLibrary", "MetaScrapeError"]

