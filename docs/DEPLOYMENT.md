# Deployment Guide

## Current Status

**✅ Fixed:**
- `vaultAddress=MASTER_ADDRESS` correctly set in L1 action signing
- `vaultAddress=MASTER_ADDRESS` included in payload sent to Hyperliquid
- Signature recovery is consistent (agent wallet: `0x86C6...`)

**⚠️ Current Issue:**
- Hyperliquid returns: "User or API Wallet 0x86c672b3553576fa436539f21bd660f44ce10a86 does not exist"
- This suggests an API wallet authorization issue, not a code issue

## Setup

### Environment Variables (`.env.testnet`)

```env
NETWORK=testnet

# Pyth
PYTH_HERMES_URL=https://hermes-beta.pyth.network/api
PYTH_FEED_ID_XAU_USD=<feed-id>

# Hyperliquid
HL_API_URL=https://api.hyperliquid-testnet.xyz
HL_MASTER_ADDRESS=0x47515db2eab01758c740ab220352a34b8d5a3826
HL_API_PRIVATE_KEY=<builder-wallet-private-key>
HL_API_ADDRESS=0x47515db2eab01758c740ab220352a34b8d5a3826

# HIP-3 Market
HL_DEX_NAME=XAU
HL_COIN_SYMBOL=XAU-TEST
HL_PUBLISH_ENABLED=false  # Set to true after market is deployed
```

### Key Configuration

- **Master Account**: `0xC0D3...` - The account with funds, trading enabled
- **API Wallet (Agent)**: `0x86C6...` - Signs actions on behalf of master account
- **vaultAddress**: Must be set to `MASTER_ADDRESS` in L1 actions

## Deployment Steps

### 1. Deploy Market

```bash
cd apps/oracle-service
NETWORK=testnet python3 scripts/deploy-correct.py
```

This will:
- Sign with agent wallet (`HL_API_PRIVATE_KEY`)
- Set `vaultAddress=MASTER_ADDRESS` in signature hash
- Include `vaultAddress=MASTER_ADDRESS` in payload
- Deploy `registerAsset` action to Hyperliquid

### 2. Set Oracle Price

```bash
NETWORK=testnet python3 scripts/set-oracle.py 1924.5
```

Or from Node.js:
```typescript
// Automatically called by oracle service when HL_PUBLISH_ENABLED=true
```

### 3. Start Oracle Service

```bash
cd apps/oracle-service
NETWORK=testnet npm run dev
```

## Troubleshooting

### "User or API Wallet does not exist"

1. **Verify API wallet authorization** in Hyperliquid Testnet UI
   - Go to API settings
   - Confirm API wallet `0x86C6...` is authorized
   - Check it's not expired
   - Verify it's associated with master account `0xC0D3...`

2. **Verify master account**
   - Trading enabled ✅
   - Funds deposited ✅
   - Account exists ✅

3. **Check code**
   - `vaultAddress=MASTER_ADDRESS` in signing ✅
   - `vaultAddress=MASTER_ADDRESS` in payload ✅
   - Agent wallet signs ✅

## Code Structure

### Deployment Script (`deploy-correct.py`)

```python
# Agent signs, master is the account
agent_wallet = Account.from_key(HL_API_PRIVATE_KEY)
exchange = Exchange(
    wallet=agent_wallet,
    base_url=constants.TESTNET_API_URL,
    account_address=MASTER_ADDRESS
)

# Sign with vaultAddress=MASTER_ADDRESS
signature = sign_l1_action(
    agent_wallet,
    action,
    MASTER_ADDRESS,  # vaultAddress (critical!)
    timestamp,
    expires_after,
    is_mainnet
)

# Payload includes vaultAddress
payload = {
    "action": action,
    "nonce": timestamp,
    "signature": signature,
    "vaultAddress": MASTER_ADDRESS,  # critical!
    "expiresAfter": None,
}
```

### Oracle Script (`set-oracle.py`)

Same pattern - agent signs, `vaultAddress=MASTER_ADDRESS`.

## HIP-3 Market Types

### Solo Market (Recommended for v0)

Start with a **solo market** (single asset) rather than composite:
- Simpler: matches v0 identity function (`index = pyth_price`)
- Easier to debug: one feed, one price
- Faster to test: less complexity

**Suggested Test Markets:**
- **GOLD/USD** (XAU/USD) - Stable, well-understood
- **Swiss Franc (CHF/USD)** - FX pair, good liquidity
- **BTC/USD** - Most liquid, easiest to test

### Composite Market (Later)

Once solo works, deploy composite markets:
- **50% GOLD + 50% CHF** - Requires fetching two Pyth feeds and weighted average
- Needs index calculation logic (beyond v0 identity function)

## HIP-3 Prerequisites

1. **1M staked HYPE** (may be waived on testnet - verify)
2. **API Wallet** authorized and associated with master account
3. **Market Definition**:
   - Asset name (e.g., `XAU-TEST`)
   - Oracle definition (points to your oracle service)
   - Contract specifications (leverage, margin, etc.)
   - Size decimals (recommended: $1-10 per unit at initial price)

## References

- [Hyperliquid HIP-3 Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
- [Hyperliquid Signing Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/signing)
- [Hyperliquid Builder Tools](https://hyperliquid.gitbook.io/hyperliquid-docs/builder-tools/hypercore-tools)

