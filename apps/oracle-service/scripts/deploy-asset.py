#!/usr/bin/env python3
"""
Register an additional HIP-3 asset on an existing perp DEX.

Usage:
    NETWORK=testnet python3 scripts/deploy-asset.py

Assumes:
  - The DEX already exists (e.g. created via deploy-dex.py).
  - Single-wallet model: HL_MASTER_ADDRESS / HL_MASTER_PRIVATE_KEY.
  - HL_DEX_NAME is the existing DEX tag (e.g. "wa").
  - HL_COIN_SYMBOL is the NEW asset name (e.g. "ESV"), and the on-chain
    coin id will be "<dex>:<ASSET_NAME>" (e.g. "wa:ESV").
"""

import os
import sys
import json
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
        from eth_account import Account
        from hyperliquid.exchange import Exchange
        from hyperliquid.utils import constants
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account")
        sys.exit(1)

    master_address = required("HL_MASTER_ADDRESS")
    master_private_key = required("HL_MASTER_PRIVATE_KEY")

    dex = required("HL_DEX_NAME").lower()  # existing DEX, e.g. "wa"
    asset_name = required("HL_COIN_SYMBOL").upper()  # new asset, e.g. "ESV"
    coin = f"{dex}:{asset_name}"
    initial_oracle_price = os.getenv("INITIAL_ORACLE_PRICE", "100.0")
    sz_decimals_env = os.getenv("HL_SZ_DECIMALS", "").strip()
    sz_decimals = int(sz_decimals_env) if sz_decimals_env else 2
    max_gas_env = os.getenv("HL_MAX_GAS", "").strip()
    max_gas = int(max_gas_env) if max_gas_env else None

    wallet = Account.from_key(master_private_key)

    print("🚀 HIP-3 additional asset deployment via SDK (registerAsset)")
    print(f"   DEX (existing):      {dex}")
    print(f"   Asset name:          {asset_name}")
    print(f"   Coin (HL id):        {coin}")
    print(f"   Initial oracle px:   {initial_oracle_price}")
    print()
    print(f"✅ Wallet (signer):     {wallet.address}")
    print(f"✅ Master address env:  {master_address}")
    print()

    if wallet.address.lower() != master_address.lower():
        print("❌ HL_MASTER_ADDRESS must match the address derived from HL_MASTER_PRIVATE_KEY.")
        print(f"   HL_MASTER_ADDRESS:           {master_address}")
        print(f"   HL_MASTER_PRIVATE_KEY -> addr {wallet.address}")
        sys.exit(1)

    exchange = Exchange(
        wallet=wallet,
        base_url=constants.TESTNET_API_URL,
    )

    print("✅ Exchange client:")
    print(f"   base_url:        {exchange.base_url}")
    print(f"   account_address: {exchange.account_address}")
    print()

    # For additional assets on an existing DEX, schema can be omitted.
    schema = None

    print("📝 Calling exchange.perp_deploy_register_asset(...) for NEW asset")
    print(f"   dex:             {dex}")
    print(f"   coin:            {coin}")
    print(f"   sz_decimals:     {sz_decimals}")
    print(f"   oracle_px:       {initial_oracle_price}")
    print(f"   margin_table_id: 1")
    print(f"   only_isolated:   True")
    print(f"   max_gas:         {max_gas}")
    print(f"   schema:          {schema}")
    print()

    try:
        result = exchange.perp_deploy_register_asset(
            dex=dex,
            max_gas=max_gas,
            coin=coin,
            sz_decimals=sz_decimals,
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
        print("\n🎉 Additional asset registered successfully on existing DEX.")
    else:
        print("\n⚠️ Additional asset registration did not return status == 'ok'.")
        print("   Please share this script, your SDK version, and the response above with Hyperliquid if needed.")


if __name__ == "__main__":
    main()


