"""
Order placement orchestration.

Sits between the CLI and the client: builds the validated OrderRequest,
prints a clear before/after summary, and translates client-layer
exceptions into a simple success/failure result the CLI can display.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from bot.client import BinanceFuturesTestnetClient, TradingBotError
from bot.validators import OrderRequest, ValidationError, validate_order

logger = logging.getLogger("trading_bot")


@dataclass
class OrderResult:
    success: bool
    message: str
    response: Optional[dict] = None


def print_order_summary(order: OrderRequest) -> None:
    """Print a clear, human-readable summary of the order about to be sent."""
    print("\n--- Order Request Summary ---")
    print(f"  Symbol:     {order.symbol}")
    print(f"  Side:       {order.side}")
    print(f"  Type:       {order.order_type}")
    print(f"  Quantity:   {order.quantity}")
    if order.order_type == "LIMIT":
        print(f"  Price:      {order.price}")
    print("------------------------------\n")


def print_order_response(response: dict) -> None:
    """Print the key fields of Binance's order response."""
    print("--- Order Response ---")
    print(f"  Order ID:      {response.get('orderId')}")
    print(f"  Status:        {response.get('status')}")
    print(f"  Executed Qty:  {response.get('executedQty')}")
    print(f"  Avg Price:     {response.get('avgPrice', 'N/A')}")
    print("-----------------------\n")


def submit_order(
    client: BinanceFuturesTestnetClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> OrderResult:
    """
    Validate input, submit the order, and return a structured result.

    This is the single entry point the CLI layer calls - it never talks
    to the Binance client directly.
    """
    try:
        order: OrderRequest = validate_order(symbol, side, order_type, quantity, price)
    except ValidationError as exc:
        logger.warning("Validation failed: %s", exc)
        return OrderResult(success=False, message=f"Invalid input: {exc}")

    print_order_summary(order)

    try:
        response = client.place_order(order)
    except TradingBotError as exc:
        return OrderResult(success=False, message=str(exc))

    print_order_response(response)
    return OrderResult(
        success=True,
        message=f"{order.order_type} {order.side} order for {order.symbol} placed successfully.",
        response=response,
    )
