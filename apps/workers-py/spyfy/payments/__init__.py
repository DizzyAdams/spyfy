"""SpyFy Payments — Multi-gateway payment router + anti-fraud.

Registers:
  POST /v1/payments/create           → cria pagamento no gateway escolhido
  POST /v1/payments/verify           → verifica status de um pagamento
  POST /v1/payments/webhook/{gateway} → recebe webhooks (Mercado Pago, PIX)
  POST /v1/payments/estimate-crypto  → cotação crypto → BRL
  GET  /v1/payments/methods          → lista gateways disponíveis

Cada endpoint aplica camadas de anti-fraude antes de processar.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .fraud import AntiFraud
from .mercadopago import MercadoPagoClient
from .pix import PixClient
from .crypto import CryptoClient
from .models import PaymentGateway, PaymentStatus

__all__ = ["register_payment_routes"]

# ─── Pydantic schemas ───────────────────────────────────────────────

class CreatePaymentRequest(BaseModel):
    amount_brl: float = Field(..., gt=0, le=5000, description="Valor em BRL")
    gateway: str = Field(..., description="mercadopago | pix | usdt | bitcoin")
    email: str = Field(..., description="Email do pagador")
    user_id: str = Field(..., description="ID do usuário")
    description: str = ""
    payer_cpf: str = ""
    pix_key: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

class CreatePaymentResponse(BaseModel):
    payment_id: str
    gateway: str
    status: str
    amount_brl: float
    qr_code: str = ""
    qr_code_base64: str = ""
    checkout_url: str = ""
    wallet_address: str = ""
    crypto_amount: float = 0
    crypto_currency: str = ""
    expires_in: int = 0

class VerifyPaymentRequest(BaseModel):
    payment_id: str
    gateway: str

class VerifyPaymentResponse(BaseModel):
    payment_id: str
    gateway: str
    status: str
    paid: bool
    amount_brl: float = 0
    gateway_details: dict[str, Any] = Field(default_factory=dict)

class EstimateCryptoResponse(BaseModel):
    crypto: str
    fiat: str
    fiat_amount: float
    crypto_amount: float
    rate: float
    wallet_address: str
    network: str
    expires_in: int
    payment_id: str

class PaymentMethod(BaseModel):
    key: str
    label: str
    description: str
    icon: str
    enabled: bool
    fee_pct: float

class WebhookAck(BaseModel):
    ok: bool
    dedup: bool = False
    payment_id: str = ""

# ─── In-memory payment store (dev; substituir por DB em produção) ──

_payments: dict[str, dict[str, Any]] = {}
_webhook_seen: set[str] = set()


def _make_payment_id() -> str:
    return f"pay_{uuid.uuid4().hex[:12]}"


def _check_webhook_dedup(event_id: str) -> bool:
    if event_id in _webhook_seen:
        return True
    _webhook_seen.add(event_id)
    return False


# ─── Router factory ─────────────────────────────────────────────────

def register_payment_routes(app: FastAPI) -> None:
    fraud = AntiFraud()
    mp = MercadoPagoClient()
    pix = PixClient()
    crypto = CryptoClient()

    router = APIRouter(prefix="/v1/payments", tags=["payments"])

    @router.get("/methods", response_model=list[PaymentMethod])
    def list_methods() -> list[PaymentMethod]:
        """Lista gateways de pagamento disponíveis com taxas."""
        return [
            PaymentMethod(key="mercadopago", label="Mercado Pago",
                          description="Cartão de crédito, boleto, PIX via Mercado Pago",
                          icon="credit-card", enabled=True, fee_pct=4.99),
            PaymentMethod(key="pix", label="PIX",
                          description="PIX direto (QR code dinâmico) — menor taxa",
                          icon="qr-code", enabled=True, fee_pct=0.99),
            PaymentMethod(key="usdt", label="USDT (TRC-20)",
                          description="Cripto stablecoin — dólar digital sem volatilidade",
                          icon="wallet", enabled=True, fee_pct=1.0),
            PaymentMethod(key="bitcoin", label="Bitcoin",
                          description="BTC — aceito globalmente, sem chargeback",
                          icon="bitcoin", enabled=True, fee_pct=1.0),
        ]

    @router.post("/create", response_model=CreatePaymentResponse)
    async def create_payment(req: CreatePaymentRequest, request: Request) -> CreatePaymentResponse:
        """Cria um pagamento no gateway escolhido, com validação anti-fraude."""

        # ── Anti-fraude ──────────────────────────────────────────────
        rate_key = f"{req.user_id}:{req.gateway}"
        if not fraud.rate_limit(rate_key):
            raise HTTPException(429, "Muitas tentativas. Aguarde 60 segundos.")

        amount_ok, amount_msg = fraud.validate_amount(req.amount_brl)
        if not amount_ok:
            raise HTTPException(422, amount_msg)

        if not fraud.validate_email(req.email):
            raise HTTPException(422, "Email inválido")

        # ── Identificador único (HMAC anti-tamper opcional) ──────────
        payment_id = _make_payment_id()
        expires_in = 3600  # 1h padrão

        # ── Roteamento por gateway ────────────────────────────────────
        gateway = req.gateway.lower()

        if gateway == "mercadopago":
            try:
                pref = mp.create_checkout(
                    amount=req.amount_brl,
                    email=req.email,
                    description=req.description or "SpyFy",
                    external_ref=payment_id,
                )
                init_point = (pref.get("init_point") or
                              pref.get("sandbox_init_point") or "")
                _payments[payment_id] = {
                    "id": payment_id, "gateway": gateway,
                    "status": PaymentStatus.PENDING.value,
                    "amount_brl": req.amount_brl,
                    "checkout_url": init_point,
                    "gateway_id": pref.get("id", ""),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                return CreatePaymentResponse(
                    payment_id=payment_id, gateway=gateway,
                    status=PaymentStatus.PENDING.value,
                    amount_brl=req.amount_brl,
                    checkout_url=init_point,
                    expires_in=expires_in,
                )
            except Exception as exc:
                raise HTTPException(502, f"Mercado Pago: {exc}")

        elif gateway == "pix":
            try:
                charge = pix.create_charge(
                    amount_brl=req.amount_brl,
                    key=req.pix_key,
                    payer_cpf=req.payer_cpf,
                )
                _payments[payment_id] = {
                    "id": payment_id, "gateway": gateway,
                    "status": PaymentStatus.PENDING.value,
                    "amount_brl": req.amount_brl,
                    "qr_code": charge["qr_code"],
                    "qr_code_base64": charge["qr_code_base64"],
                    "txid": charge["txid"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                return CreatePaymentResponse(
                    payment_id=payment_id, gateway=gateway,
                    status=PaymentStatus.PENDING.value,
                    amount_brl=req.amount_brl,
                    qr_code=charge["qr_code"],
                    qr_code_base64=charge["qr_code_base64"],
                    expires_in=charge["expires_in"],
                )
            except Exception as exc:
                raise HTTPException(502, f"PIX: {exc}")

        elif gateway in ("usdt", "bitcoin"):
            crypto_label = "USDT" if gateway == "usdt" else "BTC"
            try:
                estimate = crypto.estimate(req.amount_brl, crypto=crypto_label)
                _payments[payment_id] = {
                    "id": payment_id, "gateway": gateway,
                    "status": PaymentStatus.PENDING.value,
                    "amount_brl": req.amount_brl,
                    "wallet_address": estimate["wallet_address"],
                    "crypto_amount": estimate["crypto_amount"],
                    "crypto_currency": estimate["crypto"],
                    "network": estimate["network"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                return CreatePaymentResponse(
                    payment_id=payment_id, gateway=gateway,
                    status=PaymentStatus.PENDING.value,
                    amount_brl=req.amount_brl,
                    wallet_address=estimate["wallet_address"],
                    crypto_amount=estimate["crypto_amount"],
                    crypto_currency=estimate["crypto"],
                    expires_in=estimate["expires_in"],
                )
            except Exception as exc:
                raise HTTPException(502, f"Crypto: {exc}")

        else:
            raise HTTPException(400, f"Gateway não suportado: {gateway}")

    @router.post("/verify", response_model=VerifyPaymentResponse)
    async def verify_payment(req: VerifyPaymentRequest) -> VerifyPaymentResponse:
        """Verifica status de um pagamento."""
        pid = req.payment_id
        gateway = req.gateway.lower()
        payment = _payments.get(pid)

        if not payment:
            # Fallback: consulta no próprio gateway
            if gateway == "mercadopago":
                try:
                    info = mp.get_payment(pid)
                    status = _mp_status(info.get("status", ""))
                    return VerifyPaymentResponse(
                        payment_id=pid, gateway=gateway, status=status,
                        paid=status == PaymentStatus.APPROVED.value,
                        amount_brl=float(info.get("transaction_amount", 0)),
                        gateway_details=info,
                    )
                except Exception:
                    pass
            raise HTTPException(404, "Pagamento não encontrado")

        status = payment.get("status", PaymentStatus.PENDING.value)
        return VerifyPaymentResponse(
            payment_id=pid, gateway=gateway, status=status,
            paid=status == PaymentStatus.APPROVED.value,
            amount_brl=payment.get("amount_brl", 0),
            gateway_details=payment,
        )

    @router.post("/estimate-crypto", response_model=EstimateCryptoResponse)
    async def estimate_crypto(amount_brl: float = Query(..., gt=0),
                               crypto: str = Query("USDT")) -> EstimateCryptoResponse:
        """Estima quanto o usuário precisa pagar em crypto."""
        try:
            est = crypto.estimate(amount_brl, crypto=crypto)
            return EstimateCryptoResponse(**est)
        except Exception as exc:
            raise HTTPException(502, f"Cotação indisponível: {exc}")

    @router.post("/webhook/{gateway}", response_model=WebhookAck)
    async def payment_webhook(gateway: str, request: Request) -> WebhookAck:
        """Recebe webhooks de cada gateway (Mercado Pago, PIX)."""
        body_bytes = await request.body()
        body_str = body_bytes.decode()
        sig = request.headers.get("x-signature", "")
        payment_id = ""

        if gateway == "mercadopago":
            if not mp.verify_webhook(body_bytes, sig):
                raise HTTPException(401, "Assinatura inválida (MP)")
            try:
                payload = json.loads(body_str)
                action = payload.get("action", "")
                data = payload.get("data", {})
                pid = data.get("id", "") or payload.get("payment_id", "")
                payment_id = pid
                if action == "payment.created" or action == "payment.updated":
                    # Consulta status atualizado
                    info = mp.get_payment(pid)
                    status = _mp_status(info.get("status", ""))
                    if pid in _payments:
                        _payments[pid]["status"] = status
                        _payments[pid]["gateway_id"] = pid
            except Exception:
                pass

        elif gateway == "pix":
            if not pix.verify_webhook(body_bytes, sig):
                raise HTTPException(401, "Assinatura inválida (PIX)")
            try:
                payload = json.loads(body_str)
                txid = payload.get("txid", "")
                payment_id = txid
                status = PaymentStatus.APPROVED.value
                # Atualiza pagamentos que tenham este txid
                for pid, p in _payments.items():
                    if p.get("txid") == txid:
                        p["status"] = status
                        p["paid_at"] = datetime.now(timezone.utc).isoformat()
            except Exception:
                pass

        else:
            raise HTTPException(400, f"Gateway não suportado: {gateway}")

        return WebhookAck(ok=True, payment_id=payment_id)

    app.include_router(router)


def _mp_status(mp_status: str) -> str:
    """Mapeia status Mercado Pago → PaymentStatus."""
    mapping = {
        "approved": PaymentStatus.APPROVED.value,
        "pending": PaymentStatus.PENDING.value,
        "in_process": PaymentStatus.PROCESSING.value,
        "in_mediation": PaymentStatus.PROCESSING.value,
        "rejected": PaymentStatus.REJECTED.value,
        "cancelled": PaymentStatus.REJECTED.value,
        "refunded": PaymentStatus.REFUNDED.value,
        "charged_back": PaymentStatus.REFUNDED.value,
    }
    return mapping.get(mp_status, PaymentStatus.PENDING.value)
