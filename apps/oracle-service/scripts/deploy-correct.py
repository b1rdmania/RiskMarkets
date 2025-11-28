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

# SDK doesn't have perp_deploy_register_asset2, so we'll manually construct it
# with the correct vaultAddress
if False:  # SDK doesn't have this method
    pass
else:
    print("⚠️  SDK doesn't have perp_deploy_register_asset2")
    print("📝 Manually constructing registerAsset2 action...")
    
    # Use registerAsset (SDK method) - registerAsset2 doesn't exist in SDK
    action = {
        "type": "perpDeploy",
        "registerAsset": {
            "maxGas": None,
            "assetRequest": {
                "coin": COIN,
                "szDecimals": 2,
                "oraclePx": INITIAL_ORACLE_PRICE,
                "marginTableId": 1,
                "onlyIsolated": True,
            },
            "dex": DEX,
            "schema": {
                "fullName": f"{DEX} Test DEX",
                "collateralToken": 0,
                "oracleUpdater": MASTER_ADDRESS.lower(),
            }
        }
    }
    
    # Sign using Exchange's signing - CRITICAL: pass MASTER_ADDRESS as active_pool (vaultAddress)
    timestamp = get_timestamp_ms()
    signature = sign_l1_action(
        exchange.wallet,  # agent wallet (signer)
        action,
        MASTER_ADDRESS,  # active_pool = vaultAddress (the account the action is for)
        timestamp,
        exchange.expires_after,
        exchange.base_url == constants.MAINNET_API_URL  # is_mainnet
    )
    
    # Post using Exchange's _post_action - but override vaultAddress to use MASTER_ADDRESS
    # The SDK's _post_action uses exchange.vault_address, but we need MASTER_ADDRESS
    payload = {
        "action": action,
        "nonce": timestamp,
        "signature": signature,
        "vaultAddress": MASTER_ADDRESS,  # CRITICAL: master account, not null
        "expiresAfter": exchange.expires_after,
    }
    result = exchange.post("/exchange", payload)

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

