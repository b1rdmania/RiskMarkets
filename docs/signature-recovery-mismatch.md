# Signature Recovery Mismatch Issue

## Problem

- **Local signature recovery**: ✅ Correctly recovers to `0x86C672b3553576Fa436539F21BD660F44Ce10a86`
- **Hyperliquid recovery**: ❌ Reports different address (changes each run)
  - Run 1: `0x4839574114fe26c1dce651e7fd8908f50b19c715`
  - Run 2: `0x8dceccf0b995cfd9b7b539f2909ae9ce92b62d49`

## Analysis

The fact that:
1. Local recovery works correctly
2. Hyperliquid reports a different address
3. The error address changes each run

Suggests that Hyperliquid might be:
- Recovering from a different part of the payload
- Using a different recovery method
- Checking a different signature field

## Possible Causes

1. **Action serialization mismatch**: The action might be serialized differently on Hyperliquid's side
2. **Nonce handling**: The nonce might be affecting signature recovery
3. **Wallet authorization**: The wallet might need to be explicitly authorized/registered first
4. **API wallet vs L1 action**: There might be a distinction between API wallet actions and L1 actions

## Next Steps

1. Check if wallet needs to be registered/authorized in Hyperliquid UI first
2. Verify the exact action structure Hyperliquid expects
3. Check if there's a different endpoint or method for HIP-3 deployments
4. Contact Hyperliquid support with the exact payload and signature

