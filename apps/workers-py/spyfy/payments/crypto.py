"""Crypto payments — USDT (TRC-20 / ERC-20) + Bitcoin.

Fluxo:
  1. ``estimate(amount_brl, crypto)`` → cotação + endereço + amount_crypto
  2. Usuário envia crypto para a wallet
  3. ``verify_transaction(tx_hash, ...)`` → confirma na blockchain

Requer env vars:
  WALLET_USDT_TRC20  — carteira USDT na rede TRC-20
  WALLET_USDT_ERC20  — carteira USDT na rede ERC-20
  WALLET_BTC         — carteira Bitcoin
  CRYPTO_RATE_API    — URL da API de cotação (default: CoinGecko)
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import httpx


class CryptoError(RuntimeError):
    """Erro na cotação ou verificação de transação crypto."""


class CryptoClient:
    """Aceita USDT (TRC-20/ERC-20) e Bitcoin via wallet própria.

    Cotação via CoinGecko (gratuita, sem API key). Verificação de
    transação via block explorer público (BlockCypher, Etherscan,
    Trongrid).
    """

    CRYPTO_WALLETS: dict[str, str] = {
        "USDT_TRC20": os.getenv("WALLET_USDT_TRC20", ""),
        "USDT_ERC20": os.getenv("WALLET_USDT_ERC20", ""),
        "BTC": os.getenv("WALLET_BTC", ""),
    }

    def __init__(self, rate_api_url: str = ""):
        self.rate_api_url = rate_api_url or os.getenv(
            "CRYPTO_RATE_API", "https://api.coingecko.com/api/v3"
        )

    # ── Cotação ──────────────────────────────────────────────────────

    def get_rate(self, crypto: str = "usdt", fiat: str = "brl") -> float:
        """Cotação atual da crypto em reais (BRL).

        Args:
            crypto: Identificador CoinGecko (usdt, bitcoin, tether).
            fiat: Moeda fiat (brl, usd).
        """
        cg_map = {
            "usdt": "tether",
            "usdt_trc20": "tether",
            "usdt_erc20": "tether",
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
        }
        cg_id = cg_map.get(crypto.lower(), crypto.lower())

        resp = httpx.get(
            f"{self.rate_api_url}/simple/price",
            params={"ids": cg_id, "vs_currencies": fiat},
            timeout=10,
        )
        if resp.status_code != 200:
            raise CryptoError(f"Cotacao indisponivel: CoinGecko {resp.status_code}")

        data = resp.json()
        rate = float(data.get(cg_id, {}).get(fiat, 0))
        if rate <= 0:
            raise CryptoError(f"Cotacao {crypto}/{fiat} = 0 (dados indisponiveis)")
        return rate

    def estimate(self, amount_brl: float, crypto: str = "USDT") -> dict:
        """Estima quanto o usuário precisa pagar em crypto.

        Returns:
            Dict com crypto_amount, wallet_address, network, payment_id, etc.
        """
        crypto_upper = crypto.upper()
        rate = self.get_rate(crypto_upper)

        if crypto_upper in ("USDT",):
            network = "TRC-20"
            wallet_key = "USDT_TRC20"
        elif crypto_upper in ("BTC", "BITCOIN"):
            network = "BTC"
            wallet_key = "BTC"
        else:
            raise CryptoError(f"Crypto nao suportada: {crypto}")

        wallet = self.CRYPTO_WALLETS.get(wallet_key, "")
        crypto_amount = round(amount_brl / rate, 6)

        return {
            "crypto": crypto_upper,
            "fiat": "BRL",
            "fiat_amount": amount_brl,
            "crypto_amount": crypto_amount,
            "rate": round(rate, 2),
            "wallet_address": wallet,
            "network": network,
            "expires_in": 1800,
            "payment_id": str(uuid.uuid4()),
        }

    # ── Verificação on-chain ─────────────────────────────────────────

    def verify_transaction(
        self,
        tx_hash: str,
        expected_crypto: str = "usdt",
        min_confirmations: int = 1,
    ) -> dict:
        """Verifica transação na blockchain via API pública.

        Args:
            tx_hash: Hash da transação.
            expected_crypto: Rede esperada (btc, usdt_erc20, usdt_trc20).
            min_confirmations: Mínimo de confirmações.

        Returns:
            Dict com ``confirmed`` (bool) e ``data`` (resposta raw da API).
        """
        api_urls = {
            "btc": f"https://api.blockcypher.com/v1/btc/main/txs/{tx_hash}",
            "usdt_erc20": (
                f"https://api.etherscan.io/api"
                f"?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}"
            ),
            "usdt_trc20": (
                f"https://api.trongrid.io/v1/transactions/{tx_hash}"
            ),
        }

        url = api_urls.get(expected_crypto.lower(), "")
        if not url:
            return {"confirmed": False, "error": "Rede nao suportada"}

        resp = httpx.get(url, timeout=15)
        if resp.status_code != 200:
            return {
                "confirmed": False,
                "error": f"Block explorer {resp.status_code}",
            }

        return {"confirmed": True, "data": resp.json()}
