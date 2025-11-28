# L1 Action Signing Question

## Current Situation

✅ **Master Account**: Exists, has funds (1022 USDC withdrawable)
✅ **API Wallet**: Exists (0 balance, expected)
✅ **Signature Recovery**: Consistent (`0x86c672b3553576fa436539f21bd660f44ce10a86`)
❌ **Error**: "User or API Wallet does not exist" for L1 actions

## Key Question

**Do API wallets (agents) have permission to sign L1 actions (`perpDeploy`), or do L1 actions require signing with the master wallet's private key?**

## What We Know

1. API wallets are used for **regular trading** (orders, positions)
2. L1 actions (`perpDeploy.registerAsset`, `perpDeploy.setOracle`) are **deployer actions**
3. The error says the API wallet "does not exist" specifically for L1 actions

## Hypothesis

**API wallets may only be authorized for regular trading operations, not for L1/deployer actions.**

If this is true, we need to:
1. Use the **master wallet's private key** for L1 actions
2. Keep API wallet for regular trading operations

## What to Check

1. **Hyperliquid Documentation**: Do L1 actions require master wallet signing?
2. **API Wallet Permissions**: Are API wallets restricted from L1 actions?
3. **Try Master Wallet**: Test signing with master wallet private key (if available)

## Next Steps

1. Check if we have the master wallet private key (`0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`)
2. If yes, try signing L1 actions with master wallet instead of API wallet
3. If no, ask user if API wallets can perform L1 actions or if master wallet key is needed

