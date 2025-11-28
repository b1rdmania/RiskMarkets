#!/usr/bin/env python3
"""
Script A: Deploy HIP-3 perp DEX + asset via registerAsset2 only.

Usage:
    NETWORK=testnet python3 scripts/deploy-dex.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment (.env.testnet by default)
env_file = os.getenv("ENV_FILE", ".env.testnet")
load_dotenv(env_file)

try:
    from eth_account import Account
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    from hyperliquid.utils.signing import sign_l1_action
    from hyperliquid.exchange import get_timestamp_ms
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account")
    sys.exit(1)


def required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"❌ Missing env var: {name}")
        sys.exit(1)
    return v


def main() -> None:
    pk = required("HL_MASTER_PRIVATE_KEY")
    dex = required("HL_DEX_NAME")
    coin = required("HL_COIN_SYMBOL")
    master = required("HL_MASTER_ADDRESS")
    initial_oracle_price = os.getenv("INITIAL_ORACLE_PRICE", "1924.5")

    wallet = Account.from_key(pk)
    print(f"✅ Builder wallet (signer/account): {wallet.address}")
    print(f"✅ Target master account:          {master}")
    print()

    exchange = Exchange(wallet=wallet, base_url=constants.TESTNET_API_URL)

    print("✅ Exchange client:")
    print(f"   base_url:       {exchange.base_url}")
    print(f"   account_address {exchange.account_address}")
    print()

    # Construct registerAsset2 action (no maxGas, uses marginMode)
    action = {
        "type": "perpDeploy",
        "registerAsset2": {
            "assetRequest": {
                "coin": coin,
                "szDecimals": 2,
                "oraclePx": initial_oracle_price,
                "marginTableId": 1,
                "marginMode": "strictIsolated",
            },
            "dex": dex,
            "schema": {
                "fullName": f"{dex} test DEX",
                "collateralToken": 0,
                "oracleUpdater": master.lower(),
            },
        },
    }

    print("📝 registerAsset2 action:")
    print(json.dumps(action, indent=2))
    print()

    nonce = get_timestamp_ms()
    is_mainnet = exchange.base_url == constants.MAINNET_API_URL

    print(f"🔐 Signing L1 action...")
    print(f"   nonce:     {nonce}")
    print(f"   is_mainnet {is_mainnet}")
    print()

    sig = sign_l1_action(
        wallet,
        action,
        None,  # active_pool / vaultAddress override: do NOT set
        nonce,
        exchange.expires_after,
        is_mainnet,
    )

    payload = {
        "action": action,
        "nonce": nonce,
        "signature": sig,
        "expiresAfter": exchange.expires_after,
    }

    print("📦 Full payload to /exchange:")
    print(json.dumps(payload, indent=2))
    print()

    result = exchange.post("/exchange", payload)

    print("📥 Raw HL response:")
    print(json.dumps(result, indent=2))

    if result.get("status") == "ok":
        print("\n🎉 registerAsset2 succeeded (DEX + asset created).")
    else:
        print("\n⚠️ registerAsset2 failed.")


if __name__ == "__main__":
    main()


