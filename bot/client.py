"""
Thin wrapper around python-binance's Futures Testnet client.

Isolating all direct API/network calls here (rather than in cli.py)
means the CLI layer never needs to know about HTTP, signing, or the
Binance SDK - it just calls place_order() and gets back a plain dict
or an exception.
"""

import logging
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from bot.validators import OrderRequest

FUTURES_TESTNET_BASE_URL = "demo-fapi.binance.com"

logger = logging.getLogger("trading_bot")


class TradingBotError(Exception):
    """Raised for any failure while communicating with the exchange."""


class BinanceFuturesTestnetClient:
    """
    Wraps the python-binance Client, pinned to the Futures Testnet.

    All methods log the outgoing request and the raw response/error so
    that every order attempt is traceable in the log file.
    """

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise TradingBotError(
                "Missing API credentials. Set BINANCE_TESTNET_API_KEY and "
                "BINANCE_TESTNET_API_SECRET (env vars) or pass them explicitly."
            )
        try:
            self._client = Client(api_key, api_secret, testnet=True)
            # python-binance's testnet flag targets spot testnet by default;
            # explicitly point the futures endpoint at the futures testnet.
            self._client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"
        except Exception as exc:  # SDK init failures (e.g. bad key format)
            logger.error("Failed to initialize Binance client: %s", exc)
            raise TradingBotError(f"Could not initialize Binance client: {exc}") from exc

    def place_order(self, order: OrderRequest) -> dict:
        """
        Submit a MARKET or LIMIT order to Binance Futures Testnet.

        Args:
            order: A validated OrderRequest.

        Returns:
            The raw order response dict from Binance
            (orderId, status, executedQty, avgPrice, etc.).

        Raises:
            TradingBotError: on any API, order, network, or unexpected error.
        """
        params = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
        }
        if order.order_type == "LIMIT":
            params["price"] = order.price
            params["timeInForce"] = "GTC"  # Good-Til-Cancelled, required for LIMIT orders

        logger.info("Submitting order request: %s", params)
        logger.debug("Full order request payload: %s", params)

        try:
            response = self._client.futures_create_order(**params)
            logger.info(
                "Order accepted | orderId=%s status=%s executedQty=%s avgPrice=%s",
                response.get("orderId"),
                response.get("status"),
                response.get("executedQty"),
                response.get("avgPrice"),
            )
            logger.debug("Full order response: %s", response)
            return response

        except (BinanceAPIException, BinanceOrderException) as exc:
            logger.error("Binance API rejected the order: %s", exc)
            raise TradingBotError(f"Order rejected by Binance: {exc}") from exc

        except BinanceRequestException as exc:
            logger.error("Malformed request sent to Binance: %s", exc)
            raise TradingBotError(f"Malformed request: {exc}") from exc

        except (ConnectionError, TimeoutError) as exc:
            logger.error("Network error while contacting Binance: %s", exc)
            raise TradingBotError(f"Network error, please check your connection: {exc}") from exc

        except Exception as exc:  # catch-all so the CLI never crashes uncontrolled
            logger.error("Unexpected error while placing order: %s", exc)
            raise TradingBotError(f"Unexpected error: {exc}") from exc

    def get_account_balance(self) -> Optional[list]:
        """Convenience helper: fetch USDT-M futures account balances (used for a quick connectivity check)."""
        try:
            balances = self._client.futures_account_balance()
            logger.debug("Fetched account balance: %s", balances)
            return balances
        except Exception as exc:
            logger.error("Failed to fetch account balance: %s", exc)
            raise TradingBotError(f"Could not fetch account balance: {exc}") from exc
