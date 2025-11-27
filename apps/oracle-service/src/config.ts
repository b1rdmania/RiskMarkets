import * as path from 'path';
import * as dotenv from 'dotenv';

const NETWORK = process.env.NETWORK;

if (!NETWORK) {
  throw new Error('NETWORK env var is required (e.g. testnet).');
}

if (NETWORK !== 'testnet') {
  throw new Error(`oracle-service can only run in testnet mode. NETWORK=${NETWORK}`);
}

const envFile = process.env.ENV_FILE ?? '.env.testnet';
dotenv.config({ path: path.resolve(process.cwd(), envFile) });

export interface ServiceConfig {
  network: string;
  port: number;
  pythFeedId: string;
  pythApiUrl: string;
  pythCluster?: string;
  hlUrl: string;
  hlApiKey: string;
  hlApiSecret: string;
  publishIntervalMs: number;
  staleThresholdMs: number;
}

function required(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (!value) {
    throw new Error(`Missing env var: ${name}`);
  }
  return value;
}

export const config: ServiceConfig = {
  network: NETWORK,
  port: Number(process.env.PORT ?? 4000),
  pythFeedId: required('PYTH_FEED_ID'),
  pythApiUrl: required('PYTH_API_URL', 'https://hermes-beta.pyth.network/api'),
  pythCluster: process.env.PYTH_CLUSTER,
  hlUrl: required('HL_TESTNET_URL'),
  hlApiKey: required('HL_API_KEY'),
  hlApiSecret: required('HL_API_SECRET'),
  publishIntervalMs: Number(process.env.PUBLISH_INTERVAL_MS ?? 3000),
  staleThresholdMs: Number(process.env.STALE_THRESHOLD_MS ?? 10000),
};
