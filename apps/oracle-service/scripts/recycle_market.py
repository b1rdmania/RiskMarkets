#!/usr/bin/env python3
"""
Recycle an existing HIP-3 market by pushing a static oracle price twice.

This does NOT call any hidden haltTrading API – it simply:
  1) Sets HL_DEX_NAME / HL_COIN_SYMBOL based on --coin (dex:ASSET)
  2) Calls scripts/set-oracle.py twice with the given price

Usage:
    NETWORK=testnet python3 scripts/recycle_market.py --coin wa:XAU2 --price 4235.12

After this, place tiny limit orders at the oracle price in the UI to
bootstrap OI, then restart the oracle-service to resume live updates.
"""

import argparse
import os
import subprocess
import sys
import time

from dotenv import load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coin", required=True, help="Coin id in form dex:ASSET (e.g. wa:XAU2)")
    parser.add_argument("--price", required=True, help="Static price to push twice, e.g. 4235.12")
    args = parser.parse_args()

    env_file = os.getenv("ENV_FILE", ".env.testnet")
    load_dotenv(env_file)

    try:
        dex_tag, asset_name = args.coin.split(":", 1)
    except ValueError:
        print("❌ --coin must be of form dex:ASSET, e.g. wa:XAU2", file=sys.stderr)
        sys.exit(1)

    dex_tag = dex_tag.lower()
    asset_name = asset_name.upper()

    print(f"♻️  Recycling market: coin={args.coin}")
    print(f"   Using dex={dex_tag}, asset={asset_name}, price={args.price}")

    # Prepare environment for child calls to set-oracle.py
    child_env = os.environ.copy()
    child_env["ENV_FILE"] = env_file
    child_env["NETWORK"] = child_env.get("NETWORK", "testnet")
    child_env["HL_DEX_NAME"] = dex_tag
    child_env["HL_COIN_SYMBOL"] = asset_name

    script_path = os.path.join(os.path.dirname(__file__), "set-oracle.py")
    if not os.path.exists(script_path):
        print(f"❌ Cannot find set-oracle script at {script_path}", file=sys.stderr)
        sys.exit(1)

    # Push static oracle price twice
    for i in range(2):
        print(f"➡️  Push {i + 1}/2: setOracle(dex={dex_tag}, coin={dex_tag}:{asset_name}, price={args.price})")
        try:
            out = subprocess.check_output(
                ["python3", script_path, str(args.price)],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
                env=child_env,
                stderr=sys.stderr,
                text=True,
            )
            print(out.strip())
        except subprocess.CalledProcessError as e:
            print(f"❌ set-oracle.py failed on push {i + 1}: {e}", file=sys.stderr)
            sys.exit(1)

        if i == 0:
            time.sleep(5)

    print("✅ Static oracle pushed twice. Now place tiny 0.01 trades at this price in the UI,")
    print("   then restart the oracle-service (npm run dev) if you want live Pyth again.")


if __name__ == "__main__":
    main()


