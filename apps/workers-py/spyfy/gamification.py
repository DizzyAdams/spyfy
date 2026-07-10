"""
SpyFy — Gamification Engine (Loop 3)
====================================
XP, níveis, badges e streaks para reter usuários (loops de hábito).
Concorrência não gamifica — aqui vira vantagem de engajamento/retenção.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# XP por ação (recompensa comportamento de valor)
XP_TABLE = {
    "login": 5, "search": 2, "save": 8, "clone": 25,
    "alert_create": 10, "share": 15, "publish_marketplace": 40,
    "first_clone": 100,
}

# Níveis (limiar cumulativo de XP)
LEVELS = [
    (0, "Explorador"), (150, "Caçador"), (500, "Analista"),
    (1500, "Estrategista"), (4000, "Mestre"), (10000, "Lenda"),
]


@dataclass
class GameState:
    user_id: str
    xp: int = 0
    streak_days: int = 0
    badges: set[str] = field(default_factory=set)
    counters: dict[str, int] = field(default_factory=dict)


@dataclass
class GameEvent:
    action: str          # chave de XP_TABLE
    unlocked: list[str] = field(default_factory=list)  # badges novos
    xp_gained: int = 0
    level: str = ""
    level_up: bool = False


BADGE_RULES = {
    "first_clone": lambda s: s.counters.get("clone", 0) == 1,
    "clone_10": lambda s: s.counters.get("clone", 0) == 10,
    "clone_100": lambda s: s.counters.get("clone", 0) == 100,
    "trend_hunter": lambda s: s.counters.get("save", 0) >= 50,
    "streak_7": lambda s: s.streak_days == 7,
    "streak_30": lambda s: s.streak_days == 30,
    "seller": lambda s: s.counters.get("publish_marketplace", 0) >= 1,
}


def level_for(xp: int) -> str:
    name = LEVELS[0][1]
    for threshold, label in LEVELS:
        if xp >= threshold:
            name = label
    return name


def apply_action(state: GameState, action: str) -> GameEvent:
    """Aplica uma ação: soma XP, atualiza contadores e desbloqueia badges."""
    prev_level = level_for(state.xp)
    xp = XP_TABLE.get(action, 0)

    # bônus de primeira clonagem
    state.counters[action] = state.counters.get(action, 0) + 1
    if action == "clone" and state.counters["clone"] == 1:
        xp += XP_TABLE["first_clone"]

    state.xp += xp

    unlocked = []
    for badge, rule in BADGE_RULES.items():
        if badge not in state.badges and rule(state):
            state.badges.add(badge)
            unlocked.append(badge)

    new_level = level_for(state.xp)
    return GameEvent(action, unlocked, xp, new_level, new_level != prev_level)


def register_daily_login(state: GameState, consecutive: bool) -> GameEvent:
    """Atualiza streak no login diário."""
    state.streak_days = state.streak_days + 1 if consecutive else 1
    return apply_action(state, "login")


def progress_to_next_level(xp: int) -> dict:
    """Quanto falta para o próximo nível (barra de progresso)."""
    cur = 0
    nxt = None
    for threshold, _ in LEVELS:
        if xp >= threshold:
            cur = threshold
        elif nxt is None:
            nxt = threshold
    if nxt is None:
        return {"current": cur, "next": None, "pct": 100.0}
    pct = round((xp - cur) / (nxt - cur) * 100, 1)
    return {"current": cur, "next": nxt, "pct": pct}


if __name__ == "__main__":
    s = GameState("u1")
    for act in ["login", "search", "save", "clone", "clone"]:
        ev = apply_action(s, act)
        tag = " [LEVEL UP]" if ev.level_up else ""
        print(f"{act:<8} +{ev.xp_gained}xp -> {s.xp} ({ev.level}){tag} "
              f"badges={ev.unlocked}")
    print("progresso:", progress_to_next_level(s.xp))
