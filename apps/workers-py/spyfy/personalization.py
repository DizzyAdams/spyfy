"""
SpyFy — Personalization Engine (Loop 1)
=======================================
Monta a "aba/home" de cada usuário conforme persona, comportamento e plano.
Cada usuário vê um dashboard DIFERENTE — feature de retenção que a
concorrência (AdSpy/BigSpy/Minea) não tem.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Persona(str, Enum):
    MEDIA_BUYER = "media_buyer"
    COPYWRITER = "copywriter"
    AFFILIATE = "affiliate"
    AGENCY = "agency"
    INFOPRODUCER = "infoproducer"
    UNKNOWN = "unknown"


@dataclass
class UserContext:
    user_id: str
    persona: Persona = Persona.UNKNOWN
    plan: str = "free"
    fav_niches: list[str] = field(default_factory=list)
    last_actions: list[str] = field(default_factory=list)   # ex.: ["clone","save"]
    onboarded: bool = False


@dataclass
class Widget:
    key: str
    title: str
    priority: int          # menor = mais acima
    reason: str = ""       # por que apareceu (explainability)


# Widgets base por persona (a "cara" de cada aba)
PERSONA_WIDGETS: dict[Persona, list[tuple[str, str, int]]] = {
    Persona.MEDIA_BUYER: [
        ("scaling_now", "Escalando agora no seu nicho", 1),
        ("longevity_feed", "Ativos há +30 dias", 2),
        ("competitor_watch", "Concorrentes monitorados", 3),
    ],
    Persona.COPYWRITER: [
        ("vsl_transcripts", "VSLs resumidas", 1),
        ("angle_radar", "Ângulos emergentes", 2),
        ("headline_swipe", "Headlines que convertem", 3),
    ],
    Persona.AFFILIATE: [
        ("clone_ready", "Funis prontos para clonar", 1),
        ("winning_offers", "Ofertas vencedoras", 2),
        ("stack_detector", "Stacks/checkout detectados", 3),
    ],
    Persona.AGENCY: [
        ("team_collections", "Coleções do time", 1),
        ("client_reports", "Relatórios white-label", 2),
        ("multi_niche", "Visão multi-nicho", 3),
    ],
    Persona.INFOPRODUCER: [
        ("saturation", "Saturação do nicho", 1),
        ("trends", "Tendências", 2),
        ("winning_offers", "Ofertas vencedoras", 3),
    ],
}

# Widgets só de planos pagos
PRO_ONLY = {"competitor_watch", "client_reports", "multi_niche", "stack_detector"}


def build_home_tab(ctx: UserContext) -> list[Widget]:
    """Retorna widgets ordenados para a home do usuário."""
    widgets: list[Widget] = []

    # onboarding tem prioridade máxima até concluir
    if not ctx.onboarded:
        widgets.append(Widget("onboarding", "Complete seu setup", 0,
                              "usuario ainda nao concluiu onboarding"))

    base = PERSONA_WIDGETS.get(ctx.persona, PERSONA_WIDGETS[Persona.AFFILIATE])
    for key, title, prio in base:
        locked = key in PRO_ONLY and ctx.plan == "free"
        reason = "bloqueado no free (upsell)" if locked else f"persona={ctx.persona.value}"
        title = f"🔒 {title}" if locked else title
        widgets.append(Widget(key, title, prio + 1, reason))

    # boost por comportamento: quem clona muito vê clone_ready no topo
    if ctx.last_actions.count("clone") >= 3:
        widgets.append(Widget("clone_ready", "Continue de onde parou (clones)", 1,
                              "usuario clona com frequencia"))

    # nichos favoritos viram atalho
    for i, niche in enumerate(ctx.fav_niches[:3]):
        widgets.append(Widget(f"niche_{niche}", f"Nicho: {niche}", 5 + i,
                              "nicho favorito do usuario"))

    # dedup por key mantendo maior prioridade (menor número)
    best: dict[str, Widget] = {}
    for w in widgets:
        if w.key not in best or w.priority < best[w.key].priority:
            best[w.key] = w
    return sorted(best.values(), key=lambda w: w.priority)


def infer_persona(last_actions: list[str]) -> Persona:
    """Heurística simples para inferir persona pelo comportamento."""
    if not last_actions:
        return Persona.UNKNOWN
    counts = {a: last_actions.count(a) for a in set(last_actions)}
    top = max(counts, key=lambda k: counts[k])
    return {
        "clone": Persona.AFFILIATE,
        "transcribe": Persona.COPYWRITER,
        "scale_check": Persona.MEDIA_BUYER,
        "report": Persona.AGENCY,
        "saturation": Persona.INFOPRODUCER,
    }.get(top, Persona.UNKNOWN)


if __name__ == "__main__":
    ctx = UserContext("u1", Persona.MEDIA_BUYER, "pro",
                      fav_niches=["keto", "finance"],
                      last_actions=["clone", "clone", "clone"], onboarded=True)
    for w in build_home_tab(ctx):
        print(f"{w.priority:>2}  {w.key:<18} {w.title}")
