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

  const payload = {
    market: config.hlMarketId,
    price: value,
    timestamp: new Date(now).toISOString(),
  };

  const body = JSON.stringify(payload);
  const signature = crypto.createHmac('sha256', config.hlApiSecret).update(body).digest('hex');

  const response = await request(config.hlUrl, {
    method: 'POST',
    body,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `HL ${config.hlApiKey}:${signature}`,
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
