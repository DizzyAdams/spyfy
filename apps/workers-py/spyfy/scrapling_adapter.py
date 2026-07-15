"""
SpyFy — Scrapling adapter (REAL fetch layer)
============================================
O Scrapling (https://github.com/D4Vinci/Scrapling) é um framework de web
scraping adaptativo que contorna anti-bot (Cloudflare Turnstile, login walls
do Facebook/TikTok/Google) OUT OF THE BOX via ``StealthyFetcher`` (Playwright
patchado + browserforge + curl_cffi).

Este módulo é a ÚNICA ponte entre o Scrapling e as ``*_library.py`` do SpyFy.
Ele expõe um ``ScraplingClient`` compatível com a interface mínima do
``httpx.Client`` que as bibliotecas de Ad Library esperam
(``.get(url, params=..., headers=...)`` -> objeto com ``.status_code`` /
``.text``), para que os parsers existentes (JSON embutido + regex, já testados)
continuem idênticos — só a camada de TRANSPORTE muda de httpx para Scrapling.

Sem Scrapling instalado (ex.: deploy sem a dep), o client degrada para
``httpx.Client`` graciosamente (``SCRAPLING_AVAILABLE = False``), preservando
o comportamento anterior. Nada quebra.

Uso:
    from .scrapling_adapter import ScraplingClient, SCRAPLING_AVAILABLE
    client = ScraplingClient(country="BR", timeout=20)
    resp = client.get("https://www.facebook.com/ads/library/?q=keto")
    if resp.status_code == 200:
        html = resp.text
"""

from __future__ import annotations

import os
import urllib.parse
from typing import Any

# ---- Scrapling availability ----------------------------------------------
try:
    from scrapling.fetchers import StealthyFetcher  # type: ignore
    from scrapling.parser import Selector  # type: ignore

    SCRAPLING_AVAILABLE = True
except Exception:  # noqa: BLE001 - Scrapling (ou uma de suas deps) ausente
    SCRAPLING_AVAILABLE = False
    StealthyFetcher = None  # type: ignore
    Selector = None  # type: ignore

import httpx  # fallback de transporte (sempre presente)

# Configuração global do fetcher stealth (anti-bot). Definida uma vez.
if SCRAPLING_AVAILABLE:
    try:
        StealthyFetcher.adaptive = True  # parser aprende mudanças no site
    except Exception:  # noqa: BLE001
        pass


class _ScraplingResponse:
    """Mini-resposta estilo httpx (status_code + text) devolvida pelo
    ``ScraplingClient.get``."""

    __slots__ = ("status_code", "text", "url", "_error")

    def __init__(self, status_code: int, text: str = "", url: str = "",
                 error: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.url = url
        self._error = error

    @property
    def ok(self) -> bool:
        return self.status_code == 200

    def json(self):  # pragma: no cover - não usado pelas libs
        import json

        return json.loads(self.text)

    def raise_for_status(self):  # pragma: no cover
        if not self.ok:
            raise httpx.HTTPError(f"Scrapling fetch falhou: {self.status_code}")


class ScraplingClient:
    """Cliente de fetch REAL via Scrapling ``StealthyFetcher``.

    Interface mínima compatível com ``httpx.Client`` usada pelas
    ``*_library.py``: ``get(url, params=None, headers=None)``.

    Parâmetros aceitos pelas libs (``params``, ``headers``, ``proxy``) são
    respeitados quando aplicável; o Scrapling cuida dos headers/UA/fingerprint
    internamente, então ``headers`` é ignorado (o fetcher já é stealth).
    """

    def __init__(
        self,
        *,
        country: str = "BR",
        timeout: float = 25.0,
        proxy: str | None = None,
        headless: bool = True,
    ) -> None:
        self.country = country
        self.timeout = timeout
        self.proxy = proxy or os.getenv("SCRAPE_PROXY") or os.getenv("FREE_PROXY")
        self.headless = headless

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> _ScraplingResponse:
        """Busca ``url`` (com ``params`` opcionais) via Scrapling.

        Em caso de erro de rede/anti-bot, devolve ``status_code=000`` com
        ``.text=''`` para que o caller faça fallback (igual ao comportamento
        anterior com httpx + except).
        """
        full_url = url
        if params:
            sep = "&" if "?" in full_url else "?"
            full_url = f"{full_url}{sep}{urllib.parse.urlencode(params)}"

        if not SCRAPLING_AVAILABLE:
            # Fallback: httpx puro (sem stealth) — preserva comportamento antigo.
            try:
                resp = httpx.get(
                    full_url,
                    headers=headers or {"User-Agent": "Mozilla/5.0"},
                    timeout=timeout or self.timeout,
                    follow_redirects=True,
                )
                return _ScraplingResponse(resp.status_code, resp.text, full_url)
            except Exception as exc:  # noqa: BLE001
                return _ScraplingResponse(000, "", full_url, error=repr(exc))

        # IMPORTANTE: o StealthyFetcher repassa o `proxy` ao
        # `browser.launch_persistent_context`, que exige objeto ou None —
        # uma string vazia ("") quebra o lançamento do browser
        # ("expected object, got string"). Só passamos proxy quando há um
        # valor real; caso contrário, omitimos o kwarg (equivale a None).
        fetch_kwargs = dict(
            headless=self.headless,
            timeout=int((timeout or self.timeout) * 1000),
        )
        if self.proxy:
            fetch_kwargs["proxy"] = self.proxy
        try:
            page = StealthyFetcher.fetch(full_url, **fetch_kwargs)
            html = page.body if isinstance(page.body, str) else str(page.body)
            return _ScraplingResponse(200, html or "", full_url)
        except Exception as exc:  # noqa: BLE001 - anti-bot / timeout / bloqueio
            return _ScraplingResponse(000, "", full_url, error=repr(exc))

    # Alias para API estilo context manager (as libs não usam, mas evita surpresas).
    def __enter__(self) -> "ScraplingClient":
        return self

    def __exit__(self, *exc) -> None:
        return None


def fetch_html(url: str, *, timeout: float = 25.0, proxy: str | None = None) -> str:
    """Helper: retorna o HTML de ``url`` via Scrapling (string vazia se falhar)."""
    client = ScraplingClient(timeout=timeout, proxy=proxy)
    resp = client.get(url)
    return resp.text if resp.status_code == 200 else ""


__all__ = [
    "ScraplingClient",
    "fetch_html",
    "SCRAPLING_AVAILABLE",
    "_ScraplingResponse",
]
