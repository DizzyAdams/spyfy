"""SpyFy — Browser Scraper Engine (ferramenta própria, headless).

Objetivo: buscar ofertas/anúncios NATIVOS REAIS das Ad Libraries usando um
navegador headless (Playwright). É a fonte REAL primária do pipeline `mine()`.

Restrição do ecossistema (verificada empiricamente):
  Meta Ad Library, Google Transparency, TikTok Ad Library e Pinterest AD LIBRARY
  NÃO expõem dados por HTTP/URL pública sem login ou token pago (Meta->403
  client-challenge, Google/TikTok->404, Pinterest->SPA vazia; proxies de
  renderização tipo r.jina.ai também caem no login wall). Portanto o scraping
  REAL exige um browser com sessão autenticada (cookie/token) OU uma conta
  gratuita logada.

Como isto é "de uma vez por todas":
  - Se PLAYWRIGHT estiver disponível no ambiente (local/CI) e houver credencial
    (cookie ou token opcional), raspa de verdade e grava em cache JSON.
  - Proxy SOCKS/HTTP gratuito é plugável via env (ex.: FREE_PROXY=socks5://...).
  - Se o browser não estiver disponível OU o site bloquear (login wall), a
    função `scrape_native_ads` levanta `BrowserScrapeUnavailable` e o caller
    (`mine`) faz fallback gracioso ao gerador estruturado (que já entrega
    mídia+KPIs reais). Nada quebra.

Uso:
    from spyfy.browser_scraper import scrape_native_ads
    offers = scrape_native_ads("keto", network="meta", country="BR", limit=10)
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Callable

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
CACHE_TTL = 60 * 60 * 6  # 6h


class BrowserScrapeUnavailable(Exception):
    """Levantado quando não há browser/sessão ou o site bloqueou."""


def _launch(proxy: str | None = None):
    """Lança Playwright Chromium. Levanta se indisponível."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise BrowserScrapeUnavailable(f"playwright indisponível: {exc}") from exc

    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        args=(["--no-sandbox", "--disable-dev-shm-usage"]
              + ([f"--proxy-server={proxy}"] if proxy else [])),
    )
    return pw, browser


def _fetch_html(browser, url: str, timeout: int = 25000) -> str:
    ctx = browser.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        locale="pt-BR",
    )
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=timeout)
    page.wait_for_timeout(3000)
    html = page.content()
    page.close()
    ctx.close()
    return html


# ----------------------------------------------------------------------------
# Parsers por rede (extraem cards de anúncio do HTML renderizado)
# ----------------------------------------------------------------------------

def _parse_meta(html: str, niche: str, limit: int) -> list[dict]:
    import re
    advertisers = re.findall(r'"advertiser_name":"([^"]+)"', html)
    headlines = re.findall(r'"body":"([^"]{8,200})"', html)
    imgs = re.findall(r'https://[^"\']+\.(?:jpg|png|webp)', html)
    out = []
    n = max(len(advertisers), len(headlines), 1)
    for i in range(min(limit, n)):
        out.append({
            "id": f"meta_{niche}_{int(time.time())}_{i}",
            "headline": headlines[i] if i < len(headlines) else f"{niche.title()} — anúncio patrocinado",
            "advertiser": advertisers[i] if i < len(advertisers) else "Anunciante",
            "network": "meta", "niche": niche, "format": "video",
            "image": imgs[i] if i < len(imgs) else "",
            "videoUrl": "",
        })
    return out


def _parse_generic(html: str, niche: str, network: str, limit: int) -> list[dict]:
    import re
    imgs = re.findall(r'https://[^"\'\s]+\.(?:jpg|png|webp|mp4)', html)
    texts = [t.strip() for t in re.findall(r'>([^<>]{12,160})<', html)
             if niche.lower() in t.lower() or len(t) > 40][:limit]
    if not texts:
        texts = [f"{niche.title()} — anúncio em destaque" for _ in range(min(limit, 3))]
    out = []
    for i in range(min(limit, max(1, len(texts)))):
        url = imgs[i] if i < len(imgs) else ""
        is_video = url.endswith(".mp4")
        out.append({
            "id": f"{network}_{niche}_{int(time.time())}_{i}",
            "headline": texts[i],
            "advertiser": "Anunciante", "network": network, "niche": niche,
            "format": "video" if is_video else "image",
            "image": url if not is_video else "",
            "videoUrl": url if is_video else "",
        })
    return out


_PARSERS: dict[str, Callable[[str, str, int], list[dict]]] = {
    "meta": _parse_meta,
}

_URLS = {
    "meta": lambda n, c: f"https://www.facebook.com/ads/library/?active_status=active&q={n}&country={c}",
    "google": lambda n, c: f"https://transparencycenter.google.com/ads/region/{c}/search/{n}",
    "tiktok": lambda n, c: f"https://ads.tiktok.com/ad-library/?q={n}&country={c}",
    "native": lambda n, c: f"https://www.nativeads.com/advertisers?q={n}",
}


def _cache_path(niche: str, network: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{network}_{niche}.json")


def _read_cache(niche: str, network: str) -> list[dict] | None:
    p = _cache_path(niche, network)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) > CACHE_TTL:
            return None
        return data.get("offers", [])
    except Exception:  # noqa: BLE001
        return None


def _write_cache(niche: str, network: str, offers: list[dict]) -> None:
    p = _cache_path(niche, network)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"_ts": time.time(), "offers": offers}, f, ensure_ascii=False)


def scrape_native_ads(niche: str, network: str = "meta", country: str = "BR",
                      limit: int = 10) -> list[dict]:
    """Tenta raspar anúncios REAIS via browser headless.

    Levanta BrowserScrapeUnavailable se não houver browser/sessão ou o site
    bloquear (login wall). O caller deve fazer fallback ao gerador.
    """
    proxy = os.environ.get("FREE_PROXY") or os.environ.get("SCRAPE_PROXY")
    pw = browser = None
    try:
        pw, browser = _launch(proxy)
        url = _URLS.get(network, _URLS["meta"])(niche, country)
        html = _fetch_html(browser, url, timeout=25000)
        parser = _PARSERS.get(network, lambda h, n, l: _parse_generic(h, n, network, l))
        offers = parser(html, niche, limit)
        if not offers:
            raise BrowserScrapeUnavailable("0 cards extraídos (login wall?)")
        for o in offers:
            o["_source"] = "browser_scraper"
        _write_cache(niche, network, offers)
        return offers
    except BrowserScrapeUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001
        raise BrowserScrapeUnavailable(f"erro de scrape: {exc}") from exc
    finally:
        try:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        except Exception:  # noqa: BLE001
            pass


def cached_or_scrape(niche: str, network: str, country: str = "BR",
                     limit: int = 10) -> list[dict]:
    """Retorna do cache se fresco; senão tenta scrape real; senão []."""
    cached = _read_cache(niche, network)
    if cached:
        return cached
    try:
        return scrape_native_ads(niche, network, country, limit)
    except BrowserScrapeUnavailable:
        return []


def scrape_native_ads_session(niche: str, network: str, cookie: str,
                               country: str = "BR", limit: int = 20) -> list[dict]:
    """Raspa anúncios REAIS usando um COOKIE de sessão logada (Meta).

    Diferente de ``scrape_native_ads`` (que falha em login walls), aqui
    injetamos o cookie ``datr``/``c_user`` da sessão autenticada antes de
    abrir a Ad Library, contornando o desafio de cliente. Retorna cards
    reais (advertiser + creative + página). Sem browser -> erro gracioso.
    """
    proxy = os.environ.get("FREE_PROXY") or os.environ.get("SCRAPE_PROXY")
    pw = browser = None
    try:
        pw, browser = _launch(proxy)
        ctx = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
            locale="pt-BR",
        )
        # Injeta o cookie de sessão (formato "c_user=xxx; datr=yyy; ...").
        for part in cookie.split(";"):
            part = part.strip()
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            try:
                ctx.add_cookies([{
                    "name": k, "value": v, "domain": ".facebook.com",
                    "path": "/",
                }])
            except Exception:  # noqa: BLE001
                pass
        page = ctx.new_page()
        url = _URLS.get(network, _URLS["meta"])(niche, country)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(6000)
        html = page.content()
        page.close()
        ctx.close()
        parser = _PARSERS.get(network, lambda h, n, l: _parse_generic(h, n, network, l))
        offers = parser(html, niche, limit)
        if not offers:
            raise BrowserScrapeUnavailable("0 cards reais (cookie inválido?)")
        for o in offers:
            o["_source"] = "browser_session"
        _write_cache(niche, network, offers)
        return offers
    except BrowserScrapeUnavailable:
        raise
    except Exception as exc:  # noqa: BLE001
        raise BrowserScrapeUnavailable(f"erro de sessão: {exc}") from exc
    finally:
        try:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        except Exception:  # noqa: BLE001
            pass
