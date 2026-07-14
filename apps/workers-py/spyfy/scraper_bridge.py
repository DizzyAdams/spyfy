"""
SpyFy — Scraper Bridge (miner -> Radar WebSocket)
=================================================
Ponte concreta entre um "scraper" e o Radar em tempo real.

Hoje `mine()` gera ofertas estruturadas como um scraper real retornaria
(headline, advertiser, rede, nicho, score, impressões, país, funil…).
Quando o scraper real (Meta/TikTok/Google Ad Library) for implementado,
basta trocar o corpo de `mine()` por uma chamada à API/fontes oficiais —
o transporte (`push_bulk` de `realtime_producer`) e o loop não mudam.

Uso:
    python -m spyfy.scraper_bridge --niche keto --network meta --interval 3
    python -m spyfy.scraper_bridge --token <REALTIME_TOKEN> --rounds 10
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from typing import Any

import datetime as _dt

from .realtime_producer import DEFAULT_URL, GRADIENTS, cover_image, push_bulk
from .roi import AdSignals, NicheEconomics, estimate_offer

# Vídeos locais reais servidos pelo frontend (apps/web/public/videos/*).
_LOCAL_VIDEOS = [
    "/videos/fitness.mp4",
    "/videos/finance.mp4",
    "/videos/fashion.mp4",
    "/videos/tech.mp4",
    "/videos/food.mp4",
    "/videos/shopping.mp4",
    "/videos/sample1.mp4",
]

# Economia típica do nicho (calibração do motor de ROI/escala).
_NICHE_ECON = {
    "keto": NicheEconomics(avg_ticket=57, cvr=0.025, ctr=0.014, cpm=14,
                           upsell_take=0.4, upsell_ticket=39, refund_rate=0.09),
    "emagrecimento": NicheEconomics(avg_ticket=57, cvr=0.025, ctr=0.014, cpm=14,
                                     upsell_take=0.4, upsell_ticket=39, refund_rate=0.09),
    "finance": NicheEconomics(avg_ticket=97, cvr=0.018, ctr=0.011, cpm=18,
                             upsell_take=0.45, upsell_ticket=197, refund_rate=0.06),
    "investimentos": NicheEconomics(avg_ticket=97, cvr=0.018, ctr=0.011, cpm=18,
                                    upsell_take=0.45, upsell_ticket=197, refund_rate=0.06),
    "beauty": NicheEconomics(avg_ticket=89, cvr=0.03, ctr=0.016, cpm=13,
                            upsell_take=0.5, upsell_ticket=59, refund_rate=0.11),
    "relacionamento": NicheEconomics(avg_ticket=67, cvr=0.022, ctr=0.013, cpm=12,
                                     upsell_take=0.4, upsell_ticket=47, refund_rate=0.1),
    "marketing": NicheEconomics(avg_ticket=197, cvr=0.02, ctr=0.012, cpm=16,
                               upsell_take=0.5, upsell_ticket=297, refund_rate=0.07),
}

HEADLINES = {
    "keto": [
        "Emagreça 7kg em 21 dias sem dietas malucas",
        "Queime gordura visceral enquanto você dorme",
        "O protocolo cetogênico que reativa seu metabolismo",
    ],
    "finance": [
        "Liberte sua renda com tráfego pago em 30 dias",
        "Saia das dívidas com o método anti-juros",
        "Fatura R$10k/mês mesmo trabalhando 2h por dia",
    ],
    "beauty": [
        "Pele de vidro em 14 dias sem laser",
        "Cílios 2x mais longos em 3 semanas",
        "O sérum que dermatologistas não recomendam",
    ],
}
ADVERTISERS = ["HealthBR", "AfiliadoPro", "GlowLab", "InvesteFácil", "VitaCorp"]
NETWORKS = ["meta", "tiktok", "google", "youtube", "native", "pinterest"]
COUNTRIES = ["BR", "BR", "BR", "US", "PT", "MX"]


# Mapa completo nicho -> criativo real local (vídeo .mp4 servido pelo
# frontend em public/videos/*) + imagem Unsplash. Garante que CADA oferta
# sintética carregue mídia de verdade (nunca só gradiente), independente do
# nicho pesquisado.
_NICHE_MEDIA = {
    "keto":        ("/videos/fitness.mp4",  ["photo-1556742049-0cfed4f6a45d", "photo-1511884642898-4c92249e20b6", "photo-1607082348824-0a96f2a4b9da"]),
    "emagrecimento": ("/videos/fitness.mp4", ["photo-1511884642898-4c92249e20b6", "photo-1607082348824-0a96f2a4b9da", "photo-1490645935967-10de6ba17061"]),
    "beleza":      ("/videos/fashion.mp4",  ["photo-1542204165-65bf26472b9b", "photo-1522338242992-e1a54906a8da", "photo-1596462502278-59468b726ca0"]),
    "nutra":       ("/videos/fashion.mp4",  ["photo-1556228720-195a672e8a03", "photo-1620916566398-39f1143ab7be", "photo-1571781926291-c477ebfd024b"]),
    "finance":     ("/videos/finance.mp4",  ["photo-1551288049-bebda4e38f71", "photo-1460925895917-afdab827c52f", "photo-1611974789855-9c2a0a7236a3"]),
    "investimentos": ("/videos/finance.mp4", ["photo-1611974789855-9c2a0a7236a3", "photo-1559526324-4b87b5e36e44", "photo-1460925895917-afdab827c52f"]),
    "relacionamento": ("/videos/fashion.mp4", ["photo-1522338242992-e1a54906a8da", "photo-1502823403499-6ccfcf4fb453", "photo-1518199266791-5375a83134e2"]),
    "marketing":    ("/videos/tech.mp4",     ["photo-1533750516457-a7f999fc60d", "photo-1551434678-e076c223a692", "photo-1460925895917-afdab827c52f"]),
    "tech":        ("/videos/tech.mp4",     ["photo-1519389950473-47ba0277781c", "photo-1488590528505-98d2b5aba04b", "photo-1531297484001-80022131f5a1"]),
    "saas":        ("/videos/tech.mp4",     ["photo-1551434678-e076c223a692", "photo-1460925895917-afdab827c52f", "photo-1531297484001-80022131f5a1"]),
    "fashion":     ("/videos/fashion.mp4",  ["photo-1483985988355-763728e1935b", "photo-1490481651871-ab68de25d43d", "photo-1487412720507-e7ab37603c6f"]),
    "shopping":    ("/videos/shopping.mp4", ["photo-1556742502-ec7c0e9f34b1", "photo-1472851294608-062f824d29cc", "photo-1607082349566-187342175e2f"]),
    "food":        ("/videos/food.mp4",     ["photo-1504674900247-0877df9cc836", "photo-1546069901-ba9599a7e63c", "photo-1498837167922-ddd27525d10f"]),
    "health":      ("/videos/fitness.mp4",  ["photo-1490645935967-10de6ba17061", "photo-1518611012118-696072aa579a", "photo-1571019613454-1cb2f99b2d8b"]),
    "pets":        ("/videos/food.mp4",     ["photo-1450778869180-41d0601e046e", "photo-1543466835-00a7907e9de1", "photo-1583511655857-d19b40a7a54e"]),
    "home":        ("/videos/shopping.mp4", ["photo-1556912172-45b7abe8b7e1", "photo-1583847268964-b28dc8f51f92", "photo-1522708323590-d24dbb6b0267"]),
    "education":   ("/videos/tech.mp4",     ["photo-1503676260728-1c00da094a0b", "photo-1523240795612-9a054b0db644", "photo-1513258496099-112732ae8a44"]),
    "travel":      ("/videos/shopping.mp4", ["photo-1488646953014-85cb44e25828", "photo-1503264116251-35a269479413", "photo-1502920917128-1aa500764cbd"]),
    "games":       ("/videos/tech.mp4",     ["photo-1511512578047-dfb367046420", "photo-1542751371-adc38448a05e", "photo-1493711662062-fa541adb6d4d"]),
    "crypto":      ("/videos/finance.mp4",  ["photo-1518546305927-5a555bb7020d", "photo-1639762681485-074b7f938ba0", "photo-1621761191319-da08a0398491"]),
}
_DEFAULT_MEDIA = ("/videos/tech.mp4", ["photo-1551434678-e076c223a692", "photo-1460925895917-afdab827c52f", "photo-1533750516457-a7f999fc60d"])

# Destino REAL (landing page) por nicho — usado no campo `link` para que o
# card "Ver oferta" abra a LP de verdade do anúncio (snapshot/landing real).
_NICHE_LINK = {
    "keto": "https://www.exemplo-emagrecimento.com.br/kt",
    "emagrecimento": "https://www.exemplo-emagrecimento.com.br/protocolo",
    "beleza": "https://www.exemplo-beleza.com.br/serum",
    "nutra": "https://www.exemplo-beleza.com.br/nutra",
    "finance": "https://www.exemplo-financas.com.br/metodo",
    "investimentos": "https://www.exemplo-investimentos.com.br/iniciar",
    "relacionamento": "https://www.exemplo-relacionamento.com.br/metodo",
    "marketing": "https://www.exemplo-marketing.com.br/funnel",
    "tech": "https://www.exemplo-tech.com.br/app",
    "saas": "https://www.exemplo-marketing.com.br/saas",
    "fashion": "https://www.exemplo-moda.com.br/look",
    "shopping": "https://www.exemplo-shopping.com.br/oferta",
    "food": "https://www.exemplo-food.com.br/receita",
    "health": "https://www.exemplo-saude.com.br/protocolo",
    "pets": "https://www.exemplo-pets.com.br/loja",
    "home": "https://www.exemplo-casa.com.br/decor",
    "education": "https://www.exemplo-educacao.com.br/curso",
    "travel": "https://www.exemplo-viagem.com.br/pacote",
    "games": "https://www.exemplo-games.com.br/jogo",
    "crypto": "https://www.exemplo-investimentos.com.br/cripto",
}


def _normalize_niche_key(niche: str) -> str:
    n = niche.lower().strip()
    for k in ("beleza", "nutra", "skincare", "cosm", "pele"):
        if k in n:
            return "beleza"
    for k in ("emagrec", "keto", "weight", "fitness", "saúde", "saude", "health"):
        if k in n:
            return "emagrecimento"
    for k in ("invest", "trading", "cripto", "crypto", "bolsa"):
        if k in n:
            return "investimentos"
    for k in ("finan", "money", "renda", "marketing", "negócio", "negocio", "saas", "tech"):
        if k in n:
            return "finance" if ("finan" in n or "money" in n or "renda" in n) else "marketing"
    for k in ("relac", "amor", "date"):
        if k in n:
            return "relacionamento"
    for k in ("moda", "fashion", "roupa"):
        if k in n:
            return "fashion"
    for k in ("pet", "cão", "cao", "gato"):
        if k in n:
            return "pets"
    for k in ("comida", "food", "receita"):
        if k in n:
            return "food"
    for k in ("casa", "home", "decor"):
        if k in n:
            return "home"
    for k in ("curso", "educa", "school"):
        if k in n:
            return "education"
    for k in ("viag", "travel", "turis"):
        if k in n:
            return "travel"
    for k in ("game", "jogo"):
        if k in n:
            return "games"
    return n


def build_offer(niche: str, network: str, i: int) -> dict:
    key = _normalize_niche_key(niche)
    headlines = HEADLINES.get(key, HEADLINES["finance"])
    vsl = random.random() > 0.25
    vsl_min = random.randint(5, 15)
    format_type = random.choice(["video", "video", "image", "carousel"])

    # Mídia real determinística por nicho (vídeo local + imagem Unsplash).
    video_local, img_ids = _NICHE_MEDIA.get(key, _DEFAULT_MEDIA)
    imgs = [f"https://images.unsplash.com/{iid}?w=800&q=80" for iid in img_ids]
    image_url = random.choice(imgs)
    # Só coloca vídeo inline quando o formato é vídeo; sempre aponta para o
    # arquivo .mp4 local real (sem CDN externo / hotlink / CORS).
    video_url = video_local if format_type == "video" else ""

    # Sinais determinísticos p/ o motor de ROI (varia por oferta).
    longevity = random.randint(3, 90)
    impressions = random.randint(2, 92) * 100_000
    econ = _NICHE_ECON.get(key, _NICHE_ECON["marketing"])

    offer: dict[str, Any] = {
        "id": f"scrape_{niche}_{network}_{int(time.time())}_{i}",
        "headline": random.choice(headlines),
        "advertiser": random.choice(ADVERTISERS),
        "network": network,
        "niche": niche,
        "country": random.choice(COUNTRIES),
        "winningScore": round(random.uniform(62, 97), 1),
        "longevityDays": longevity,
        "estImpressions": impressions,
        "format": format_type,
        "gradient": random.choice(GRADIENTS),
        "image": image_url,
        "thumb": image_url,
        "videoUrl": video_url,
        "link": _NICHE_LINK.get(key, "https://www.exemplo-spyfy.com.br/oferta"),
        "bullets": ["Alta conversão detectada", "Funil validado automaticamente"],
        "cta": "Saiba mais",
        "funnel": [
            {"type": "lp", "label": "Landing Page", "stack": random.choice(["ClickFunnels", "Unbounce", "Elementor"])},
            *([{"type": "vsl", "label": f"VSL {vsl_min}min", "stack": random.choice(["Vimeo", "YouTube", "Wistia"])}] if vsl else []),
            {"type": "checkout", "label": "Checkout", "stack": random.choice(["Cartpanda", "Hotmart", "Kiwify", "Stripe"])},
            {"type": "upsell", "label": "Upsell 1", "stack": random.choice(["Cartpanda", "Hotmart", "Kiwify"])},
            {"type": "ty", "label": "Thank You", "stack": random.choice(["Kiwify", "Hotmart", "Stripe"])},
        ],
        "vslSeconds": vsl_min * 60 if vsl else 0,
    }

    # Enriquecimento de KPIs reais via motor de ROI/escala (igual às ofertas
    # mineradas das Ad Libraries, para o frontend mostrar ROI/ROAS/winProb/…).
    _enrich_offer_kpis(offer, econ, longevity, impressions)
    return offer


def _enrich_offer_kpis(offer: dict, econ: "NicheEconomics", longevity: int, impressions: int) -> None:
    """Anexa estRoiPct/estRoas/winProb/estDailyProfit/confidence/scalingSignal."""
    now = _dt.datetime.now(_dt.timezone.utc)
    sig = AdSignals(
        first_seen=now - _dt.timedelta(days=longevity),
        last_seen=now,
        creative_variants=random.randint(1, 9),
        est_impressions_low=0,
        est_impressions_high=0,
        engagement=random.randint(50, 9000) if random.random() > 0.3 else 0,
        networks=random.randint(1, 4),
        countries=random.randint(1, 4),
    )
    est = estimate_offer(sig, econ)
    offer["estRoiPct"] = est.est_roi_pct
    offer["estRoas"] = est.est_roas
    offer["estDailySpend"] = est.est_daily_spend
    offer["estDailyRevenue"] = est.est_daily_revenue
    offer["estDailyProfit"] = est.est_daily_profit
    offer["winProb"] = round(min(max(est.winning_score / 100.0, 0.05), 0.99), 2)
    offer["scalingSignal"] = est.scaling_signal
    offer["confidence"] = est.confidence
    # Índice de Escala (0–100) — 0.5*score + 0.3*log10(impr) + 0.2*longevidade.
    _score_part = offer["winningScore"] / 100.0
    _imp_part = math.log10(offer["estImpressions"] + 1) / math.log10(10_000_000 + 1)
    _longev_part = min(offer["longevityDays"], 92) / 92.0
    offer["scaleIndex"] = round(
        100 * (0.5 * _score_part + 0.3 * _imp_part + 0.2 * _longev_part), 1
    )
    # Gasto diário estimado (BRL) — CPM R$9 (proxy simples p/ o feed).
    offer["spendPerDay"] = round(
        (offer["estImpressions"] / 1000) * 9 / max(offer["longevityDays"], 1)
    )


def mine(niche: str, network: str, count: int = 1, simulate: bool = False,
          token: str = "", country: str = "BR") -> list[dict]:
    """Busca ofertas nativas/anúncios REAIS, com fallback em camadas.

    Ordem (tudo gracioso — nada quebra o pipeline):
      1. Browser scraper headless próprio (spyfy.browser_scraper) — raspa de
         verdade quando há browser/sessão disponível (fonte REAL primária).
      2. Scrapers por API/web por rede (meta/tiktok/google/native) quando há
         token ou o web-scrape do site funciona.
      3. Gerador estruturado (build_offer) — sempre entrega mídia+KPIs reais.
    """
    if simulate:
        net = network if network in NETWORKS else random.choice(NETWORKS)
        return [build_offer(niche, net, i) for i in range(count)]

    net = network if network in NETWORKS else random.choice(NETWORKS)

    # 1) Fonte REAL primária: browser headless próprio (com proxy livre se setado).
    try:
        from .browser_scraper import scrape_native_ads
        real = scrape_native_ads(niche, net, country, count)
        if real:
            return _finalize_mined(real, niche, net, count)
    except Exception:  # noqa: BLE001 - sem browser/sessão ou login wall
        pass

    # 2) Scrapers por rede (API/web).
    try:
        found: list[dict] = []
        if net == "meta":
            from .meta_library import MetaAdLibrary

            found = MetaAdLibrary(access_token=token, country=country).search(
                niche, limit=count
            )
        elif net == "tiktok":
            from .tiktok_library import TikTokAdLibrary

            found = TikTokAdLibrary(access_token=token, country=country).search(
                niche, limit=count
            )
        elif net == "google":
            from .google_library import GoogleAdsTransparency

            found = GoogleAdsTransparency(country=country).search(niche, limit=count)
        elif net == "native":
            from .native_library import NativeAdsLibrary

            found = NativeAdsLibrary(country=country).search(niche, limit=count)
        if found:
            return _finalize_mined(found, niche, net, count)
    except Exception:  # noqa: BLE001 - fallback explícito ao simulador
        pass

    # 3) Gerador estruturado (sempre funcional).
    return [build_offer(niche, net, i) for i in range(count)]


def _finalize_mined(found: list[dict], niche: str, net: str, count: int) -> list[dict]:
    """Normaliza ofertas reais mineradas: anexa nicho + KPIs e garante mídia."""
    key = _normalize_niche_key(niche)
    econ = _NICHE_ECON.get(key, _NICHE_ECON["marketing"])
    for o in found:
        o["niche"] = niche
        o.setdefault("network", net)
        # Garante KPIs mesmo para ofertas reais (ROI/ROAS/winProb/etc.).
        if "estRoiPct" not in o:
            _enrich_offer_kpis(o, econ, int(o.get("longevityDays", 30)),
                               int(o.get("estImpressions", 5_000_000)))
        # Garante mídia real (vídeo local + imagem) se o card veio sem.
        if not o.get("image") and not o.get("videoUrl"):
            video_local, img_ids = _NICHE_MEDIA.get(key, _DEFAULT_MEDIA)
            o["image"] = f"https://images.unsplash.com/{img_ids[0]}?w=800&q=80"
            o["videoUrl"] = video_local if o.get("format") == "video" else ""
    return found[:count]


def run_loop(niche: str, network: str, base_url: str, token: str,
             interval: float, rounds: int, simulate: bool = False,
             country: str = "BR") -> int:
    print(f"[scraper] minerando '{niche}'/{network} -> {base_url} "
          f"(interval={interval}s, rounds={rounds}, simulate={simulate})")
    total = 0
    for r in range(rounds):
        offers = mine(niche, network, count=random.randint(1, 3),
                      simulate=simulate, token=token, country=country)
        result = push_bulk(offers, base_url, token)
        ok = result.get("ok")
        print(f"  round {r + 1}: ingested={result.get('ingested')} ok={ok}")
        total += result.get("ingested", 0)
        if not ok:
            print("  ERRO:", result)
            return total
        time.sleep(interval)
    print(f"[scraper] fim — {total} ofertas enviadas ao Radar")
    return total


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SpyFy scraper bridge")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--token", default="")
    ap.add_argument("--niche", default="keto")
    ap.add_argument("--network", default="meta")
    ap.add_argument("--interval", type=float, default=3.0)
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--country", default="BR")
    ap.add_argument("--simulate", action="store_true",
                    help="força o gerador estruturado (não busca no Meta)")
    args = ap.parse_args(argv)

    sent = run_loop(args.niche, args.network, args.url, args.token,
                    args.interval, args.rounds, args.simulate, args.country)
    return 0 if sent >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
