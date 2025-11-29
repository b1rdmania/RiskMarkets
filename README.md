## WAR.MARKET

Static WAR.MARKET front-end mockups plus a small testnet oracle service used for HIP‑3 experiments.

### Demo

- **Product reel**: [`assets/Video_Generation_With_GIF_Added(1).mp4`](assets/Video_Generation_With_GIF_Added(1).mp4)

### Overview

Three HTML/CSS pages showcasing the WAR.MARKET interface:
- **Landing Page** — Hero section with video area, explainer strip, and branding
- **Trading Terminal** — Markets table, tension ticker, trading drawer with oracle breakdown
- **riskHYPE Vault** — Staking interface with metrics, deposit/withdraw, and activity feed

### Design notes

- **Dark terminal theme** (0A0A0A / 121212 / 171717)
- **Neon green** for signals and primary actions
- **Amber/Gold** for highlights
- Subtle map/ticker animations; no literal conflict imagery

### Pages

- **`index.html`** — Landing page with hero, explainer strip, and video slot
- **`terminal.html`** — Markets table and trading drawer mock
- **`vault.html`** — riskHYPE vault mock

### Assets

- **Map overlay**: `assets/map-overlay.svg`
- **Video files**: in `assets/`, including the demo reel linked above

### Oracle service

- **Location**: `apps/oracle-service`
- **Purpose**: small Node/TypeScript service for testnet Pyth → index → Hyperliquid experiments
- **Setup**:

  ```bash
  cd apps/oracle-service
  npm install
  cp .env.testnet.example .env.testnet
  npm run dev
  ```

For deployment notes and the technical plan, see `docs/DEPLOYMENT.md` and `docs/whitepaper-v0.2.md`.


