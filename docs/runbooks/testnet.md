# Testnet Runbook (Internal)

Goal: keep testnet indices flowing for internal testers with fast recovery paths.

## Quickstart
1) Copy env: `cp .env.testnet.example .env.testnet` (one per index instance).
2) Set `PYTH_FEED_ID`, `HL_COIN_SYMBOL`, `HL_DEX_NAME`, `HL_MASTER_*`, `HL_PUBLISH_ENABLED=true`.
3) Sanity: `npm run regression` (fixtures), then `npm run build`.
4) Run service: `npm run dev` (logs show feed validation + publish status).

## Monitoring (manual for now)
- HTTP: `GET /health` (stale flag, last error, publish count).
- Pricing: `GET /price` (index value + timestamp).
- Logs: watch for `[price] stale`, `sanity check failed`, `HL publish error`.
- Pyth freshness: stale if `now - publish_time > STALE_THRESHOLD_MS` (default 10s).
- Publish cadence: every ~3s; skip if no material change or stale.

## Alerts to wire (next step)
- Stale data > 30s.
- Sanity jump rejection triggered.
- Publish failures or consecutive retries exhausted.
- Empty orderbook (no bids/asks) for >5 minutes.

## Operational playbooks

### Halt / unhalt trading
- Halt: `NETWORK=testnet python3 scripts/halt-trading.py --coin wa:GDR1 --halted true`
- Unhalt: `NETWORK=testnet python3 scripts/halt-trading.py --coin wa:GDR1 --halted false`

### Recycle a market
- Push static oracle twice: `NETWORK=testnet python3 scripts/recycle_market.py --coin wa:GDR1 --price 100.1`
- Place tiny 0.01 bid/ask at that price in UI, then restart oracle-service.

### Reseed liquidity (presets)
- Dry run: `python3 scripts/seed-from-preset.py --market gdr --dry-run`
- Place: `NETWORK=testnet python3 scripts/seed-from-preset.py --market gdr`
- Presets: edit `scripts/seed-presets.json` (mid, spread_bps, levels, size).

### Adding another index instance
- Create new env file per index (e.g., `.env.gdr.testnet`, `.env.esv.testnet`).
- Set `PYTH_FEED_ID`, `HL_COIN_SYMBOL`, `INDEX_SCALE` as needed.
- Run separate process per index; each publishes to its own HIP-3 market.

### Debugging data issues
- Validate feed ID: `GET /feeds/:feedId/validate` or `GET /feeds/:feedId`.
- If repeated `stale` or `Jump too large`:
  - Halt market (see above).
  - Switch to static oracle via `recycle_market.py`.
  - Investigate feed freshness with `/feeds/:feedId`.
  - Resume live after feed stabilizes.

## Reference configs
- Index specs: `docs/indices/testnet-indices.md`.
- Preset seeds: `apps/oracle-service/scripts/seed-presets.json`.


