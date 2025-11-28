#!/usr/bin/env python3
"""
HIP-3 Market Deployment - CORRECT setup
Following exact pattern from user's dev team instructions:
- Agent signs
- Master is the account we act on
- account_address must be master address

Usage:
    NETWORK=testnet python3 scripts/deploy-correct.py
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
    from eth_account import Account
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    from hyperliquid.utils.signing import sign_l1_action
    from hyperliquid.exchange import get_timestamp_ms
except ImportError as e:
    print(f"❌ Error: Missing dependency: {e}")
    print("Install with: pip3 install hyperliquid-python-sdk python-dotenv eth-account")
    sys.exit(1)

# Get environment variables - EXACTLY as specified
MASTER_ADDRESS = os.environ["HL_MASTER_ADDRESS"]  # Master account (user)
AGENT_PK = os.environ["HL_API_PRIVATE_KEY"]  # Agent private key
DEX = os.getenv("HL_DEX_NAME", "XAU")
COIN = os.getenv("HL_COIN_SYMBOL", "XAU-TEST")
INITIAL_ORACLE_PRICE = os.getenv("INITIAL_ORACLE_PRICE", "1924.5")

if not MASTER_ADDRESS:
    print("❌ Error: Missing HL_MASTER_ADDRESS")
    sys.exit(1)

if not AGENT_PK:
    print("❌ Error: Missing HL_API_PRIVATE_KEY")
    sys.exit(1)

# Verify agent wallet
agent_wallet = Account.from_key(AGENT_PK)
print(f"✅ Agent wallet (signer): {agent_wallet.address}")
print(f"✅ Master account (target): {MASTER_ADDRESS}")
print()

# Initialize Exchange EXACTLY as specified
exchange = Exchange(
    wallet=agent_wallet,                   # signer = agent
    base_url=constants.TESTNET_API_URL,
    account_address=MASTER_ADDRESS         # target account = master
)

print(f"✅ Exchange initialized:")
print(f"   wallet.address: {exchange.wallet.address}")
print(f"   account_address: {exchange.account_address}")
print(f"   base_url: {exchange.base_url}")
print()

# Check if SDK has perp_deploy_register_asset2
if hasattr(exchange, 'perp_deploy_register_asset2'):
    print("📝 SDK has perp_deploy_register_asset2 - using it...")
    result = exchange.perp_deploy_register_asset2(
        dex=DEX,
        asset_request={
            "coin": COIN,
            "szDecimals": 2,
            "oraclePx": INITIAL_ORACLE_PRICE,
            "marginTableId": 1,
            "marginMode": "strictIsolated",
        },
        schema={
            "fullName": f"{DEX} Test DEX",
            "collateralToken": 0,
            "oracleUpdater": MASTER_ADDRESS.lower(),
        },
    )
else:
    print("⚠️  SDK doesn't have perp_deploy_register_asset2")
    print("📝 Manually constructing registerAsset2 action...")
    
    # Manually construct registerAsset2 action
    action = {
        "type": "perpDeploy",
        "registerAsset2": {
            "assetRequest": {
                "coin": COIN,
                "szDecimals": 2,
                "oraclePx": INITIAL_ORACLE_PRICE,
                "marginTableId": 1,
                "marginMode": "strictIsolated",
            },
            "dex": DEX,
            "schema": {
                "fullName": f"{DEX} Test DEX",
                "collateralToken": 0,
                "oracleUpdater": MASTER_ADDRESS.lower(),
            }
        }
    }
    
    # Sign using Exchange's signing (same as SDK's perp_deploy_register_asset)
    timestamp = get_timestamp_ms()
    signature = sign_l1_action(
        exchange.wallet,  # agent wallet
        action,
        None,  # active_pool
        timestamp,
        exchange.expires_after,
        exchange.base_url == constants.MAINNET_API_URL  # is_mainnet
    )
    
    # Post using Exchange's _post_action
    result = exchange._post_action(action, signature, timestamp)

print("\n✅ Response:")
print(json.dumps(result, indent=2))

if result.get('status') == 'ok':
    print("\n🎉 Market registered successfully!")
    print(f"\n📝 Next steps:")
    print(f"   1. Update .env.testnet with:")
    print(f"      HL_DEX_NAME={DEX}")
    print(f"      HL_COIN_SYMBOL={COIN}")
    print(f"      HL_PUBLISH_ENABLED=true")
    print(f"   2. Start oracle service: npm run dev")
    print(f"   3. Check market at: https://app.hyperliquid-testnet.xyz/perps")
else:
    print(f"\n⚠️  Response status: {result.get('status')}")
    print(f"   Response: {result.get('response')}")

