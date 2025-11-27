#!/usr/bin/env ts-node
/**
 * Verify the signer address matches the expected API wallet
 * 
 * Usage:
 *   NETWORK=testnet npx ts-node scripts/check-signer.ts
 */

import * as dotenv from 'dotenv';
import * as path from 'path';
import { Wallet } from 'ethers';

// Load environment
const envFile = path.resolve(__dirname, '../.env.testnet');
dotenv.config({ path: envFile });

const pk = process.env.HL_API_PRIVATE_KEY;
if (!pk) {
  console.error('❌ Error: HL_API_PRIVATE_KEY not set');
  process.exit(1);
}

const wallet = new Wallet(pk);
const expectedAddress = '0x86C672b3553576Fa436539F21BD660F44Ce10a86';

console.log('\n🔍 Signer Verification\n');
console.log(`Signer from HL_API_PRIVATE_KEY: ${wallet.address}`);
console.log(`Expected address:              ${expectedAddress}\n`);

if (wallet.address.toLowerCase() === expectedAddress.toLowerCase()) {
  console.log('✅ Signer address matches!');
  process.exit(0);
} else {
  console.log('❌ Signer address mismatch!');
  console.log('   You are using the wrong key or wrong env file.');
  process.exit(1);
}

