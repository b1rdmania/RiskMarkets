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
  hlMasterAddress: string;  // Master/builder account (where funds are deposited and signing happens)
  hlApiPrivateKey: string;  // Private key for signing L1 actions
  hlDexName?: string;  // DEX name for HIP-3 markets (2-4 chars, e.g., "XAU")
  hlCoinSymbol?: string;  // Coin symbol (e.g., "XAU-TEST")
  hlAssetId?: number;  // Numeric asset ID from meta.universe (for trading)
  hlPublishEnabled: boolean;
  hlOracleEndpoint?: string;
  publishIntervalMs: number;
  staleThresholdMs: number;
  minPublishIntervalMs: number;
  priceChangeEpsilon: number;
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
  hlMasterAddress: required('HL_MASTER_ADDRESS'),
  hlApiPrivateKey: required('HL_API_PRIVATE_KEY'),
  hlDexName: process.env.HL_DEX_NAME,  // DEX name (2-4 chars, e.g., "XAU")
  hlCoinSymbol: process.env.HL_COIN_SYMBOL,  // Coin symbol (e.g., "XAU-TEST")
  hlAssetId: process.env.HL_ASSET_ID ? Number(process.env.HL_ASSET_ID) : undefined,  // Asset ID for trading
  hlPublishEnabled: (process.env.HL_PUBLISH_ENABLED ?? 'false').toLowerCase() === 'true',
  hlOracleEndpoint: process.env.HL_ORACLE_ENDPOINT ?? '/exchange',  // Hyperliquid exchange endpoint
  publishIntervalMs: Number(process.env.PUBLISH_INTERVAL_MS ?? 3000),
  staleThresholdMs: Number(process.env.STALE_THRESHOLD_MS ?? 10000),
  minPublishIntervalMs: Number(process.env.MIN_PUBLISH_INTERVAL_MS ?? 10000),
  priceChangeEpsilon: Number(process.env.PRICE_EPSILON ?? 0.01),
};
