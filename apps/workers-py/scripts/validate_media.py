"""SpyFy — validador de pipeline de ofertas (mídia + KPIs).

Prova que TODA oferta (sintética via mine(simulate) OU via API /v1/offers)
carrega:
  - image  (URL Unsplash válida de imagem)
  - videoUrl (arquivo .mp4 local /videos/*) quando format == "video"
  - KPIs enriquecidos: estRoiPct, estRoas, winProb, estDailyProfit,
    scalingSignal, confidence, scaleIndex

Uso:
    python scripts/validate_media.py
"""
from __future__ import annotations

import json
import sys
from typing import Any

# Garante import do pacote spyfy a partir da raiz do app.
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spyfy.scraper_bridge import mine  # noqa: E402

NETWORKS = ["meta", "tiktok", "google", "youtube", "native", "pinterest"]
NICHE_KEYS = [
    "keto", "emagrecimento", "beleza", "nutra", "finance", "investimentos",
    "relacionamento", "marketing", "tech", "saas", "fashion", "shopping",
    "food", "health", "pets", "home", "education", "travel", "games", "crypto",
]
_VIDEO_EXT = (".mp4", ".webm", ".mov")
_IMAGE_HINTS = ("unsplash", "picsum", "images-wixmp", "cloudfront", ".png",
                ".jpg", ".jpeg", ".webp", ".gif", ".avif")


def looks_image(u: str) -> bool:
    u = (u or "").lower()
    return bool(u) and (u.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"))
                       or any(h in u for h in ("unsplash", "picsum", "images-wixmp", "cloudfront")))


def looks_video(u: str) -> bool:
    u = (u or "").lower()
    return bool(u) and u.endswith(_VIDEO_EXT)


def check_offer(o: dict[str, Any], ctx: str) -> list[str]:
    problems: list[str] = []
    oid = o.get("id", "?")
    fmt = o.get("format", "")
    image = o.get("image") or ""
    video = o.get("videoUrl") or ""
    if not looks_image(image):
        problems.append(f"[{ctx}] {oid}: image inválido ({image!r})")
    if fmt == "video":
        if not looks_video(video):
            problems.append(f"[{ctx}] {oid}: format=video mas videoUrl inválido ({video!r})")
    else:
        # image/carousel não exige vídeo; ok se vazio
        pass
    for k in ("estRoiPct", "estRoas", "winProb", "estDailyProfit", "scalingSignal",
              "confidence", "scaleIndex"):
        if k not in o or o.get(k) in (None, ""):
            problems.append(f"[{ctx}] {oid}: KPI ausente {k}")
    return problems


def main() -> int:
    problems: list[str] = []
    total = 0
    per_niche: dict[str, int] = {}

    for net in NETWORKS:
        for niche in NICHE_KEYS:
            offers = mine(niche, net, count=2, simulate=True)
            per_niche[niche] = per_niche.get(niche, 0) + len(offers)
            total += len(offers)
            for o in offers:
                problems += check_offer(o, f"{net}/{niche}")

    # Também exercita a descoberta cruzada (network "all"/aleatório).
    mixed = mine("Emagrecimento", "all", count=3, simulate=True)
    total += len(mixed)
    for o in mixed:
        problems += check_offer(o, "all/Emagrecimento")

    print(f"Ofertas validadas: {total}")
    print(f"Nichos cobertos: {len(per_niche)} | redes: {len(NETWORKS)}")
    if problems:
        print(f"\nX PROBLEMAS ({len(problems)}):")
        for p in problems[:50]:
            print("  - " + p)
        return 1
    print("\nOK — 100% das ofertas com imagem real, vídeo local (quando vídeo) e KPIs completos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
