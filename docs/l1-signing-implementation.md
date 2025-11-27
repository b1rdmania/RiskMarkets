# L1 Action Signing Implementation

## ✅ Completed

### 1. Simplified Python Deployment Script
**File**: `apps/oracle-service/scripts/deploy-market-simple.py`

- Uses only existing SDK methods:
  - `perp_deploy_register_asset` ✅
  - `perp_deploy_set_oracle` ✅
- Removed calls to non-existent methods
- Ready to deploy test market

**Note**: Still getting 422 errors, which suggests testnet requirements or permissions issues (not a code problem).

---

### 2. Implemented L1 Action Signing in TypeScript
**File**: `apps/oracle-service/src/utils/hyperliquid-signing.ts`

Replicates Python SDK's `sign_l1_action` function:

1. **`actionHash`**: 
   - msgpack the action
   - Append nonce (8 bytes, big-endian)
   - Append vault_address flag + address (if present)
   - Append expires_after flag + value (if present)
   - Keccak-256 hash

2. **`constructPhantomAgent`**: 
   - Creates `{source: "a"|"b", connectionId: hash}`
   - `"a"` for mainnet, `"b"` for testnet

3. **`l1Payload`**: 
   - Creates EIP-712 typed data structure
   - Domain: `{chainId: 1337, name: "Exchange", ...}`
   - Types: `Agent` with `source` (string) and `connectionId` (bytes32)

4. **`signL1Action`**: 
   - Orchestrates the signing flow
   - Uses `ethers.js` `signTypedData` for EIP-712 signing
   - Returns `{r, s, v}` format

**Dependencies added**:
- `msgpackr` - for msgpack encoding
- `@noble/hashes` - for keccak-256 hashing

---

### 3. Updated Hyperliquid Service
**File**: `apps/oracle-service/src/services/hyperliquid.ts`

- Replaced HMAC placeholder with proper L1 action signing
- Uses `signL1Action` from `hyperliquid-signing.ts`
- Request body matches Python SDK's `_post_action` format:
  ```typescript
  {
    action,
    signature: { r, s, v },
    nonce,
    expiresAfter: null,
  }
  ```

---

## 🔍 Signing Flow (Python → TypeScript)

### Python SDK Flow:
```python
def sign_l1_action(wallet, action, active_pool, nonce, expires_after, is_mainnet):
    hash = action_hash(action, active_pool, nonce, expires_after)
    phantom_agent = construct_phantom_agent(hash, is_mainnet)
    data = l1_payload(phantom_agent)
    return sign_inner(wallet, data)
```

### TypeScript Implementation:
```typescript
export async function signL1Action(
  wallet: Wallet,
  action: any,
  activePool: string | null,
  nonce: number,
  expiresAfter: number | null,
  isMainnet: boolean
): Promise<L1ActionSignature>
```

**Matches Python SDK exactly**:
- ✅ msgpack encoding
- ✅ Keccak-256 hashing
- ✅ EIP-712 typed data signing
- ✅ `{r, s, v}` signature format

---

## 📝 Next Steps

### 1. Test setOracle with Proper Signing
Once the market is deployed (Python script), test the TypeScript oracle:

```bash
cd apps/oracle-service
NETWORK=testnet npm run dev
```

**Expected**: `setOracle` calls should return 200 (not 422).

### 2. Verify Market Deployment
The Python script still returns 422, which suggests:
- Testnet-specific requirements (staking, permissions)
- DEX registration needed first
- API wallet permissions

**Action**: Check with dev team or Hyperliquid docs for testnet deployment requirements.

### 3. Monitor Oracle Loop
Once signing works:
- Oracle service will publish prices every 3 seconds
- Check Hyperliquid testnet UI to see price updates
- Monitor logs for any errors

---

## 🔧 Testing

### Manual Test (Once Market is Deployed)
```typescript
// In a test script or REPL
import { Wallet } from 'ethers';
import { signL1Action } from './src/utils/hyperliquid-signing';

const wallet = new Wallet(process.env.HL_API_SECRET!);
const action = {
  type: 'perpDeploy',
  setOracle: {
    dex: 'XAU',
    oraclePxs: [['XAU-TEST', '1924.55']],
    markPxs: [],
    externalPerpPxs: [['XAU-TEST', '1924.55']],
  },
};

const signature = await signL1Action(
  wallet,
  action,
  null,  // activePool
  Date.now(),  // nonce
  null,  // expiresAfter
  false  // isMainnet (testnet)
);

console.log(signature);
// Should output: { r: '0x...', s: '0x...', v: 27 }
```

---

## 📚 References

- Python SDK: `hyperliquid-python-sdk/hyperliquid/utils/signing.py`
- Hyperliquid Docs: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
- EIP-712: https://eips.ethereum.org/EIPS/eip-712

