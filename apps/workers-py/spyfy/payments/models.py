"""SpyFy Payments — Data models."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentGateway(Enum):
    MERCADO_PAGO = "mercadopago"
    PIX = "pix"
    USDT = "usdt"
    BITCOIN = "bitcoin"


@dataclass
class PaymentRequest:
    amount_brl: float
    gateway: PaymentGateway
    user_id: str
    email: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentResult:
    id: str
    status: PaymentStatus
    gateway: PaymentGateway
    amount_brl: float
    qr_code: str = ""              # PIX QR code (texto copia-e-cola)
    qr_code_base64: str = ""        # PIX QR image (base64 PNG)
    checkout_url: str = ""          # Mercado Pago / crypto redirect
    wallet_address: str = ""        # Crypto wallet
    crypto_amount: float = 0        # Crypto equivalent
    crypto_currency: str = ""       # USDT, BTC
    paid_at: datetime | None = None
    gateway_id: str = ""            # ID externo no gateway
    metadata: dict[str, Any] = field(default_factory=dict)


class FraudFlag(Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
