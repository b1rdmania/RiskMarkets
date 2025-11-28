#!/usr/bin/env python3
"""
Set Oracle Price for HIP-3 Market
Uses Python SDK's sign_l1_action (canonical implementation)

Usage:
    NETWORK=testnet python3 scripts/set-oracle.py <price>
    
Or call from Node.js:
    const { execSync } = require('child_process');
    execSync(`python3 scripts/set-oracle.py ${price}`, { cwd: __dirname });
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
HL_MASTER_ADDRESS = os.getenv('HL_MASTER_ADDRESS')  # Master account
HL_API_PRIVATE_KEY = os.getenv('HL_API_PRIVATE_KEY')  # API wallet private key
HL_DEX_NAME = os.getenv('HL_DEX_NAME', 'XAU')
HL_COIN_SYMBOL = os.getenv('HL_COIN_SYMBOL', 'XAU-TEST')

if not HL_API_PRIVATE_KEY:
    print("❌ Error: Missing HL_API_PRIVATE_KEY")
    sys.exit(1)

if not HL_MASTER_ADDRESS:
    print("❌ Error: Missing HL_MASTER_ADDRESS")
    sys.exit(1)

# Get price from command line or stdin
if len(sys.argv) > 1:
    price = sys.argv[1]
else:
    price = sys.stdin.read().strip()

if not price:
    print("❌ Error: No price provided")
    sys.exit(1)

try:
    price_float = float(price)
    price_str = f"{price_float:.8f}".rstrip('0').rstrip('.')
except ValueError:
    print(f"❌ Error: Invalid price: {price}")
    sys.exit(1)

def set_oracle(price: str):
    """Set oracle price using Python SDK (canonical signing)."""
    
    # Initialize wallet and exchange
    # Exchange uses agent wallet for signing, but master address is the account
    api_wallet = eth_account.Account.from_key(HL_API_PRIVATE_KEY)
    exchange = Exchange(api_wallet, constants.TESTNET_API_URL, account_address=HL_MASTER_ADDRESS)
    
    # Verify API wallet address
    EXPECTED_API_ADDRESS = "0x47515db2eab01758c740ab220352a34b8d5a3826"
    if api_wallet.address.lower() != EXPECTED_API_ADDRESS.lower():
        print(f"❌ Error: API wallet address mismatch")
        print(f"   Expected: {EXPECTED_API_ADDRESS}")
        print(f"   Got:      {api_wallet.address}")
        sys.exit(1)
    
    print(f"✅ API wallet (agent): {api_wallet.address}")
    print(f"✅ Master account: {HL_MASTER_ADDRESS}")
    
    # Use SDK's perp_deploy_set_oracle but override vaultAddress
    # SDK passes None as active_pool, but we need MASTER_ADDRESS
    from hyperliquid.utils.signing import sign_l1_action
    from hyperliquid.exchange import get_timestamp_ms
    
    # Build setOracle action
    oracle_pxs_wire = sorted(list({HL_COIN_SYMBOL: price_str}.items()))
    mark_pxs_wire = []
    external_perp_pxs_wire = sorted(list({HL_COIN_SYMBOL: price_str}.items()))
    
    action = {
        "type": "perpDeploy",
        "setOracle": {
            "dex": HL_DEX_NAME,
            "oraclePxs": oracle_pxs_wire,
            "markPxs": mark_pxs_wire,
            "externalPerpPxs": external_perp_pxs_wire,
        },
    }
    
    # Sign with vaultAddress=MASTER_ADDRESS
    timestamp = get_timestamp_ms()
    signature = sign_l1_action(
        api_wallet,
        action,
        HL_MASTER_ADDRESS,  # vaultAddress (the account the action is for)
        timestamp,
        exchange.expires_after,
        exchange.base_url == constants.MAINNET_API_URL,
    )
    
    # Post with vaultAddress in payload
    payload = {
        "action": action,
        "nonce": timestamp,
        "signature": signature,
        "vaultAddress": HL_MASTER_ADDRESS,  # CRITICAL: master account
        "expiresAfter": exchange.expires_after,
    }
    
    try:
        result = exchange.post("/exchange", payload)
        
        # Output JSON for Node.js to parse
        print(json.dumps({
            'ok': result.get('status') == 'ok',
            'status': result.get('status'),
            'response': result.get('response'),
            'price': price_str,
        }))
        
        if result.get('status') == 'ok':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({
            'ok': False,
            'error': str(e),
            'price': price_str,
        }))
        sys.exit(1)

if __name__ == '__main__':
    set_oracle(price_str)

