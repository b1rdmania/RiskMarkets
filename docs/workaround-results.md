# Workaround Results - Manual Payload Construction

## Attempt 1: Omit maxGas, omit vaultAddress/expiresAfter
**Result**: ❌ 422 Error

**Payload**:
```json
{
  "action": {
    "type": "perpDeploy",
    "registerAsset": {
      "assetRequest": {
        "coin": "XAU-TEST",
        "szDecimals": 2,
        "oraclePx": "1924.5",
        "marginTableId": 0,
        "onlyIsolated": true
      },
      "dex": "XAU",
      "schema": { ... }
    }
  },
  "nonce": 1764276688092,
  "signature": { ... }
}
```

## Attempt 2: Omit maxGas, include vaultAddress/expiresAfter as null
**Result**: ❌ 422 Error

**Payload**:
```json
{
  "action": { ... },
  "nonce": 1764276705033,
  "signature": { ... },
  "vaultAddress": null,
  "expiresAfter": null
}
```

## Analysis

The 422 error persists even after:
- ✅ Removing `maxGas: null`
- ✅ Using SDK's `sign_l1_action` (signing is correct)
- ✅ Matching SDK's payload structure (except maxGas)

This suggests the issue is **not** just `maxGas: null`, but potentially:

1. **Field structure**: The nested `assetRequest` structure may be wrong
2. **Field names**: `marginTableId` vs `marginTable` vs something else
3. **Testnet permissions**: HIP-3 deployment may be permission-gated
4. **DEX registration**: DEX name "XAU" may need to be registered first
5. **Schema structure**: The `schema` object may have wrong fields

## Next Steps

1. **Check Hyperliquid docs** for exact field names and structure
2. **Contact Hyperliquid team** with both payloads (with and without maxGas)
3. **Verify testnet permissions** - is HIP-3 open to all wallets?
4. **Try different field combinations**:
   - Flatten `assetRequest` fields?
   - Different `marginTableId` value?
   - Omit `schema` for test?

## Questions for Hyperliquid

1. Is the `assetRequest` nesting correct, or should fields be flattened?
2. Is `marginTableId: 0` valid, or does it need a specific value?
3. Is the `schema` object required for first asset, or optional?
4. Is HIP-3 testnet deployment currently open or permission-gated?
5. Does the DEX name need to be registered before registering assets?

