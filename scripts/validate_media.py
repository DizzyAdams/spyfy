"""Validacao automatica de midia das ofertas (SpyFy).

Para CADA oferta (demo do frontend, simulador do backend, e guards das
bibliotecas reais) confere se `image` / `videoUrl` apontam para uma
URL de midia REAL e acessive (HTTP < 400 + content-type correto).
Falha (exit 1) se alguma oferta ficar sem imagem valida ou com
videoUrl apontando para uma pagina web em vez de um arquivo de video.

Uso:
    python scripts/validate_media.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "apps" / "web" / "lib" / "data.ts"
WEB_PUBLIC = ROOT / "apps" / "web" / "public"
sys.path.insert(0, str(ROOT / "apps" / "workers-py"))

IMG_TYPES = ("image/",)
VID_TYPES = ("video/",)

client = httpx.Client(timeout=12.0, follow_redirects=True, headers={
    "User-Agent": "Mozilla/5.0 (compatible; SpyFyMediaValidator/1.0)",
})


def check(url: str, types) -> tuple[bool, str]:
    if not url:
        return False, "vazio"
    # URL local (asset estatico em apps/web/public) — checagem por arquivo
    if url.startswith("/"):
        p = WEB_PUBLIC / url.lstrip("/")
        if not p.exists():
            return False, f"LOCAL AUSENTE {url}"
        b = p.read_bytes()[:12]
        magic = bytes(b[4:8]).decode("latin-1", "replace")
        size_kb = p.stat().st_size // 1024
        is_mp4 = magic == "ftyp"
        is_img = p.suffix.lower() in (
            ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg",
        )
        ok = ("video/" in types and is_mp4) or ("image/" in types and is_img)
        return ok, f"LOCAL {size_kb}KB ftyp={magic}"
    try:
        with client.stream("GET", url) as r:
            ct = (r.headers.get("content-type") or "").lower()
            ok = r.status_code < 400 and any(t in ct for t in types)
            return ok, f"{r.status_code} {ct or '?'}"
    except Exception as e:  # noqa: BLE001
        return False, f"ERR {type(e).__name__}: {e}"


results: list[tuple[str, str, bool, str]] = []


def rec(kind: str, ident: str, ok: bool, detail: str) -> None:
    results.append((kind, ident, ok, detail))
    mark = "OK  " if ok else "FAIL"
    print(f"[{mark}] {kind:10} {ident:26} {detail}")


# 1) Demo do frontend (apps/web/lib/data.ts) -------------------------------
def validate_demo() -> None:
    txt = WEB_DATA.read_text(encoding="utf-8")
    offers = re.split(r"\n  \{", txt)  # separa blocos de oferta
    # coleta (id, image, videoUrl) via regex simples
    ids = re.findall(r'id:\s*"([^"]+)"', txt)
    imgs = dict(re.findall(r'image:\s*"([^"]+)"', txt)) if False else None
    # pega pares image:/videoUrl: por oferta usando captura de bloco
    blocks = re.findall(
        r'id:\s*"([^"]+)".*?image:\s*"([^"]+)".*?'
        r'(?:videoUrl:\s*"([^"]*)")?',
        txt, re.S,
    )
    if not blocks:
        rec("demo", "nenhum bloco", False, "nao parsei ofertas")
        return
    seen = set()
    for oid, img, vid in blocks:
        if oid in seen:
            continue
        seen.add(oid)
        ok_i, msg_i = check(img, IMG_TYPES)
        rec("demo img", oid, ok_i, f"{msg_i} <- {img[:60]}")
        if vid:
            ok_v, msg_v = check(vid, VID_TYPES)
            rec("demo vid", oid, ok_v, f"{msg_v} <- {vid[:60]}")


# 2) Simulador do backend (build_offer) -------------------------------------
def validate_simulator() -> None:
    from spyfy.scraper_bridge import build_offer

    niches = ["keto", "finance", "beauty"]
    nets = ["meta", "tiktok", "google", "native", "youtube", "pinterest"]
    bad = 0
    for niche in niches:
        for net in nets:
            for i in range(4):
                o = build_offer(niche, net, i)
                oid = o.get("id", f"{niche}_{net}_{i}")
                img = o.get("image") or ""
                fmt = o.get("format")
                vid = o.get("videoUrl") or ""
                ok_i, msg_i = check(img, IMG_TYPES)
                rec("sim img", oid, ok_i, f"{msg_i} <- {img[:50]}")
                if not ok_i:
                    bad += 1
                if fmt == "video":
                    ok_v, msg_v = check(vid, VID_TYPES)
                    rec("sim vid", oid, ok_v, f"{msg_v} <- {vid[:50]}")
                    if not ok_v:
                        bad += 1
    if bad == 0:
        print(f"[OK  ] simulador: todas as midias acessiveis ({len(niches)*len(nets)*4} ofertas)")


# 3) Guards das bibliotecas reais -----------------------------------------
def validate_guards() -> None:
    from spyfy.native_library import NativeAdsLibrary

    # native SEM imagem real -> deve gerar cover (picsum), nunca vazio
    n = NativeAdsLibrary()
    o = n._finalize(
        uid="x1", headline="h", advertiser="a", country="BR", body="b",
        fmt="image", start=None, impr=1000, snapshot="https://x.com/page",
        image="https://x.com/some-ad-page", video="",
    )
    cover = o.get("image") or ""
    ok_c, msg_c = check(cover, IMG_TYPES)
    rec("guard native cover", "native_x1", ok_c, f"{msg_c} <- {cover[:60]}")
    rec("guard native no-video", "native_x1", o.get("videoUrl") == "",
         f"videoUrl='{o.get('videoUrl')}' (esperado vazio)")


def main() -> int:
    print("== Validação de mídia das ofertas ==\n")
    validate_demo()
    print()
    validate_simulator()
    print()
    validate_guards()

    fails = [r for r in results if not r[2]]
    print(f"\nTOTAL checado: {len(results)} | FALHAS: {len(fails)}")
    if fails:
        print("FALHAS:")
        for r in fails:
            print(f"  - [{r[0]}] {r[1]} :: {r[3]}")
        return 1
    print("100% das ofertas com midia real e acessiveL. PRONTO P/ DEPLOY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
