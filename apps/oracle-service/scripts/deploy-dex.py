#!/usr/bin/env python3
"""
Clean HIP-3 perp DEX + asset deployment using SDK-only path.

Usage:
    NETWORK=testnet python3 scripts/deploy-dex.py

Behavior:
- Uses ONE wallet as both signer and builder account:
    HL_MASTER_ADDRESS == Account(HL_API_PRIVATE_KEY).address
- Uses Exchange.perp_deploy_register_asset (no manual sign_l1_action, no custom payload).
"""

import os
import sys
import json
from dotenv import load_dotenv


# Load environment (.env.testnet by default)
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
        from eth_account import Account
        from hyperliquid.exchange import Exchange, get_timestamp_ms
        from hyperliquid.utils import constants
        from hyperliquid.utils.signing import sign_l1_action
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account")
        sys.exit(1)

    # Single-wallet model: this is both the signer and the builder/master account.
    master_address = required("HL_MASTER_ADDRESS")
    master_private_key = required("HL_MASTER_PRIVATE_KEY")

    # HIP-3 DEX naming for first-time deploy:
    # - Env provides a human DEX tag (2–4 lowercase chars) and coin:
    #     HL_DEX_NAME=war
    #     HL_COIN_SYMBOL=gdr
    # - For RegisterAsset2, `dex` is just the DEX tag ("war"), and `coin` is the asset ("gdr").
    raw_dex = required("HL_DEX_NAME").lower()
    coin = required("HL_COIN_SYMBOL")
    dex = raw_dex
    initial_oracle_price = os.getenv("INITIAL_ORACLE_PRICE", "1924.5")

    # Build wallet from private key
    wallet = Account.from_key(master_private_key)

    print("🚀 HIP-3 DEX Deployment using RegisterAsset2 (first-time DEX init)")
    print(f"   Human DEX tag:       {raw_dex}")
    print(f"   DEX (HL short):      {dex}")
    print(f"   Coin:                {coin}")
    print(f"   Initial oracle px:   {initial_oracle_price}")
    print()
    print(f"✅ Wallet (signer):     {wallet.address}")
    print(f"✅ Master address env:  {master_address}")
    print()

    # Enforce the "one wallet" invariant to avoid identity confusion.
    if wallet.address.lower() != master_address.lower():
        print("❌ HL_MASTER_ADDRESS must match the address derived from HL_MASTER_PRIVATE_KEY.")
        print("   Current values:")
        print(f"   - HL_MASTER_ADDRESS:         {master_address}")
        print(f"   - HL_MASTER_PRIVATE_KEY -> addr {wallet.address}")
        sys.exit(1)

    # Initialize Exchange: no account_address override, no vault, no manual signing.
    exchange = Exchange(
        wallet=wallet,
        base_url=constants.TESTNET_API_URL,
    )

    print("✅ Exchange client:")
    print(f"   base_url:        {exchange.base_url}")
    print(f"   account_address: {exchange.account_address}")
    print()

    # Build RegisterAsset2 action: first-time DEX + asset registration.
    schema = {
        "fullName": f"{dex}:{coin} Test DEX",
        "collateralToken": 0,
        "oracleUpdater": wallet.address.lower(),
    }

    print("📝 Calling RegisterAsset2 via signed L1 action...")
    print(f"   dex (2-4 chars): {dex}")
    print(f"   coin:            {coin}")
    print(f"   sz_decimals:     2")
    print(f"   oracle_px:       {initial_oracle_price}")
    print(f"   margin_table_id: 1")
    print(f"   onlyIsolated:    True")
    print(f"   schema:          {json.dumps(schema)}")
    print()

    # Construct registerAsset2 action matching SDK's signing pattern as closely as possible.
    timestamp = get_timestamp_ms()
    action = {
        "type": "perpDeploy",
        "registerAsset2": {
            "maxGas": 5_000_000,
            "assetRequest": {
                "coin": coin,
                "szDecimals": 2,
                "oraclePx": initial_oracle_price,
                "marginTableId": 1,
                # HIP-3 docs often use marginMode for registerAsset2.
                "marginMode": "strictIsolated",
            },
            "dex": dex,
            "schema": schema,
        },
    }

    try:
        signature = sign_l1_action(
            exchange.wallet,
            action,
            None,
            timestamp,
            exchange.expires_after,
            exchange.base_url == constants.MAINNET_API_URL,
        )

        result = exchange._post_action(
            action,
            signature,
            timestamp,
        )
    except Exception as e:
        print(f"❌ Error calling RegisterAsset2: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("📥 Raw Hyperliquid response:")
    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and result.get("status") == "ok":
        print("\n🎉 perp_deploy_register_asset succeeded (DEX + asset created).")
        print("   You can now enable HL_PUBLISH_ENABLED and wire up set_oracle using the same SDK path.")
    else:
        print("\n⚠️ perp_deploy_register_asset did not return status == 'ok'.")
        print("   If the error is 'User or API Wallet 0x.... does not exist' with a random address,")
        print("   send this exact script, your SDK version, and the response above to Hyperliquid.")


if __name__ == "__main__":
    main()
