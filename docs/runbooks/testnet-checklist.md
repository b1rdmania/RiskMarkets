# Testnet Launch Checklist (Internal)

Use this before sharing the indices testnet link with the team. Target: stable 48–72h runtime.

## T-2 days: plumbing verification
- [ ] Confirm env per index (`PYTH_FEED_ID`, `HL_*`, `INDEX_SCALE`, `HL_PUBLISH_ENABLED=true`).
- [ ] `npm run regression` passes in `apps/oracle-service`.
- [ ] `npm run build` passes.
- [ ] Dry-run seeding presets: `python3 scripts/seed-from-preset.py --market gdr --dry-run`.

## T-1 day: end-to-end dry run
- [ ] Start oracle-service (one instance per index) with testnet env.
- [ ] Check `/health` and `/price` respond (no stale flag).
- [ ] Watch logs for jump rejections / retries; none sustained.
- [ ] If market stuck, run `recycle_market.py` with a static price, then seed orders.
- [ ] Seed orderbook: `NETWORK=testnet python3 scripts/seed-from-preset.py --market gdr` (and others as needed).
- [ ] Verify orders visible in HL testnet UI and marks follow oracle value.

## T-0: share with internal users
- [ ] Open `terminal.html?api=<oracle_url>&index=GDR` and confirm env banner shows `TESTNET`.
- [ ] Confirm price cell updates every few seconds from `/price`.
- [ ] Confirm drawer text shows correct index name and composition.
- [ ] Send internal note with:
  - API base: `<oracle_url>`
  - Supported indices: GDR / ESV / SHR (proxies)
  - Usage link: `terminal.html?api=<oracle_url>&index=GDR`
  - Runbook link: `docs/runbooks/testnet.md`
  - Expectations: internal only, funds are testnet, expect occasional halts/reseeds.

## Monitoring during test
- [ ] Check `/health` every ~10 minutes for stale flag.
- [ ] If stale or jump rejections repeat:
  - Halt market: `halt-trading.py --coin wa:GDR1 --halted true`
  - Push static price twice: `recycle_market.py --coin wa:GDR1 --price <value>`
  - Reseed orders via presets.
- [ ] Log issues and follow up with feed validation (`/feeds/:feedId/validate`).

