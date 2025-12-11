#!/usr/bin/env python3
"""
Seed a HIP-3 perp orderbook using preset configs.

Example (testnet):
  NETWORK=testnet python3 scripts/seed-from-preset.py --market gdr
  NETWORK=testnet python3 scripts/seed-from-preset.py --market gdr --preset-file scripts/seed-presets.json --dry-run

Presets live in scripts/seed-presets.json and can be edited per index.
"""

import argparse
import json
import os
import sys
from typing import Dict, List

from dotenv import load_dotenv


def load_presets(path: str) -> Dict[str, dict]:
    if not os.path.exists(path):
        print(f"❌ Preset file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_orders(config: dict) -> List[dict]:
    mid = float(config["mid"])
    spread_bps = float(config.get("spread_bps", 25))
    step_bps = float(config.get("step_bps", 0))
    levels = int(config.get("levels", 1))
    size = float(config["size"])

    orders: List[dict] = []
    for level in range(levels):
        spread = spread_bps + level * step_bps
        factor = spread / 10000.0
        bid_px = round(mid * (1 - factor), 4)
        ask_px = round(mid * (1 + factor), 4)
        orders.append({"side": "buy", "price": bid_px, "size": size})
        orders.append({"side": "sell", "price": ask_px, "size": size})
    return orders


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a HIP-3 market from preset config.")
    parser.add_argument("--market", required=True, help="Preset key (e.g. gdr, esv, shr)")
    parser.add_argument(
        "--preset-file",
        default=os.path.join(os.path.dirname(__file__), "seed-presets.json"),
        help="Path to presets JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print orders without placing them",
    )
    args = parser.parse_args()

    env_file = os.getenv("ENV_FILE", ".env.testnet")
    load_dotenv(env_file)

    presets = load_presets(args.preset_file)
    key = args.market.lower()
    if key not in presets:
        print(f"❌ Preset {args.market} not found in {args.preset_file}", file=sys.stderr)
        sys.exit(1)

    preset = presets[key]
    coin = preset["coin"]
    orders = generate_orders(preset)

    print(f"✅ Using preset '{key}' for coin={coin}")
    print(f"   mid={preset['mid']}, spread_bps={preset.get('spread_bps', 25)}, levels={preset.get('levels', 1)}, size={preset['size']}")

    if args.dry_run:
        print("💤 Dry-run mode; generated orders:")
        print(json.dumps(orders, indent=2))
        sys.exit(0)

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

    order_type: OrderType = {"limit": {"tif": "Gtc"}}

    results: List[dict] = []
    for order in orders:
        is_buy = order["side"] == "buy"
        print(f"➡️  {order['side']} {order['size']} {coin} @ {order['price']}", file=sys.stderr)
        try:
            resp = exchange.order(
                name=coin,
                is_buy=is_buy,
                sz=order["size"],
                limit_px=order["price"],
                order_type=order_type,
                reduce_only=False,
            )
            results.append({"ok": True, "side": order["side"], "price": order["price"], "size": order["size"], "response": resp})
        except Exception as e:
            results.append({"ok": False, "side": order["side"], "price": order["price"], "size": order["size"], "error": str(e)})

    print(json.dumps({"coin": coin, "orders": results}, indent=2))

    failures = [r for r in results if not r.get("ok")]
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()

