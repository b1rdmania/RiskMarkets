#!/usr/bin/env python3
"""
Minimal HIP-3 Market Deployment - Single register_asset call
Goal: Get ONE asset registered on testnet, nothing more.

Usage:
    NETWORK=testnet python3 scripts/deploy-minimal.py
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Enable verbose logging to see the exact payload
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

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
HL_API_KEY = os.getenv('HL_API_KEY')
HL_API_SECRET = os.getenv('HL_API_SECRET')
HL_DEX_NAME = os.getenv('HL_DEX_NAME', 'XAU')
HL_COIN_SYMBOL = os.getenv('HL_COIN_SYMBOL', 'XAU-TEST')
INITIAL_ORACLE_PRICE = os.getenv('INITIAL_ORACLE_PRICE', '1924.5')

if not HL_API_KEY or not HL_API_SECRET:
    print("❌ Error: Missing HL_API_KEY or HL_API_SECRET")
    sys.exit(1)

def deploy_minimal():
    """Minimal deployment: ONE register_asset call, nothing else."""
    
    print("\n🚀 Minimal HIP-3 Deployment (v0)")
    print(f"   DEX: {HL_DEX_NAME}")
    print(f"   Coin: {HL_COIN_SYMBOL}")
    print(f"   Initial Oracle Price: {INITIAL_ORACLE_PRICE}")
    print(f"   Wallet: {HL_API_KEY}\n")
    
    # Initialize wallet and exchange
    try:
        wallet = eth_account.Account.from_key(HL_API_SECRET)
        print(f"✅ Wallet: {wallet.address}\n")
        
        exchange = Exchange(wallet, constants.TESTNET_API_URL)
        print(f"✅ Exchange initialized (testnet)\n")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        sys.exit(1)
    
    # Minimal configuration
    # Based on: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
    dex = HL_DEX_NAME
    coin = HL_COIN_SYMBOL
    sz_decimals = 2  # $0.01 increments
    oracle_px = INITIAL_ORACLE_PRICE  # String, not float
    margin_table_id = 0  # Default margin table
    only_isolated = True  # Start with isolated margin (safer)
    
    # Schema only needed for FIRST asset in a DEX
    # Since we're creating a new DEX, include schema
    schema = {
        'fullName': f'{HL_DEX_NAME} Test DEX',
        'collateralToken': 0,  # USDC index
        'oracleUpdater': wallet.address.lower(),  # Our wallet address
    }
    
    print("📝 Calling perp_deploy_register_asset with:")
    print(f"   dex: {dex}")
    print(f"   coin: {coin}")
    print(f"   sz_decimals: {sz_decimals}")
    print(f"   oracle_px: {oracle_px} (string)")
    print(f"   margin_table_id: {margin_table_id}")
    print(f"   only_isolated: {only_isolated}")
    print(f"   schema: {json.dumps(schema, indent=2)}")
    print()
    
    try:
        # Monkey-patch the post method to capture the exact payload
        original_post = exchange.post
        captured_payload = None
        
        def capture_post(url_path, payload=None):
            nonlocal captured_payload
            captured_payload = payload
            print("\n📦 EXACT PAYLOAD BEING SENT:")
            print(json.dumps(payload, indent=2))
            print()
            return original_post(url_path, payload)
        
        exchange.post = capture_post
        
        # Make the call
        result = exchange.perp_deploy_register_asset(
            dex=dex,
            max_gas=None,  # Let HL decide
            coin=coin,
            sz_decimals=sz_decimals,
            oracle_px=oracle_px,
            margin_table_id=margin_table_id,
            only_isolated=only_isolated,
            schema=schema,
        )
        
        print("✅ Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'ok':
            print("\n🎉 Asset registered successfully!")
            print(f"\n📝 Next steps:")
            print(f"   1. Update .env.testnet with:")
            print(f"      HL_DEX_NAME={dex}")
            print(f"      HL_COIN_SYMBOL={coin}")
            print(f"      HL_PUBLISH_ENABLED=true")
            print(f"   2. Start oracle service: npm run dev")
            print(f"   3. Check market at: https://app.hyperliquid-testnet.xyz/perps")
        else:
            print(f"\n⚠️  Response status: {result.get('status')}")
            print(f"   Full response: {result}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n📋 Debugging info:")
        print(f"   Error type: {type(e).__name__}")
        
        # Show the captured payload if we have it
        if captured_payload:
            print(f"\n📦 Payload that caused the error:")
            print(json.dumps(captured_payload, indent=2))
        
        # Try to extract the actual request payload if possible
        if hasattr(e, 'args') and len(e.args) > 0:
            print(f"   Error details: {e.args}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Compare the payload above to the docs:")
        print(f"      https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions")
        print(f"   2. Check for:")
        print(f"      - Missing required fields")
        print(f"      - Wrong field names/types")
        print(f"      - Extra fields that shouldn't be there")
        print(f"   3. Verify testnet allows HIP-3 deployment")
        print(f"   4. Share this payload with Hyperliquid team if needed")
        
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    deploy_minimal()

