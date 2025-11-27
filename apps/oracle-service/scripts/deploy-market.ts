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

  const registerAsset: RegisterAsset = {
    type: 'registerAsset',
    name: assetName,
    szDecimals,
    maxLeverage,
  };

  const action = {
    type: 'perpDeploy',
    registerAsset,
  };

  const payload = {
    action,
  };

  const body = JSON.stringify(payload);
  
  // Sign the request (authentication method may vary - verify with HL docs)
  const signature = crypto.createHmac('sha256', HL_API_SECRET)
    .update(body)
    .digest('hex');

  const endpoint = `${HL_URL}/exchange`;
  
  console.log(`📡 Sending to: ${endpoint}`);
  console.log(`📦 Payload:`, JSON.stringify(payload, null, 2));
  // ⚠️ SECURITY: Never log HL_API_SECRET or full API keys in production

  try {
    const response = await request(endpoint, {
      method: 'POST',
      body,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${HL_API_KEY}:${signature}`,
        'X-API-Key': HL_API_KEY,
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
  // Example: Deploy GOLD-TEST market
  // Adjust these parameters based on your needs
  
  const marketConfig = {
    assetName: 'GOLD-TEST',  // Change to your desired asset name
    szDecimals: 2,  // For $0.01 increments (if price ~$2000)
    maxLeverage: 20,  // 20x leverage
  };

  // Uncomment to deploy:
  // await deployMarket(marketConfig);

  console.log(`
⚠️  DEPLOYMENT SCRIPT READY

This script is ready to deploy a HIP-3 market, but you should:

1. Verify the exact API structure with Hyperliquid docs
2. Check if testnet requires staking (may be waived)
3. Confirm authentication method (HMAC vs wallet signature)
4. Review market parameters before deploying

To deploy, uncomment the deployMarket() call above and run:
  NETWORK=testnet ts-node scripts/deploy-market.ts

Recommended first market: GOLD-TEST (solo asset, simple to test)
  `);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

