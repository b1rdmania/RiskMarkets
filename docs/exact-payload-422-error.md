# Exact Payload Causing 422 Error

## Payload Being Sent

```json
{
  "action": {
    "type": "perpDeploy",
    "registerAsset": {
      "maxGas": null,
      "assetRequest": {
        "coin": "XAU-TEST",
        "szDecimals": 2,
        "oraclePx": "1924.5",
        "marginTableId": 0,
        "onlyIsolated": true
      },
      "dex": "XAU",
      "schema": {
        "fullName": "XAU Test DEX",
        "collateralToken": 0,
        "oracleUpdater": "0x9ee94f9e4f0577cf2f93ee427bd0ca57052952e1"
      }
    }
  },
  "nonce": 1764265350956,
  "signature": {
    "r": "0x3da8c75fdd0409880826570ffc563bef0fb834a6b08731dd99d35203a3b72679",
    "s": "0x27bde963000f22ac382d3632be3384dd74c45bbf6ab6558a3c6ca07798d48c25",
    "v": 27
  },
  "vaultAddress": null,
  "expiresAfter": null
}
```

## Error

```
422: Failed to deserialize the JSON body into the target type
```

## Potential Issues

### 1. `maxGas: null` ❌
**Issue**: Hyperliquid may not accept `null` for `maxGas`. It should either be:
- Omitted entirely, or
- A number (e.g., `0` or a specific gas limit)

**Python SDK behavior**: When we pass `max_gas=None`, the SDK sets it to `null` in JSON, which may not match Hyperliquid's Rust type.

### 2. `vaultAddress: null` and `expiresAfter: null`
These are added by the SDK's `_post_action` method. They may need to be omitted rather than `null`.

### 3. Schema Structure
The `schema` field structure may need verification against current API spec.

## Comparison with Docs

According to [Hyperliquid HIP-3 docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions):

The `registerAsset` action should have:
- `dex`: string ✅
- `assetRequest`: object with:
  - `coin`: string ✅
  - `szDecimals`: number ✅
  - `oraclePx`: string ✅
  - `marginTableId`: number ✅
  - `onlyIsolated`: boolean ✅
- `schema`: object (for first asset) ✅
- `maxGas`: **May need to be omitted or a number, not null**

## Next Steps

1. **Try omitting `maxGas`** instead of passing `null`
2. **Try omitting `vaultAddress` and `expiresAfter`** instead of `null`
3. **Check if testnet requires DEX registration first**
4. **Share this payload with Hyperliquid team** to confirm the exact structure

## Question for Hyperliquid Team

> Using the Python SDK on testnet, `perp_deploy_register_asset` is returning 422 (Failed to deserialize JSON body).
> 
> **Payload being sent:**
> ```json
> [PASTE PAYLOAD ABOVE]
> ```
> 
> **Questions:**
> 1. Is `maxGas: null` valid, or should it be omitted/a number?
> 2. Should `vaultAddress` and `expiresAfter` be omitted for `perpDeploy` actions?
> 3. Is HIP-3 deployment open on testnet for any wallet, or is it permission-gated?
> 4. Does the DEX name "XAU" need to be registered first before registering assets?

