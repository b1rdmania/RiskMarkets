# createMarket Payload for XAU-TEST

## Exact Payload Structure

Based on Hyperliquid docs, here's the exact `createMarket` (registerAsset) payload:

```json
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

## Required Fields

- **coin**: `"XAU-TEST"` - Market symbol
- **szDecimals**: `2` - Size decimals (for $0.01 increments)
- **oraclePx**: `"1924.55"` - Initial oracle price as **string**
- **marginTableId**: `0` - Margin table ID (0 for default)
- **onlyIsolated**: `false` - Allow cross margin

## Signing Issue

The 422 error suggests the **signature format** is incorrect. Hyperliquid uses a **specific L1 action signing scheme** that's different from standard Ethereum message signing.

### What We're Doing (Wrong)
```typescript
const message = JSON.stringify({ action, nonce });
const signature = await wallet.signMessage(message);
```

### What Hyperliquid Expects
Hyperliquid's Python SDK uses `sign_l1_action(action, wallet, nonce)` which:
1. Serializes the action in a specific format
2. Signs with a specific scheme (not standard `signMessage`)
3. Returns signature in `{r, s, v}` format

## Solution Options

### Option 1: Use Python SDK (Fastest)
The Python SDK has the correct signing implementation. We can:
1. Create a simple Python script to deploy
2. Get the exact signature format
3. Port to TypeScript

### Option 2: Replicate Python SDK Signing
Check the Python SDK source for `sign_l1_action`:
- Location: `hyperliquid-python-sdk/hyperliquid/utils/signing.py`
- Replicate the exact signing logic in TypeScript

### Option 3: Check Hyperliquid Docs
Look for:
- Exact signing specification
- Example code snippets
- Discord/community examples

## Next Steps

1. **Check Python SDK**: Look at `sign_l1_action` implementation
2. **Try Python script**: Quick test deployment with Python
3. **Port to TypeScript**: Once we know the exact signing format

## Current Status

✅ Payload structure: **Correct**  
✅ Required fields: **All present**  
❌ Signature format: **Needs verification**

The payload structure matches the docs, but the signing method needs to match Hyperliquid's specific L1 action signing scheme.

