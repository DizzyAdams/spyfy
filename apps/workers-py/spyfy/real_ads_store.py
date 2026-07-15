"""SpyFy — Real Native Ads Store.

Holds genuinely-collected native ads (from a logged-in browser session or a
pasted ad dump) on disk, and exposes them to the offers pipeline.

Why this exists:
  Every official Ad Library (Meta/TikTok/Google/Pinterest) blocks anonymous /
  headless scraping (empirically verified: Meta 403 challenge, Google DNS
  blocked in headless env, TikTok/Pinterest JS-only). Competitors obtain REAL
  native ads the same way this store enables: via a logged-in session cookie or
  a batch export of ads the operator collected. The deployed API (Vercel, no
  browser) serves these real ads when present; otherwise the rich structured
  generator (real media + KPIs) keeps the product 100% functional.

Storage: apps/workers-py/cache/real_ads.json  (list of normalized offers)
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
STORE_PATH = os.path.join(CACHE_DIR, "real_ads.json")

# Fields we keep from a real native ad (everything else is enriched by the
# ROI/scale engine downstream).
_REAL_FIELDS = (
    "headline", "advertiser", "network", "niche", "country",
    "image", "videoUrl", "format", "pageUrl", "link", "cta",
)


def _ensure_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_all() -> list[dict[str, Any]]:
    if not os.path.exists(STORE_PATH):
        return []
    try:
        with open(STORE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


def save_all(offers: list[dict[str, Any]]) -> None:
    _ensure_dir()
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(offers, f, ensure_ascii=False, indent=2)


# Campos de mídia/destino — garantimos "" (nunca None) para o
# frontend não renderizar `undefined`/mídia quebrada.
_MEDIA_FIELDS = ("image", "videoUrl", "thumb", "format", "pageUrl", "link", "cta", "snapshotUrl")


def add_real_ads(offers: list[dict[str, Any]]) -> int:
    """Normaliza e anexa anúncios nativos REAIS à loja. Retorna nº adicionado."""
    existing = load_all()
    seen = {(o.get("advertiser"), o.get("headline"), o.get("network")) for o in existing}
    added = 0
    for o in offers:
        rec = {k: o.get(k) for k in _REAL_FIELDS if o.get(k) not in (None, "")}
        if not rec.get("headline") and not rec.get("advertiser"):
            continue
        # Normaliza mídia/destino para string ("" se ausente).
        for k in _MEDIA_FIELDS:
            v = o.get(k)
            rec[k] = v if isinstance(v, str) and v.strip() else ""
        # `_source`/`_ts` são meta — NÃO sobrescrevemos o source informado
        # pelo extrator (ex.: "synthetic", "tiktok_creative_center",
        # "browser_session") para o dashboard nunca mentir sobre a origem.
        incoming = o.get("_source")
        rec["_source"] = incoming if isinstance(incoming, str) and incoming else "real_native"
        rec["_ts"] = int(time.time())
        key = (rec.get("advertiser"), rec.get("headline"), rec.get("network"))
        if key in seen:
            continue
        existing.append(rec)
        seen.add(key)
        added += 1
    if added:
        save_all(existing)
    return added


def query(niche: str | None = None, network: str | None = None,
          country: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Filtra a loja por nicho/rede/país.

    Garante que todo anúncio tenha `link` (destino real) não vazio:
    deriva de `link` -> `pageUrl` -> `snapshotUrl`, senão "". Assim o
    card "Ver oferta" sempre abre algo (ou "#" tratado no frontend).
    """
    ads = load_all()
    if niche:
        nk = niche.lower()
        ads = [a for a in ads if nk in (a.get("niche") or "").lower()]
    if network and network != "all":
        ads = [a for a in ads if a.get("network") == network]
    if country:
        ads = [a for a in ads if (a.get("country") or "").upper() == country.upper()]
    for a in ads:
        if not a.get("link"):
            a["link"] = a.get("pageUrl") or a.get("snapshotUrl") or ""
    return ads[:limit]


def count() -> int:
    return len(load_all())
