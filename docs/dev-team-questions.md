# Questions for Dev Team: HIP-3 Market Creation on Hyperliquid Testnet

## What We're Trying To Do

Create a HIP-3 perpetual market (`XAU-TEST`) on Hyperliquid testnet via API, then publish oracle prices to it.

## Current Status

### ✅ What's Working
- API wallet created and authorized on testnet
- Credentials configured (`HL_API_KEY`, `HL_API_SECRET`)
- Payload structure matches Hyperliquid docs
- Ethereum wallet signing implemented (using `ethers.js`)

### ❌ What's Failing
**422 Error**: "Failed to deserialize the JSON body into the target type"

## Exact Payload We're Sending

```json
POST https://api.hyperliquid-testnet.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "perpDeploy",
    "registerAsset": {
      "type": "registerAsset",
      "coin": "XAU-TEST",
      "szDecimals": 2,
      "oraclePx": "1924.55",
      "marginTableId": 0,
      "onlyIsolated": false
    }
  },
  "nonce": 1764259757160,
  "signature": {
    "r": "0x...",
    "s": "0x...",
    "v": 27
  }
}
```

## Current Signing Implementation

We're using `ethers.js` to sign:

```typescript
const wallet = new Wallet(API_SECRET); // API wallet private key
const message = JSON.stringify({ action, nonce });
const signature = await wallet.signMessage(message);
// Then parsing into {r, s, v} format
```

## Questions for Dev Team

### 1. Signature Format
**Question**: What is the exact signing scheme for Hyperliquid L1 actions?

- Is it standard Ethereum `signMessage()` (EIP-191)?
- Or a custom signing format specific to Hyperliquid?
- What exactly should be signed? (action + nonce? specific serialization?)

### 2. Payload Structure
**Question**: Is the `registerAsset` payload structure correct?

- Are all required fields present?
- Is `oraclePx` format correct (string vs number)?
- Should `marginTableId` be 0 or a specific value?
- Any other required fields we're missing?

### 3. API Wallet Authentication
**Question**: How should API wallets authenticate for `perpDeploy` actions?

- Should we use the API wallet's private key directly?
- Or is there a different authentication method for API wallets?
- Does the signature need to come from the main wallet, not the API wallet?

### 4. Testnet-Specific Requirements
**Question**: Are there testnet-specific requirements for HIP-3 deployment?

- Do we need staked HYPE on testnet? (docs say 1M for mainnet)
- Any testnet-only parameters or restrictions?
- Different endpoint or payload format for testnet?

### 5. Example Code
**Question**: Can you provide a working example?

- TypeScript/JavaScript example for `perpDeploy` with `registerAsset`
- Or Python SDK example we can reference
- Exact signing code that works

## What We've Tried

1. ✅ Standard Ethereum `signMessage()` - **422 error**
2. ✅ HMAC signing - **422 error**  
3. ✅ Various payload structures - **422 error**
4. ✅ Different field names (`name` vs `coin`) - **422 error**

## Expected Response Format

When successful, we expect:
```json
{
  "status": "ok",
  "response": {
    "assetId": <number>,
    "symbol": "XAU-TEST",
    ...
  }
}
```

The `assetId` becomes our `HL_MARKET_ID` for oracle publishing.

## Code Location

Our deployment script: `apps/oracle-service/scripts/deploy-market.ts`

We can share the full code if needed.

---

**TL;DR**: We have the correct payload structure but getting 422 errors. Need to know:
1. Exact signing format for Hyperliquid L1 actions
2. If payload structure is correct
3. Working example code

