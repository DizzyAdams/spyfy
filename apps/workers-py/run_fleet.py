"""SpyFy — Daemon local da frota de mini-bots de anúncios nativos REAIS.

Mantém a extração nativa rodando 24/7 num host de longa duração
(VM/container), o "sempre online" de verdade. No Vercel (serverless) use
o Cron em vez disso: ele chama GET /v1/cron/collect-ads a cada 15 min.

Uso:
    python run_fleet.py --rounds 0 --interval 300
    python run_fleet.py --rounds 5 --interval 60   # teste finito
"""
from __future__ import annotations

import argparse
import sys

from spyfy.ad_fleet import main

if __name__ == "__main__":
    sys.exit(main())
