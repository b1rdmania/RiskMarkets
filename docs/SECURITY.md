# Security Guidelines

## ✅ Secrets Management

### Environment Files
- **`.env.testnet`** is **gitignored** and will **NEVER** be committed
- Only `.env.testnet.example` (with placeholders) is in the repository
- All secrets are loaded from environment variables only

### What's Protected
- ✅ `HL_API_KEY` - Your Hyperliquid API wallet address
- ✅ `HL_API_SECRET` - Your Hyperliquid API wallet private key
- ✅ `PYTH_FEED_ID` - Pyth feed IDs (not sensitive, but good practice)
- ✅ Any other credentials in `.env.testnet`

### Verification
Run this to verify your secrets are not tracked:
```bash
git check-ignore apps/oracle-service/.env.testnet
# Should output: apps/oracle-service/.env.testnet
```

## ⚠️ Important Notes

### API Wallet Security
- Your API wallet is linked to your **main wallet** as a sub-account
- The API wallet private key (`HL_API_SECRET`) has trading permissions but **NOT withdrawal permissions**
- However, it can still perform actions on your account, so keep it secure

### Best Practices
1. **Never commit** `.env.testnet` or any file containing secrets
2. **Never log** `HL_API_SECRET` or full API keys in production
3. **Never share** your `.env.testnet` file
4. **Use different keys** for testnet vs mainnet (when you graduate)
5. **Rotate keys** if you suspect they've been compromised

### If Secrets Are Exposed
If you accidentally commit secrets:
1. **Immediately rotate** the API keys on Hyperliquid
2. **Remove** the secrets from git history (if possible)
3. **Update** `.env.testnet` with new keys
4. **Review** git history to ensure no other exposures

## 🔒 Current Status

✅ **All secrets are secure:**
- `.env.testnet` is gitignored
- No secrets in git history
- All code uses environment variables
- No hardcoded credentials

## 📝 Deployment Security

When deploying to production (Vercel, VPS, etc.):
- Use **environment variables** in the deployment platform
- **Never** commit production secrets to git
- Use **different API keys** for production vs testnet
- Enable **2FA** on your Hyperliquid account
- Monitor for **unauthorized activity**

