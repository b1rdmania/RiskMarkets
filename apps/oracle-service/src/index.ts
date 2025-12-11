import express from 'express';
import { config } from './config';
import { fetchPythPrice } from './services/pyth';
import { publishToHyperliquid } from './services/hyperliquid';
import { fetchFeedMetadata, listAvailableFeeds, validateFeedId } from './services/pyth-metadata';
import { priceState, publishStats } from './state';
import { sanityCheckJump, scaleToIndex } from './pipeline';

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
    error: priceState.lastError ?? null,
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

app.get('/feeds', async (_req, res) => {
  const query = _req.query.search as string | undefined;
  const feeds = await listAvailableFeeds(query);
  res.json({ feeds });
});

app.get('/feeds/:feedId', async (_req, res) => {
  const feedId = _req.params.feedId;
  const metadata = await fetchFeedMetadata(feedId);
  if (metadata) {
    res.json(metadata);
  } else {
    res.status(404).json({ error: 'Feed not found' });
  }
});

app.get('/feeds/:feedId/validate', async (_req, res) => {
  const feedId = _req.params.feedId;
  const isValid = await validateFeedId(feedId);
  res.json({ feedId, valid: isValid });
});

let lastComputedIndex: number | null = null;

async function main() {
  console.log(`[boot] WAR.MARKET oracle-service running on network=${config.network}`);
  console.log(`[boot] Using feed=${config.pythFeedId}`);
  console.log(`[boot] Index scale=${config.indexScale}`);
  console.log(`[boot] Hyperliquid publish ${config.hlPublishEnabled ? 'ENABLED' : 'DISABLED'}`);
  
  // Validate feed ID on startup
  console.log(`[boot] Validating feed ID...`);
  const isValid = await validateFeedId(config.pythFeedId);
  if (!isValid) {
    console.warn(`[boot] WARNING: Feed ID ${config.pythFeedId} validation failed. Service will continue but may fail to fetch prices.`);
  } else {
    const metadata = await fetchFeedMetadata(config.pythFeedId);
    if (metadata) {
      console.log(`[boot] Feed metadata: ${metadata.symbol || 'unknown'} (${metadata.description || 'no description'})`);
    }
    console.log(`[boot] Feed ID validated successfully`);
  }

  setInterval(async () => {
    try {
      const { value, timestamp } = await fetchPythPrice(config.pythFeedId);

      // Scale raw Pyth price into an index level suitable for the DEX.
      // For example, XAUT ~ 4200 / 40 ~= 105.
      const indexValue = scaleToIndex(value, config.indexScale);

      const stale = Date.now() - timestamp > config.staleThresholdMs;
      priceState.stale = stale;

      if (stale) {
        console.warn('[price] stale data detected, skipping publish');
        return;
      }

      const jumpCheck = sanityCheckJump(lastComputedIndex, indexValue, config.maxJumpFraction);
      if (!jumpCheck.ok) {
        priceState.lastError = jumpCheck.reason;
        console.warn(`[price] sanity check failed: ${jumpCheck.reason}`);
        return;
      }

      priceState.value = indexValue;
      priceState.timestamp = timestamp;
      priceState.lastError = undefined;
      lastComputedIndex = indexValue;

      const result = await publishToHyperliquid(indexValue);
      if (result.skipped && result.reason) {
        console.log(`[HL] skipped publish: ${result.reason}`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      priceState.stale = true;
      priceState.lastError = message;
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
