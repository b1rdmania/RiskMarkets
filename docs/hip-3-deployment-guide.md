# HIP-3 Market Deployment Guide

## Recommendation: Start with Solo Market

For **v0 testing**, we recommend starting with a **solo market** (single asset) rather than a composite:

### Why Solo Market First?
1. **Simpler**: Matches our v0 identity function (`index = pyth_price`)
2. **Easier to debug**: One feed, one price, clear cause/effect
3. **Faster to test**: Less complexity = faster iteration
4. **Proven concept**: Once solo works, composites are straightforward

### Suggested Test Markets

**Option 1: GOLD/USD** (Recommended)
- Stable, well-understood asset
- Good Pyth feed availability
- Clear price movements for testing
- Market symbol: `GOLD-TEST` or `XAU-USD-TEST`

**Option 2: Swiss Franc (CHF/USD)**
- FX pair, good liquidity
- Pyth feed available
- Market symbol: `CHF-USD-TEST`

**Option 3: BTC/USD** (If you want crypto)
- Most liquid, easiest to test
- Market symbol: `BTC-TEST`

### Composite Market (Later)
Once solo works, you can deploy:
- **50% GOLD + 50% CHF**: Requires fetching two Pyth feeds and calculating weighted average
- This needs index calculation logic (beyond v0 identity function)

---

## HIP-3 Deployment Requirements

### Prerequisites
1. **1M staked HYPE** (may be waived on testnet - verify)
2. **API Wallet** (already created ✅)
3. **Market Definition**:
   - Asset name (e.g., `GOLD-TEST`)
   - Oracle definition (points to your oracle service)
   - Contract specifications (leverage, margin, etc.)
   - Size decimals (recommended: $1-10 per unit at initial price)

### Deployment Process

HIP-3 markets are deployed via Hyperliquid's API using a **deploy action**. The deployment happens through a **Dutch auction** every 31 hours, where you pay gas in **HYPE** tokens.

---

## Deployment Steps

### Step 1: Get Pyth Feed IDs

First, identify the Pyth feed IDs for your chosen asset:

**GOLD/USD**: 
- Check Pyth docs: https://pyth.network/developers/price-feed-ids
- Or use our `/feeds` endpoint to search

**CHF/USD**:
- Search Pyth feeds for "CHF" or "Swiss Franc"

### Step 2: Prepare Market Configuration

You'll need to define:
- **Asset Name**: `GOLD-TEST` (or your choice, <= 6 chars recommended)
- **DEX Name**: `WARMARKET` (already configured)
- **Size Decimals**: Based on initial price
  - If GOLD starts at ~$2000, use `szDecimals: 2` (min increment = $0.01)
  - If GOLD starts at ~$2000, use `szDecimals: 0` (min increment = $1)
- **Initial Margin**: Typically 1/leverage (e.g., 5% for 20x)
- **Maintenance Margin**: Half of initial margin
- **Oracle Definition**: Points to your oracle service (your API wallet address)

### Step 3: Deploy via API

The deployment uses Hyperliquid's `/exchange` endpoint with a `perpDeploy` action containing `registerAsset`.

**API Structure** (based on HIP-3 docs):

```typescript
{
  action: {
    type: "perpDeploy",
    registerAsset: {
      type: "registerAsset",
      name: "GOLD-TEST",  // Asset name (<= 6 chars recommended)
      szDecimals: 2,  // Size decimals (for $0.01 increments)
      maxLeverage: 20,  // Maximum leverage (optional, default 20)
      oracle: {
        // Oracle definition - may need your API wallet address
      }
    }
  }
}
```

**Deployment Script**: See `apps/oracle-service/scripts/deploy-market.ts` for a ready-to-use deployment script.

### Step 4: Verify Deployment

After deployment:
1. Check market appears on Hyperliquid testnet
2. Verify market ID matches your `HL_MARKET_ID`
3. Test oracle price updates via your service

---

## Next Steps

1. **Find exact deployment API**: Check Hyperliquid Python SDK examples or API docs
2. **Create deployment script**: TypeScript script to deploy via API
3. **Test deployment**: Deploy on testnet with minimal config
4. **Verify oracle**: Once deployed, test price publishing

---

## Resources

- **HIP-3 Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals
- **API Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
- **Python SDK**: https://github.com/hyperliquid-dex/hyperliquid-python-sdk (check examples/)

---

## Recommendation Summary

**For v0**: Deploy **GOLD-TEST** as a solo market
- Simple, stable, easy to test
- Matches our v0 identity function
- Once working, expand to composites

**For later**: Deploy composite markets (50% GOLD + 50% CHF)
- Requires index calculation logic
- Multiple Pyth feeds
- Weighted averaging

