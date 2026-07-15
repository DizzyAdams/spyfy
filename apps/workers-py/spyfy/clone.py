"""
SpyFy — Offer/Landing-Page Cloner (A11 do time de 14 agents)
============================================================
Motor de clonagem de LP/funil 100% offline-safe e leve (apenas
``httpx`` + stdlib ``html.parser`` — sem Playwright/bs4, p/ free tier).
Dado uma URL (ou um ``offer`` simulado), ele:
  1. faz fetch da LP (graceful fallback se a rede falhar),
  2. extrai copy (headline, sub, bullets, CTA, seções, imagens),
  3. detecta o stack (checkout/pixels/VSL host),
  4. mapeia o funil (lp -> vsl -> checkout -> upsell -> thank-you),
  5. monta um *clone bundle* estruturado + um HTML reconstruído.
Espelha docs/14-mining/team-14-agents.md (A11) e docs/03-features/offer-cloner.md.
"""
from __future__ import annotations

import hashlib
import html
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin

import httpx

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Assinaturas de plataforma presentes no HTML (checkout / pixels / VSL host).
STACK_SIGS: dict[str, list[str]] = {
    "Hotmart": ["hotmart.com", "hotmart"],
    "Kiwify": ["kiwify.com", "kiwify"],
    "Cartpanda": ["cartpanda.com", "cartpanda"],
    "Stripe": ["stripe.com", "stripe"],
    "Eduzz": ["eduzz.com", "eduzz"],
    "Monetizze": ["monetizze.com.br", "monetizze"],
    "PerfectPay": ["perfectpay.com.br", "perfectpay"],
    "Yampi": ["yampi.com.br", "yampi"],
    "Vindi": ["vindi.com.br", "vindi"],
    "Meta Pixel": ["connect.facebook.net", "fbq("],
    "TikTok Pixel": ["analytics.tiktok.com", "ttq("],
    "Google Tag Manager": ["googletagmanager.com"],
    "Google Analytics": ["google-analytics.com", "gtag("],
    "ActiveCampaign": ["activecampaign.com"],
    "RD Station": ["rdstation.com", "rdstationjs"],
    "Mailchimp": ["mailchimp.com", "mailchimp"],
    "Vimeo": ["vimeo.com", "player.vimeo"],
    "YouTube": ["youtube.com", "youtu.be"],
    "Wistia": ["wistia.com", "wistia"],
}

# Palavras-chave de URL -> etapa de funil.
_FUNNEL_KW: dict[str, str] = {
    "checkout": "Checkout",
    "pagamento": "Checkout",
    "obrigado": "Thank You",
    "thank": "Thank You",
    "upsell": "Upsell",
    "order": "Order",
    "vsl": "VSL",
    "video": "VSL",
    "lead": "Lead",
    "inscricao": "Lead",
    "confirmacao": "Thank You",
}


class _PageExtractor(HTMLParser):
    """Coleta titulo, headings, paragrafos, bullets, CTAs, imagens e links."""

    _VOID_SKIP = {"script", "style", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1: list[str] = []
        self.h2: list[str] = []
        self.paras: list[str] = []
        self.bullets: list[str] = []
        self.ctas: list[dict[str, str]] = []
        self.images: list[str] = []
        self.links: list[dict[str, str]] = []
        self._buf: list[str] = []
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
            self._buf = []
        elif tag in self._VOID_SKIP:
            self._skip += 1
        elif tag in ("h1", "h2", "p", "li", "button"):
            self._buf = []
        elif tag == "img":
            src = d.get("src") or d.get("data-src") or ""
            if not src and d.get("srcset"):
                src = d["srcset"].split()[0]
            if src:
                self.images.append(src)
        elif tag == "a":
            href = d.get("href", "")
            if href:
                self.links.append({"href": href, "text": d.get("title", "")})
            cls = (d.get("class", "") or "").lower()
            if any(k in cls for k in ("btn", "cta", "button", "comprar", "buy")):
                self.ctas.append({"href": href, "text": d.get("title", "") or "(botao)"})

    def handle_endtag(self, tag: str) -> None:
        if tag in self._VOID_SKIP and self._skip > 0:
            self._skip -= 1
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = " ".join(self._buf).strip()
            self._buf = []
        elif tag == "h1":
            self._flush(self.h1)
        elif tag == "h2":
            self._flush(self.h2)
        elif tag == "p":
            self._flush(self.paras)
        elif tag == "li":
            self._flush(self.bullets)
        elif tag == "button":
            self._flush(self.ctas, as_text=True)

    def handle_data(self, data: str) -> None:
        if self._skip > 0:
            return
        self._buf.append(data)

    def _flush(self, target: list[Any], as_text: bool = False) -> None:
        text = " ".join(self._buf).strip()
        self._buf = []
        if not text:
            return
        if as_text:
            target.append({"href": "", "text": text})
        else:
            target.append(text)


def _fetch(url: str, timeout: float = 12) -> str:
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_HEADERS) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.text


def detect_stack(page_html: str) -> list[str]:
    low = page_html.lower()
    found: list[str] = []
    for name, sigs in STACK_SIGS.items():
        if any(s.lower() in low for s in sigs):
            found.append(name)
    return found


def detect_funnel(links: list[dict[str, str]]) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    seen: set[str] = set()
    for link in links:
        u = (link.get("href") or "").lower()
        for kw, label in _FUNNEL_KW.items():
            if kw in u and label not in seen:
                seen.add(label)
                steps.append(
                    {"type": label.lower().replace(" ", "_"), "label": label, "url": link.get("href", "")}
                )
    if not any(s["label"] == "Checkout" for s in steps):
        steps.append({"type": "checkout", "label": "Checkout", "url": ""})
    if not steps or steps[0]["label"] != "Landing Page":
        steps.insert(0, {"type": "lp", "label": "Landing Page", "url": ""})
    return steps


def _extract(page_html: str, base_url: str) -> dict[str, Any]:
    ex = _PageExtractor()
    ex.feed(page_html)
    for link in ex.links:
        if link.get("href"):
            link["href"] = urljoin(base_url, link["href"])
    for i, src in enumerate(ex.images):
        ex.images[i] = urljoin(base_url, src)
    return {
        "title": ex.title,
        "h1": [h for h in ex.h1 if h][:5],
        "h2": [h for h in ex.h2 if h][:8],
        "paras": [p for p in ex.paras if len(p) > 12][:10],
        "bullets": [b for b in ex.bullets if b][:15],
        "ctas": ex.ctas[:10],
        "images": ex.images[:24],
        "links": ex.links,
    }



def _clone_id(seed: str) -> str:
    return "cl_" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]


def _build_html(bundle: dict[str, Any]) -> str:
    """Monta um HTML standalone reconstruindo o funil a partir do copy extraido."""
    title = html.escape(bundle.get("headline") or bundle.get("title") or "Oferta clonada")
    sub = html.escape(bundle.get("subheadline") or "")
    bullets = "".join(f"<li>{html.escape(b)}</li>" for b in bundle.get("bullets", [])[:12])
    steps = "".join(
        f'<li><b>{html.escape(s["label"])}</b>'
        f'{(" — " + html.escape(s["url"])) if s.get("url") else ""}</li>'
        for s in bundle.get("funnel", [])
    )
    stack = "".join(f"<span class=\"tag\">{html.escape(s)}</span>" for s in bundle.get("detected_stack", [])) or "<i>nao detectado</i>"
    cta = html.escape((bundle.get("ctas") or [{}])[0].get("text", "Quero saber mais"))
    # CTA do clone aponta para a LP/oferta REAL (bundle["url"]) em vez de "#".
    # Assim o clone exportado leva o usuário para o anúncio de verdade.
    cta_href = html.escape(bundle.get("url") or "#")
    imgs = "".join(
        f'<img src="{html.escape(i)}" alt="criativo" style="max-width:100%;border-radius:12px;margin:8px 0"/>'
        for i in bundle.get("images", [])[:6]
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<style>
 body{{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:0;background:#0b0b12;color:#eaeaf2}}
 .wrap{{max-width:720px;margin:0 auto;padding:32px 20px}}
 h1{{font-size:34px;line-height:1.15;margin:0 0 8px}}
 .sub{{color:#b9b9c9;font-size:18px;margin:0 0 20px}}
 ul{{padding-left:20px}} li{{margin:6px 0}}
 .cta{{display:inline-block;margin-top:18px;padding:14px 26px;background:#7c5cff;color:#fff;
   border-radius:10px;font-weight:700;text-decoration:none}}
 .tag{{display:inline-block;background:#1b1b2b;color:#9aa;padding:4px 10px;border-radius:999px;font-size:12px;margin:3px}}
 .card{{background:#12121c;border:1px solid #23233a;border-radius:16px;padding:20px;margin:18px 0}}
 .note{{color:#8a8aa0;font-size:13px}}
</style></head>
<body><div class="wrap">
 <h1>{title}</h1>
 <p class="sub">{sub}</p>
 <div class="card"><h3>Copy extraida (engenharia reversa)</h3><ul>{bullets}</ul></div>
 {imgs}
 <div class="card"><h3>Funil mapeado</h3><ul>{steps}</ul></div>
 <div class="card"><h3>Stack detectado</h3><div>{stack}</div></div>
 <a class="cta" href="{cta_href}" target="_blank" rel="noopener">{cta}</a>
 <p class="note">Clone gerado pelo SpyFy (estudo/referencia). ID: {html.escape(bundle.get('clone_id',''))}</p>
</div></body></html>"""


def _fallback_clone(
    offer: dict[str, Any] | None, niche: str | None, clone_id: str, url: str | None = None
) -> dict[str, Any]:
    o = offer or {}
    headline = o.get("headline") or "Oferta em alta no seu nicho"
    bullets = o.get("bullets") or ["Angulo comprovado de escala", "Funil detectado automaticamente"]
    funnel = [
        {"type": f.get("type"), "label": f.get("label", f.get("type")), "url": ""}
        for f in o.get("funnel", [])
    ] or [
        {"type": "lp", "label": "Landing Page", "url": ""},
        {"type": "checkout", "label": "Checkout", "url": ""},
    ]
    stack = [f.get("stack") for f in o.get("funnel", []) if f.get("stack")]
    bundle = {
        "clone_id": clone_id,
        "source": "template",
        "reason": "sem URL ou fetch falhou — bundle reconstruido a partir do offer",
        "title": headline,
        "headline": headline,
        "subheadline": o.get("advertiser") or niche or "Oferta detectada pelo SpyFy",
        "bullets": bullets,
        "ctas": [{"href": "", "text": o.get("cta") or "Ver oferta"}],
        "images": [],
        "funnel": funnel,
        "detected_stack": list(dict.fromkeys(stack)),
        "offer_id": o.get("id"),
        "niche": o.get("niche") or niche,
        "network": o.get("network"),
        "url": url,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    bundle["html"] = _build_html(bundle)
    return bundle


def clone_offer(
    url: str | None = None,
    offer: dict[str, Any] | None = None,
    niche: str | None = None,
    country: str = "BR",
    timeout: float = 12,
) -> dict[str, Any]:
    """Clona uma LP/oferta.

    Se ``url`` for informada, faz fetch real (com fallback gracioso).
    Caso contrario (ou em falha), reconstrói a partir do ``offer``.
    """
    seed = url or (offer or {}).get("id") or (niche or "offer")
    clone_id = _clone_id(seed)
    if url:
        try:
            page = _fetch(url, timeout)
            ex = _extract(page, url)
            bundle = {
                "clone_id": clone_id,
                "source": "live",
                "url": url,
                "title": ex["title"],
                "headline": ex["h1"][0] if ex["h1"] else (ex["title"] or "Oferta clonada"),
                "subheadline": ex["h2"][0] if ex["h2"] else (ex["paras"][0] if ex["paras"] else ""),
                "bullets": ex["bullets"] or ex["paras"][:6],
                "ctas": ex["ctas"] or [{"href": "", "text": "Ver oferta"}],
                "images": ex["images"],
                "funnel": detect_funnel(ex["links"]),
                "detected_stack": detect_stack(page),
                "offer_id": (offer or {}).get("id"),
                "niche": (offer or {}).get("niche") or niche,
                "network": (offer or {}).get("network"),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            bundle["html"] = _build_html(bundle)
            return bundle
        except Exception as e:  # noqa: BLE001 - fallback explicito
            fb = _fallback_clone(offer, niche, clone_id, url=url)
            fb["reason"] = f"fetch falhou ({type(e).__name__}) — fallback p/ template"
            return fb
    return _fallback_clone(offer, niche, clone_id, url=url)


__all__ = ["clone_offer", "detect_stack", "detect_funnel"]

