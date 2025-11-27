# Master vs Agent Wallet Configuration Fix

## Problem Identified

The error "User or API Wallet does not exist" is caused by **master vs agent wallet confusion**, not just authorization.

## Key Distinction

- **Master Account** (`0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`): 
  - Main wallet where funds are deposited
  - Used for account queries (`user_state`)
  - This is the "user" that Hyperliquid recognizes

- **API Wallet / Agent** (`0x86C672b3553576Fa436539F21BD660F44Ce10a86`):
  - Used **only for signing** L1 actions
  - Must be authorized for the master account
  - Not used as the "user" address

## What Was Wrong

1. **Using agent address as "user"**: We were treating `0x86C6...` as both signer and user
2. **Missing master address**: No distinction between master and agent
3. **Incorrect `oracleUpdater`**: Was using agent address instead of master

## Fix Applied

### Environment Variables
```env
# Master account (where funds are deposited)
HL_MASTER_ADDRESS=0xC0D35857e87F5ADe6055714706fb4dFD96DE087E

# API wallet (agent - used only for signing)
HL_API_ADDRESS=0x86C672b3553576Fa436539F21BD660F44Ce10a86
HL_API_PRIVATE_KEY=0x2b4596e948e1b164b05264c17cf0b4e47ef39509e896074f76e9e23c0a0542a7
```

### Code Changes

1. **`deploy-manual.py`**:
   - Uses `HL_API_PRIVATE_KEY` for signing (agent)
   - Uses `HL_MASTER_ADDRESS` for `oracleUpdater` (master)

2. **`set-oracle.py`**:
   - Uses `HL_API_PRIVATE_KEY` for signing (agent)
   - Logs both addresses for verification

3. **`config.ts`**:
   - Added `hlMasterAddress` field
   - Separated master vs agent addresses

## Additional Checks Needed

1. **Trading Enabled**: Master account must have trading enabled in Hyperliquid UI
2. **Funds Deposited**: Master account must have testnet USDC deposited (not just in Arbitrum wallet)
3. **API Wallet Authorized**: API wallet must be authorized in Hyperliquid UI → API Wallets

## Next Steps

1. Verify in Hyperliquid Testnet UI:
   - Master account (`0xC0D3...`) has trading enabled
   - Master account has deposited testnet USDC
   - API wallet (`0x86C6...`) is authorized and not expired

2. Re-run deployment:
   ```bash
   python3 scripts/deploy-manual.py
   ```

3. If error changes (e.g., "Must deposit before performing actions"), we've fixed the auth layer.

