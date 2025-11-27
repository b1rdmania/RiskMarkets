# Wallet Setup Instructions

## Required Wallet

**Address**: `0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`

This wallet:
- Has traded on Hyperliquid
- Generated the API keys
- Must be used for all HIP-3 deployments and oracle updates

## Setup Steps

1. **Update `.env.testnet`**:
   ```bash
   HL_API_KEY=0xC0D35857e87F5ADe6055714706fb4dFD96DE087E
   HL_API_SECRET=<private_key_for_0xC0D35857e87F5ADe6055714706fb4dFD96DE087E>
   ```

2. **Verify wallet address**:
   ```bash
   cd apps/oracle-service
   python3 scripts/deploy-manual.py
   ```
   
   The script will verify the wallet address matches before proceeding.

3. **Ensure wallet is funded on testnet**:
   - The wallet needs testnet USDC for gas/transactions
   - Check balance at: https://app.hyperliquid-testnet.xyz

## Verification

The deployment script automatically verifies:
- ✅ Wallet address from `HL_API_SECRET` matches `0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`
- ✅ Exits with error if mismatch detected

## Important Notes

- **Never commit** `.env.testnet` to git (it's in `.gitignore`)
- The private key must correspond to `0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`
- All deployments and oracle updates will be signed with this wallet

