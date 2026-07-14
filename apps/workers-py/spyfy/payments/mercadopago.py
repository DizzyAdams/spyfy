"""Mercado Pago payment integration.

Integração oficial Mercado Pago — checkout, PIX, webhook verification.
Requer env vars:
  MP_ACCESS_TOKEN  — access token do Mercado Pago (APP)
  MP_WEBHOOK_SECRET — secret para verificar assinatura dos webhooks
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Any

import httpx

MP_API = "https://api.mercadopago.com/v1"


class MercadoPagoError(RuntimeError):
    """Erro na comunicação com a API do Mercado Pago."""


class MercadoPagoClient:
    """Cliente Mercado Pago — checkout, PIX QR code e webhook verification."""

    def __init__(self, access_token: str = "", webhook_secret: str = ""):
        self.access_token = access_token or os.getenv("MP_ACCESS_TOKEN", "")
        self.webhook_secret = webhook_secret or os.getenv("MP_WEBHOOK_SECRET", "")

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # ── PIX (QR code estático/dinâmico via Mercado Pago) ────────────

    def create_pix_payment(
        self,
        amount: float,
        email: str,
        description: str = "",
        external_ref: str = "",
    ) -> dict:
        """Cria pagamento PIX via Mercado Pago (gera QR code copia-e-cola)."""
        body = {
            "transaction_amount": amount,
            "description": description or "SpyFy - Assinatura",
            "payment_method_id": "pix",
            "payer": {"email": email},
            "external_reference": external_ref,
        }
        resp = httpx.post(
            f"{MP_API}/payments", json=body, headers=self._headers, timeout=15
        )
        if resp.status_code not in (200, 201):
            _raise_mp_error(resp)
        return resp.json()

    # ── Checkout (cartão de crédito, boleto, PIX via página MP) ─────

    def create_checkout(
        self,
        amount: float,
        email: str,
        description: str = "",
        external_ref: str = "",
        back_urls: dict | None = None,
    ) -> dict:
        """Cria preferência de checkout Mercado Pago.

        Retorna um dict com ``init_point`` (URL para redirecionar o
        comprador) e ``id`` (preference_id).
        """
        body = {
            "items": [
                {
                    "title": description or "SpyFy",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": amount,
                }
            ],
            "payer": {"email": email},
            "external_reference": external_ref,
            "back_urls": back_urls
            or {
                "success": "https://spyfyprod.vercel.app/app/checkout/success",
                "failure": "https://spyfyprod.vercel.app/app/checkout/cancel",
                "pending": "https://spyfyprod.vercel.app/app/checkout/pending",
            },
            "auto_return": "approved",
            "statement_descriptor": "SpyFy",
        }
        resp = httpx.post(
            f"{MP_API}/checkout/preferences",
            json=body,
            headers=self._headers,
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            _raise_mp_error(resp)
        return resp.json()

    # ── Consulta ─────────────────────────────────────────────────────

    def get_payment(self, payment_id: str) -> dict:
        """Retorna os dados de um pagamento pelo ID do Mercado Pago."""
        resp = httpx.get(
            f"{MP_API}/payments/{payment_id}",
            headers=self._headers,
            timeout=10,
        )
        if resp.status_code != 200:
            _raise_mp_error(resp)
        return resp.json()

    # ── Webhook verification ─────────────────────────────────────────

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        """Verifica assinatura HMAC-SHA256 do webhook Mercado Pago.

        Em modo dev (sem secret configurado), retorna True.
        """
        if not self.webhook_secret:
            return True  # dev mode
        expected = hmac.new(
            self.webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)


def _raise_mp_error(resp: httpx.Response) -> None:
    """Levanta MercadoPagoError com detalhes da resposta."""
    detail = resp.text[:300] if resp.text else f"HTTP {resp.status_code}"
    raise MercadoPagoError(f"Mercado Pago {resp.status_code}: {detail}")
