"""PIX — Integração direta com PSP/banco via API.

Cobranças PIX com QR code dinâmico, consulta e verificação de webhook.

Requires env vars:
  PIX_API_URL        — base URL da API do PSP (ex: https://api.pix.psp.com/v1)
  PIX_CLIENT_ID      — client_id OAuth2
  PIX_CLIENT_SECRET  — client_secret OAuth2
  PIX_CERT_PATH      — caminho do certificado .p12/.pem (se exigido)
  PIX_KEY            — chave PIX da empresa (CNPJ/CPF/telefone/email)
  PIX_WEBHOOK_SECRET — secret para HMAC dos webhooks
"""

from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

PIX_API_URL = os.getenv("PIX_API_URL", "https://api.pix.example.com/v1")


class PixError(RuntimeError):
    """Erro na comunicação com a API PIX."""


class PixClient:
    """Cliente PIX próprio — conexão direta com PSP/banco.

    Fluxo:
      1. ``create_charge(amount_brl, key, payer_cpf)`` → QR code dinâmico
      2. Usuário lê o QR e paga pelo app do banco
      3. Webhook PSP → ``verify_webhook`` + atualização de status
      4. ``check_payment(txid)`` → consulta manual
    """

    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        cert_path: str = "",
    ):
        self.client_id = client_id or os.getenv("PIX_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("PIX_CLIENT_SECRET", "")
        self.cert_path = cert_path or os.getenv("PIX_CERT_PATH", "")
        self._token: str = ""
        self._token_expires: float = 0

    def _auth(self) -> str:
        """OAuth2 client_credentials para API PIX.

        Faz cache do token até 60s antes do expiry.
        """
        if self._token and datetime.now().timestamp() < self._token_expires - 60:
            return self._token
        resp = httpx.post(
            f"{PIX_API_URL}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            raise PixError(f"PIX auth failed: {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires = datetime.now().timestamp() + data.get("expires_in", 3600)
        return self._token

    def create_charge(
        self,
        amount_brl: float,
        key: str = "",
        payer_cpf: str = "",
    ) -> dict:
        """Cria cobrança PIX com QR code dinâmico.

        Args:
            amount_brl: Valor em reais.
            key: Chave PIX do recebedor (default: env PIX_KEY).
            payer_cpf: CPF do pagador (opcional, default: 000.000.000-00).

        Returns:
            dict com ``txid``, ``qr_code`` (copia-e-cola) e ``qr_code_base64`` (imagem).
        """
        txid = str(uuid.uuid4()).replace("-", "")[:35]
        pix_key = key or os.getenv("PIX_KEY", "")

        body = {
            "calendario": {"expiracao": 3600},
            "devedor": {
                "cpf": payer_cpf or "00000000000",
                "nome": "SpyFy User",
            },
            "valor": {"original": f"{amount_brl:.2f}"},
            "chave": pix_key,
            "solicitacaoPagador": "SpyFy",
        }

        resp = httpx.put(
            f"{PIX_API_URL}/cob/{txid}",
            json=body,
            headers={
                "Authorization": f"Bearer {self._auth()}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            raise PixError(f"PIX cobranca {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        return {
            "txid": txid,
            "qr_code": data.get("pixCopiaECola", ""),
            "qr_code_base64": data.get("imagemQrcode", ""),
            "expires_in": 3600,
        }

    def check_payment(self, txid: str) -> dict:
        """Consulta o status de uma cobrança PIX pelo txid."""
        resp = httpx.get(
            f"{PIX_API_URL}/cob/{txid}",
            headers={"Authorization": f"Bearer {self._auth()}"},
            timeout=10,
        )
        if resp.status_code != 200:
            raise PixError(f"PIX consulta {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        """Verifica assinatura HMAC-SHA256 do webhook PIX.

        Em modo dev (sem env PIX_WEBHOOK_SECRET), retorna True.
        """
        expected = os.getenv("PIX_WEBHOOK_SECRET", "")
        if not expected:
            return True  # dev mode
        computed = hmac.new(
            expected.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed, signature)
