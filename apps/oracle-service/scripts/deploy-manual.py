#!/usr/bin/env python3
"""
Manual HIP-3 Deployment - Bypass SDK's maxGas: null issue
Manually construct the payload without maxGas and use SDK's signing.

Usage:
    NETWORK=testnet python3 scripts/deploy-manual.py
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
    from hyperliquid.utils.signing import sign_l1_action
    import time
    import requests
    
    def get_timestamp_ms():
        return int(time.time() * 1000)
except ImportError:
    print("❌ Error: Hyperliquid Python SDK not installed")
    print("Install with: pip3 install hyperliquid-python-sdk python-dotenv requests")
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

def deploy_manual():
    """Manually construct payload without maxGas: null."""
    
    print("\n🚀 Manual HIP-3 Deployment (using registerAsset2)")
    print(f"   DEX: {HL_DEX_NAME}")
    print(f"   Coin: {HL_COIN_SYMBOL}")
    print(f"   Initial Oracle Price: {INITIAL_ORACLE_PRICE}\n")
    
    # Initialize wallet
    # Note: Hyperliquid API uses sub-wallets, but L1 actions should be signed by main wallet
    # The main wallet address is: 0xC0D35857e87F5ADe6055714706fb4dFD96DE087E
    try:
        wallet = eth_account.Account.from_key(HL_API_SECRET)
        wallet_address = wallet.address
        print(f"✅ Wallet from secret: {wallet_address}")
        
        print(f"✅ Using API wallet: {wallet_address}\n")
    except Exception as e:
        print(f"❌ Error initializing wallet: {e}")
        sys.exit(1)
    
    # Manually construct the action using registerAsset2 (current HIP-3 spec)
    # Based on: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
    # 
    # Key differences from old registerAsset:
    # - Use registerAsset2 (not registerAsset)
    # - Use marginMode: "strictIsolated" (not onlyIsolated: true)
    # - Omit maxGas entirely (optional field)
    action = {
        "type": "perpDeploy",
        "registerAsset2": {
            # Omit "maxGas" entirely (optional field)
            "assetRequest": {
                "coin": HL_COIN_SYMBOL,
                "szDecimals": 2,
                "oraclePx": INITIAL_ORACLE_PRICE,  # String
                "marginTableId": 1,  # Use 1 instead of 0 (more standard)
                "marginMode": "strictIsolated",  # Use marginMode, not onlyIsolated
            },
            "dex": HL_DEX_NAME,
        "schema": {
          "fullName": f"{HL_DEX_NAME} Test DEX",
          "collateralToken": 0,
          "oracleUpdater": wallet_address.lower(),
        }
        }
    }
    
    print("📝 Constructed action (without maxGas):")
    print(json.dumps(action, indent=2))
    print()
    
    # Sign using SDK's sign_l1_action
    nonce = get_timestamp_ms()
    active_pool = None
    expires_after = None
    is_mainnet = False
    
    print(f"🔐 Signing action...")
    print(f"   Nonce: {nonce}")
    print(f"   Active Pool: {active_pool}")
    print(f"   Expires After: {expires_after}")
    print(f"   Is Mainnet: {is_mainnet}\n")
    
    try:
        signature = sign_l1_action(
            wallet,
            action,
            active_pool,
            nonce,
            expires_after,
            is_mainnet
        )
        
        print("✅ Signature generated:")
        print(json.dumps(signature, indent=2))
        print()
        
        # Construct the full payload
        # The SDK's _post_action adds vaultAddress and expiresAfter
        # Try with null first (as SDK does), then try omitting if needed
        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature,
            "vaultAddress": None,  # SDK adds this as null
            "expiresAfter": None,  # SDK adds this as null
        }
        
        print("📦 Full payload (using registerAsset2 with marginMode):")
        print(json.dumps(payload, indent=2))
        print()
        
        # POST to /exchange
        url = f"{constants.TESTNET_API_URL}/exchange"
        print(f"📡 POSTing to: {url}\n")
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}\n")
        
        try:
            response_json = response.json()
            print("✅ Response JSON:")
            print(json.dumps(response_json, indent=2))
            
            if response.status_code == 200:
                print("\n🎉 Market registered successfully!")
                print(f"\n📝 Next steps:")
                print(f"   1. Update .env.testnet with:")
                print(f"      HL_DEX_NAME={HL_DEX_NAME}")
                print(f"      HL_COIN_SYMBOL={HL_COIN_SYMBOL}")
                print(f"      HL_PUBLISH_ENABLED=true")
                print(f"   2. Start oracle service: npm run dev")
                print(f"   3. Check market at: https://app.hyperliquid-testnet.xyz/perps")
            else:
                print(f"\n⚠️  Non-200 response: {response.status_code}")
                if response_json.get('error'):
                    print(f"   Error: {response_json['error']}")
        except ValueError:
            print(f"❌ Response is not JSON:")
            print(response.text)
            if response.status_code == 422:
                print(f"\n💡 Still getting 422. Possible issues:")
                print(f"   1. vaultAddress/expiresAfter may need to be null (not omitted)")
                print(f"   2. Field names/types may still be wrong")
                print(f"   3. Testnet may require permissions")
                print(f"   4. DEX may need registration first")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    deploy_manual()

