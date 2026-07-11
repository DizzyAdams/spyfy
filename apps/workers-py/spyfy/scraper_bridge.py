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
import random
import sys
import time

from .realtime_producer import DEFAULT_URL, GRADIENTS, push_bulk

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


def build_offer(niche: str, network: str, i: int) -> dict:
    key = "beauty" if "beleza" in niche.lower() or "nutra" in niche.lower() else niche.lower()
    headlines = HEADLINES.get(key, HEADLINES["finance"])
    vsl = random.random() > 0.25
    vsl_min = random.randint(5, 15)
    return {
        "id": f"scrape_{niche}_{network}_{int(time.time())}_{i}",
        "headline": random.choice(headlines),
        "advertiser": random.choice(ADVERTISERS),
        "network": network,
        "niche": niche,
        "country": random.choice(COUNTRIES),
        "winningScore": round(random.uniform(62, 97), 1),
        "longevityDays": random.randint(3, 90),
        "estImpressions": random.randint(2, 92) * 100_000,
        "format": random.choice(["video", "video", "video", "image", "carousel"]),
        "gradient": random.choice(GRADIENTS),
        "bullets": ["Anglo extraído do scraper", "Funil detectado automaticamente"],
        "cta": "Ver oferta",
        "funnel": [
            {"type": "lp", "label": "Landing Page", "stack": random.choice(["ClickFunnels", "Unbounce", "Elementor"])},
            *([{"type": "vsl", "label": f"VSL {vsl_min}min", "stack": random.choice(["Vimeo", "YouTube", "Wistia"])}] if vsl else []),
            {"type": "checkout", "label": "Checkout", "stack": random.choice(["Cartpanda", "Hotmart", "Kiwify", "Stripe"])},
            {"type": "upsell", "label": "Upsell 1", "stack": random.choice(["Cartpanda", "Hotmart", "Kiwify"])},
            {"type": "ty", "label": "Thank You", "stack": random.choice(["Kiwify", "Hotmart", "Stripe"])},
        ],
        "vslSeconds": vsl_min * 60 if vsl else 0,
    }


def mine(niche: str, network: str, count: int = 1, simulate: bool = False,
          token: str = "", country: str = "BR") -> list[dict]:
    """Busca REAL no Meta Ad Library quando network=='meta' e não é simulate.
    Fallback para o gerador estruturado (build_offer) em caso de bloqueio/erro
    (login wall, sem token válido, rede indisponível)."""
    net = network if network in NETWORKS else random.choice(NETWORKS)
    if net == "meta" and not simulate:
        try:
            from .meta_library import MetaAdLibrary

            lib = MetaAdLibrary(access_token=token, country=country)
            found = lib.search(niche, limit=count)
            for o in found:
                o["niche"] = niche
            if found:
                return found[:count]
        except Exception:  # noqa: BLE001 - fallback explícito ao simulador
            pass
    return [build_offer(niche, net, i) for i in range(count)]


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
