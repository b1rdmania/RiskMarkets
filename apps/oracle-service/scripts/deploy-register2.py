#!/usr/bin/env python3
"""
One-shot HIP-3 DEX + asset deployment using RegisterAsset2 directly.

This follows the documented type exactly:

  type RegisterAsset2 = { maxGas?, assetRequest, dex, schema? }

and sends a single `perpDeploy.registerAsset2` action to /exchange, signed with
the builder wallet (single EOA, 100 HYPE staked, abstractions off).

Env (example):

  NETWORK=testnet

  HL_MASTER_ADDRESS=0x47515db2eab01758c740ab220352a34b8d5a3826
  HL_MASTER_PRIVATE_KEY=0x562ceba358986532fea84347f412e0d282783bdaf4b3bd79134f6ddacba9d3fa

  # 2–4 char dex tag and coin symbol
  HL_DEX_NAME=war
  HL_COIN_SYMBOL=gdr

  INITIAL_ORACLE_PRICE=100.0
"""

import json
import os
import sys
import time

from dotenv import load_dotenv


env_file = os.getenv("ENV_FILE", ".env.testnet")
load_dotenv(env_file)


def required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        print(f"❌ Missing env var: {name}")
        sys.exit(1)
    return v


def main() -> None:
    try:
        import requests
        from eth_account import Account
        from hyperliquid.utils import constants
        from hyperliquid.utils.signing import sign_l1_action
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account requests")
        sys.exit(1)

    base_url = constants.TESTNET_API_URL

    pk = required("HL_MASTER_PRIVATE_KEY")
    master_address = required("HL_MASTER_ADDRESS")
    dex = required("HL_DEX_NAME").lower()  # 2–4 lowercase chars
    asset_name = required("HL_COIN_SYMBOL").upper()
    # Per HIP-3 examples, coin identifier should be "{dex_name}:{ASSET_NAME}" (ASSET_NAME uppercase).
    coin = f"{dex}:{asset_name}"
    initial_oracle_price = os.getenv("INITIAL_ORACLE_PRICE", "100.0")

    wallet = Account.from_key(pk)

    print("🚀 HIP-3 DEX Deployment via RegisterAsset2 (direct)")
    print(f"   Base URL:      {base_url}")
    print(f"   DEX tag:       {dex}")
    print(f"   Asset name:    {asset_name}")
    print(f"   Coin (HL id):  {coin}")
    print(f"   Oracle px:     {initial_oracle_price}")
    print()
    print(f"✅ Wallet (signer): {wallet.address}")
    print(f"✅ Master address:  {master_address}")
    print()

    if wallet.address.lower() != master_address.lower():
        print("❌ HL_MASTER_ADDRESS must match the address derived from HL_MASTER_PRIVATE_KEY.")
        print(f"   HL_MASTER_ADDRESS:           {master_address}")
        print(f"   HL_MASTER_PRIVATE_KEY -> addr {wallet.address}")
        sys.exit(1)

    # Build RegisterAsset2 action for first-time DEX + asset.
    action = {
        "type": "perpDeploy",
        "registerAsset2": {
            "maxGas": 5_000_000,
            "assetRequest": {
                "coin": coin,
                "szDecimals": 2,
                "oraclePx": str(initial_oracle_price),
                "marginTableId": 1,
                "marginMode": "strictIsolated",
            },
            "dex": dex,
            "schema": {
                "fullName": f"{dex}:{coin} Test DEX",
                "collateralToken": 0,
                "oracleUpdater": wallet.address.lower(),
            },
        },
    }

    print("📝 RegisterAsset2 action:")
    print(json.dumps(action, indent=2))
    print()

    nonce = int(time.time() * 1000)

    signature = sign_l1_action(
        wallet,
        action,
        None,        # vaultAddress
        nonce,
        None,        # expiresAfter
        False,       # is_mainnet
    )

    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None,
        "expiresAfter": None,
    }

    print("📦 Payload to /exchange:")
    print(json.dumps(payload, indent=2))
    print()

    resp = requests.post(
        f"{base_url}/exchange",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )

    print(f"📥 HTTP {resp.status_code}")
    print(resp.text)


if __name__ == "__main__":
    main()


