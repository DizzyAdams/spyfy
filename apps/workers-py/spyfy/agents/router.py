"""
SpyFy — Roteamento multi-tenant (admin / afiliado / usuário)
=============================================================
Conecta a camada autônoma LangGraph ao acesso por papel (Role), dando
a cada perfil **memória RAG isolada**, limites por plano e filtragem de
nichos — exatamente o pedido "LangChain para admin, afiliados e usuários".

O `Role` é distinto do `Persona` de marketing (personalization.py, que
define a "cara" do dashboard). Aqui `Role` governa **acesso e quotas** do
pipeline autônomo:
  - ADMIN      -> acesso total, memória RAG global, pode clonar, todos os nichos.
  - AFFILIATE  -> seus verticais, memória própria, pode clonar, quotas de plano.
  - USER       -> tier free/limited, memória própria, sem clone, nichos restritos.

A memória RAG é namespaced por `collection_name` (ex.: ``rag_admin``,
``rag_u1``) sobre o cliente chromadb singleton — isolamento real entre
tenants no mesmo processo, sem arquivos de lock.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .memory import OfferMemory
from .orchestrator import run_offer_pipeline


class Role(str, Enum):
    ADMIN = "admin"
    AFFILIATE = "affiliate"
    USER = "user"


@dataclass
class TenantPolicy:
    """Quotas e escopo de acesso de um tenant (role + user)."""

    role: Role
    user_id: str
    memory_collection: str
    allowed_niches: list[str] | None  # None = todos os nichos
    max_count: int
    min_score: float
    can_clone: bool
    label: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "user_id": self.user_id,
            "memory_collection": self.memory_collection,
            "allowed_niches": self.allowed_niches,
            "max_count": self.max_count,
            "min_score": self.min_score,
            "can_clone": self.can_clone,
            "label": self.label,
        }


# Nichos liberados no tier free (USER) — o resto exige plano/afiliado.
FREE_NICHES = ["keto", "finance", "beauty"]


def policy_for(
    role: Role,
    user_id: str,
    *,
    user_niches: list[str] | None = None,
    plan: str = "free",
) -> TenantPolicy:
    """Monta a política de acesso do tenant conforme role/plano."""
    if role == Role.ADMIN:
        return TenantPolicy(
            Role.ADMIN, user_id, "rag_admin", None, 20, 0.0, True,
            "Admin (acesso total)",
        )
    if role == Role.AFFILIATE:
        niches = user_niches or ["keto", "finance"]
        max_count = 12 if plan == "pro" else 8
        return TenantPolicy(
            Role.AFFILIATE, user_id, f"rag_{user_id}", niches, max_count,
            45.0, True, f"Afiliado {user_id}",
        )
    # USER (tier free/limited por padrão)
    niches = user_niches or FREE_NICHES
    max_count = 5 if plan == "pro" else 3
    return TenantPolicy(
        Role.USER, user_id, f"rag_{user_id}", niches, max_count,
        65.0, False, f"Usuário {user_id}",
    )


def tenant_memory(policy: TenantPolicy) -> OfferMemory:
    """Memória RAG isolada do tenant (collection namespaced)."""
    return OfferMemory(collection_name=policy.memory_collection)


def _apply_policy(final: dict[str, Any], policy: TenantPolicy) -> dict[str, Any]:
    """Filtra descobertas/analytics pela política do tenant (nícho + score)."""
    ads: list[dict[str, Any]] = final.get("discovered_ads", []) or []
    allowed = {n.lower() for n in (policy.allowed_niches or [])}

    def keep(o: dict[str, Any]) -> bool:
        if allowed and (o.get("niche") or "").lower() not in allowed:
            return False
        if (o.get("winningScore") or 0.0) < policy.min_score:
            return False
        return True

    kept = [o for o in ads if keep(o)]
    dropped = len(ads) - len(kept)
    final["discovered_ads"] = kept
    if final.get("analytics"):
        aoffs = [o for o in final["analytics"].get("offers", []) if keep(o)]
        final["analytics"]["offers"] = aoffs
        final["analytics"]["best"] = (
            max(aoffs, key=lambda r: r["winning_score"]) if aoffs else None
        )
    final["policy"] = policy.as_dict()
    final["policy_filtered_out"] = dropped
    return final


async def run_for_tenant(
    role: Role,
    user_id: str,
    objective: str,
    *,
    niche: str | None = None,
    network: str | None = None,
    country: str | None = None,
    min_score: float = 0.0,
    count: int = 3,
    simulate: bool = True,
    bus: Any = None,
    plan: str = "free",
    user_niches: list[str] | None = None,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """Roda o pipeline autônomo com a política do tenant aplicada.

    Memória RAG e limites de acesso são isolados por role/user — o mesmo
    grafo serve admin, afiliados e usuários com escopo diferente.
    """
    policy = policy_for(role, user_id, user_niches=user_niches, plan=plan)
    count = min(count, policy.max_count)
    memory = tenant_memory(policy)
    final = await run_offer_pipeline(
        objective,
        niche=niche, network=network, country=country,
        min_score=min_score, memory=memory, bus=bus,
        simulate=simulate, count=count, thread_id=thread_id,
    )
    return _apply_policy(final, policy)


def demo_policies() -> dict[str, dict[str, Any]]:
    """Catálogo das 3 políticas de tenant (demo de multi-tenancy)."""
    out: dict[str, dict[str, Any]] = {}
    for role in (Role.ADMIN, Role.AFFILIATE, Role.USER):
        p = policy_for(role, "demo", plan="free")
        out[role.value] = p.as_dict()
    return out
