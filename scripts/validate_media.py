"""
Validacao automatica de midia das ofertas (SpyFy).

Para CADA oferta (demo do frontend, simulador do backend, scrapers reais
e guards das bibliotecas) confere se `image` / `videoUrl` apontam para uma
URL de midia REAL e acessivel (HTTP < 400 + content-type correto, ou
arquivo local existente em apps/web/public).

Falha (exit 1) se alguma oferta ficar sem imagem valida ou se uma oferta
cujo formato e' video ficar sem videoUrl valido.

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
                if fmt == "video":
                    ok_v, msg_v = check(vid, VID_TYPES)
                    rec("sim vid", oid, ok_v, f"{msg_v} <- {vid[:50]}")


# 3) Scrapers REAIS (mine simulate=False) — ofertas de verdade ----------
def validate_real_scrapers() -> None:
    from spyfy.scraper_bridge import mine

    nets = ["meta", "tiktok", "google", "native"]
    for net in nets:
        try:
            offers = mine("keto", net, count=4, simulate=False)
        except Exception as exc:  # noqa: BLE001
            rec("real", f"{net} (erro)", False, f"mine levantou: {exc}")
            continue
        if not offers:
            rec("real", f"{net} (vazio)", False, "nenhuma oferta real")
            continue
        for o in offers:
            oid = o.get("id", net)
            img = o.get("image") or ""
            fmt = o.get("format")
            vid = o.get("videoUrl") or ""
            ok_i, msg_i = check(img, IMG_TYPES)
            rec(f"real img {net}", oid, ok_i, f"{msg_i} <- {img[:40]}")
            if fmt == "video":
                ok_v, msg_v = check(vid, VID_TYPES)
                rec(f"real vid {net}", oid, ok_v, f"{msg_v} <- {vid[:40]}")
            else:
                # mesmo sem ser video, nao pode ficar quebrado
                rec(f"real fmt {net}", oid, ok_i, f"formato={fmt}")


# 4) Guards das bibliotecas reais -----------------------------------------
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

    # native FORMATO VIDEO -> deve vir com videoUrl local valido (fix)
    o2 = n._finalize(
        uid="x2", headline="h", advertiser="a", country="BR", body="b",
        fmt="video", start=None, impr=1000, snapshot="https://x.com/page",
        image="", video="",
    )
    vid2 = o2.get("videoUrl") or ""
    ok_v, msg_v = check(vid2, VID_TYPES)
    rec("guard native video", "native_x2", ok_v, f"{msg_v} <- {vid2[:40]}")


def main() -> int:
    print("== Validação de mídia das ofertas ==\n")
    validate_demo()
    print()
    validate_simulator()
    print()
    validate_real_scrapers()
    print()
    validate_guards()

    fails = [r for r in results if not r[2]]
    print(f"\nTOTAL checado: {len(results)} | FALHAS: {len(fails)}")
    if fails:
        print("FALHAS:")
        for r in fails:
            print(f"  - [{r[0]}] {r[1]} :: {r[3]}")
        return 1
    print("100% das ofertas com midia real e acessivel. PRONTO P/ DEPLOY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
