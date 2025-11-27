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

  if (!config.hlCoinSymbol) {
    return { ok: false, reason: 'Missing HL_COIN_SYMBOL' };
  }

  if (!config.hlDexName) {
    return { ok: false, reason: 'Missing HL_DEX_NAME' };
  }

  // Hyperliquid setOracle action for HIP-3 markets
  // Correct structure: perpDeploy with setOracle
  // Based on: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
  //
  // Structure:
  // {
  //   action: {
  //     type: "perpDeploy",
  //     setOracle: {
  //       dex: "XAU",  // DEX name (2-4 chars)
  //       oraclePxs: [["XAU-TEST", "1924.55"]],  // Array of [coin, price] pairs, sorted by coin
  //       markPxs: [],  // Optional: mark prices
  //       externalPerpPxs: [["XAU-TEST", "1924.55"]]  // Optional: external perp prices
  //     }
  //   },
  //   nonce: <timestamp>,
  //   signature: { r, s, v }
  // }

  if (!config.hlCoinSymbol) {
    return { ok: false, reason: 'Missing HL_COIN_SYMBOL' };
  }

  if (!config.hlDexName) {
    return { ok: false, reason: 'Missing HL_DEX_NAME' };
  }

  // Format price as string (Hyperliquid expects string prices)
  const priceStr = value.toFixed(8);  // Use sufficient precision

  // setOracle action structure for HIP-3
  // Based on Python SDK: perp_deploy_set_oracle
  // Structure matches: { type: "perpDeploy", setOracle: { dex, oraclePxs, markPxs, externalPerpPxs } }
  // 
  // Note: oraclePxs, markPxs, externalPerpPxs are sorted arrays of [coin, price] pairs
  // Python SDK converts Dict[str, str] to sorted list for wire format

  // Build oracle price dict (coin -> price)
  const oraclePxsDict: Record<string, string> = {
    [config.hlCoinSymbol]: priceStr,
  };
  
  // Convert to sorted array of [coin, price] pairs (wire format)
  const oraclePxs = Object.entries(oraclePxsDict).sort(([a], [b]) => a.localeCompare(b));
  
  // Mark prices (optional - empty array for now)
  const markPxs: string[][] = [];
  
  // External perp prices (optional - same as oracle for now)
  const externalPerpPxsDict: Record<string, string> = {
    [config.hlCoinSymbol]: priceStr,
  };
  const externalPerpPxs = Object.entries(externalPerpPxsDict).sort(([a], [b]) => a.localeCompare(b));

  const action = {
    type: 'perpDeploy',
    setOracle: {
      dex: config.hlDexName,
      oraclePxs,  // Sorted array of [coin, price] pairs
      markPxs,  // List of sorted arrays (empty for now)
      externalPerpPxs,  // Sorted array of [coin, price] pairs
    },
  };

  // Hyperliquid requires: action, nonce (timestamp), signature
  // Signature must be L1 action signature using sign_l1_action equivalent
  // TODO: Implement proper L1 action signing (like Python SDK's sign_l1_action)
  // For now, this is a placeholder that will need proper Ethereum signing
  
  const nonce = Date.now();
  const body = JSON.stringify({ action, nonce });
  
  // TODO: Replace with proper L1 action signing
  // The Python SDK uses: sign_l1_action(wallet, action, None, timestamp, expires_after, is_mainnet)
  // We need to replicate this in TypeScript using ethers.js
  const signature = crypto.createHmac('sha256', config.hlApiSecret).update(body).digest('hex');

  const endpoint = `${config.hlUrl}${config.hlOracleEndpoint}`;
  console.log(`[HL] Publishing setOracle: dex=${config.hlDexName}, coin=${config.hlCoinSymbol}, price=${priceStr}`);

  // TODO: Proper signature format {r, s, v} from Ethereum L1 action signing
  const requestBody = {
    action,
    nonce,
    signature: {
      r: signature.slice(0, 64),
      s: signature.slice(64, 128),
      v: 27,
    },
  };

  const response = await request(endpoint, {
    method: 'POST',
    body: JSON.stringify(requestBody),
    headers: {
      'Content-Type': 'application/json',
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
