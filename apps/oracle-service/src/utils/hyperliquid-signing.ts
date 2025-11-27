/**
 * Hyperliquid L1 Action Signing
 * 
 * Replicates Python SDK's sign_l1_action function:
 * 1. action_hash: msgpack action + nonce + vault_address + expires_after → keccak hash
 * 2. construct_phantom_agent: {source: "a"|"b", connectionId: hash}
 * 3. l1_payload: EIP-712 typed data structure
 * 4. sign_inner: sign EIP-712 and return {r, s, v}
 */

import { pack } from 'msgpackr';
import { keccak_256 } from '@noble/hashes/sha3';
import { Wallet, TypedDataDomain, TypedDataField } from 'ethers';

export interface L1ActionSignature {
  r: string;
  s: string;
  v: number;
}

/**
 * Convert Ethereum address to bytes (20 bytes)
 */
function addressToBytes(address: string): Uint8Array {
  // Remove 0x prefix and convert to bytes
  const hex = address.startsWith('0x') ? address.slice(2) : address;
  const bytes = new Uint8Array(20);
  for (let i = 0; i < 20; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

/**
 * Convert number to 8-byte big-endian buffer
 */
function numberToBytes8(value: number): Uint8Array {
  const buffer = new ArrayBuffer(8);
  const view = new DataView(buffer);
  view.setBigUint64(0, BigInt(value), false); // big-endian
  return new Uint8Array(buffer);
}

/**
 * Hash the action using msgpack + nonce + vault_address + expires_after
 * Replicates Python: action_hash(action, vault_address, nonce, expires_after)
 */
function actionHash(
  action: any,
  vaultAddress: string | null,
  nonce: number,
  expiresAfter: number | null
): Uint8Array {
  // 1. msgpack the action
  const actionBytes = pack(action);

  // 2. Append nonce (8 bytes, big-endian)
  const nonceBytes = numberToBytes8(nonce);

  // 3. Append vault_address flag + address (if present)
  let vaultBytes: Uint8Array;
  if (vaultAddress === null) {
    vaultBytes = new Uint8Array([0x00]);
  } else {
    const flag = new Uint8Array([0x01]);
    const addrBytes = addressToBytes(vaultAddress);
    vaultBytes = new Uint8Array(flag.length + addrBytes.length);
    vaultBytes.set(flag);
    vaultBytes.set(addrBytes, flag.length);
  }

  // 4. Append expires_after (if present)
  let expiresBytes: Uint8Array;
  if (expiresAfter === null) {
    expiresBytes = new Uint8Array(0);
  } else {
    const flag = new Uint8Array([0x00]);
    const expiresValueBytes = numberToBytes8(expiresAfter);
    expiresBytes = new Uint8Array(flag.length + expiresValueBytes.length);
    expiresBytes.set(flag);
    expiresBytes.set(expiresValueBytes, flag.length);
  }

  // Combine all bytes
  const totalLength = actionBytes.length + nonceBytes.length + vaultBytes.length + expiresBytes.length;
  const combined = new Uint8Array(totalLength);
  let offset = 0;
  combined.set(actionBytes, offset);
  offset += actionBytes.length;
  combined.set(nonceBytes, offset);
  offset += nonceBytes.length;
  combined.set(vaultBytes, offset);
  offset += vaultBytes.length;
  combined.set(expiresBytes, offset);

  // 5. Keccak-256 hash
  const hash = keccak_256(combined);
  return new Uint8Array(hash);
}

/**
 * Construct phantom agent from hash
 * Replicates Python: construct_phantom_agent(hash, is_mainnet)
 */
function constructPhantomAgent(hash: Uint8Array, isMainnet: boolean): {
  source: string;
  connectionId: string;
} {
  return {
    source: isMainnet ? 'a' : 'b',
    connectionId: '0x' + Array.from(hash).map(b => b.toString(16).padStart(2, '0')).join(''),
  };
}

/**
 * Create EIP-712 typed data payload for L1 action
 * Replicates Python: l1_payload(phantom_agent)
 */
function l1Payload(phantomAgent: { source: string; connectionId: string }): {
  domain: TypedDataDomain;
  types: Record<string, TypedDataField[]>;
  primaryType: string;
  message: typeof phantomAgent;
} {
  return {
    domain: {
      chainId: 1337,
      name: 'Exchange',
      verifyingContract: '0x0000000000000000000000000000000000000000',
      version: '1',
    },
    types: {
      Agent: [
        { name: 'source', type: 'string' },
        { name: 'connectionId', type: 'bytes32' },
      ],
      EIP712Domain: [
        { name: 'name', type: 'string' },
        { name: 'version', type: 'string' },
        { name: 'chainId', type: 'uint256' },
        { name: 'verifyingContract', type: 'address' },
      ],
    },
    primaryType: 'Agent',
    message: phantomAgent,
  };
}

/**
 * Sign L1 action using Hyperliquid's signing scheme
 * Replicates Python SDK's sign_l1_action function
 * 
 * @param wallet - Ethereum wallet (from private key)
 * @param action - The action object (e.g., {type: "perpDeploy", setOracle: {...}})
 * @param activePool - Vault address (null for most actions)
 * @param nonce - Timestamp in milliseconds
 * @param expiresAfter - Expiration timestamp (null for most actions)
 * @param isMainnet - true for mainnet, false for testnet
 * @returns Signature in {r, s, v} format
 */
export async function signL1Action(
  wallet: Wallet,
  action: any,
  activePool: string | null,
  nonce: number,
  expiresAfter: number | null,
  isMainnet: boolean
): Promise<L1ActionSignature> {
  // 1. Hash the action
  const hash = actionHash(action, activePool, nonce, expiresAfter);

  // 2. Construct phantom agent
  const phantomAgent = constructPhantomAgent(hash, isMainnet);

  // 3. Create EIP-712 payload
  const payload = l1Payload(phantomAgent);

  // 4. Sign using ethers.js EIP-712 signing
  const signature = await wallet.signTypedData(
    payload.domain,
    payload.types,
    payload.message
  );

  // 5. Parse signature into {r, s, v}
  // ethers signature format: "0x" + r (64 chars) + s (64 chars) + v (2 chars)
  const sigBytes = Buffer.from(signature.slice(2), 'hex');
  const r = '0x' + sigBytes.slice(0, 32).toString('hex');
  const s = '0x' + sigBytes.slice(32, 64).toString('hex');
  const v = sigBytes[64];

  return { r, s, v };
}

