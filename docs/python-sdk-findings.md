# Python SDK Findings - HIP-3 Deployment

## Status
Even using the official Python SDK with the correct method signature, we're still getting **422 error**: "Failed to deserialize the JSON body into the target type"

## What We Tried

### Correct Method Call
```python
exchange.perp_deploy_register_asset(
    dex='WARMARKET',
    max_gas=None,
    coin='XAU-TEST',
    sz_decimals=2,
    oracle_px='1924.55',
    margin_table_id=0,
    only_isolated=False,
    schema=None,
)
```

### SDK Payload Structure
Based on SDK source code, it creates:
```json
{
  "type": "perpDeploy",
  "registerAsset": {
    "maxGas": null,
    "assetRequest": {
      "coin": "XAU-TEST",
      "szDecimals": 2,
      "oraclePx": "1924.55",
      "marginTableId": 0,
      "onlyIsolated": false
    }
  }
}
```

## Possible Issues

### 1. Testnet Requirements
- **Staking**: May need staked HYPE even on testnet (docs say 1M for mainnet)
- **Permissions**: API wallet might need specific permissions
- **Prerequisites**: May need to complete other steps first

### 2. DEX Name
- `dex: 'WARMARKET'` - might need to be registered first
- Or might need to be a specific format

### 3. Margin Table ID
- `margin_table_id: 0` - might need to be a valid, non-zero ID
- Or might need to be created first

### 4. Schema
- `schema: None` - might be required, not optional
- Might need to provide oracle updater address

### 5. API Wallet Permissions
- API wallet might not have permission to deploy markets
- Might need to use main wallet, not API wallet

## Questions for Dev Team

1. **Testnet Requirements**: Are there testnet-specific requirements for HIP-3 deployment?
   - Staking requirements?
   - Prerequisites?
   - Different process than mainnet?

2. **DEX Registration**: Does the DEX name need to be registered first?
   - How do we register a DEX name?
   - Or should we use an existing DEX?

3. **Margin Table**: Does `margin_table_id: 0` work, or do we need a valid margin table?
   - How do we create/get a margin table ID?

4. **Schema**: Is the `schema` parameter required?
   - What should `oracleUpdater` be set to?
   - Should it be the API wallet address?

5. **API Wallet vs Main Wallet**: Should we use:
   - API wallet (current approach)
   - Main wallet that authorized the API wallet

6. **Working Example**: Can you provide a working example of HIP-3 market creation on testnet?

## Next Steps

1. Try with `schema` parameter filled in
2. Try with main wallet instead of API wallet
3. Check if DEX needs to be registered first
4. Verify margin table ID requirements

