import express from 'express';
import { config } from './config';
import { fetchPythPrice } from './services/pyth';
import { publishToHyperliquid } from './services/hyperliquid';
import { priceState, publishStats } from './state';

const app = express();
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    network: config.network,
    lastPrice: priceState.value || null,
    lastUpdate: priceState.timestamp ? new Date(priceState.timestamp).toISOString() : null,
    stale: priceState.stale,
    publishes: publishStats.totalPublishes,
  });
});

app.get('/price', (_req, res) => {
  res.json({
    index: 'testnet-index',
    value: priceState.value || null,
    source: {
      pyth: priceState.value || null,
      timestamp: priceState.timestamp || null,
    },
  });
});

async function main() {
  console.log(`[boot] WAR.MARKET oracle-service running on network=${config.network}`);
  console.log(`[boot] Using feed=${config.pythFeedId}`);

  setInterval(async () => {
    try {
      const { value } = await fetchPythPrice(config.pythFeedId);
      await publishToHyperliquid(value);
    } catch (err) {
      console.error('[loop] error', err);
    }
  }, config.publishIntervalMs);

  app.listen(config.port, () => {
    console.log(`[server] listening on port ${config.port}`);
  });
}

main().catch((err) => {
  console.error('Fatal error during startup', err);
  process.exit(1);
});
