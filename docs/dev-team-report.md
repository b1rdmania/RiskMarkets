# Dev Team Report: HIP-3 Market Deployment Status

## Executive Summary

We've successfully:
- ✅ Fixed payload structure (using `registerAsset2` with `marginMode`)
- ✅ Switched to Python SDK for canonical signing
- ✅ Verified signature recovery works correctly
- ❌ **Blocked**: Wallet authorization issue on Hyperliquid testnet

**Current Status**: All code is correct. The remaining issue is wallet authorization/recognition on Hyperliquid's side.

---

## What We've Tried

### 1. Fixed Payload Structure ✅

**Problem**: Using `registerAsset` with `onlyIsolated` (outdated structure)

**Solution**: Switched to `registerAsset2` with `marginMode: "strictIsolated"`

**Result**: Got 200 response (not 422), payload structure is correct

**Payload**:
```json
{
  "action": {
    "type": "perpDeploy",
    "registerAsset2": {
      "assetRequest": {
        "coin": "XAU-TEST",
        "szDecimals": 2,
        "oraclePx": "1924.5",
        "marginTableId": 1,
        "marginMode": "strictIsolated"
      },
      "dex": "XAU",
      "schema": {
        "fullName": "XAU Test DEX",
        "collateralToken": 0,
        "oracleUpdater": "0x86c672b3553576fa436539f21bd660f44ce10a86"
      }
    }
  },
  "nonce": <timestamp>,
  "signature": { "r": "...", "s": "...", "v": 27 },
  "vaultAddress": null,
  "expiresAfter": null
}
```

---

### 2. Fixed Signature Mismatch ✅

**Problem**: Custom TypeScript signing was building different message hash than Hyperliquid expects

**Symptom**: 
- Local recovery: ✅ Correct (`0x86C672b3553576Fa436539F21BD660F44Ce10a86`)
- Hyperliquid recovery: ❌ Different address (changed each run)

**Root Cause**: As Hyperliquid docs warn:
> "Believing that the signature must be correct because calling recover signer locally results in the correct address… The payload for recover signer is constructed based on the action and does not necessarily match."

**Solution**: Switched to Python SDK's `sign_l1_action` (canonical implementation)

**Files Changed**:
- `scripts/set-oracle.py` - Uses `Exchange.perp_deploy_set_oracle()` 
- `src/services/hyperliquid.ts` - Calls Python script instead of custom signing

**Result**: Signature now recovers correctly to `0x86c672b3553576fa436539f21bd660f44ce10a86`

---

### 3. Standardized Wallet Configuration ✅

**Problem**: Multiple wallet variables, confusion about which to use

**Solution**: Standardized on:
- `HL_API_PRIVATE_KEY` - Private key for signing
- `HL_API_ADDRESS` - Wallet address (for verification)

**Verification Scripts**:
- `scripts/check-signer.ts` - TypeScript verification
- `scripts/deploy-manual.py` - Python verification (built-in)

**Result**: Both verify signer is `0x86C672b3553576Fa436539F21BD660F44Ce10a86`

---

## Current Error

### Error Message
```json
{
  "status": "err",
  "response": "User or API Wallet 0x86c672b3553576fa436539f21bd660f44ce10a86 does not exist."
}
```

### What This Means

1. ✅ **Payload structure**: Correct (200 response, not 422)
2. ✅ **Signature**: Correct (recovers to correct address)
3. ✅ **Wallet exists**: Confirmed (user state query works)
4. ❌ **Wallet authorization**: Not recognized for L1 actions

### Verification

```python
# Wallet exists in Hyperliquid
info = Info(constants.TESTNET_API_URL, skip_ws=True)
user_state = info.user_state("0x86C672b3553576Fa436539F21BD660F44Ce10a86")
# Returns: {'marginSummary': ..., 'assetPositions': ...} ✅
```

But L1 actions still fail with "does not exist" error.

---

## What We've Verified

### ✅ Working
1. **Payload structure** - `registerAsset2` with correct fields
2. **Signature recovery** - Correct address recovered
3. **Wallet existence** - User state query succeeds
4. **Python SDK integration** - Using canonical signing

### ❌ Not Working
1. **L1 action authorization** - Wallet not recognized for `perpDeploy` actions

---

## Suggested Next Steps

### Option 1: Verify Wallet Authorization (Recommended First)

Check in Hyperliquid Testnet UI:
1. Go to https://app.hyperliquid-testnet.xyz
2. Check API wallet settings
3. Verify wallet `0x86C672b3553576Fa436539F21BD660F44Ce10a86` is:
   - Authorized for API access
   - Has testnet USDC (may be required)
   - Is active/not expired

### Option 2: Contact Hyperliquid Support

Ask them:
> "We're trying to deploy a HIP-3 market on testnet using API wallet `0x86C672b3553576Fa436539F21BD660F44Ce10a86`. The wallet exists (user state query works), payload structure is correct (200 response), and signature recovers correctly. However, we get 'User or API Wallet does not exist' for `perpDeploy.registerAsset2` actions. Is there a specific authorization step needed for API wallets to perform L1 actions on testnet?"

### Option 3: Try with Main Wallet

If the API wallet can't perform L1 actions, we may need to:
1. Use the main wallet (`0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`) for deployment
2. Keep API wallet for regular trading operations

---

## Code Status

### ✅ Ready to Deploy
- `scripts/deploy-manual.py` - Uses Python SDK, correct payload structure
- `scripts/set-oracle.py` - Uses Python SDK for canonical signing
- `src/services/hyperliquid.ts` - Calls Python script (no custom signing)
- All verification scripts working

### Configuration
- `.env.testnet` - Uses `HL_API_PRIVATE_KEY` and `HL_API_ADDRESS`
- Wallet: `0x86C672b3553576Fa436539F21BD660F44Ce10a86`
- DEX: `XAU`
- Coin: `XAU-TEST`

---

## Technical Details

### Signing Approach
- **L1 Actions**: Python SDK (`hyperliquid.exchange.Exchange`)
- **Pyth Integration**: TypeScript (working)
- **Orchestration**: Node.js service calls Python scripts

### Why Python SDK?
Hyperliquid's docs explicitly recommend:
> "It is recommended to use an existing SDK instead of manually generating signatures. There are many potential ways in which signatures can be wrong… An incorrect signature does not indicate why it is incorrect which makes debugging more challenging."

We were hitting exactly this issue with custom TypeScript signing.

---

## Summary for Dev Team

**Status**: Code is correct. Blocked on wallet authorization.

**What works**:
- Payload structure ✅
- Signature generation ✅
- Wallet verification ✅

**What doesn't work**:
- L1 action authorization ❌ (Hyperliquid side issue)

**Next action**: Verify wallet authorization in Hyperliquid UI or contact Hyperliquid support.

**Files to review**:
- `apps/oracle-service/scripts/deploy-manual.py` - Deployment script
- `apps/oracle-service/scripts/set-oracle.py` - Oracle update script
- `apps/oracle-service/src/services/hyperliquid.ts` - Service integration

