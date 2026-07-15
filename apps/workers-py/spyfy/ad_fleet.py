"""SpyFy — Real Native Ads Fleet (mini-bots de extração contínua)
===============================================================

Implementa a ideia dos "mini-bots que ficam sempre online fazendo vários
fetch em tempo real" para abastecer a loja de anúncios nativos REAIS
(``real_ads_store``), que é a fonte primária do feed (``discover_offers``
com ``simulate=false``).

Cada "bot" é um par ``(nicho, rede)``. A frota varre essa grade de forma
alternada, chamando ``spyfy.scraper_bridge.mine(simulate=False)`` — que já
faz o fallback em camadas (TikTok Creative Center público -> sessão logada
-> bibliotecas oficiais -> gerador estruturado) — e grava o que vier na
loja real. Como tudo é gracioso (nada quebra o pipeline), a frota continua
rodando mesmo se uma rede cair.

Dois modos de execução (serverless-safe + sempre-online):
  * Servidor (Vercel Cron): ``collect_once()`` roda UMA rodada curta e
    devolve quantos anúncios reais entraram — invocado por
    ``GET /v1/cron/collect-ads`` a cada N minutos.
  * Daemon local: ``run_daemon()`` roda em loop infinito (host de longa
    duração) disparando a frota em intervalos, com janela de timeout por
    rodada para caber no limite do serverless se reusado.

Uso:
    python -m spyfy.ad_fleet --rounds 10 --interval 60
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from typing import Any

# Grade de mini-bots: (nicho, rede). Redes oficiais que permitem extração
# nativa (pública ou via sessão) têm prioridade; as demais entram no
# fallback estruturado para manter o feed sempre vivo.
FLEET = [
    ("keto", "tiktok"),
    ("emagrecimento", "tiktok"),
    ("finance", "tiktok"),
    ("beauty", "tiktok"),
    ("keto", "meta"),
    ("finance", "meta"),
    ("beauty", "meta"),
    ("finance", "google"),
    ("keto", "google"),
    ("finance", "native"),
    ("emagrecimento", "native"),
    ("beauty", "pinterest"),
]


def _mine(niche: str, network: str, count: int = 3, country: str = "BR") -> list[dict]:
    """Chama o scraper real (simulate=False) e devolve o que vier."""
    from .scraper_bridge import mine

    return mine(niche, network, count=count, simulate=False, country=country)


def collect_once(
    tasks: list[tuple[str, str]] | None = None,
    *,
    count: int = 3,
    country: str = "BR",
) -> dict[str, Any]:
    """Roda UMA rodada da frota. Retorna resumo da ingestão real.

    Serverless-safe: sem loop infinito, sem bloquear. O Vercel Cron chama
    isso a cada N minutos para manter a loja de anúncios reais sempre
    atualizada (substituto dos "mini-bots sempre online").

    Cada bot reporta quantos anúncios vieram de fonte NATIVA REAL
    (source != "synthetic") vs. gerador estruturado (synthetic) — para o
    dashboard nunca mentir sobre a origem dos dados.
    """
    from .real_ads_store import add_real_ads, count as _cnt

    tasks = tasks or FLEET
    # Embaralha para não bater sempre na mesma ordem (distribui a carga).
    tasks = random.sample(tasks, len(tasks))
    total_added = 0
    real_added = 0
    synth_added = 0
    per_bot: list[dict[str, Any]] = []
    for niche, net in tasks:
        try:
            found = _mine(niche, net, count=count, country=country)
            added = add_real_ads(found) if found else 0
        except Exception as e:  # noqa: BLE001 - bot individual nunca derruba a frota
            added = 0
            found = []
            reason = repr(e)
        else:
            reason = ""
        # Contabiliza real vs sintético (origem honesta).
        real_n = sum(
            1 for o in (found or []) if o.get("source") not in ("synthetic", "", None)
        )
        synth_n = len(found or []) - real_n
        real_added += min(real_n, added)
        synth_added += max(0, added - real_n)
        total_added += added
        per_bot.append(
            {
                "niche": niche,
                "network": net,
                "scraped": len(found or []),
                "added": added,
                "real": real_n,
                "synthetic": synth_n,
                **({"reason": reason} if reason else {}),
            }
        )
    return {
        "ok": True,
        "bots": len(tasks),
        "added": total_added,
        "realAdded": real_added,
        "syntheticAdded": synth_added,
        "realAdsTotal": _cnt(),
        "bots_detail": per_bot,
    }


def run_daemon(
    *,
    rounds: int = 0,
    interval: float = 300.0,
    count: int = 3,
    country: str = "BR",
) -> int:
    """Loop infinito (ou ``rounds`` finitos) — o "sempre online" de verdade.

    Rode num host de longa duração (VM/container) para manter a extração
    nativa rodando 24/7. No serverless, use ``collect_once`` via Cron.
    """
    r = 0
    while rounds == 0 or r < rounds:
        r += 1
        res = collect_once(count=count, country=country)
        print(
            f"[ad_fleet] round {r}: bots={res['bots']} added={res['added']} "
            f"realAdsTotal={res['realAdsTotal']}",
            file=sys.stderr,
        )
        if rounds and r >= rounds:
            break
        time.sleep(interval)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SpyFy real native ads fleet")
    ap.add_argument("--rounds", type=int, default=0, help="0 = infinito")
    ap.add_argument("--interval", type=float, default=300.0)
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--country", default="BR")
    args = ap.parse_args(argv)
    return run_daemon(
        rounds=args.rounds, interval=args.interval, count=args.count, country=args.country
    )


if __name__ == "__main__":
    sys.exit(main())
