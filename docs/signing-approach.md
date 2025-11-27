# Signing Approach - Using Python SDK

## Problem Identified

We were hitting the exact issue Hyperliquid warns about in their docs:

> "Believing that the signature must be correct because calling recover signer locally results in the correct address… The payload for recover signer is constructed based on the action and does not necessarily match."

- ✅ Local TypeScript recovery: Works correctly
- ❌ Hyperliquid recovery: Different address (changes each run)
- **Root cause**: TypeScript is building a different message hash than Hyperliquid expects

## Solution: Use Python SDK for L1 Actions

Following Hyperliquid's recommendation:

> "It is recommended to use an existing SDK instead of manually generating signatures."

### Implementation

**Option A (Current)**: Python SDK for L1 actions, Node.js for orchestration

- **Python scripts** (`scripts/set-oracle.py`): Use `hyperliquid.exchange.Exchange.perp_deploy_set_oracle()` with canonical signing
- **TypeScript service** (`src/services/hyperliquid.ts`): Calls Python script via `execSync` for `setOracle`
- **Node.js service**: Handles Pyth fetching, `/health`, `/price` endpoints

### Benefits

1. ✅ Uses Hyperliquid's canonical signing implementation
2. ✅ No message hash mismatches
3. ✅ Fastest path to working testnet market
4. ✅ Can migrate to TypeScript SDK later if needed

### Files

- `scripts/set-oracle.py` - Python script using SDK's `perp_deploy_set_oracle`
- `src/services/hyperliquid.ts` - Updated to call Python script instead of custom signing

### Future: TypeScript SDK Option

If we want pure TypeScript later, use official SDK:
- `hyperliquid` or `@nktkas/hyperliquid` npm packages
- They handle EIP-712 + msgpack + tuple sorting correctly
- No hand-rolled hashes

