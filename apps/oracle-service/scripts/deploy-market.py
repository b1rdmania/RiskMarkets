#!/usr/bin/env python3
"""
HIP-3 Market Deployment Script (Python)
Deploys a HIP-3 perpetual market on Hyperliquid testnet using the official Python SDK.

Usage:
    NETWORK=testnet python3 scripts/deploy-market.py

Environment variables required:
    - HL_TESTNET_URL (default: https://api.hyperliquid-testnet.xyz)
    - HL_API_KEY (API wallet address)
    - HL_API_SECRET (API wallet private key)
"""

import os
import sys
from pathlib import Path
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
HL_TESTNET_URL = os.getenv('HL_TESTNET_URL', 'https://api.hyperliquid-testnet.xyz')

if not HL_API_KEY or not HL_API_SECRET:
    print("❌ Error: Missing HL_API_KEY or HL_API_SECRET")
    sys.exit(1)

def create_market():
    """Create a HIP-3 perpetual market on Hyperliquid testnet."""
    
    print("\n🚀 Creating HIP-3 market: XAU-TEST")
    print(f"   API URL: {HL_TESTNET_URL}")
    print(f"   API Wallet: {HL_API_KEY}\n")
    
    # Initialize wallet and exchange
    try:
        wallet = eth_account.Account.from_key(HL_API_SECRET)
        print(f"✅ Wallet initialized: {wallet.address}")
        
        # Use testnet URL
        exchange = Exchange(wallet, constants.TESTNET_API_URL)
        print(f"✅ Exchange initialized for testnet\n")
    except Exception as e:
        print(f"❌ Error initializing wallet/exchange: {e}")
        sys.exit(1)
    
    # Market configuration
    market_config = {
        'symbol': 'XAU-TEST',
        'szDecimals': 2,
        'initialOraclePrice': '1924.55',
        'marginTableId': 0,
        'onlyIsolated': False,
    }
    
    print("📋 Market Configuration:")
    print(f"   Symbol: {market_config['symbol']}")
    print(f"   Size Decimals: {market_config['szDecimals']}")
    print(f"   Initial Oracle Price: ${market_config['initialOraclePrice']}")
    print(f"   Margin Table ID: {market_config['marginTableId']}")
    print(f"   Isolated Only: {market_config['onlyIsolated']}\n")
    
    # Create the perpDeploy action
    # Based on Hyperliquid Python SDK structure
    action = {
        'type': 'perpDeploy',
        'registerAsset': {
            'type': 'registerAsset',
            'coin': market_config['symbol'],
            'szDecimals': market_config['szDecimals'],
            'oraclePx': market_config['initialOraclePrice'],
            'marginTableId': market_config['marginTableId'],
            'onlyIsolated': market_config['onlyIsolated'],
        }
    }
    
    print("📦 Action payload:")
    import json
    print(json.dumps(action, indent=2))
    print()
    
    # Use the exchange object to send the action
    # The Python SDK has a specific method: perp_deploy_register_asset
    try:
        print("📡 Sending createMarket request...\n")
        
        # Method signature: perp_deploy_register_asset(
        #   dex: str,
        #   max_gas: Optional[int],
        #   coin: str,
        #   sz_decimals: int,
        #   oracle_px: str,
        #   margin_table_id: int,
        #   only_isolated: bool,
        #   schema: Optional[PerpDexSchemaInput]
        # )
        
        dex_name = os.getenv('HL_DEX_NAME', 'WARMARKET')
        max_gas = None  # Optional, let Hyperliquid decide
        
        print("📤 Calling perp_deploy_register_asset:")
        print(f"   DEX: {dex_name}")
        print(f"   Coin: {market_config['symbol']}")
        print(f"   Size Decimals: {market_config['szDecimals']}")
        print(f"   Oracle Price: {market_config['initialOraclePrice']}")
        print(f"   Margin Table ID: {market_config['marginTableId']}")
        print(f"   Only Isolated: {market_config['onlyIsolated']}")
        print()
        
        result = exchange.perp_deploy_register_asset(
            dex=dex_name,
            max_gas=max_gas,
            coin=market_config['symbol'],
            sz_decimals=market_config['szDecimals'],
            oracle_px=market_config['initialOraclePrice'],
            margin_table_id=market_config['marginTableId'],
            only_isolated=market_config['onlyIsolated'],
            schema=None,  # Optional schema
        )
        
        print("✅ Market creation response:")
        print(json.dumps(result, indent=2))
        
        # Extract assetId from response
        if result.get('status') == 'ok':
            response_data = result.get('response', {})
            asset_id = response_data.get('assetId') or response_data.get('data', {}).get('assetId')
            
            if asset_id:
                print(f"\n🎯 Market created successfully!")
                print(f"   Asset ID: {asset_id}")
                print(f"   Symbol: {market_config['symbol']}")
                print(f"\n📝 Next steps:")
                print(f"   1. Update .env.testnet:")
                print(f"      HL_MARKET_ID={asset_id}")
                print(f"      HL_MARKET_SYMBOL={market_config['symbol']}")
                print(f"      HL_PUBLISH_ENABLED=true")
                print(f"   2. Start oracle service: npm run dev")
                print(f"   3. Verify at: https://app.hyperliquid-testnet.xyz/perps\n")
                return asset_id
            else:
                print("\n⚠️  Warning: Market created but assetId not found in response")
                print("   Check the response above for the asset ID")
        else:
            print(f"\n❌ Market creation failed: {result}")
            
    except Exception as e:
        print(f"\n❌ Error creating market: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_market()

