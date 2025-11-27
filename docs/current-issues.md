# Current Issues - What's Wrong Right Now

## 🔴 Critical Issues

### 1. TypeScript setOracle Signing (Won't Work)
**Location**: `apps/oracle-service/src/services/hyperliquid.ts` (lines 124-140)

**Problem**: Using placeholder HMAC signing instead of proper L1 action signing.

```typescript
// ❌ WRONG - This is placeholder code
const signature = crypto.createHmac('sha256', config.hlApiSecret).update(body).digest('hex');
const requestBody = {
  action,
  nonce,
  signature: {
    r: signature.slice(0, 64),  // Not a real Ethereum signature
    s: signature.slice(64, 128),
    v: 27,
  },
};
```

**What's needed**: Proper L1 action signing like Python SDK's `sign_l1_action()`.

**Impact**: `setOracle` calls will fail with 422 errors because signature is invalid.

---

### 2. Python Deployment Script - Missing SDK Methods
**Location**: `apps/oracle-service/scripts/deploy-market-full.py`

**Problem**: Script tries to use methods that don't exist in the Python SDK:

- ❌ `perp_deploy_register_asset2` - **Doesn't exist** (only `perp_deploy_register_asset` exists)
- ❌ `perp_deploy_insert_margin_table` - **Doesn't exist** (not in SDK)
- ❌ `perp_deploy_set_margin_modes` - **Doesn't exist** (not in SDK)
- ❌ `perp_deploy_set_funding_multipliers` - **Doesn't exist** (not in SDK)
- ❌ `perp_deploy_set_open_interest_caps` - **Doesn't exist** (not in SDK)

**What exists in SDK**:
- ✅ `perp_deploy_register_asset` - This exists
- ✅ `perp_deploy_set_oracle` - This exists

**Impact**: Deployment script will fail when trying to call non-existent methods.

---

### 3. Duplicate Validation Checks
**Location**: `apps/oracle-service/src/services/hyperliquid.ts` (lines 44-50 and 71-77)

**Problem**: Duplicate checks for `hlCoinSymbol` and `hlDexName`.

**Impact**: Code duplication, but not breaking.

---

## 🟡 Medium Issues

### 4. Python SDK Method Signature Mismatch
**Location**: `apps/oracle-service/scripts/deploy-market-full.py`

**Problem**: `perp_deploy_register_asset` signature doesn't match what we're calling:
- We're calling with `margin_mode` parameter
- SDK expects `only_isolated` boolean instead

**Impact**: Will fail when trying to register asset.

---

### 5. Missing Schema Validation
**Problem**: No validation that required fields are present before attempting deployment.

**Impact**: Runtime errors instead of clear validation messages.

---

## ✅ What's Correct

1. ✅ Payload structure for `setOracle` - matches Python SDK format
2. ✅ Environment variable structure - `HL_DEX_NAME`, `HL_COIN_SYMBOL`, `HL_ASSET_ID`
3. ✅ TypeScript types and interfaces
4. ✅ Overall architecture and flow

---

## Summary

**Main blockers**:
1. **TypeScript signing** - Needs proper L1 action signing (not HMAC)
2. **Python deployment** - SDK doesn't have all the methods we need, or they have different names

**Quick wins**:
1. Fix duplicate validation checks
2. Use only methods that exist in SDK (`perp_deploy_register_asset`, `perp_deploy_set_oracle`)
3. Check Python SDK source for exact method signatures

**Next steps**:
1. Check Python SDK source code for all available `perp_deploy_*` methods
2. Implement proper L1 action signing in TypeScript (or use Python SDK for signing)
3. Simplify deployment script to use only existing SDK methods

