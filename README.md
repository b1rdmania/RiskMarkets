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
- Top navigation bar with Markets/riskHYPE/Points/$RISK links
- Scrolling tension ticker with data signals
- Markets table with 5 indices (ECV, APMS, GRMI, EASCS, EUVI)
- Clickable rows that open trading drawer
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

## Next Steps

- Deploy to Vercel (see DEPLOYMENT.md)
- Add real sparkline data/graphs
- Connect wallet integration (static for now)
- Refine animations and transitions
- Add more visual assets/icons as needed

---

**Build**: v0.1-alpha  
**Status**: Ready for deployment and stakeholder presentation

