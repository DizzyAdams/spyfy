"""
SpyFy — CRM Integrado (Loop 8)
================================
CRM leve integrado (no need de Salesforce/Pipedrive). Modela
contacts, deals (pipeline de afiliado/agência) e activities, e
SINCRONIZA com o resto do SpyFy: ofertas, clones e winback.

Cada usuário do SpyFy já é um contato; o CRM vira a "cola"
entre descoberta → clonagem → venda → retenção.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class Stage(str, Enum):
    LEAD = "lead"
    CONTACTED = "contacted"
    TRIAL = "trial"
    PAYING = "paying"
    EXPANDING = "expanding"
    CHURNED = "churned"


class ActivityType(str, Enum):
    OFFER_FOUND = "offer_found"
    CLONE_DONE = "clone_done"
    SALE = "sale"
    WINBACK = "winback"
    NOTE = "note"


@dataclass
class Contact:
    id: str
    name: str
    email: str = ""
    phone: str = ""
    company: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class Deal:
    id: str
    contact_id: str
    title: str
    stage: Stage = Stage.LEAD
    value_usd: float = 0.0
    offer_id: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class Activity:
    id: str
    contact_id: str
    type: ActivityType
    payload: dict = field(default_factory=dict)
    at: float = field(default_factory=time.time)


class CRM:
    def __init__(self) -> None:
        self.contacts: dict[str, Contact] = {}
        self.deals: dict[str, Deal] = {}
        self.activities: list[Activity] = []
        self._seq = 0
        self._handlers: list[Callable[[Activity], None]] = []

    # ----- registro ----- #
    def upsert_contact(self, c: Contact) -> Contact:
        self.contacts[c.id] = c
        return c

    def add_deal(self, d: Deal) -> Deal:
        self.deals[d.id] = d
        return d

    def log(self, contact_id: str, atype: ActivityType,
            payload: dict | None = None) -> Activity:
        self._seq += 1
        a = Activity(f"act_{self._seq}", contact_id, atype, payload or {})
        self.activities.append(a)
        for h in self._handlers:
            try:
                h(a)
            except Exception:
                pass
        return a

    def on_activity(self, h: Callable[[Activity], None]) -> None:
        self._handlers.append(h)

    # ----- sinchronization com SpyFy ----- #
    def on_offer_found(self, contact_id: str, offer_id: str,
                       niche: str) -> None:
        self.log(contact_id, ActivityType.OFFER_FOUND,
                {"offer_id": offer_id, "niche": niche})

    def on_clone_done(self, contact_id: str, offer_id: str,
                      clone_id: str) -> None:
        self.log(contact_id, ActivityType.CLONE_DONE,
                {"offer_id": offer_id, "clone_id": clone_id})
        # clonar == aha -> sobe o deal para trial se existir
        for d in self.deals.values():
            if d.contact_id == contact_id and d.stage == Stage.LEAD:
                d.stage = Stage.TRIAL

    def on_sale(self, contact_id: str, value_usd: float,
                offer_id: str = "") -> None:
        self.log(contact_id, ActivityType.SALE,
                {"value_usd": value_usd, "offer_id": offer_id})
        d = self._deal_for(contact_id)
        if d:
            d.value_usd = max(d.value_usd, value_usd)
            d.stage = Stage.PAYING

    def winback(self, contact_id: str) -> None:
        self.log(contact_id, ActivityType.WINBACK, {})
        d = self._deal_for(contact_id)
        if d and d.stage == Stage.CHURNED:
            d.stage = Stage.CONTACTED

    # ----- consultas ----- #
    def _deal_for(self, contact_id: str) -> Deal | None:
        for d in self.deals.values():
            if d.contact_id == contact_id:
                return d
        return None

    def pipeline_summary(self) -> dict:
        out: dict[str, int] = {s.value: 0 for s in Stage}
        for d in self.deals.values():
            out[d.stage.value] += 1
        out["contacts"] = len(self.contacts)
        out["activities"] = len(self.activities)
        return out


if __name__ == "__main__":
    crm = CRM()
    crm.upsert_contact(Contact("u1", "Ana", "ana@x.com"))
    crm.add_deal(Deal("d1", "u1", "Keto BR", Stage.LEAD, 0, "ofr_1"))
    crm.on_offer_found("u1", "ofr_1", "keto")
    crm.on_clone_done("u1", "ofr_1", "clone_9")
    crm.on_sale("u1", 96.0)
    print("pipeline:", crm.pipeline_summary())
    print("deal d1:", crm.deals["d1"].stage.value, crm.deals["d1"].value_usd)
