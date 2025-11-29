# WAR.MARKET Oracle Service

Backend service for fetching a Pyth price on testnet, computing a simple index, and publishing it to Hyperliquid.

## Setup

1. **Create env file**

   ```bash
   cd apps/oracle-service
   cp .env.testnet.example .env.testnet
   ```

2. **Configure `.env.testnet`**

   Minimal fields:

   ```env
   NETWORK=testnet

   # Pyth
   PYTH_CLUSTER=pythnet
   PYTH_API_URL=https://hermes-beta.pyth.network/api
   PYTH_FEED_ID=<TESTNET_FEED_ID>

   # Hyperliquid testnet
   HL_TESTNET_URL=https://api.hyperliquid-testnet.xyz

   # Builder wallet (single signer)
   HL_MASTER_ADDRESS=<BUILDER_ADDRESS>
   HL_MASTER_PRIVATE_KEY=<BUILDER_PRIVATE_KEY>

   # HIP-3 market naming
   HL_DEX_NAME=war
   HL_COIN_SYMBOL=gdr

   # Oracle loop
   INITIAL_ORACLE_PRICE=100.0
   PUBLISH_ENABLED=false
   PUBLISH_INTERVAL_MS=3000
   ```

## Running

```bash
npm install
npm run dev
```

Service will start on `http://localhost:4000`.

## Endpoints

- **`GET /health`** – service health and current state
- **`GET /price`** – current index price
- **`GET /feeds`** – list/search available Pyth feeds
- **`GET /feeds/:feedId`** – get metadata for a feed
- **`GET /feeds/:feedId/validate`** – validate a feed ID

For more detail on the intended pipeline and HIP‑3 usage, see `docs/whitepaper-v0.2.md`.

