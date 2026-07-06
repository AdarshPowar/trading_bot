"""
CLI entry point for the trading bot.

Usage:
    python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000

API credentials are read from environment variables so they never end
up hard-coded or accidentally committed:
    BINANCE_TESTNET_API_KEY
    BINANCE_TESTNET_API_SECRET
"""

import argparse
import os
import sys

from bot.client import BinanceFuturesTestnetClient, TradingBotError
from bot.logging_config import setup_logging
from bot.orders import submit_order


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument(
        "--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT"
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side"
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument(
        "--price", required=False, type=float, default=None, help="Price (required for LIMIT orders)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log verbosity (file log always captures DEBUG and above)",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = setup_logging(args.log_level)

    api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
    api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")

    try:
        client = BinanceFuturesTestnetClient(api_key, api_secret)
    except TradingBotError as exc:
        logger.error("Startup failed: %s", exc)
        print(f"Error: {exc}")
        return 1

    result = submit_order(
        client=client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )

    if result.success:
        print(f"SUCCESS: {result.message}")
        return 0
    else:
        print(f"FAILED: {result.message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
