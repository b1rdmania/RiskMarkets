## Hyperliquid Notes (HIP‑3 / Oracle)

This file is a short reference for how the WAR.MARKET oracle is intended to talk to Hyperliquid.

### HIP‑3 markets (high level)

- **Deploy**: builder uses HIP‑3 deployer actions (`perpDeploy.registerAsset2`, then `perpDeploy.registerAsset` for extra assets).
- **Operate**: builder is responsible for publishing prices via `setOracle` on `/exchange`.

### Oracle publishing (`setOracle`)

- **Endpoint**: `POST /exchange`
- **Action**:

  ```ts
  {
    action: {
      type: "setOracle",
      dex: string,                   // short dex name
      oraclePxs: Array<[string,string]>,
      markPxs?: Array<Array<[string,string]>>
    }
  }
  ```

- **Notes**:
  - Prices are sent as strings.
  - Asset names must match what was used at deploy time.
  - Updates should be frequent and small (see official docs for exact limits).

For complete details, refer directly to Hyperliquid’s HIP‑3 and API docs. This repository keeps the client logic thin and defers to those sources for authoritative behaviour.


