# WAR.MARKET Oracle Service

Backend service for fetching Pyth prices and publishing to Hyperliquid testnet.

## Setup

1. Copy the example env file:
   ```bash
   cp .env.testnet.example .env.testnet
   ```

2. Fill in your credentials in `.env.testnet`:

### Pyth Feed ID
- Get a Pyth feed ID from [Pyth Network](https://pyth.network/developers/price-feed-ids)
- Common feeds:
  - BTC/USD: `0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace`
  - GOLD/USD: (check Pyth docs)
  - WTI: (check Pyth docs)

### Hyperliquid Testnet API Keys

1. Go to [Hyperliquid Testnet API page](https://app.hyperliquid-testnet.xyz/API)
2. Create an **API Wallet / API key** for your testnet account
3. Save:
   - `HL_API_KEY` - Your testnet API key
   - `HL_API_SECRET` - Your testnet API secret
   - `HL_MARKET_ID` - The market symbol you're publishing to (e.g., `GOLD-TEST`)

4. Update `.env.testnet`:
   ```env
   HL_API_KEY=<YOUR_TESTNET_API_KEY>
   HL_API_SECRET=<YOUR_TESTNET_API_SECRET>
   HL_MARKET_ID=<YOUR_MARKET_SYMBOL>
   HL_PUBLISH_ENABLED=true
   ```

## Running

```bash
npm install
npm run dev
```

Service will start on `http://localhost:4000`

## Endpoints

- `GET /health` - Service health and current state
- `GET /price` - Current index price
- `GET /feeds` - List/search available Pyth feeds
- `GET /feeds/:feedId` - Get metadata for a feed
- `GET /feeds/:feedId/validate` - Validate a feed ID

## Environment Variables

See `.env.testnet.example` for all available options.

## Testing

With the service running, test endpoints:
```bash
curl http://localhost:4000/health
curl http://localhost:4000/price
```
