## Deployment Guide (Testnet)

### 1. Environment

Create `apps/oracle-service/.env.testnet` (or use the example) with at least:

```env
NETWORK=testnet

# Pyth (testnet)
PYTH_CLUSTER=pythnet
PYTH_API_URL=https://hermes-beta.pyth.network/api
PYTH_FEED_ID=<TESTNET_FEED_ID>

# Hyperliquid testnet
HL_TESTNET_URL=https://api.hyperliquid-testnet.xyz

# Builder wallet (single signer)
HL_MASTER_ADDRESS=<BUILDER_ADDRESS>
HL_MASTER_PRIVATE_KEY=<BUILDER_PRIVATE_KEY>

# HIP-3 naming
HL_DEX_NAME=war
HL_COIN_SYMBOL=gdr

INITIAL_ORACLE_PRICE=100.0
PUBLISH_ENABLED=false
```

### 2. Deploy a testnet market (HIP‑3)

From `apps/oracle-service`:

```bash
NETWORK=testnet python3 scripts/deploy-register2.py
```

This sends a single `perpDeploy.registerAsset2` action using the builder wallet to attempt to create a new DEX + first asset on testnet.

### 3. Run the oracle service

```bash
cd apps/oracle-service
npm install
npm run dev
```

With `PUBLISH_ENABLED=true` the service can be wired to periodically publish prices once the HIP‑3 market is live.

### 4. Debugging

- Check `scripts/deploy-register2.py` and `scripts/deploy-dex.py` for the exact actions used for deployment.
- Use:

  ```bash
  curl http://localhost:4000/health
  curl http://localhost:4000/price
  ```

  to inspect the local oracle service.


