import { request } from 'undici';
import { Wallet } from 'ethers';
import { config } from '../config';
import { publishStats } from '../state';
import { signL1Action } from '../utils/hyperliquid-signing';

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

  // Build the action object (matches Python SDK structure)
  const action = {
    type: 'perpDeploy',
    setOracle: {
      dex: config.hlDexName,
      oraclePxs,  // Sorted array of [coin, price] pairs
      markPxs,  // List of sorted arrays (empty for now)
      externalPerpPxs,  // Sorted array of [coin, price] pairs
    },
  };

  // Hyperliquid L1 action signing
  // Replicates Python SDK: sign_l1_action(wallet, action, None, timestamp, expires_after, is_mainnet)
  const nonce = Date.now();
  const expiresAfter = null;  // No expiration for oracle updates
  const activePool = null;  // No vault for setOracle
  const isMainnet = false;  // We're on testnet

  // Create wallet from private key (must be HL_API_PRIVATE_KEY)
  const wallet = new Wallet(config.hlApiPrivateKey);
  
  // Verify signer address matches expected API wallet
  const expectedAddress = '0x86C672b3553576Fa436539F21BD660F44Ce10a86';
  if (wallet.address.toLowerCase() !== expectedAddress.toLowerCase()) {
    throw new Error(`Signer address mismatch! Expected ${expectedAddress}, got ${wallet.address}`);
  }

  // Sign using proper L1 action signing
  const signature = await signL1Action(
    wallet,
    action,
    activePool,
    nonce,
    expiresAfter,
    isMainnet
  );

  const endpoint = `${config.hlUrl}${config.hlOracleEndpoint}`;
  console.log(`[HL] Publishing setOracle: dex=${config.hlDexName}, coin=${config.hlCoinSymbol}, price=${priceStr}`);

  // Request body format matches Python SDK's _post_action
  // Note: vaultAddress is only included for certain action types (not setOracle)
  const requestBody: any = {
    action,
    signature,
    nonce,
    expiresAfter: expiresAfter,  // null for oracle updates
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
