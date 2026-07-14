"""
SpyFy — Real-time Producer (scraper -> Radar WebSocket)
=======================================================
Ponte entre os workers Python (scraper / Radar) e o servidor WebSocket
do app web (apps/web/server/realtime.js).

Empurra ofertas reais para o endpoint de ingestão do Radar:

    POST http://<host>:<port>/v1/radar/ingest
    Authorization: Bearer <REALTIME_TOKEN>   (se o servidor definir o token)
    body: { "offer": { ... } }  |  { "offers": [ ... ] }

Sem dependências externas (apenas stdlib: urllib + json).

Uso:
    python -m spyfy.realtime_producer --sample 5
    python -m spyfy.realtime_producer --file ofertas.json --url http://localhost:4000
    python -m spyfy.realtime_producer --token segredo --radar q1
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request

DEFAULT_URL = "http://localhost:4000"
GRADIENTS = [
    ["#6E56CF", "#22D3EE"], ["#22D3EE", "#2563EB"], ["#7C5CFF", "#2DD4FF"],
    ["#A855F7", "#22D3EE"], ["#F472B6", "#7C5CFF"], ["#34D399", "#22D3EE"],
]

# ---- Media URL guards -------------------------------------------------------
# As Ad Libraries retornam, no máximo, a URL da *página* do anúncio
# (snapshot/landing page). Usar essa URL como <img src> ou <video src>
# quebra a renderização no navegador. Estes helpers garantem que só
# passamos adiante URLs que realmente parecem ser a mídia (arquivo
# direto de imagem/vídeo), caindo num cover determinístico quando não.

_IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif")
_VIDEO_EXT = (".mp4", ".webm", ".mov", ".ogg", ".m4v")
_IMAGE_HOST_HINTS = (
    "fbcdn", "fbsbx", "googleusercontent", "twimg", "tiktokcdn",
    "picsum.photos", "unsplash", "images-wixmp", "cloudfront", "wixmp",
)


def looks_like_image(url: str | None) -> bool:
    """True só quando `url` é plausivelmente um arquivo de imagem direto."""
    u = (url or "").lower()
    if not u:
        return False
    if u.endswith(_IMAGE_EXT):
        return True
    return any(h in u for h in _IMAGE_HOST_HINTS)


def looks_like_video(url: str | None) -> bool:
    """True só quando `url` é plausivelmente um arquivo de vídeo direto."""
    u = (url or "").lower()
    if not u:
        return False
    if u.endswith(_VIDEO_EXT):
        return True
    return "video" in u and any(
        h in u for h in ("tiktokcdn", "fbcdn", "cloudfront", "googlevideo", "vimeocdn")
    )


def cover_image(seed: str, network: str = "") -> str:
    """Cover determinístico (mesmo seed -> mesma foto) p/ o card nunca ficar
    só com o gradiente quando não há imagem real confiável."""
    safe = "".join(ch for ch in (seed or "spyfy") if ch.isalnum()) or "spyfy"
    net = (network or "spyfy").lower()
    return f"https://picsum.photos/seed/{net}_{safe}/640/384"


def _post(url: str, token: str, payload: dict, timeout: int = 10) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - depends on server
        body = exc.read().decode("utf-8", "replace")
        return {"ok": False, "status": exc.code, "error": body}
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}


def push_offer(offer: dict, base_url: str = DEFAULT_URL, token: str = "",
              timeout: int = 10) -> dict:
    """Empurra UMA oferta para o Radar."""
    return _post(f"{base_url.rstrip('/')}/v1/radar/ingest", token,
                 {"offer": offer}, timeout)


def push_bulk(offers: list[dict], base_url: str = DEFAULT_URL, token: str = "",
              timeout: int = 10) -> dict:
    """Empurra VÁRIAS ofertas de uma vez."""
    return _post(f"{base_url.rstrip('/')}/v1/radar/ingest", token,
                 {"offers": offers}, timeout)


def radar_offer_to_payload(o, headline: str = "", advertiser: str = "Radar") -> dict:
    """Converte um `RadarOffer` (spyfy.radar) no payload do app web.

    O servidor normaliza campos faltantes, então mandamos o essencial.
    """
    from .radar import RadarOffer  # import local p/ evitar ciclo em alguns setups

    if not isinstance(o, RadarOffer):
        raise TypeError("esperado RadarOffer")
    return {
        "id": f"radar_{o.offer_id}",
        "headline": headline or f"Oferta {o.niche} em alta ({o.network})",
        "advertiser": advertiser,
        "network": o.network,
        "niche": o.niche,
        "country": o.country,
        "winningScore": o.winning_score,
        "longevityDays": o.longevity_days,
        "format": "video",
        "gradient": GRADIENTS[hash(o.offer_id) % len(GRADIENTS)],
        "scaling_signal": o.scaling_signal,
    }

# ===== PRODUCER CLI BELOW =====


def sample_offers(n: int = 5) -> list[dict]:
    niches = ["Emagrecimento", "Finanças", "Beleza / Nutra", "Investimentos"]
    networks = ["meta", "tiktok", "google", "youtube"]
    out = []
    for i in range(n):
        out.append({
            "id": f"ext_sample_{i}",
            "headline": f"[Real] Oferta minerada #{i + 1} — {niches[i % len(niches)]}",
            "advertiser": f"Scraper{i}",
            "network": networks[i % len(networks)],
            "niche": niches[i % len(niches)],
            "country": "BR",
            "winningScore": 70 + (i * 4) % 28,
            "longevityDays": 10 + i * 7,
            "estImpressions": (i + 1) * 500_000,
            "format": "video",
            "gradient": GRADIENTS[i % len(GRADIENTS)],
            "bullets": ["Anglo real extraído do scraper", "Funil detectado"],
            "cta": "Ver oferta",
            "funnel": [
                {"type": "lp", "label": "Landing Page", "stack": "ClickFunnels"},
                {"type": "vsl", "label": "VSL", "stack": "YouTube"},
            ],
        })
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SpyFy real-time producer")
    ap.add_argument("--url", default=DEFAULT_URL, help="base URL do Radar WS")
    ap.add_argument("--token", default="", help="REALTIME_TOKEN (se definido)")
    ap.add_argument("--sample", type=int, default=0, help="envia N ofertas de exemplo")
    ap.add_argument("--file", default="", help="path de JSON (objeto ou array)")
    ap.add_argument("--radar", default="", help="id de RadarQuery p/ usar spyfy.radar")
    args = ap.parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        offers = data if isinstance(data, list) else [data]
        result = push_bulk(offers, args.url, args.token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    if args.radar:
        from .radar import RadarOffer, RadarQuery, run_radar

        q = RadarQuery(args.radar, "u1")
        sample = [
            RadarOffer("a", "keto", "meta", "BR", 88, 63, 9, "hot", 0.05),
            RadarOffer("b", "finance", "tiktok", "US", 95, 80, 10, "hot", 0.9),
        ]
        offers = [radar_offer_to_payload(o) for o in run_radar(q, sample)]
        result = push_bulk(offers, args.url, args.token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    if args.sample:
        result = push_bulk(sample_offers(args.sample), args.url, args.token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 1

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

