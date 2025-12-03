#!/usr/bin/env python3
"""
HIP-3 perp DEX + asset deployment using the SDK's registerAsset helper.

Usage:
    NETWORK=testnet python3 scripts/deploy-dex.py

Behavior:
- Uses ONE wallet as both signer and builder account:
    HL_MASTER_ADDRESS == Account(HL_MASTER_PRIVATE_KEY).address
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
        from hyperliquid.exchange import Exchange
        from hyperliquid.utils import constants
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account")
        sys.exit(1)

    # Single-wallet model: this is both the signer and the builder/master account.
    master_address = required("HL_MASTER_ADDRESS")
    master_private_key = required("HL_MASTER_PRIVATE_KEY")

    # HIP-3 DEX naming:
    # - HL_DEX_NAME: short 2–4 char lowercase dex tag, e.g. "war"
    # - HL_COIN_SYMBOL: asset symbol, e.g. "gdr"
    dex = required("HL_DEX_NAME").lower()
    coin = required("HL_COIN_SYMBOL")
    initial_oracle_price = os.getenv("INITIAL_ORACLE_PRICE", "100.0")

    # Build wallet from private key
    wallet = Account.from_key(master_private_key)

    print("🚀 HIP-3 DEX Deployment via SDK (registerAsset)")
    print(f"   DEX:                 {dex}")
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
        print(f"   - HL_MASTER_ADDRESS:           {master_address}")
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

    # Schema metadata for the DEX.
    schema = {
        "fullName": f"{dex}:{coin} Test DEX",
        "collateralToken": 0,
        "oracleUpdater": wallet.address.lower(),
    }

    print("📝 Calling exchange.perp_deploy_register_asset(...)")
    print(f"   dex:             {dex}")
    print(f"   coin:            {coin}")
    print(f"   sz_decimals:     2")
    print(f"   oracle_px:       {initial_oracle_price}")
    print(f"   margin_table_id: 1")
    print(f"   only_isolated:   True")
    print(f"   schema:          {json.dumps(schema)}")
    print()

    try:
        # max_gas: generous value; deployer auction will charge what it needs.
        result = exchange.perp_deploy_register_asset(
            dex=dex,
            max_gas=5_000_000,
            coin=coin,
            sz_decimals=2,
            oracle_px=initial_oracle_price,
            margin_table_id=1,
            only_isolated=True,
            schema=schema,
        )
    except AttributeError:
        print("❌ Exchange.perp_deploy_register_asset is not available on this SDK version.")
        print("   Please upgrade hyperliquid-python-sdk to the latest version and retry.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error calling perp_deploy_register_asset: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("📥 Raw Hyperliquid response:")
    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and result.get("status") == "ok":
        print("\n🎉 perp_deploy_register_asset succeeded (DEX + asset created).")
    else:
        print("\n⚠️ perp_deploy_register_asset did not return status == 'ok'.")
        print("   Please share this script, your SDK version, and the response above with Hyperliquid if needed.")


if __name__ == "__main__":
    main()

