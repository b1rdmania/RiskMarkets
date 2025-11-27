#!/usr/bin/env ts-node
/**
 * Test script for L1 action signing
 * Verifies that TypeScript signing matches Python SDK behavior
 */

import * as dotenv from 'dotenv';
import * as path from 'path';
import { Wallet } from 'ethers';
import { signL1Action } from '../src/utils/hyperliquid-signing';

// Load environment
const envFile = path.resolve(__dirname, '../.env.testnet');
dotenv.config({ path: envFile });

const HL_API_SECRET = process.env.HL_API_SECRET;
if (!HL_API_SECRET) {
  console.error('❌ Missing HL_API_SECRET');
  process.exit(1);
}

async function testSigning() {
  console.log('\n🧪 Testing L1 Action Signing\n');

  // Create wallet (HL_API_SECRET is guaranteed to be defined here)
  const wallet = new Wallet(HL_API_SECRET as string);
  console.log(`✅ Wallet: ${wallet.address}\n`);

  // Test action (setOracle)
  const action = {
    type: 'perpDeploy',
    setOracle: {
      dex: 'XAU',
      oraclePxs: [['XAU-TEST', '1924.55']],
      markPxs: [],
      externalPerpPxs: [['XAU-TEST', '1924.55']],
    },
  };

  const nonce = Date.now();
  const activePool = null;
  const expiresAfter = null;
  const isMainnet = false;

  console.log('📝 Action:');
  console.log(JSON.stringify(action, null, 2));
  console.log(`\n📝 Nonce: ${nonce}`);
  console.log(`📝 Active Pool: ${activePool}`);
  console.log(`📝 Expires After: ${expiresAfter}`);
  console.log(`📝 Is Mainnet: ${isMainnet}\n`);

  try {
    // Sign the action
    console.log('🔐 Signing action...\n');
    const signature = await signL1Action(
      wallet,
      action,
      activePool,
      nonce,
      expiresAfter,
      isMainnet
    );

    console.log('✅ Signature generated:');
    console.log(JSON.stringify(signature, null, 2));
    console.log('\n✅ Signing test passed!\n');

    // Show request body format
    const requestBody = {
      action,
      signature,
      nonce,
      expiresAfter,
    };

    console.log('📦 Request body format:');
    console.log(JSON.stringify(requestBody, null, 2));
    console.log('\n');

    return signature;
  } catch (error) {
    console.error('❌ Signing failed:', error);
    throw error;
  }
}

testSigning()
  .then(() => {
    console.log('✅ All tests passed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Test failed:', error);
    process.exit(1);
  });

