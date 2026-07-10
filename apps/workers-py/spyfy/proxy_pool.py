"""
SpyFy — Proxy Pool (Loop 7)
============================
Pool de proxies rotativos para driblar Cloudflare / rate-limit em
scrapers (Meta Ad Library, TikTok, etc.). Suporta:
  - rotação round-robin / random / sticky (sessão fixa p/ CF clearance)
  - health check (latência, sucesso)
  - ban list automática (proxy que falha vira "bad")
  - seleção por região (país do alvo)
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ProxyType(str, Enum):
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"


class Rotation(str, Enum):
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    STICKY = "sticky"          # mantém o mesmo proxy por sessão


@dataclass
class Proxy:
    url: str
    ptype: ProxyType = ProxyType.RESIDENTIAL
    region: str = "any"
    sticky_id: str = ""            # para sessões sticky
    latency_ms: float = 0.0
    failures: int = 0
    successes: int = 0
    last_used: float = 0.0
    banned: bool = False

    @property
    def score(self) -> float:
        """Quanto maior, melhor. Penaliza falhas/latência."""
        if self.banned:
            return -1.0
        total = self.failures + self.successes
        ok_rate = self.successes / total if total else 1.0
        lat_penalty = min(self.latency_ms / 1000.0, 1.0)  # 1s+ => -1
        return round(ok_rate - lat_penalty, 3)


class ProxyPool:
    def __init__(self, proxies: list[Proxy] | None = None,
                 rotation: Rotation = Rotation.ROUND_ROBIN,
                 sticky_key: Callable[[], str] | None = None,
                 max_failures: int = 3):
        self.proxies = proxies or []
        self.rotation = rotation
        self._rr = 0
        self._sticky: dict[str, str] = {}      # sticky_id -> proxy url
        self.max_failures = max_failures

    # ------------------------------------------------------------------ #
    def add(self, proxy: Proxy) -> None:
        self.proxies.append(proxy)

    def _avail(self) -> list[Proxy]:
        return [p for p in self.proxies if not p.banned]

    def get(self, region: str = "any", sticky_id: str = "") -> Proxy | None:
        avail = [p for p in self._avail()
                  if region in (p.region, "any")]
        if not avail:
            return None
        if self.rotation == Rotation.STICKY and sticky_id:
            if sticky_id in self._sticky:
                url = self._sticky[sticky_id]
                found = next((p for p in avail if p.url == url), None)
                if found:
                    return found
            chosen = self._pick(avail)
            self._sticky[sticky_id] = chosen.url
            return chosen
        return self._pick(avail)

    def _pick(self, avail: list[Proxy]) -> Proxy:
        if self.rotation == Rotation.RANDOM:
            return random.choice(avail)
        # round robin ponderado por score
        self._rr = (self._rr + 1) % len(self.proxies)
        best = max(avail, key=lambda p: p.score)
        return best

    # ------------------------------------------------------------------ #
    def report(self, proxy: Proxy, ok: bool, latency_ms: float = 0.0) -> None:
        proxy.last_used = time.time()
        proxy.latency_ms = latency_ms
        if ok:
            proxy.successes += 1
        else:
            proxy.failures += 1
            if proxy.failures >= self.max_failures:
                proxy.banned = True

    def stats(self) -> dict:
        n = len(self.proxies)
        bad = sum(1 for p in self.proxies if p.banned)
        return {"total": n, "banned": bad, "available": n - bad}


if __name__ == "__main__":
    pool = ProxyPool([
        Proxy("http://p1:1@1.1.1.1:8000", ProxyType.RESIDENTIAL, "BR"),
        Proxy("http://p2:1@2.2.2.2:8000", ProxyType.RESIDENTIAL, "US"),
        Proxy("http://p3:1@3.3.3.3:8000", ProxyType.MOBILE, "BR"),
    ], rotation=Rotation.STICKY)

    p = pool.get(region="BR", sticky_id="sessao-A")
    assert p is not None, "nenhum proxy disponivel para regiao BR"
    print("escolhido (BR, sticky):", p.region, p.url)
    again = pool.get(region="BR", sticky_id="sessao-A")
    assert again is not None, "sticky session deve retornar proxy"
    print("mesma sessao:", again.url == p.url)
    pool.report(p, ok=False, latency_ms=1200)
    pool.report(p, ok=False)
    pool.report(p, ok=False)          # 3 falhas -> banned
    print("stats apos 3 falhas:", pool.stats())
