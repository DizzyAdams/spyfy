"""
SpyFy — Cart Recovery + Page Builder + Garantia 24h (Loop 9)
=====================================================
1) Carrinho abandonado: detecta checkout nao concluido e roda
   sequencia de recuperacao (email/SMS/push) ate converter ou expirar.
2) Gerador de paginas: o "nosso gerador" monta a landing do
   clone por encomenda. FLUXO: ele ENVIA UMA SOLICITACAO VIA
   EMAIL do que precisa (brief) -> produz a pagina -> entrega.
3) GARANTIA: se NAO ENTREGARMOS a pagina/clonagem em ate 24h,
   o usuario recebe 1 ANO GRATIS + TODO o valor de volta.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class CartStatus(str, Enum):
    ABANDONED = "abandoned"
    RECOVERED = "recovered"
    EXPIRED = "expired"


@dataclass
class AbandonedCart:
    id: str
    user_id: str
    plan: str
    value_usd: float
    created_at: float
    status: CartStatus = CartStatus.ABANDONED
    reminders_sent: int = 0
    recovered_at: float = 0.0


# janelas da sequencia de recuperacao (minutos apos abandono)
RECOVERY_STEPS = [30, 180, 1440]   # 30min, 3h, 24h


def next_reminder(cart: AbandonedCart, now: float) -> int | None:
    """Indice do proximo lembrete, ou None se ja enviou todos."""
    elapsed = (now - cart.created_at) / 60.0
    for i, win in enumerate(RECOVERY_STEPS):
        if i >= cart.reminders_sent and elapsed >= win:
            return i
    return None


def recover(cart: AbandonedCart, now: float) -> None:
    cart.status = CartStatus.RECOVERED
    cart.recovered_at = now


def expire(cart: AbandonedCart, now: float) -> bool:
    """Expira se passou da ultima janela e nao recuperou."""
    if cart.status != CartStatus.ABANDONED:
        return False
    if (now - cart.created_at) / 60.0 >= RECOVERY_STEPS[-1]:
        cart.status = CartStatus.EXPIRED
        return True
    return False


# --------------------------------------------------------------------------- #
# Gerador de Paginas (Page Builder)
# --------------------------------------------------------------------------- #
class PageBlock(str, Enum):
    HEADLINE = "headline"
    VIDEO = "video"          # VSL
    CTA = "cta"
    TESTIMONIAL = "testimonial"
    OFFER = "offer"


@dataclass
class PageRequest:
    id: str
    user_id: str
    offer_id: str
    brief_email: str             # SOLICITACAO via email: o que precisa
    blocks: list[PageBlock] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    delivered_at: float = 0.0
    status: str = "pending"        # pending -> building -> delivered


SLA_SECONDS = 24 * 3600              # GARANTIA: 24h


def build_page(req: PageRequest, now: float,
              builder: Callable[[PageRequest], str] | None = None) -> str:
    """Gera o HTML da pagina a partir do brief (default: template)."""
    req.status = "building"
    html = builder(req) if builder else _default_html(req)
    req.status = "delivered"
    req.delivered_at = now
    return html


def _default_html(req: PageRequest) -> str:
    return (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<title>SpyFy Clone {req.offer_id}</title></head><body>"
        "<section class='hero'><h1>Oferta clonada</h1>"
        f"<p>{req.brief_email}</p>"
        "<a class='cta' href='#comprar'>Comprar agora</a>"
        "</section></body></html>"
    )


@dataclass
class GuaranteeResult:
    within_sla: bool
    refund_usd: float
    free_months: int
    reason: str


def evaluate_guarantee(req: PageRequest, now: float, paid_usd: float,
                        base_plan_months: int = 12) -> GuaranteeResult:
    """
    GARANTIA: se NAO entregamos em ate 24h, o usuario recebe
    1 ANO GRATIS + TODO o valor de volta.
    """
    if req.status == "delivered" and req.delivered_at:
        if (req.delivered_at - req.created_at) <= SLA_SECONDS:
            return GuaranteeResult(True, 0.0, 0, "entregue dentro do SLA")
        # entregue MAS fora do prazo -> garante
        return GuaranteeResult(
            False, paid_usd, base_plan_months,
            "entregue fora de 24h -> 1 ano gratis + valor integral")
    # ainda nao entregue: so garante se ja furou o prazo
    if (now - req.created_at) > SLA_SECONDS:
        return GuaranteeResult(
            False, paid_usd, base_plan_months,
            "nao entregue em 24h -> 1 ano gratis + valor integral de volta")
    return GuaranteeResult(True, 0.0, 0, "em processamento, ainda no prazo")


if __name__ == "__main__":
    now = time.time()
    # recuperacao de carrinho
    cart = AbandonedCart("c1", "u1", "pro", 49.0, now - 31 * 60)
    print("proximo lembrete:", next_reminder(cart, now))
    recover(cart, now)
    print("status:", cart.status.value)

    # gerador de pagina + garantia
    req = PageRequest("r1", "u1", "ofr_1",
                      "Preciso de uma lander com VSL e CTA para Keto BR")
    html = build_page(req, now)
    print("pagina entregue:", req.status, "len(html)=", len(html))

    paid = 588.0
    g = evaluate_guarantee(req, now, paid)
    print("garantia OK:", g.within_sla, g.reason)

    # simula FURA do SLA -> garante
    late = PageRequest("r2", "u2", "ofr_2", "brief",
                      created_at=now - (25 * 3600))
    g2 = evaluate_guarantee(late, now, paid)
    print("garantia furou SLA:", g2.within_sla,
          "-> reembolso", g2.refund_usd, "+", g2.free_months, "meses")
