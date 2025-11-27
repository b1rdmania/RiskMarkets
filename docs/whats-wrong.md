# What's Currently Wrong

## 🔴 Critical Issues (Will Break)

### 1. TypeScript setOracle - Invalid Signing
**File**: `apps/oracle-service/src/services/hyperliquid.ts` (lines 124-140)

**Problem**: Using HMAC signing instead of proper L1 action signing.

```typescript
// ❌ WRONG - This is a placeholder
const signature = crypto.createHmac('sha256', config.hlApiSecret).update(body).digest('hex');
```

**Why it's wrong**: Hyperliquid requires L1 action signing (like Python SDK's `sign_l1_action`), not HMAC.

**Impact**: All `setOracle` calls will fail with 422 errors.

**Fix needed**: Implement proper L1 action signing using `ethers.js` or use Python SDK for signing.

---

### 2. Python Deployment Script - Methods Don't Exist
**File**: `apps/oracle-service/scripts/deploy-market-full.py`

**Problem**: Script tries to use SDK methods that don't exist:

- ❌ `perp_deploy_register_asset2` - **Doesn't exist**
- ❌ `perp_deploy_insert_margin_table` - **Doesn't exist**
- ❌ `perp_deploy_set_margin_modes` - **Doesn't exist**
- ❌ `perp_deploy_set_funding_multipliers` - **Doesn't exist**
- ❌ `perp_deploy_set_open_interest_caps` - **Doesn't exist**

**What actually exists in SDK**:
- ✅ `perp_deploy_register_asset` - This works
- ✅ `perp_deploy_set_oracle` - This works

**Impact**: Deployment script will crash when trying to call non-existent methods.

**Fix needed**: 
- Use only `perp_deploy_register_asset` (not `register_asset2`)
- Remove calls to non-existent methods
- Check if those actions need to be done manually or via different API

---

## 🟡 Code Quality Issues

### 3. Duplicate Validation Checks
**File**: `apps/oracle-service/src/services/hyperliquid.ts` (lines 44-50 and 71-77)

**Problem**: Same validation checks appear twice.

**Impact**: Code duplication, but doesn't break functionality.

**Fix**: Remove duplicate checks.

---

## ✅ What's Correct

1. ✅ Payload structure for `setOracle` - matches Python SDK format
2. ✅ Environment variables - `HL_DEX_NAME`, `HL_COIN_SYMBOL`, `HL_ASSET_ID`
3. ✅ TypeScript types and interfaces
4. ✅ Overall code structure

---

## Summary

**Main blockers**:
1. **TypeScript signing** - Needs L1 action signing (not HMAC)
2. **Python deployment** - Only 2 methods exist, script tries to use 5+ methods

**Quick fixes**:
1. Remove duplicate validation checks ✅ (just fixed)
2. Simplify Python script to use only `perp_deploy_register_asset`
3. Implement proper L1 signing in TypeScript (or use Python SDK)

**Bottom line**: The structure is correct, but:
- TypeScript won't work until we fix signing
- Python script needs to be simplified to only use existing SDK methods

