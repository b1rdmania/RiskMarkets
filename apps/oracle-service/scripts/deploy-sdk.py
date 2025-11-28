#!/usr/bin/env python3
"""
HIP-3 Market Deployment using SDK methods directly
Uses Exchange.perp_deploy_register_asset (not manual construction)

Usage:
    NETWORK=testnet python3 scripts/deploy-sdk.py
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
    print("Install with: pip3 install hyperliquid-python-sdk python-dotenv")
    sys.exit(1)

# Get environment variables
HL_MASTER_ADDRESS = os.getenv('HL_MASTER_ADDRESS')
HL_API_PRIVATE_KEY = os.getenv('HL_API_PRIVATE_KEY')
HL_DEX_NAME = os.getenv('HL_DEX_NAME', 'XAU')
HL_COIN_SYMBOL = os.getenv('HL_COIN_SYMBOL', 'XAU-TEST')
INITIAL_ORACLE_PRICE = os.getenv('INITIAL_ORACLE_PRICE', '1924.5')

if not HL_API_PRIVATE_KEY:
    print("❌ Error: Missing HL_API_PRIVATE_KEY")
    sys.exit(1)

if not HL_MASTER_ADDRESS:
    print("❌ Error: Missing HL_MASTER_ADDRESS")
    sys.exit(1)

def deploy_with_sdk():
    """Deploy using SDK's perp_deploy_register_asset method directly."""
    
    print("\n🚀 HIP-3 Deployment (using SDK method directly)")
    print(f"   DEX: {HL_DEX_NAME}")
    print(f"   Coin: {HL_COIN_SYMBOL}")
    print(f"   Initial Oracle Price: {INITIAL_ORACLE_PRICE}")
    print(f"   Master Account: {HL_MASTER_ADDRESS}")
    print()
    
    # Initialize API wallet (agent) and Exchange
    api_wallet = eth_account.Account.from_key(HL_API_PRIVATE_KEY)
    print(f"✅ API wallet (agent): {api_wallet.address}")
    print(f"✅ Master account: {HL_MASTER_ADDRESS}\n")
    
    # Initialize Exchange with agent wallet and master account address
    exchange = Exchange(
        api_wallet,
        constants.TESTNET_API_URL,
        account_address=HL_MASTER_ADDRESS  # Master account
    )
    
    try:
        # Use SDK's perp_deploy_register_asset method
        # Note: SDK uses registerAsset (not registerAsset2), but let's try it
        print("📝 Calling exchange.perp_deploy_register_asset...")
        print(f"   dex: {HL_DEX_NAME}")
        print(f"   coin: {HL_COIN_SYMBOL}")
        print(f"   sz_decimals: 2")
        print(f"   oracle_px: {INITIAL_ORACLE_PRICE}")
        print(f"   margin_table_id: 1")
        print(f"   only_isolated: True")
        print()
        
        result = exchange.perp_deploy_register_asset(
            dex=HL_DEX_NAME,
            max_gas=None,  # Let SDK handle it
            coin=HL_COIN_SYMBOL,
            sz_decimals=2,
            oracle_px=INITIAL_ORACLE_PRICE,
            margin_table_id=1,
            only_isolated=True,  # SDK uses only_isolated, not marginMode
            schema={
                'fullName': f'{HL_DEX_NAME} Test DEX',
                'collateralToken': 0,
                'oracleUpdater': HL_MASTER_ADDRESS.lower(),  # Master address
            }
        )
        
        print("✅ Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'ok':
            print("\n🎉 Market registered successfully!")
            print(f"\n📝 Next steps:")
            print(f"   1. Update .env.testnet with:")
            print(f"      HL_DEX_NAME={HL_DEX_NAME}")
            print(f"      HL_COIN_SYMBOL={HL_COIN_SYMBOL}")
            print(f"      HL_PUBLISH_ENABLED=true")
            print(f"   2. Start oracle service: npm run dev")
            print(f"   3. Check market at: https://app.hyperliquid-testnet.xyz/perps")
            return result
        else:
            print(f"\n⚠️  Response status: {result.get('status')}")
            print(f"   Response: {result.get('response')}")
            return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    deploy_with_sdk()

