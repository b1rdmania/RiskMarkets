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

import { Wallet } from 'ethers';
import { request } from 'undici';
import * as dotenv from 'dotenv';
import * as path from 'path';

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
 * Register Asset Action for HIP-3 Market Creation
 * 
 * Based on Hyperliquid docs, registerAsset requires:
 * - coin: string (asset symbol, e.g., "XAU-TEST")
 * - szDecimals: number (size decimals)
 * - oraclePx: string (initial oracle price as string)
 * - marginTableId: number (margin table ID, typically 0)
 * - onlyIsolated: boolean (whether isolated margin only)
 */
interface RegisterAsset {
  type: 'registerAsset';
  coin: string;  // Asset symbol (e.g., "XAU-TEST")
  szDecimals: number;  // Size decimals (recommended: 0-2 for $1-10 increments)
  oraclePx: string;  // Initial oracle price as string (e.g., "1924.55")
  marginTableId: number;  // Margin table ID (typically 0)
  onlyIsolated: boolean;  // Isolated margin only (false for cross margin)
}

/**
 * Create HIP-3 Market (createMarket)
 * 
 * Sends the registerAsset action to create a new HIP-3 perpetual market.
 * Returns the assetId which becomes HL_MARKET_ID.
 */
async function createMarket(config: {
  symbol: string;  // Market symbol (e.g., "XAU-TEST")
  szDecimals: number;
  initialOraclePrice: string;  // Initial price as string (e.g., "1924.55")
  marginTableId?: number;
  onlyIsolated?: boolean;
}): Promise<{ assetId: number; symbol: string }> {
  const { 
    symbol, 
    szDecimals, 
    initialOraclePrice,
    marginTableId = 0,
    onlyIsolated = false 
  } = config;

  console.log(`\n🚀 Creating HIP-3 market: ${symbol}`);
  console.log(`   Initial Oracle Price: ${initialOraclePrice}`);
  console.log(`   Size Decimals: ${szDecimals}`);
  console.log(`   Margin Table ID: ${marginTableId}`);
  console.log(`   Isolated Only: ${onlyIsolated}\n`);

  // Hyperliquid perpDeploy action with registerAsset
  const action = {
    type: 'perpDeploy',
    registerAsset: {
      type: 'registerAsset',
      coin: symbol,
      szDecimals,
      oraclePx: initialOraclePrice,  // Initial oracle price as string
      marginTableId,
      onlyIsolated,
    },
  };

  // Hyperliquid API requires: action, nonce, and signature
  // Nonce: current timestamp in milliseconds
  const nonce = Date.now();
  
  // Create wallet from private key
  const wallet = new Wallet(API_SECRET);
  
  // Hyperliquid signs: action + nonce
  // The signature format is specific to Hyperliquid's signing scheme
  // Based on Python SDK, we need to sign the action object + nonce
  const messageToSign = {
    action,
    nonce,
  };
  
  // Sign the message - Hyperliquid uses a specific signing format
  // The Python SDK uses: sign_l1_action(action, wallet, nonce)
  // For now, we'll sign the JSON stringified action + nonce
  const message = JSON.stringify(messageToSign);
  
  // Get the signature - Hyperliquid expects a specific format
  // Note: This may need adjustment based on Hyperliquid's exact signing scheme
  const signature = await wallet.signMessage(message);
  
  // Parse the signature into r, s, v format
  // Ethereum signatures are 65 bytes: r (32) + s (32) + v (1)
  const sigBytes = Buffer.from(signature.slice(2), 'hex');
  const r = '0x' + sigBytes.slice(0, 32).toString('hex');
  const s = '0x' + sigBytes.slice(32, 64).toString('hex');
  const v = sigBytes[64];

  // Create final request body
  const requestBody = {
    action,
    nonce,
    signature: {
      r,
      s,
      v,
    },
  };

  const body = JSON.stringify(requestBody);
  const endpoint = `${HL_URL}/exchange`;
  
  console.log(`📡 Sending to: ${endpoint}`);
  console.log(`📦 Action:`, JSON.stringify(action, null, 2));
  console.log(`📦 Nonce: ${nonce}`);
  console.log(`📦 Wallet Address: ${wallet.address}`);
  // ⚠️ SECURITY: Never log HL_API_SECRET or full signatures in production

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
    
    if (result.status === 'ok' && result.response) {
      // Extract assetId from response
      // The exact structure may vary - adjust based on actual response
      const assetId = result.response.assetId || result.response.data?.assetId;
      const marketSymbol = result.response.symbol || symbol;
      
      console.log(`✅ Market created successfully!`);
      console.log(`📋 Response:`, JSON.stringify(result, null, 2));
      console.log(`\n🎯 Market Details:`);
      console.log(`   Asset ID: ${assetId}`);
      console.log(`   Symbol: ${marketSymbol}`);
      
      console.log(`\n📝 Next steps:`);
      console.log(`   1. Update .env.testnet:`);
      console.log(`      HL_MARKET_ID=${assetId}`);
      console.log(`      HL_MARKET_SYMBOL=${marketSymbol}`);
      console.log(`      HL_PUBLISH_ENABLED=true`);
      console.log(`   2. Start your oracle service: npm run dev`);
      console.log(`   3. Verify market at: https://app.hyperliquid-testnet.xyz/perps`);
      console.log(`   4. Watch for price updates every ~3 seconds\n`);
      
      return { assetId, symbol: marketSymbol };
    } else {
      throw new Error(`Unexpected response format: ${responseText}`);
    }

  } catch (error) {
    console.error(`❌ Error deploying market:`, error);
    throw error;
  }
}

/**
 * Main execution
 */
async function main() {
  // Create XAU-TEST market (gold, recommended for v0)
  // Get initial price from Pyth or use a reasonable default
  const initialPrice = process.env.INITIAL_ORACLE_PRICE || '1924.55';  // Default gold price
  
  const marketConfig = {
    symbol: 'XAU-TEST',  // Market symbol
    szDecimals: 2,  // For $0.01 increments (if price ~$2000)
    initialOraclePrice: initialPrice,  // Initial oracle price as string
    marginTableId: 0,  // Default margin table
    onlyIsolated: false,  // Allow cross margin
  };

  console.log('🚀 Ready to create HIP-3 market on Hyperliquid testnet\n');
  console.log('Market configuration:');
  console.log(`  Symbol: ${marketConfig.symbol}`);
  console.log(`  Initial Oracle Price: $${marketConfig.initialOraclePrice}`);
  console.log(`  Size Decimals: ${marketConfig.szDecimals}`);
  console.log(`  Margin Table ID: ${marketConfig.marginTableId}`);
  console.log(`  Isolated Only: ${marketConfig.onlyIsolated}\n`);

  // Create the market
  const result = await createMarket(marketConfig);
  console.log(`\n✅ Market created! Asset ID: ${result.assetId}`);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

