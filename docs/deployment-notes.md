# HIP-3 Market Deployment - Current Status

## Attempt Summary

We attempted to deploy a HIP-3 market (`GOLD-TEST`) on Hyperliquid testnet but encountered a **422 error**: "Failed to deserialize the JSON body into the target type".

## Issues Identified

### 1. API Structure
The exact API structure for `perpDeploy` with `registerAsset` needs verification. We tried:
```json
{
  "action": {
    "type": "perpDeploy",
    "registerAsset": {
      "type": "registerAsset",
      "name": "GOLD-TEST",
      "szDecimals": 2,
      "maxLeverage": 20
    }
  },
  "nonce": <timestamp>,
  "signature": { ... }
}
```

### 2. Authentication Method
Hyperliquid's `/exchange` endpoint requires **Ethereum wallet signature**, not HMAC. The API wallet private key needs to be used with proper Ethereum signing (like `ethers` or `ethereumjs-util`).

Current attempt used HMAC which is incorrect.

## Next Steps

### Option 1: Use Python SDK (Recommended for Testing)
The Hyperliquid Python SDK has proper wallet signing built-in. We could:
1. Create a simple Python script using their SDK
2. Test deployment with Python first
3. Then port the exact structure to TypeScript

### Option 2: Install Ethereum Signing Library
Install `ethers` or `ethereumjs-util` and implement proper wallet signing:
```bash
cd apps/oracle-service
npm install ethers
```

Then use proper Ethereum signing:
```typescript
import { Wallet } from 'ethers';

const wallet = new Wallet(API_SECRET);
const message = JSON.stringify({ action, nonce });
const signature = await wallet.signMessage(message);
```

### Option 3: Verify API Structure
Check Hyperliquid's official docs or Discord for:
- Exact `registerAsset` structure
- Required fields (maybe `oraclePx`, `marginTableId`, etc.)
- Example deployment payload

## Required Fields (from docs)

Based on Hyperliquid docs, `registerAsset` might need:
- `coin`: string (asset name)
- `szDecimals`: number
- `oraclePx`: string (initial oracle price)
- `marginTableId`: number
- `onlyIsolated`: boolean

We may be missing required fields like `oraclePx` and `marginTableId`.

## Current Script Location

`apps/oracle-service/scripts/deploy-market.ts` - ready to update once we have correct structure.

## Recommendation

1. **First**: Check Hyperliquid Discord/community for deployment examples
2. **Second**: Try Python SDK approach to verify the exact API structure
3. **Third**: Port working solution to TypeScript with proper Ethereum signing

