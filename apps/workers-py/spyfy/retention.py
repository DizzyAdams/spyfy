"""
SpyFy — Retention Engine (Loop 2)
=================================
Health score de usuário, risco de churn e gatilhos de re-engajamento.
Objetivo: reter o cliente o máximo possível (LTV up, churn down).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ChurnRisk(str, Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CRITICAL = "critical"
    CHURNED = "churned"


@dataclass
class UsageSnapshot:
    days_since_signup: int
    days_since_last_login: int
    logins_last_30d: int
    offers_saved: int
    clones_done: int
    alerts_active: int
    seats_used: int = 1
    plan: str = "free"


@dataclass
class HealthResult:
    score: float               # 0..100
    risk: ChurnRisk
    drivers: list[str] = field(default_factory=list)   # o que puxa pra baixo
    actions: list[str] = field(default_factory=list)   # o que fazer


def health_score(u: UsageSnapshot) -> HealthResult:
    """Calcula health score (0-100) e risco de churn."""
    score = 100.0
    drivers: list[str] = []

    # recência (peso alto)
    if u.days_since_last_login >= 30:
        score -= 45
        drivers.append("sem login ha 30+ dias")
    elif u.days_since_last_login >= 14:
        score -= 25
        drivers.append("sem login ha 14+ dias")
    elif u.days_since_last_login >= 7:
        score -= 12
        drivers.append("sem login ha 7+ dias")

    # frequência
    if u.logins_last_30d <= 1:
        score -= 20
        drivers.append("baixa frequencia de login")
    elif u.logins_last_30d <= 4:
        score -= 8
        drivers.append("frequencia moderada")

    # ativação (aha = salvar + clonar)
    if u.offers_saved == 0:
        score -= 12
        drivers.append("nunca salvou oferta")
    if u.clones_done == 0:
        score -= 12
        drivers.append("nunca clonou (aha nao atingido)")
    if u.alerts_active == 0:
        score -= 6
        drivers.append("sem alertas ativos")

    score = max(0.0, min(100.0, score))
    risk = _risk_from(score, u.days_since_last_login)
    return HealthResult(round(score, 1), risk, drivers,
                        _actions_for(risk, u))


def _risk_from(score: float, days_idle: int) -> ChurnRisk:
    if days_idle >= 45:
        return ChurnRisk.CHURNED
    if score >= 70:
        return ChurnRisk.HEALTHY
    if score >= 45:
        return ChurnRisk.AT_RISK
    return ChurnRisk.CRITICAL


def _actions_for(risk: ChurnRisk, u: UsageSnapshot) -> list[str]:
    """Playbook de re-engajamento por risco."""
    if risk == ChurnRisk.HEALTHY:
        acts = ["oferecer upgrade/expansao" if u.plan != "enterprise" else "case study"]
    elif risk == ChurnRisk.AT_RISK:
        acts = ["enviar digest personalizado", "destacar oferta escalando no nicho"]
    elif risk == ChurnRisk.CRITICAL:
        acts = ["email de winback + credito de clonagem gratis",
                "onboarding assistido / call"]
    else:  # CHURNED
        acts = ["winback com desconto", "pesquisa de cancelamento"]

    if u.clones_done == 0:
        acts.append("guiar ate a primeira clonagem (aha)")
    if u.offers_saved == 0:
        acts.append("sugerir 3 ofertas para salvar")
    return acts


def should_trigger_winback(u: UsageSnapshot) -> bool:
    return _risk_from(health_score(u).score, u.days_since_last_login) in (
        ChurnRisk.CRITICAL, ChurnRisk.CHURNED)


def expansion_ready(u: UsageSnapshot) -> bool:
    """Sinaliza upsell: usuário saudável e batendo limites."""
    r = health_score(u)
    heavy = u.clones_done >= 40 or u.seats_used >= 2
    return r.risk == ChurnRisk.HEALTHY and heavy and u.plan in ("starter", "pro")


if __name__ == "__main__":
    power = UsageSnapshot(120, 1, 25, 80, 60, 5, seats_used=2, plan="pro")
    idle = UsageSnapshot(60, 40, 1, 2, 0, 0, plan="starter")
    for name, u in [("POWER", power), ("IDLE", idle)]:
        r = health_score(u)
        print(f"{name}: score={r.score} risco={r.risk.value}")
        print("  drivers:", r.drivers)
        print("  acoes:", r.actions)
    print("expansion power?", expansion_ready(power))
    print("winback idle?", should_trigger_winback(idle))
