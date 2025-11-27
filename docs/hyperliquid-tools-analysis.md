# Hyperliquid Builder Tools Deep Dive Analysis

## Overview

This document analyzes Hyperliquid's builder tools ecosystem, specifically **Hypercore Tools** and **HyperEVM Tools**, and their relevance to WAR.MARKET's oracle service implementation.

---

## 1. HIP-3: Builder-Deployed Perpetuals

### Key Concept
HIP-3 enables builders to deploy their own perpetual markets on Hyperliquid, making them responsible for:
1. **Market Definition**: Oracle definition and contract specifications
2. **Market Operation**: Setting oracle prices, leverage limits, and market settlement

### Critical Requirements for Oracle Providers

#### Staking Requirements
- **1M staked HYPE** must be maintained by deployers
- Stake can be slashed by validators via stake-weighted vote during 7-day unstaking queue
- This protects users from malicious market operation

#### Open Interest Caps
- **Notional caps**: Enforced dex-wide and per-asset
- **Size-denominated caps**: Currently constant 1B per asset
- Deployers can set custom per-asset notional caps
- Recommended: Set `szDecimals` so minimal size increment is $1-10 at initial mark price

#### Deployment Mechanics
- Gas paid via Dutch auction every 31 hours using **HYPE** token
- Deployers can set fee share up to **50%** + additional fees
- Fully permissionless deployments

---

## 2. HyperCore Tools

### What is HyperCore?
HyperCore is Hyperliquid's native Layer 1, optimized for:
- On-chain perpetual futures
- Spot order books
- High-performance trading infrastructure

### Relevant Tools for Oracle Service

#### Oracle Price Publishing
- **setOracle API**: The primary endpoint for HIP-3 deployers to update prices
- **Update Frequency**: Minimum 2.5 seconds between calls
- **Recommended**: Update every 3 seconds (matches validator oracle update cadence)
- **Stale Price Fallback**: After 10 seconds of no updates, mark price falls back to local mark price (median of best bid, best ask, last trade)

#### API Structure
```typescript
type SetOracle = {
  dex: string;  // Name of the perp dex (<= 6 characters)
  oraclePxs: Array<[string, string]>;  // Asset and oracle prices (sorted by key)
  markPxs: Array<Array<[string, string]>>;  // Optional: Asset and mark prices
}
```

#### Constraints
- **Price Change Limit**: Each update can change `oraclePx` and `markPx` by at most **1%**
- **Open Interest Limit**: Mark price cannot be updated such that open interest would be **10x the open interest cap**
- **Update Frequency**: Must be called at least every 2.5 seconds (recommended: every 3 seconds)

#### Oracle Price Sources (Reference)
Hyperliquid's native perps use weighted median of:
- Binance (weight: 3)
- OKX (weight: 2)
- Bybit (weight: 2)
- Kraken (weight: 1)
- Kucoin (weight: 1)
- Gate IO (weight: 1)
- MEXC (weight: 1)
- Hyperliquid spot (weight: 1)

**For HIP-3 markets, we provide our own oracle prices from Pyth Network.**

---

## 3. HyperEVM Tools

### What is HyperEVM?
HyperEVM is Hyperliquid's EVM-compatible smart contract platform:
- Based on **Cancun EVM** (without blobs)
- Dual block system: fast small blocks + slow big blocks
- Native integration with HyperCore state

### Oracle Feeds Available on HyperEVM

#### Supported Oracle Providers
1. **Pyth Network**: https://docs.pyth.network/price-feeds/contract-addresses/evm
2. **Stork**: https://docs.stork.network/resources/contract-addresses/evm#hyperevm
3. **Redstone**: https://app.redstone.finance/app/feeds/
4. **Blocksense**: https://coda.io/@georgi-zlatarev/blocksense-hyperevm-price-feeds
5. **Seda**: https://docs.seda.xyz/home/for-developers/deployments

#### HyperCore ↔ HyperEVM Integration
- **Read Precompiles**: Query HyperCore state from EVM (addresses start at `0x0000000000000000000000000000000000000800`)
- **CoreWriter Contract**: Send transactions from HyperEVM to HyperCore (address: `0x3333333333333333333333333333333333333333`)
- **Gas Cost**: ~47,000 gas for basic CoreWriter calls

### Relevance to Our Oracle Service

**Current Implementation**: We're using **Pyth Network** via REST API (Hermes), which is perfect for:
- Real-time price feeds
- High reliability
- Low latency updates

**Future Consideration**: If we need on-chain oracle verification or want to build smart contracts that consume our oracle data, we could:
- Deploy contracts on HyperEVM
- Use Pyth's on-chain contracts on HyperEVM
- Bridge oracle data from HyperCore to HyperEVM if needed

---

## 4. API Endpoint: setOracle

### Correct Implementation

Based on Hyperliquid documentation, the `setOracle` endpoint should be:

**Endpoint**: `POST /exchange` (on Hyperliquid API)

**Action Type**: `setOracle`

**Payload Structure**:
```typescript
{
  action: {
    type: "setOracle",
    dex: string,  // e.g., "WARMARKET" (<= 6 chars)
    oraclePxs: [["ASSET_NAME", "price_as_string"]],  // Sorted by asset name
    markPxs: [[["ASSET_NAME", "mark_price_as_string"]]]  // Optional, can be empty array
  }
}
```

**Authentication**: Uses Hyperliquid's standard API authentication (wallet signature)

### Key Differences from Our Current Implementation

1. **Endpoint Path**: Not `/oracle/update`, but `/exchange` with action type
2. **Payload Structure**: Nested action object, not flat structure
3. **Asset Names**: Must match the asset names used during market deployment
4. **Price Format**: Prices as strings, not numbers
5. **Mark Prices**: Optional but recommended for better price discovery

---

## 5. Recommendations for WAR.MARKET Oracle Service

### Immediate Updates Needed

1. **Update API Endpoint**
   - Change from `/oracle/update` to `/exchange`
   - Use Hyperliquid's action-based API structure

2. **Implement setOracle Action**
   - Use correct payload structure with `action.type = "setOracle"`
   - Include `dex` name (e.g., "WARMARKET")
   - Format prices as strings
   - Optionally include `markPxs` for better price discovery

3. **Update Frequency**
   - Maintain 3-second update cadence (matches validator oracle updates)
   - Ensure minimum 2.5 seconds between calls
   - Handle rate limiting gracefully

4. **Price Change Validation**
   - Enforce 1% maximum change per update
   - Implement sanity checks for price jumps > 20% (already in our code)

5. **Error Handling**
   - Handle stale price fallback scenarios
   - Monitor for open interest cap violations
   - Log all publish attempts for debugging

### Future Enhancements

1. **Mark Price Calculation**
   - Implement mark price calculation using local order book data
   - Combine with oracle price for robust pricing

2. **Multi-Asset Support**
   - Support publishing prices for multiple assets in single call
   - Useful when deploying multiple indices (GDR, ESV, SHR)

3. **HyperEVM Integration** (Optional)
   - Deploy smart contracts for on-chain oracle verification
   - Enable other protocols to consume our oracle data
   - Use Pyth's on-chain contracts for additional verification

4. **Monitoring & Alerting**
   - Monitor staking requirements (1M HYPE)
   - Alert on price update failures
   - Track open interest caps

---

## 6. Resources & Documentation

### Official Documentation
- **HIP-3 Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals
- **API Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
- **HyperEVM Docs**: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm

### Python SDK Reference
- **GitHub**: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- **Examples**: Check `examples/` directory for HIP-3 deployment examples

### Oracle Providers
- **Pyth Network**: https://docs.pyth.network/
- **Hyperliquid Oracle System**: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle

---

## 7. Next Steps

1. ✅ Research complete - understand HIP-3 and builder tools
2. ⏳ Update `hyperliquid.ts` to use correct `setOracle` API structure
3. ⏳ Test with Hyperliquid testnet API
4. ⏳ Deploy HIP-3 market on testnet
5. ⏳ Verify end-to-end price publishing
6. ⏳ Monitor and optimize update frequency

---

## Summary

**HyperCore Tools** are essential for our oracle service - specifically the `setOracle` API for HIP-3 markets. We need to update our implementation to match Hyperliquid's action-based API structure.

**HyperEVM Tools** are less immediately relevant but provide future opportunities for:
- On-chain oracle verification
- Smart contract integration
- Cross-protocol oracle consumption

The key insight: We're building a **HIP-3 oracle provider**, which requires us to use the `setOracle` action through Hyperliquid's `/exchange` endpoint, not a custom oracle endpoint.

