"""Fonte REAL pública da TikTok Creative Center (sem token, sem login).

Usa o endpoint `/creative/creativeCenter/trends/hashtag` (SSR) que devolve
JSON `dehydratedState` com as hashtags em alta por país — dados REAIS da
Ad Library do TikTok, sem auth (confirmado ao vivo). Mapeia cada hashtag
para uma oferta no formato SpyFy.
"""
import os
import sys
import json
import time
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spyfy.scrapling_adapter import ScraplingClient


def _clean(txt: str) -> str:
    s = txt.strip()
    if s.startswith("b'") or s.startswith('b"'):
        try:
            import ast
            s = ast.literal_eval(s)
            if isinstance(s, bytes):
                s = s.decode("utf-8", "replace")
        except Exception:
            s = s[2:-1] if s.endswith(("'", '"')) else s[2:]
    for pre in [")]}while(1);", ")]}'", ")]}", "for (;;);"]:
        if s.startswith(pre):
            s = s[len(pre):]
    return s


def _extract_hashtags(state: dict) -> list[str]:
    """Caminha o dehydratedState e coleta hashtags reais de tendência."""
    found = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("hashtag", "tag", "hashtagName", "name") and isinstance(v, str) and v:
                    if v not in found and not v.isupper():
                        found.append(v)
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)
    walk(state)
    # filtra só hashtags com '#' ou textuais curtas
    out = [h for h in found if isinstance(h, str) and 1 < len(h) < 40][:50]
    return out


def fetch_tiktok_trends(niche: str, country: str = "BR", period: int = 30,
                        limit: int = 10) -> list[dict]:
    """Busca tendências REAIS de hashtags da TikTok Creative Center (público).

    Retorna ofertas SpyFy (network='tiktok') ou [] se a fonte falhar.
    """
    client = ScraplingClient(country=country, timeout=35)
    url = (f"https://ads.tiktok.com/creative/creativeCenter/trends/hashtag"
           f"?country={country}&period={period}"
           f"&__loader=creativeCenter%2Ftrends%2F%28tab%29%2Fpage&__ssrDirect=true")
    try:
        resp = client.get(url, headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hub.html",
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        })
        data = json.loads(_clean(resp.text or ""))
    except Exception:
        return []

    # o JSON é { dehydratedState: { queries: [ { state: { data: {...} } } ] } }
    queries = ((data.get("dehydratedState") or {}).get("queries") or [])
    hashtags: list[str] = []
    for q in queries:
        dq = (q.get("state") or {}).get("data") or {}
        hashtags += _extract_hashtags(dq)
    hashtags = list(dict.fromkeys(hashtags))[:limit]  # dedupe
    if not hashtags:
        return []

    ts = int(time.time())
    offers = []
    for i, tag in enumerate(hashtags):
        offers.append({
            "id": f"tiktok_trend_{niche}_{ts}_{i}",
            "headline": f"#{tag} — tendência em alta ({country})",
            "advertiser": f"#{tag}",
            "network": "tiktok", "niche": niche, "format": "video",
            "image": "", "videoUrl": "",
            "estImpressions": 0, "estRoas": 0.0, "estDailyProfit": 0.0,
            "_source": "tiktok_creative_center",
            "trend": tag,
        })
    return offers


if __name__ == "__main__":
    out = fetch_tiktok_trends("keto", "BR")
    print("total:", len(out))
    for o in out[:10]:
        print(" ", o["trend"])
