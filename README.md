## WAR.MARKET — Testnet MVP (HIP-3 Builder Sandbox)

WAR.MARKET is an experimental synthetic-index project exploring macro-volatility surfaces built on top of Hyperliquid’s HIP‑3 system.

This repository contains:

- **Static front-end prototype** (HTML/CSS/JS)
- **Small testnet oracle + deploy service** used to validate HIP‑3 flows end-to-end

The goal of this MVP is to stand up a single testnet perp DEX with synthetic sector indices (defence rotation, energy shock, safe-haven rotation), then stress-test:

- **Pyth → Hyperliquid price updates**
- **HIP‑3 oracle posting**
- **Market index structures**
- **DEX lifecycle** (deploy, oracle flow, health checks)

This is a builder-level prototype, not a production app.

### Demo

- **Product reel**: [`assets/Video_Generation_With_GIF_Added(1).mp4`](assets/Video_Generation_With_GIF_Added(1).mp4)

---

## Front-End Prototype

- **Location**: root HTML/CSS pages (`index.html`, `terminal.html`, `vault.html`)

Three pages demonstrate the UI direction:

1. **Landing Page** (`index.html`)
   - Hero section with video reel slot
   - Branding + WAR.MARKET messaging
   - Simple explainer strip
   - Map-style visual language (no conflict imagery)

2. **Trading Terminal** (`terminal.html`)
   - Synthetic index table (GDR, ESV, SHR)
   - Volatility/tension ticker
   - Drawer mock for oracle breakdown + trade inputs
   - Designed for future integration with HIP‑3 asset metadata

3. **riskHYPE Vault** (`vault.html`)
   - Mock staking panel
   - Deposit / withdraw flow
   - Metrics + activity feed
   - Mirrors HIP‑3 “builder staking” but uses testnet placeholder logic

Assets live under `assets/` (map overlay, video files, etc.).

---

## Oracle + HIP-3 Testnet Service

- **Location**: `apps/oracle-service/`

A minimal TypeScript service for:

- **Fetching** Pyth testnet price feeds
- **Computing** lightweight synthetic index values
- **Posting** them to Hyperliquid using `setOracle`
- **Executing** HIP‑3 deploy actions (via Python SDK / scripts)
- **Logging** behaviour for iteration and debugging

This is deliberately small and transparent, aimed at early HIP‑3 experiments.

### Setup

```bash
cd apps/oracle-service
npm install
cp .env.testnet.example .env.testnet
npm run dev
```

The `.env.testnet` is designed to pair cleanly with the Python deploy scripts.

---

## HIP-3 Deploy Scripts

- **Location**: `apps/oracle-service/scripts/`

### `deploy-dex.py`

First-time DEX + asset deploy for HIP‑3.

- **Intended behaviour**:
  - Use the official Hyperliquid Python SDK’s deployment helper
  - Ensure canonical L1 action signing and payload structure
  - Avoid vault/account overrides and custom signing logic

- **Builder wallet requirements**:
  - 100 HyperCore HYPE staked (plus any additional HYPE required for gas auctions)
  - Abstractions disabled
  - Clean EOA pointing at testnet (`https://api.hyperliquid-testnet.xyz`)

- **Testnet observations so far**:
  - **DEX name** must be a 2–4 character lowercase string
  - **First asset** is expected to use `registerAsset2` semantics (new DEX + first asset)
  - Some DEX names may already be in use by other builders

### `set-oracle.py`

Posts updated oracle prices for the deployer’s HIP‑3 assets:

- Pulls from Pyth
- Computes the index
- Calls Hyperliquid `setOracle` with sorted feeds
- Only runs once a DEX/asset exists

---

## Current Status

We are in the process of:

- Standing up the first testnet DEX
- Pushing Pyth → Hyperliquid oracle updates
- Verifying HIP‑3 deployment flow (DEX, asset, margin tables, oracle)
- Experimenting with realistic volatility surfaces

Once one test DEX is live, expanding to multiple indices, richer oracle composition, and deeper UI integration should be straightforward.



