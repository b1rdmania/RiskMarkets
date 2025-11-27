#!/usr/bin/env python3
"""
HIP-3 Market Deployment Script (Minimal v0)
Deploys a HIP-3 perpetual market on Hyperliquid testnet using ONLY methods that exist in SDK:
- perp_deploy_register_asset
- perp_deploy_set_oracle (optional, to test)

Usage:
    NETWORK=testnet python3 scripts/deploy-market-simple.py

Environment variables required:
    - HL_API_KEY (API wallet address)
    - HL_API_SECRET (API wallet private key)
    - HL_DEX_NAME (optional, defaults to "XAU")
    - HL_COIN_SYMBOL (optional, defaults to "XAU-TEST")
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment
env_file = os.getenv('ENV_FILE', '.env.testnet')
load_dotenv(env_file)

# Import Hyperliquid SDK
try:
    import eth_account
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    from hyperliquid.info import Info
except ImportError:
    print("❌ Error: Hyperliquid Python SDK not installed")
    print("Install with: pip3 install hyperliquid-python-sdk python-dotenv")
    sys.exit(1)

# Get environment variables
HL_API_KEY = os.getenv('HL_API_KEY')
HL_API_SECRET = os.getenv('HL_API_SECRET')
HL_DEX_NAME = os.getenv('HL_DEX_NAME', 'XAU')
HL_COIN_SYMBOL = os.getenv('HL_COIN_SYMBOL', 'XAU-TEST')
INITIAL_ORACLE_PRICE = os.getenv('INITIAL_ORACLE_PRICE', '1924.55')

if not HL_API_KEY or not HL_API_SECRET:
    print("❌ Error: Missing HL_API_KEY or HL_API_SECRET")
    sys.exit(1)

def deploy_market_minimal():
    """Deploy HIP-3 market using only existing SDK methods."""
    
    print("\n🚀 Deploying HIP-3 market (minimal v0)")
    print(f"   DEX Name: {HL_DEX_NAME}")
    print(f"   Coin Symbol: {HL_COIN_SYMBOL}")
    print(f"   Initial Oracle Price: ${INITIAL_ORACLE_PRICE}")
    print(f"   API Wallet: {HL_API_KEY}\n")
    
    # Initialize wallet and exchange
    try:
        wallet = eth_account.Account.from_key(HL_API_SECRET)
        print(f"✅ Wallet initialized: {wallet.address}")
        
        exchange = Exchange(wallet, constants.TESTNET_API_URL)
        print(f"✅ Exchange initialized for testnet\n")
    except Exception as e:
        print(f"❌ Error initializing wallet/exchange: {e}")
        sys.exit(1)
    
    try:
        # Step 1: Register asset
        print("📝 Step 1: Registering asset with perp_deploy_register_asset...")
        print(f"   DEX: {HL_DEX_NAME}")
        print(f"   Coin: {HL_COIN_SYMBOL}")
        print(f"   Oracle Price: {INITIAL_ORACLE_PRICE}")
        print(f"   Size Decimals: 2")
        print(f"   Margin Table ID: 0 (default)")
        print(f"   Only Isolated: False (cross margin)\n")
        
        register_result = exchange.perp_deploy_register_asset(
            dex=HL_DEX_NAME,
            max_gas=None,  # Let Hyperliquid decide
            coin=HL_COIN_SYMBOL,
            sz_decimals=2,
            oracle_px=INITIAL_ORACLE_PRICE,
            margin_table_id=0,  # Default margin table
            only_isolated=False,  # Allow cross margin
            schema={
                'fullName': f'{HL_DEX_NAME} Test DEX',
                'collateralToken': 0,  # USDC index (verify if needed)
                'oracleUpdater': wallet.address.lower(),  # Your wallet address
            }
        )
        
        print("✅ Registration response:")
        print(json.dumps(register_result, indent=2))
        
        if register_result.get('status') != 'ok':
            print(f"\n❌ Asset registration failed: {register_result}")
            sys.exit(1)
        
        print("\n✅ Asset registered successfully!\n")
        
        # Step 2: Set oracle once to test the path
        print("📝 Step 2: Setting initial oracle price with perp_deploy_set_oracle...")
        print(f"   DEX: {HL_DEX_NAME}")
        print(f"   Coin: {HL_COIN_SYMBOL}")
        print(f"   Price: {INITIAL_ORACLE_PRICE}\n")
        
        oracle_result = exchange.perp_deploy_set_oracle(
            dex=HL_DEX_NAME,
            oracle_pxs={HL_COIN_SYMBOL: INITIAL_ORACLE_PRICE},  # Dict[str, str]
            all_mark_pxs=[],  # List[Dict[str, str]] - empty for now
            external_perp_pxs={HL_COIN_SYMBOL: INITIAL_ORACLE_PRICE},  # Dict[str, str]
        )
        
        print("✅ Oracle set response:")
        print(json.dumps(oracle_result, indent=2))
        
        if oracle_result.get('status') != 'ok':
            print(f"\n⚠️  Warning: Oracle set returned non-ok status: {oracle_result}")
        else:
            print("\n✅ Oracle set successfully!\n")
        
        # Step 3: Get asset ID from meta
        print("📝 Step 3: Fetching asset ID from meta...")
        info = Info(constants.TESTNET_API_URL, skip_ws=True)
        meta = info.meta()
        
        asset_id = None
        for idx, asset in enumerate(meta.get('universe', [])):
            if asset.get('name') == HL_COIN_SYMBOL:
                asset_id = idx
                print(f"✅ Found asset in universe at index: {asset_id}")
                break
        
        if asset_id is None:
            print("⚠️  Warning: Asset not found in meta.universe yet")
            print("   It may take a moment to appear. Check again later.")
        else:
            print(f"   Asset details: {json.dumps(meta['universe'][asset_id], indent=2)}")
        
        print()
        print("🎯 Market deployment complete!")
        print(f"\n📝 Update your .env.testnet with:")
        print(f"   HL_DEX_NAME={HL_DEX_NAME}")
        print(f"   HL_COIN_SYMBOL={HL_COIN_SYMBOL}")
        if asset_id is not None:
            print(f"   HL_ASSET_ID={asset_id}")
        print(f"   HL_PUBLISH_ENABLED=true")
        print(f"\n📡 Next steps:")
        print(f"   1. Verify market at: https://app.hyperliquid-testnet.xyz/perps")
        print(f"   2. Implement L1 action signing in TypeScript for setOracle")
        print(f"   3. Start oracle service: npm run dev\n")
        
        return {
            'dex': HL_DEX_NAME,
            'coin': HL_COIN_SYMBOL,
            'assetId': asset_id,
        }
        
    except Exception as e:
        print(f"\n❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    deploy_market_minimal()

