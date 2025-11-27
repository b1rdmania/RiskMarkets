# Wallet Verification

## Expected Wallet Address
**0xC0D35857e87F5ADe6055714706fb4dFD96DE087E**

This is the wallet that:
- ✅ Has traded on Hyperliquid
- ✅ Generated the API keys we're using
- ✅ Should be signing all deployment actions
- ✅ Should be used for oracle updates

## Configuration

Update `.env.testnet`:
```bash
HL_API_KEY=0xC0D35857e87F5ADe6055714706fb4dFD96DE087E
HL_API_SECRET=<private_key_for_0xC0D35857e87F5ADe6055714706fb4dFD96DE087E>
```

## Current Issue

The deployment script is using a wallet derived from `HL_API_SECRET`, but we need to verify:
1. The wallet address matches `0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`
2. The API keys were generated from this wallet
3. The wallet is registered/funded on testnet

## Error Message

The previous error mentioned:
```
"User or API Wallet 0x52d165d0a513072bb4ed267807832dfd589b8d1f does not exist."
```

This suggests the signature is being recovered to a different address than expected.

## Next Steps

1. Verify the wallet address from `HL_API_SECRET` matches `0xC0D35857e87F5ADe6055714706fb4dFD96DE087E`
2. If not, update `HL_API_SECRET` to the private key for the correct wallet
3. Ensure the wallet is funded/registered on Hyperliquid testnet
4. Retry deployment

