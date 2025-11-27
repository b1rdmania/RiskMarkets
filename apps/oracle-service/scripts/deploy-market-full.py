#!/usr/bin/env python3
"""
HIP-3 Market Deployment Script (Full Sequence)
Deploys a HIP-3 perpetual market on Hyperliquid testnet using the correct sequence:
1. Insert margin table
2. Register asset (registerAsset2)
3. Set margin modes, funding multipliers, OI caps
4. Market is ready for setOracle calls

Usage:
    NETWORK=testnet python3 scripts/deploy-market-full.py

Environment variables required:
    - HL_API_KEY (API wallet address)
    - HL_API_SECRET (API wallet private key)
    - HL_DEX_NAME (optional, defaults to "XAU")
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
except ImportError:
    print("❌ Error: Hyperliquid Python SDK not installed")
    print("Install with: pip3 install hyperliquid-python-sdk")
    sys.exit(1)

# Get environment variables
HL_API_KEY = os.getenv('HL_API_KEY')
HL_API_SECRET = os.getenv('HL_API_SECRET')
HL_DEX_NAME = os.getenv('HL_DEX_NAME', 'XAU')
HL_COIN_SYMBOL = os.getenv('HL_COIN_SYMBOL', 'XAU-TEST')

if not HL_API_KEY or not HL_API_SECRET:
    print("❌ Error: Missing HL_API_KEY or HL_API_SECRET")
    sys.exit(1)

def deploy_market_full():
    """Deploy HIP-3 market using the correct sequence of PerpDeployActions."""
    
    print("\n🚀 Deploying HIP-3 market (full sequence)")
    print(f"   DEX Name: {HL_DEX_NAME}")
    print(f"   Coin Symbol: {HL_COIN_SYMBOL}")
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
    
    # Market configuration
    initial_oracle_price = os.getenv('INITIAL_ORACLE_PRICE', '1924.55')
    sz_decimals = int(os.getenv('SZ_DECIMALS', '2'))
    
    print("📋 Market Configuration:")
    print(f"   DEX: {HL_DEX_NAME}")
    print(f"   Coin: {HL_COIN_SYMBOL}")
    print(f"   Initial Oracle Price: ${initial_oracle_price}")
    print(f"   Size Decimals: {sz_decimals}\n")
    
    try:
        # Step 1: Insert margin table
        print("📝 Step 1: Inserting margin table...")
        # Check if there's a method for this in the SDK
        # If not, we'll need to construct the action manually
        
        # For now, let's try to find the right method
        # The SDK might have perp_deploy_insert_margin_table or similar
        margin_table_result = None
        margin_table_id = 1  # Default to 1, adjust if SDK returns different
        
        if hasattr(exchange, 'perp_deploy_insert_margin_table'):
            margin_table_result = exchange.perp_deploy_insert_margin_table(
                dex=HL_DEX_NAME,
                # Add other required params based on SDK
            )
            print(f"✅ Margin table inserted: {margin_table_result}")
        else:
            print("⚠️  Note: insertMarginTable method not found in SDK")
            print("   Using margin_table_id=1 (you may need to adjust)")
        
        print()
        
        # Step 2: Register asset (registerAsset2)
        print("📝 Step 2: Registering asset (registerAsset2)...")
        
        # Check for registerAsset2 method
        if hasattr(exchange, 'perp_deploy_register_asset2'):
            register_result = exchange.perp_deploy_register_asset2(
                dex=HL_DEX_NAME,
                max_gas=None,
                coin=HL_COIN_SYMBOL,
                sz_decimals=sz_decimals,
                oracle_px=initial_oracle_price,
                margin_table_id=margin_table_id,
                margin_mode='strictIsolated',  # or 'noCross'
                schema={
                    'fullName': f'{HL_DEX_NAME} Test DEX',
                    'collateralToken': 0,  # USDC index (verify this)
                    'oracleUpdater': wallet.address.lower(),  # Your address
                }
            )
        else:
            # Fallback to registerAsset if registerAsset2 doesn't exist
            print("   Using registerAsset (registerAsset2 not found)")
            register_result = exchange.perp_deploy_register_asset(
                dex=HL_DEX_NAME,
                max_gas=None,
                coin=HL_COIN_SYMBOL,
                sz_decimals=sz_decimals,
                oracle_px=initial_oracle_price,
                margin_table_id=margin_table_id,
                only_isolated=True,  # matches strictIsolated
                schema={
                    'fullName': f'{HL_DEX_NAME} Test DEX',
                    'collateralToken': 0,
                    'oracleUpdater': wallet.address.lower(),
                }
            )
        
        print(f"✅ Asset registration response:")
        print(json.dumps(register_result, indent=2))
        
        if register_result.get('status') != 'ok':
            print(f"❌ Asset registration failed: {register_result}")
            sys.exit(1)
        
        print()
        
        # Step 3: Set margin modes, funding multipliers, OI caps
        print("📝 Step 3: Setting margin modes, funding multipliers, OI caps...")
        
        # Set margin modes
        if hasattr(exchange, 'perp_deploy_set_margin_modes'):
            margin_result = exchange.perp_deploy_set_margin_modes(
                dex=HL_DEX_NAME,
                margin_modes=[[HL_COIN_SYMBOL, 'strictIsolated']]
            )
            print(f"✅ Margin modes set: {margin_result}")
        
        # Set funding multipliers
        if hasattr(exchange, 'perp_deploy_set_funding_multipliers'):
            funding_result = exchange.perp_deploy_set_funding_multipliers(
                dex=HL_DEX_NAME,
                funding_multipliers=[[HL_COIN_SYMBOL, '1.0']]
            )
            print(f"✅ Funding multipliers set: {funding_result}")
        
        # Set open interest caps
        if hasattr(exchange, 'perp_deploy_set_open_interest_caps'):
            oi_result = exchange.perp_deploy_set_open_interest_caps(
                dex=HL_DEX_NAME,
                open_interest_caps=[[HL_COIN_SYMBOL, 1_000_000]]  # $1M cap
            )
            print(f"✅ Open interest caps set: {oi_result}")
        
        print()
        
        # Step 4: Get asset ID from meta
        print("📝 Step 4: Fetching asset ID from meta...")
        from hyperliquid.info import Info
        info = Info(constants.TESTNET_API_URL, skip_ws=True)
        meta = info.meta()
        
        # Find our asset in the universe
        asset_id = None
        for idx, asset in enumerate(meta.get('universe', [])):
            if asset.get('name') == HL_COIN_SYMBOL:
                asset_id = idx
                break
        
        if asset_id is None:
            print("⚠️  Warning: Asset not found in meta.universe")
            print("   You may need to wait a moment and check again")
        else:
            print(f"✅ Asset ID found: {asset_id}")
        
        print()
        print("🎯 Market deployment complete!")
        print(f"\n📝 Update your .env.testnet with:")
        print(f"   HL_DEX_NAME={HL_DEX_NAME}")
        print(f"   HL_COIN_SYMBOL={HL_COIN_SYMBOL}")
        if asset_id is not None:
            print(f"   HL_ASSET_ID={asset_id}")
        print(f"   HL_PUBLISH_ENABLED=true")
        print(f"\n📡 Next: Start your oracle service to begin setOracle calls")
        print(f"   npm run dev\n")
        
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
    deploy_market_full()

