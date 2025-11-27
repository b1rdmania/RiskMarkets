# Correct HIP-3 Structure (Based on User Clarification)

## Key Insights

1. **No single "createMarket" call** - it's a series of `PerpDeployAction`s
2. **Correct structure**: `{ type: "perpDeploy", registerAsset2: {...} }` or `{ type: "perpDeploy", setOracle: {...} }`
3. **Three IDs needed**:
   - `dex`: DEX name (2-4 chars, e.g., "XAU")
   - `coin`: Coin symbol (e.g., "XAU-TEST")
   - `assetId`: Numeric index from `meta.universe` (for trading)

## Deployment Sequence

### Step 1: Insert Margin Table (Optional but usually needed)
```python
# Insert margin table for your DEX
perp_deploy_insert_margin_table(dex="XAU", ...)
```

### Step 2: Register Asset
```python
exchange.perp_deploy_register_asset2(
    dex="XAU",
    max_gas=None,
    coin="XAU-TEST",
    sz_decimals=2,
    oracle_px="1924.55",
    margin_table_id=1,  # From step 1
    margin_mode="strictIsolated",  # or "noCross"
    schema={
        "fullName": "XAU Test DEX",
        "collateralToken": 0,  # USDC index
        "oracleUpdater": wallet.address.lower(),
    }
)
```

### Step 3: Set Margin Modes, Funding, OI Caps
```python
# Set margin modes
perp_deploy_set_margin_modes(dex="XAU", margin_modes=[["XAU-TEST", "strictIsolated"]])

# Set funding multipliers
perp_deploy_set_funding_multipliers(dex="XAU", funding_multipliers=[["XAU-TEST", "1.0"]])

# Set open interest caps
perp_deploy_set_open_interest_caps(dex="XAU", open_interest_caps=[["XAU-TEST", 1_000_000]])
```

### Step 4: Get Asset ID
```python
from hyperliquid.info import Info
info = Info(constants.TESTNET_API_URL, skip_ws=True)
meta = info.meta()

# Find asset in universe
asset_id = None
for idx, asset in enumerate(meta['universe']):
    if asset['name'] == "XAU-TEST":
        asset_id = idx
        break
```

## setOracle Structure (For Oracle Service)

### Correct Payload
```typescript
{
  action: {
    type: "perpDeploy",
    setOracle: {
      dex: "XAU",  // DEX name (2-4 chars)
      oraclePxs: [["XAU-TEST", "1924.55"]],  // Sorted array of [coin, price] pairs
      markPxs: [],  // List of sorted arrays (optional)
      externalPerpPxs: [["XAU-TEST", "1924.55"]]  // Sorted array (optional)
    }
  },
  nonce: <timestamp>,
  signature: { r, s, v }  // L1 action signature
}
```

### Python SDK Method
```python
exchange.perp_deploy_set_oracle(
    dex="XAU",
    oracle_pxs={"XAU-TEST": "1924.55"},  # Dict[str, str]
    all_mark_pxs=[],  # List[Dict[str, str]]
    external_perp_pxs={"XAU-TEST": "1924.55"},  # Dict[str, str]
)
```

The SDK automatically:
- Converts dicts to sorted arrays for wire format
- Signs using `sign_l1_action`
- Sends to `/exchange` endpoint

## Environment Variables (Updated)

```env
HL_DEX_NAME=XAU          # DEX name (2-4 chars)
HL_COIN_SYMBOL=XAU-TEST  # Coin symbol
HL_ASSET_ID=42           # Numeric asset ID from meta.universe (for trading)
```

## Next Steps

1. **Python deployment script**: Do full sequence (insertMarginTable → registerAsset2 → setMarginModes → etc.)
2. **TypeScript setOracle**: Update to match Python SDK structure
3. **L1 action signing**: Implement `sign_l1_action` equivalent in TypeScript (or use Python SDK for now)

