"""
Input validation for order requests.

Keeping validation separate from the CLI and client layers means the
same rules can be reused (and unit tested) regardless of whether input
originates from argparse, a future GUI, or another caller.
"""

import re
from dataclasses import dataclass
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}

# Binance Futures symbols are uppercase alphanumeric, e.g. BTCUSDT, ETHUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class ValidationError(Exception):
    """Raised when user-supplied order input fails validation."""


@dataclass
class OrderRequest:
    """A validated, normalized order ready to be sent to the API layer."""

    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None


def validate_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> OrderRequest:
    """
    Validate and normalize raw CLI input into an OrderRequest.

    Raises:
        ValidationError: if any field is missing, malformed, or inconsistent
            (e.g. a LIMIT order submitted without a price).
    """
    if not symbol:
        raise ValidationError("Symbol is required (e.g. BTCUSDT).")
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected an uppercase alphanumeric "
            "trading pair like 'BTCUSDT'."
        )

    if not side:
        raise ValidationError("Side is required (BUY or SELL).")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")

    if not order_type:
        raise ValidationError("Order type is required (MARKET or LIMIT).")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )

    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError(f"Quantity must be positive, got {quantity}.")

    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValidationError(f"Price must be positive, got {price}.")
    else:
        # MARKET orders ignore any supplied price
        price = None

    return OrderRequest(
        symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price
    )
