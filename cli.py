#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet
Usage examples in README.md
"""

import os
import sys
import argparse

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import place_order
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger("cli")


def get_client() -> BinanceClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("❌ Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set.")
        print("   Create a .env file or export them as environment variables.")
        sys.exit(1)

    return BinanceClient(api_key, api_secret)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

  # Stop-Market BUY (bonus)
  python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000

  # Check account balance
  python cli.py account
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- order subcommand ---
    order_parser = subparsers.add_parser("order", help="Place a futures order")
    order_parser.add_argument("--symbol",    required=True,  help="Trading pair, e.g. BTCUSDT")
    order_parser.add_argument("--side",      required=True,  help="BUY or SELL")
    order_parser.add_argument("--type",      required=True,  dest="order_type", help="MARKET, LIMIT, or STOP_MARKET")
    order_parser.add_argument("--quantity",  required=True,  help="Order quantity")
    order_parser.add_argument("--price",     required=False, default=None, help="Limit price (required for LIMIT orders)")
    order_parser.add_argument("--stop-price",required=False, default=None, dest="stop_price", help="Stop price (for STOP_MARKET)")

    # --- account subcommand ---
    subparsers.add_parser("account", help="View account balance summary")

    return parser


def cmd_order(args, client: BinanceClient):
    try:
        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as e:
        logger.warning("Validation error: %s", e)
        print(f"\n❌ Validation Error: {e}\n")
        sys.exit(1)
    except (ConnectionError, TimeoutError) as e:
        logger.error("Network error: %s", e)
        print(f"\n❌ Network Error: {e}\n")
        sys.exit(1)
    except RuntimeError as e:
        logger.error("API/runtime error: %s", e)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


def cmd_account(client: BinanceClient):
    print("\nFetching account info...")
    data = client.get_account_info()
    assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) > 0]
    if not assets:
        print("No assets found or unable to fetch account.")
        return
    print("\n" + "=" * 50)
    print("  ACCOUNT BALANCE")
    print("=" * 50)
    for asset in assets:
        print(f"  {asset['asset']:<8} Wallet: {float(asset['walletBalance']):.4f}  Available: {float(asset['availableBalance']):.4f}")
    print("=" * 50 + "\n")


def main():
    parser = build_parser()
    args = parser.parse_args()
    client = get_client()

    if args.command == "order":
        cmd_order(args, client)
    elif args.command == "account":
        cmd_account(client)


if __name__ == "__main__":
    main()
