#!/usr/bin/env python3
"""
Seed tiny perp orders on a HIP-3 market to help build initial chart history.

Usage (testnet example):

    # Place a single tiny GTC bid on wa:XAU2 at a given price
    NETWORK=testnet python3 scripts/seed-orders.py --coin wa:XAU2 --side buy --size 0.01 --price 4235.2

    # Place a small ask
    NETWORK=testnet python3 scripts/seed-orders.py --coin wa:XAU2 --side sell --size 0.01 --price 4235.4

Env:
  - ENV_FILE (default .env.testnet)
  - HL_MASTER_ADDRESS
  - HL_MASTER_PRIVATE_KEY
"""

import argparse
import os
import sys
import json

from dotenv import load_dotenv


def main() -> None:
    env_file = os.getenv("ENV_FILE", ".env.testnet")
    load_dotenv(env_file)

    parser = argparse.ArgumentParser(description="Place a tiny perp order on a HIP-3 market.")
    parser.add_argument("--coin", required=True, help="Full coin id, e.g. wa:XAU2")
    parser.add_argument("--side", required=True, choices=["buy", "sell"], help="Order side")
    parser.add_argument("--size", required=True, type=float, help="Order size in contract units")
    parser.add_argument("--price", required=True, type=float, help="Limit price")
    args = parser.parse_args()

    hl_master_address = os.getenv("HL_MASTER_ADDRESS")
    hl_master_private_key = os.getenv("HL_MASTER_PRIVATE_KEY")

    if not hl_master_private_key:
        print("❌ Error: Missing HL_MASTER_PRIVATE_KEY in env", file=sys.stderr)
        sys.exit(1)
    if not hl_master_address:
        print("❌ Error: Missing HL_MASTER_ADDRESS in env", file=sys.stderr)
        sys.exit(1)

    try:
        import eth_account
        from hyperliquid.exchange import Exchange, OrderType
        from hyperliquid.utils import constants
    except ImportError as e:
        print(f"❌ Missing dependency: {e}", file=sys.stderr)
        print("   Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account", file=sys.stderr)
        sys.exit(1)

    api_wallet = eth_account.Account.from_key(hl_master_private_key)
    exchange = Exchange(api_wallet, constants.TESTNET_API_URL)

    # Simple GTC limit
    order_type: OrderType = {"limit": {"tif": "Gtc"}}
    is_buy = args.side == "buy"

    print(f"✅ Wallet: {api_wallet.address}", file=sys.stderr)
    print(f"➡️  Placing {args.side} {args.size} {args.coin} @ {args.price}", file=sys.stderr)

    try:
        resp = exchange.order(
            name=args.coin,
            is_buy=is_buy,
            sz=args.size,
            limit_px=args.price,
            order_type=order_type,
            reduce_only=False,
        )
        print(json.dumps(resp, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()



