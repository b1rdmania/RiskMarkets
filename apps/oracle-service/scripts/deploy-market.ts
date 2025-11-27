/**
 * HIP-3 Market Deployment Script
 * 
 * Deploys a HIP-3 perpetual market on Hyperliquid testnet.
 * 
 * Usage:
 *   NETWORK=testnet ts-node scripts/deploy-market.ts
 * 
 * Environment variables required:
 *   - HL_TESTNET_URL
 *   - HL_API_KEY
 *   - HL_API_SECRET
 *   - HL_DEX_NAME (optional, defaults to "WARMARKET")
 */

import crypto from 'crypto';
import { request } from 'undici';
import * as dotenv from 'dotenv';
import * as path from 'path';

// For Ethereum wallet signing
// Note: Hyperliquid uses wallet signature, not HMAC
// We'll need to use ethereum signing - for now, let's try the API wallet approach

// Load environment
const envFile = process.env.ENV_FILE ?? '.env.testnet';
dotenv.config({ path: path.resolve(process.cwd(), envFile) });

const HL_URL = process.env.HL_TESTNET_URL || 'https://api.hyperliquid-testnet.xyz';
const HL_API_KEY = process.env.HL_API_KEY;
const HL_API_SECRET = process.env.HL_API_SECRET;
const HL_DEX_NAME = process.env.HL_DEX_NAME || 'WARMARKET';

if (!HL_API_KEY || !HL_API_SECRET) {
  throw new Error('Missing HL_API_KEY or HL_API_SECRET');
}

// TypeScript: ensure these are strings after the check
const API_KEY: string = HL_API_KEY;
const API_SECRET: string = HL_API_SECRET;

/**
 * Register Asset Action
 * 
 * This is the first step in deploying a HIP-3 market.
 * Registers the asset with market parameters.
 */
interface RegisterAsset {
  type: 'registerAsset';
  name: string;  // Asset name (e.g., "GOLD-TEST")
  szDecimals: number;  // Size decimals (recommended: 0-2 for $1-10 increments)
  maxLeverage?: number;  // Maximum leverage (default: 20)
  oracle?: {
    // Oracle definition - points to your oracle service
    // This may need to be your API wallet address or a contract address
    address?: string;
  };
}

/**
 * Deploy Perpetual Market
 * 
 * Sends the registerAsset action to deploy a new HIP-3 market.
 */
async function deployMarket(config: {
  assetName: string;
  szDecimals: number;
  maxLeverage?: number;
}): Promise<void> {
  const { assetName, szDecimals, maxLeverage = 20 } = config;

  console.log(`\n🚀 Deploying HIP-3 market: ${assetName}`);
  console.log(`   DEX: ${HL_DEX_NAME}`);
  console.log(`   Size Decimals: ${szDecimals}`);
  console.log(`   Max Leverage: ${maxLeverage}x\n`);

  // Try different action structures - Hyperliquid API might expect different format
  // Option 1: Nested perpDeploy
  const action = {
    type: 'perpDeploy',
    registerAsset: {
      type: 'registerAsset',
      name: assetName,
      szDecimals,
      maxLeverage,
    },
  };

  // Hyperliquid API requires: action, nonce, and signature
  // The signature is a wallet signature (Ethereum signature), not HMAC
  // For API wallets, we may need to use the private key to sign
  const nonce = Date.now();
  
  // Create the full request body with nonce
  const requestBody = {
    action: payload.action,
    nonce,
    // signature will be added after signing
  };

  const bodyToSign = JSON.stringify(requestBody);
  
  // TODO: Use proper Ethereum wallet signing here
  // For now, trying HMAC as a fallback (may not work)
  // Hyperliquid API wallets might use different auth - need to verify
  const signature = crypto.createHmac('sha256', API_SECRET)
    .update(bodyToSign)
    .digest('hex');

  // Add signature to request body
  const finalBody = {
    ...requestBody,
    signature: {
      r: signature.slice(0, 64),  // Placeholder - need proper Ethereum signature
      s: signature.slice(64, 128),
      v: 27,
    },
  };

  const body = JSON.stringify(finalBody);
  const endpoint = `${HL_URL}/exchange`;
  
  console.log(`📡 Sending to: ${endpoint}`);
  console.log(`📦 Payload (without signature):`, JSON.stringify({ ...finalBody, signature: '***HIDDEN***' }, null, 2));
  // ⚠️ SECURITY: Never log HL_API_SECRET or full API keys in production

  try {
    const response = await request(endpoint, {
      method: 'POST',
      body,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const responseText = await response.body.text();
    
    if (response.statusCode >= 400) {
      console.error(`❌ Deployment failed (${response.statusCode}):`, responseText);
      throw new Error(`Deployment failed: ${responseText}`);
    }

    const result = JSON.parse(responseText);
    console.log(`✅ Deployment successful!`);
    console.log(`📋 Response:`, JSON.stringify(result, null, 2));
    
    console.log(`\n📝 Next steps:`);
    console.log(`   1. Update HL_MARKET_ID in .env.testnet: ${assetName}`);
    console.log(`   2. Start your oracle service: npm run dev`);
    console.log(`   3. Verify market appears on Hyperliquid testnet`);
    console.log(`   4. Test price publishing via setOracle\n`);

  } catch (error) {
    console.error(`❌ Error deploying market:`, error);
    throw error;
  }
}

/**
 * Main execution
 */
async function main() {
  // Deploy GOLD-TEST market (solo asset, recommended for v0)
  const marketConfig = {
    assetName: 'GOLD-TEST',  // Asset name (<= 6 chars recommended)
    szDecimals: 2,  // For $0.01 increments (if price ~$2000)
    maxLeverage: 20,  // 20x leverage
  };

  console.log('🚀 Ready to deploy HIP-3 market on Hyperliquid testnet\n');
  console.log('Market configuration:');
  console.log(`  Asset: ${marketConfig.assetName}`);
  console.log(`  Size Decimals: ${marketConfig.szDecimals}`);
  console.log(`  Max Leverage: ${marketConfig.maxLeverage}x`);
  console.log(`  DEX: ${HL_DEX_NAME}\n`);

  // Deploy the market
  await deployMarket(marketConfig);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

