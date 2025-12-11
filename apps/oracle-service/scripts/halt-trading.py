#!/usr/bin/env python3
"""
Toggle trading halt state for a HIP-3 perp market (haltTrading action).

This is the "unhalt" / "re-enable trading" path support pointed to:

    {
      "type": "perpDeploy",
      "haltTrading": { "coin": string, "isHalted": boolean },
    }

Usage examples (testnet):

    # Unhalt a single market
    NETWORK=testnet python3 scripts/halt-trading.py --coin wa:XAU2 --halted false

    # Explicitly halt a market again
    NETWORK=testnet python3 scripts/halt-trading.py --coin wa:XAU2 --halted true

Relies on the same single-wallet, builder/master model as the other scripts:
  - HL_MASTER_ADDRESS          (builder/master account)
  - HL_MASTER_PRIVATE_KEY      (wallet private key)
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv


def main() -> None:
    # Load env (same convention as other scripts)
    env_file = os.getenv("ENV_FILE", ".env.testnet")
    load_dotenv(env_file)

    parser = argparse.ArgumentParser(description="Toggle haltTrading for a HIP-3 perp market.")
    parser.add_argument(
        "--coin",
        required=True,
        help="Full coin id, e.g. wa:XAU2",
    )
    parser.add_argument(
        "--halted",
        required=True,
        choices=["true", "false", "True", "False", "0", "1"],
        help="Whether the market should be halted (true/false). Use false to re-enable trading.",
    )
    args = parser.parse_args()

    # Normalise halted flag
    halted_str = args.halted.lower()
    if halted_str in ("true", "1"):
        is_halted = True
    elif halted_str in ("false", "0"):
        is_halted = False
    else:
        print(f"❌ Invalid --halted value: {args.halted}", file=sys.stderr)
        sys.exit(1)

    # Basic env
    hl_master_address = os.getenv("HL_MASTER_ADDRESS")
    hl_master_private_key = os.getenv("HL_MASTER_PRIVATE_KEY")

    if not hl_master_private_key:
        print("❌ Error: Missing HL_MASTER_PRIVATE_KEY in environment", file=sys.stderr)
        sys.exit(1)
    if not hl_master_address:
        print("❌ Error: Missing HL_MASTER_ADDRESS in environment", file=sys.stderr)
        sys.exit(1)

    # Import Hyperliquid SDK pieces
    try:
        import eth_account
        from hyperliquid.exchange import Exchange, get_timestamp_ms
        from hyperliquid.utils import constants
        from hyperliquid.utils.signing import sign_l1_action
    except ImportError as e:
        print(f"❌ Error: Hyperliquid Python SDK not installed: {e}", file=sys.stderr)
        print("   Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account", file=sys.stderr)
        sys.exit(1)

    # Wallet / exchange client
    api_wallet = eth_account.Account.from_key(hl_master_private_key)
    exchange = Exchange(api_wallet, constants.TESTNET_API_URL)

    # Optional sanity check (same pattern as set-oracle.py)
    EXPECTED_API_ADDRESS = "0x47515db2eab01758c740ab220352a34b8d5a3826"
    if api_wallet.address.lower() != EXPECTED_API_ADDRESS.lower():
        print("❌ Error: API wallet address mismatch", file=sys.stderr)
        print(f"   Expected: {EXPECTED_API_ADDRESS}", file=sys.stderr)
        print(f"   Got:      {api_wallet.address}", file=sys.stderr)
        sys.exit(1)

    # Log important context to stderr so stdout can stay JSON-only if needed
    print(f"✅ API wallet (agent): {api_wallet.address}", file=sys.stderr)
    print(f"✅ Master account:     {hl_master_address}", file=sys.stderr)
    print(f"➡️  haltTrading coin={args.coin}, isHalted={is_halted}", file=sys.stderr)

    # Build haltTrading action
    action = {
        "type": "perpDeploy",
        "haltTrading": {
            "coin": args.coin,
            "isHalted": is_halted,
        },
    }

    timestamp = get_timestamp_ms()
    signature = sign_l1_action(
        api_wallet,
        action,
        None,  # vaultAddress / activePool override – let HL infer from signer
        timestamp,
        exchange.expires_after,
        exchange.base_url == constants.MAINNET_API_URL,
    )

    payload = {
        "action": action,
        "nonce": timestamp,
        "signature": signature,
        "expiresAfter": exchange.expires_after,
    }

    try:
        result = exchange.post("/exchange", payload)

        # Print machine-readable result on stdout
        out = {
            "ok": result.get("status") == "ok",
            "status": result.get("status"),
            "response": result.get("response"),
            "coin": args.coin,
            "isHalted": is_halted,
        }
        print(json.dumps(out))

        if result.get("status") == "ok":
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(e),
                    "coin": args.coin,
                    "isHalted": is_halted,
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()



