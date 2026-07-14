"""SpyFy Anti-Fraud — Multi-layer fraud prevention.

Camadas:
  1. Rate limit por user/IP (5 tentativas / 60s)
  2. Validação de valor (máx R$ 5.000 / transação)
  3. Validação de email (regex)
  4. HMAC-SHA256 anti-tamper (sign_payload / verify_signature)
  5. Bloqueio de países sancionados

Todas as camadas funcionam em modo dev (sem envs configuradas)
com defaults seguros.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from collections import defaultdict
from typing import Any


class AntiFraud:
    """Anti-fraude multi-camada.

    Uso:
        fraud = AntiFraud()
        if not fraud.rate_limit(user_id):
            raise HTTPException(429, "...")
        ok, msg = fraud.validate_amount(amount)
        if not ok: raise HTTPException(422, msg)
    """

    def __init__(self) -> None:
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._rate_limit_window: int = 60   # segundos
        self._max_attempts: int = 5         # máx por janela
        self._max_amount_brl: float = 5000  # valor máximo
        self._blocked_ips: set[str] = set()
        self._email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    # ── Rate Limit ───────────────────────────────────────────────────

    def rate_limit(self, key: str) -> bool:
        """Verifica rate limit por chave (user_id, IP, etc).

        Permite até ``_max_attempts`` requisições em ``_rate_limit_window``
        segundos. Sliding window.

        Returns:
            True se dentro do limite, False se bloqueado.
        """
        now = time.time()
        window = self._rate_limit_window
        attempts = [
            t for t in self._attempts[key] if now - t < window
        ]
        self._attempts[key] = attempts
        if len(attempts) >= self._max_attempts:
            return False
        self._attempts[key].append(now)
        return True

    def reset_rate_limit(self, key: str) -> None:
        """Reseta o contador de rate limit para uma chave."""
        self._attempts.pop(key, None)

    # ── Validação de valor ───────────────────────────────────────────

    def validate_amount(self, amount_brl: float) -> tuple[bool, str]:
        """Valida valor da transação.

        Returns:
            (ok: bool, mensagem_erro: str)
        """
        if amount_brl <= 0:
            return False, "Valor inválido"
        if amount_brl > self._max_amount_brl:
            return (
                False,
                f"Valor máximo por transação: R$ {self._max_amount_brl:,.2f}",
            )
        return True, ""

    # ── Validação de email ───────────────────────────────────────────

    def validate_email(self, email: str) -> bool:
        """Valida formato de email."""
        return bool(self._email_re.match(email))

    # ── HMAC anti-tamper ─────────────────────────────────────────────

    def sign_payload(self, payload: dict, secret: str = "") -> str:
        """HMAC-SHA256 da requisição (anti-tamper).

        O payload é serializado sort_keys + separators compactos para
        garantir determinismo cross-linguagem.
        """
        s = secret or os.getenv("PAYMENT_SIGNING_SECRET", "dev_secret")
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hmac.new(s.encode(), raw.encode(), hashlib.sha256).hexdigest()

    def verify_signature(
        self, payload: dict, signature: str, secret: str = ""
    ) -> bool:
        """Verifica assinatura HMAC-SHA256."""
        expected = self.sign_payload(payload, secret)
        return hmac.compare_digest(expected, signature)

    # ── Bloqueio geográfico ──────────────────────────────────────────

    def is_blocked_country(self, country: str) -> bool:
        """Bloqueia países sancionados/de alto risco."""
        blocked: set[str] = {"KP", "IR", "SY", "CU", "RU"}
        return country.upper() in blocked

    # ── Configuração dinâmica ────────────────────────────────────────

    def set_max_amount(self, value: float) -> None:
        """Altera o valor máximo permitido por transação."""
        self._max_amount_brl = value

    def set_rate_limit(self, max_attempts: int, window_sec: int) -> None:
        """Altera os parâmetros de rate limit."""
        self._max_attempts = max_attempts
        self._rate_limit_window = window_sec
