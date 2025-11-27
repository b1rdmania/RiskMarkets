import crypto from 'crypto';
import { request } from 'undici';
import { config } from '../config';
import { publishStats } from '../state';

export interface PublishResult {
  ok: boolean;
  skipped?: boolean;
  reason?: string;
}

let lastPublishedValue: number | null = null;
let lastPublishTimestamp = 0;

function shouldPublish(nextValue: number, now: number): { publish: boolean; reason?: string } {
  if (lastPublishedValue === null) {
    return { publish: true };
  }

  const diff = Math.abs(nextValue - lastPublishedValue);
  if (diff >= config.priceChangeEpsilon) {
    return { publish: true };
  }

  if (now - lastPublishTimestamp >= config.minPublishIntervalMs) {
    return { publish: true };
  }

  return { publish: false, reason: 'No material change' };
}

export async function publishToHyperliquid(value: number): Promise<PublishResult> {
  const now = Date.now();

  if (!config.hlPublishEnabled) {
    return { ok: true, skipped: true, reason: 'HL publish disabled' };
  }

  const { publish, reason } = shouldPublish(value, now);
  if (!publish) {
    return { ok: true, skipped: true, reason };
  }

  if (!config.hlMarketId) {
    return { ok: false, reason: 'Missing HL_MARKET_ID' };
  }

  // Hyperliquid setOracle action for HIP-3 markets
  // Based on: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
  // 
  // Note: Authentication method needs verification - Hyperliquid may use:
  // 1. Wallet signature (like Python SDK)
  // 2. API key + HMAC (current implementation)
  // 3. API key only
  //
  // The exact endpoint and auth method should be verified with Hyperliquid testnet API

  if (!config.hlMarketId) {
    return { ok: false, reason: 'Missing HL_MARKET_ID' };
  }

  // Format price as string (Hyperliquid expects string prices)
  const priceStr = value.toFixed(8);  // Use sufficient precision

  // setOracle action structure for HIP-3
  const action = {
    type: 'setOracle',
    dex: config.hlDexName || 'WARMARKET',
    oraclePxs: [[config.hlMarketId, priceStr]],  // Array of [asset, price] pairs, sorted by asset
    markPxs: [],  // Optional: can provide mark prices for better price discovery
  };

  const payload = {
    action,
  };

  const body = JSON.stringify(payload);
  
  // Try HMAC signature (may need to switch to wallet signature based on actual API)
  const signature = crypto.createHmac('sha256', config.hlApiSecret).update(body).digest('hex');

  const endpoint = `${config.hlUrl}${config.hlOracleEndpoint}`;
  console.log(`[HL] Publishing setOracle to ${endpoint}: asset=${config.hlMarketId}, price=${priceStr}, dex=${config.hlDexName}`);

  const response = await request(endpoint, {
    method: 'POST',
    body,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.hlApiKey}:${signature}`,
      'X-API-Key': config.hlApiKey,
    },
  });

  if (response.statusCode >= 400) {
    const text = await response.body.text();
    throw new Error(`HL publish failed (${response.statusCode}): ${text}`);
  }

  lastPublishedValue = value;
  lastPublishTimestamp = now;
  publishStats.lastPublish = now;
  publishStats.totalPublishes += 1;

  return { ok: true };
}
