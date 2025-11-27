import { request } from 'undici';
import { config } from '../config';

export interface PythPriceResult {
  value: number;
  timestamp: number;
}

type PythApiResponse = {
  price?: {
    price: string;
    expo: number;
    publish_time?: number;
  };
  ema_price?: {
    price: string;
    expo: number;
    publish_time?: number;
  };
}[];

const DEFAULT_EXPO = 0;

function decodePrice(price: string, expo: number): number {
  const base = Number(price);
  if (Number.isNaN(base)) {
    throw new Error('Invalid price value from Pyth');
  }
  return base * Math.pow(10, expo);
}

export async function fetchPythPrice(feedId: string): Promise<PythPriceResult> {
  const url = new URL(`${config.pythApiUrl}/latest_price_feeds`);
  url.searchParams.append('ids[]', feedId);
  if (config.pythCluster) {
    url.searchParams.append('cluster', config.pythCluster);
  }

  const response = await request(url, { method: 'GET' });
  if (response.statusCode !== 200) {
    const body = await response.body.text();
    throw new Error(`Pyth API error (${response.statusCode}): ${body}`);
  }

  const json = (await response.body.json()) as PythApiResponse;
  if (!Array.isArray(json) || json.length === 0) {
    throw new Error('Pyth API returned empty result');
  }

  const feed = json[0];
  const priceData = feed.price ?? feed.ema_price;
  if (!priceData) {
    throw new Error('Pyth API missing price field');
  }

  const value = decodePrice(priceData.price, priceData.expo ?? DEFAULT_EXPO);
  const publishTimeSec = priceData.publish_time ?? Math.floor(Date.now() / 1000);
  return { value, timestamp: publishTimeSec * 1000 };
}
