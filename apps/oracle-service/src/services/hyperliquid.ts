import { request } from 'undici';
import { execSync } from 'child_process';
import * as path from 'path';
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

  // Use Python SDK for setOracle (canonical signing implementation)
  // This avoids the message hash mismatch issue described in Hyperliquid docs
  const scriptPath = path.join(__dirname, '../../scripts/set-oracle.py');
  
  console.log(`[HL] Publishing setOracle via Python SDK: dex=${config.hlDexName}, coin=${config.hlCoinSymbol}, price=${priceStr}`);
  
  try {
    // Call Python script with price
    const output = execSync(
      `python3 "${scriptPath}" "${priceStr}"`,
      {
        cwd: path.join(__dirname, '../..'),
        encoding: 'utf-8',
        env: {
          ...process.env,
          NETWORK: config.network,
        },
      }
    );
    
    const result = JSON.parse(output.trim());
    
    if (!result.ok) {
      throw new Error(`HL publish failed: ${result.response || result.error || 'Unknown error'}`);
    }
    
    console.log(`[HL] setOracle successful: ${result.response || 'ok'}`);

    lastPublishedValue = value;
    lastPublishTimestamp = now;
    publishStats.lastPublish = now;
    publishStats.totalPublishes += 1;

    return { ok: true };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`HL publish error: ${message}`);
  }
}
