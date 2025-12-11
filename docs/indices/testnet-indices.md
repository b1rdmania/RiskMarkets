# Testnet Index Specifications (Internal)

Target: internal testnet launch in ~1 week. Scope is correctness and reliability over breadth. Each index maps to a single Pyth testnet feed (identity transform) to keep the pipeline deterministic and simple.

## Global parameters
- Environment: `testnet` only.
- Publish cadence: every 3s (`PUBLISH_INTERVAL_MS`), min publish interval 10s (`MIN_PUBLISH_INTERVAL_MS`).
- Stale threshold: 10s (`STALE_THRESHOLD_MS`); stale → skip publish.
- Price sanity: skip publish if tick-to-tick change >20% (apply in publisher).
- Scaling: raw Pyth price divided by `INDEX_SCALE` (default 40) to land around 100–150 notional.
- Logging: log inputs + computed index per tick; persist last error for health visibility.

## Index definitions (v0 identity on Pyth testnet)

### GDR — Defence Rotation (proxy: LMT/USD)
- Purpose: defense-sector proxy for internal testing.
- Data source: Pyth testnet feed for `LMT/USD` (set `PYTH_FEED_ID`).
- Formula: identity — `index = pyth_price / INDEX_SCALE`.
- Composition: single-constituent proxy for now (LMT). Future basket target: 30% LMT / 25% RTX / 25% NOC / 20% PLTR.
- Rebalance: none (static).
- Corporate actions: ignore in v0; rely on Pyth adjusted price.
- Market params: HL coin symbol e.g., `wa:GDR1`, DEX name `war`.

### ESV — Energy Shock Volatility (proxy: WTI/USD)
- Purpose: crude-led energy stress proxy.
- Data source: Pyth testnet feed for `WTI/USD` (set `PYTH_FEED_ID` when running this index).
- Formula: identity — `index = pyth_price / INDEX_SCALE`.
- Composition: single-constituent proxy for now (WTI). Future basket target: 40% WTI / 25% NatGas / 20% Freight proxy / 15% Gold.
- Rebalance: none (static).
- Corporate actions: ignore; use Pyth adjusted feed.
- Market params: HL coin symbol e.g., `wa:ESV1`, DEX name `war`.

### SHR — Safe Haven Rotation (proxy: XAU/USD)
- Purpose: risk-off proxy anchored to gold.
- Data source: Pyth testnet feed for `XAU/USD` (set `PYTH_FEED_ID`).
- Formula: identity — `index = pyth_price / INDEX_SCALE`.
- Composition: single-constituent proxy for now (Gold). Future basket target: 40% Gold / 30% CHF (USD/CHF inverse) / 30% JPY (USD/JPY inverse).
- Rebalance: none (static).
- Corporate actions: ignore; rely on Pyth adjusted feed.
- Market params: HL coin symbol e.g., `wa:SHR1`, DEX name `war`.

## Operational notes
- One index per service instance: run separate env files per index (each with its own `PYTH_FEED_ID`, `HL_COIN_SYMBOL`, and `INDEX_SCALE` if needed).
- Validate feed ID on boot via `/feeds/:feedId/validate`; store confirmed IDs in env files and note them in runbooks.
- For testnet sharing, publish is allowed only when `HL_PUBLISH_ENABLED=true` and data is fresh.
- Document actual feed IDs and HL asset IDs in the runbook once confirmed.


