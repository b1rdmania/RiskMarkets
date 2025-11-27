# Question for Hyperliquid Team

## Context

Using the **official Python SDK** (`hyperliquid-python-sdk`) on **testnet**, `perp_deploy_register_asset` is returning **422: "Failed to deserialize the JSON body into the target type"**.

## Exact Payload Being Sent

```json
POST https://api.hyperliquid-testnet.xyz/exchange
Content-Type: application/json

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

## Code Used

```python
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import eth_account

wallet = eth_account.Account.from_key(PRIVATE_KEY)
exchange = Exchange(wallet, constants.TESTNET_API_URL)

result = exchange.perp_deploy_register_asset(
    dex="XAU",
    max_gas=None,  # SDK sets this to null in JSON
    coin="XAU-TEST",
    sz_decimals=2,
    oracle_px="1924.5",
    margin_table_id=0,
    only_isolated=True,
    schema={
        'fullName': 'XAU Test DEX',
        'collateralToken': 0,
        'oracleUpdater': wallet.address.lower(),
    }
)
```

## Questions

1. **Is `maxGas: null` valid?** Or should it be:
   - Omitted entirely (not in JSON)?
   - A number (e.g., `0` or specific gas limit)?

2. **Should `vaultAddress` and `expiresAfter` be omitted** for `perpDeploy` actions, or is `null` acceptable?

3. **Is HIP-3 deployment open on testnet** for any wallet, or is it currently permission-gated?

4. **Does the DEX name need to be registered first** before registering assets, or can we register a DEX+asset in one call?

5. **Is the payload structure correct** according to the current API spec? The SDK may be out of sync.

## What We've Verified

- ✅ Wallet signing works (signature format is correct)
- ✅ Using official Python SDK
- ✅ Payload structure matches SDK examples
- ✅ All required fields appear to be present

## Potential Issues

- `maxGas: null` may not match Rust `Option<u64>` type (needs `Some(value)` or omitted)
- Testnet may require special permissions for HIP-3
- SDK may be out of sync with current API spec

## Next Steps

Once we know:
- The correct `maxGas` handling
- Whether testnet HIP-3 is permission-gated
- If DEX registration is required first

We can proceed with deployment.

