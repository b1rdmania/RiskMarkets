# WAR.MARKET — Static Mockup Pages

Static HTML/CSS mockups for the WAR.MARKET project with a **"Hacker-Ops Terminal for a World on Fire"** aesthetic.

## Overview

Three complete mockup pages showcasing the WAR.MARKET brand identity:
- **Landing Page** — Hero section with video placeholder, explainer strip, and branding
- **Trading Terminal** — Markets table, tension ticker, trading drawer with oracle breakdown
- **riskHYPE Vault** — Staking interface with metrics, deposit/withdraw, and activity feed

## Design Aesthetic

- **Dark terminal theme** (#0A0A0A, #121212, #171717)
- **Neon green** (#02FF81) for signals and primary actions
- **Amber/Gold** (#F4C95D) for warnings and highlights
- **Desaturated red** (#FF5A5A) for alerts
- **Hacker-ops terminal vibes** with subtle glitch effects, pulsing map overlays, scanning animations
- **No literal conflict imagery** — optics-safe for Hyperliquid

## Pages

### `index.html` — Landing Page
- Full viewport hero with world map background
- WAR.MARKET logo with neon glow
- "Launch App" CTA button
- Mini-explainer strip (Volatility Indices, War-Room UI, $RISK Token)
- Video section with placeholder (ready for your 10-second video)
- Footer with links

### `terminal.html` — Trading Terminal
- Top navigation bar with Markets/Stake/About/$RISK links
- Scrolling tension ticker with neutral data signals
- Markets table with three active indices (GDR, ESV, SHR)
- Clickable rows that open a trading drawer
- Side drawer with chart placeholder, order panel, oracle breakdown, stress bar
- Bottom global risk meter
- Visual CLI prompts in corner

### `vault.html` — riskHYPE Vault
- Vault metrics grid (Total Staked, Minimum Required, Buffer, APY, etc.)
- Deposit module with stake button
- Withdraw module (collapsible)
- Balance display
- Activity feed with hacker ops log style

## Assets

The `assets/` folder contains:
- `map-overlay.svg` — World map silhouette with trade corridors and data nodes
- `README.md` — Instructions for adding your video

## Adding Your Video

1. Add your 10-second video file to `assets/` folder
2. In `index.html`, replace the `.video-placeholder` div with:
   ```html
   <video autoplay loop muted class="hero-video">
     <source src="assets/your-video.mp4" type="video/mp4">
   </video>
   ```

## Features

- **Pure HTML/CSS** — No JavaScript dependencies (minimal JS for drawer interactions)
- **Responsive** — Desktop-optimized with mobile fallbacks
- **Animated** — Pulsing map, scrolling ticker, glitch effects, scan lines
- **Terminal aesthetic** — Monospace fonts, HUD-style panels, CLI prompts
- **Ready for review** — Complete visual mockups ready to show stakeholders

## Color Palette

```css
--dark-bg: #0A0A0A
--dark-panel: #121212
--dark-surface: #171717
--neon-green: #02FF81
--amber: #F4C95D
--alert-red: #FF5A5A
```

## Typography

- **Titles**: Eurostile, Agency FB, Conthrax (square/tech fonts)
- **Body**: IBM Plex Mono, Space Mono (monospace)
- **Numbers**: Monospace everywhere

## Animations

- Map pulse glow (3s cycle)
- Scanning line (8s cycle)
- Ticker scroll (continuous)
- Sparkline pulse
- Stress bar animations
- Glitch effects on hover
- Button hover transitions

## Deployment

Ready to deploy to Vercel! See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

### Quick Deploy

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project
3. Select `b1rdmania/RiskMarkets`
4. Deploy!

## Oracle Service (Testnet Backend)

The testnet oracle lives inside this repo at `apps/oracle-service`. It follows the whitepaper in `docs/whitepaper-v0.2.md` and currently exposes stubbed `/health` and `/price` endpoints while we wire the real data sources.

### Day 1 Setup

```bash
cd apps/oracle-service
npm install
cp .env.testnet.example .env.testnet   # fill in feed + HL creds when ready
npm run dev                            # starts ts-node-dev with hot reload
```

Environment guardrails ensure it only runs when `NETWORK=testnet`. When the service is running you can hit:

- `http://localhost:4000/health`
- `http://localhost:4000/price`

Use the whitepaper to track the day-by-day plan for wiring Pyth and Hyperliquid.

### Day 2–3 Notes
- Real Pyth data fetch is already wired (Hermes API). Update `PYTH_FEED_ID`, `PYTH_API_URL`, `PYTH_CLUSTER` in your `.env.testnet`.
- Hyperliquid publishing is disabled by default. Set `HL_PUBLISH_ENABLED=true` plus `HL_MARKET_ID`, `HL_API_KEY`, `HL_API_SECRET`, and a valid `HL_TESTNET_URL` when you’re ready to send prices to HL testnet.
- Tuning knobs:
  - `PUBLISH_INTERVAL_MS` – fetch/publish cadence (default 3s)
  - `MIN_PUBLISH_INTERVAL_MS` – force publish at least every 10s even if price hasn’t moved
  - `PRICE_EPSILON` – minimum price delta before we publish again
  - `STALE_THRESHOLD_MS` – mark data stale if Pyth hasn’t updated within this window

## Next Steps

- Deploy to Vercel (see DEPLOYMENT.md)
- Add real sparkline data/graphs
- Connect wallet integration (static for now)
- Refine animations and transitions
- Add more visual assets/icons as needed

---

**Build**: v0.1-alpha  
**Status**: Ready for deployment and stakeholder presentation

