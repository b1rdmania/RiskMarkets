# WAR.MARKET — Technical Whitepaper v0.2 (Testnet-First Edition)

## Goal
Stand up a simple Pyth → Index → Hyperliquid testnet pipeline.

One index. One feed. One tradable synthetic perp on HL testnet.

No baskets. No smoothing. No over-architecture. Just plumbing first.

---

## 0. Overview
WAR.MARKET runs on a simple loop:

**Pyth Testnet Feed → Index Value → HL Testnet Oracle → HL Testnet Market**

This document covers the minimal backend needed to:

1. Read a price feed on testnet
2. Compute a deterministic index value
3. Publish that value to Hyperliquid testnet
4. Expose HTTP endpoints for debugging
5. Avoid touching mainnet until ready

We begin with **one index only**, using **one asset only**:

- **GOLD/USD (Pyth)** — safe, stable, neutral
- **WTI (Pyth)** — if available
- **LMT** — defence stock (Pyth)

Pick one. Build one. Make it tradeable. Expand later.

---

## 1. Architecture (Minimal Implementation)

### Repo Structure
```
/apps
  /oracle-service   # backend for testnet index + price publishing
  /frontend         # optional, current static site
/packages
  /hl-client        # thin wrapper (later)
  /pyth-client      # thin wrapper (later)
  /types            # shared interfaces (later)
```

### Service Basics
- Node + TypeScript
- Entry file: `index.ts`
- Runs only when `NETWORK=testnet`

### Environment
`.env.testnet` includes:
```
NETWORK=testnet
PYTH_FEED_ID=xxxxxxxx
HL_TESTNET_URL=https://...
HL_API_KEY=xxxxxxxx
```
Service refuses to start if `NETWORK !== testnet`.

---

## 2. Data Source (Pyth Testnet)

### Feeds
Choose **one** of:
- GOLD/USD
- WTI/Oil
- LMT / RTX / NOC

No composites. No weighting. No normalization.

### Fetch Model
Every **3 seconds**:
- Pull latest price from Pyth testnet
- Store last value + timestamp
- Mark stale if older than 10 seconds

### v0 Client
```ts
async function fetchPythPrice(feedId: string) {
  const price = await pythConnection.getPrice(feedId)
  return { price, timestamp: Date.now() }
}
```
No subscription. No exotic retries. Keep it simple.

---

## 3. Index Computation (v0)

### Formula
Identity function:
```
index = pyth_price
```

No z-scores, moving averages, windows, smoothing, or weighting. Add later once real behaviour is observed.

### Sanity Check
If price jump > 20% in one tick → skip publish and log warning.

### Logging
```
[PRICE] 1782.43 @ 2025-01-01T12:00:01Z (fresh)
```

---

## 4. Publishing to Hyperliquid Testnet

### Goal
Make the testnet market tradable:
1. Create a HIP-3 market on testnet
2. Provide HL a consistent index price every few seconds
3. Allow LONG/SHORT positions on HL testnet

### Publishing Logic (v0)
Every **3 seconds** (after computing index):
- POST to HL testnet oracle/test API
- Include index price, timestamp, signature (HL keypair from env)

### Update Conditions
Publish when:
- `newValue !== previousValue`, or
- ≥10 seconds since last publish

### Error Handling
- Retry once
- If second failure → log warning, continue loop

---

## 5. Service Endpoints
Expose **two** endpoints only:

### `GET /health`
```json
{
  "status": "ok",
  "lastPrice": 1782.43,
  "lastUpdate": "2025-01-01T12:00:04Z",
  "stale": false,
  "publishes": 8421
}
```

### `GET /price`
```json
{
  "index": "gold-index",
  "value": 1782.43,
  "source": {
    "pyth": 1782.43,
    "timestamp": 1700000000000
  }
}
```
No history, no auth (testnet only).

---

## 6. HL Testnet Market Setup

### Steps
1. Deploy HIP-3 testnet market (e.g., `GOLD-TEST`)
2. Point market to oracle-service endpoint
3. Fund testnet account
4. Place LONG/SHORT orders via HL interface/API
5. Validate mark price, funding, OI, latency

### Success Criteria
- Index updates visible on HL testnet
- Able to open/close positions
- Funding + PnL behave as expected
- Oracle errors remain zero

---

## 7. Deployment (Simple)

### v0 Deployment
- Run locally in tmux or on a small VPS
- Manual restarts acceptable
- No Docker/CI required yet
- Logs to stdout

### Monitoring
- Hit `/health` periodically
- Target continuous runtime of 48–72 hours to observe drift & stability

---

## 8. Phase 2 (after v0 success)
Once the basic loop works:
- Add 2 more indices (gold, oil, defence) with identity formulas
- Introduce normalization / smoothing once behaviour is known
- Build composites (GDR / ESV / SHR)
- Add fallback logic & containerization
- Wire backend to WAR.MARKET UI (optional toggle)
- Prepare production formula spec for HL review
- Graduate to HIP-3 mainnet

---

## 9. Risk Notes
- Pyth testnet feeds can stall → mark stale and skip publish
- HL testnet endpoints may change → keep client thin, typed
- Never run with mainnet keys in testnet stack
- Strict `NETWORK=testnet` guard prevents accidental promotion
- When moving to mainnet, formalize formula spec + audits

---

## 10. Summary
This v0 plan delivers:
- A working oracle service
- A verifiable index
- A tradable HIP-3 testnet market
- Zero over-architecture
- A safe path to expansion
- A preview of WAR.MARKET without narrative risk

Next steps:
1. Scaffold `/apps/oracle-service`
2. Implement Pyth fetch loop
3. Wire HL publish
4. Run continuously and observe

