# Vercel Deployment Guide

## Quick Deploy

### Option 1: Deploy via GitHub (Recommended)

1. **Push to GitHub** (already done!)
   ```bash
   git add .
   git commit -m "Add Vercel config"
   git push origin master
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository: `b1rdmania/RiskMarkets`
   - Vercel will auto-detect it's a static site
   - Click "Deploy"

3. **Done!** Your site will be live at `riskmarkets.vercel.app` (or your custom domain)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# From project directory
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (your account)
# - Link to existing project? N
# - Project name? RiskMarkets
# - Directory? ./
# - Override settings? N

# For production deploy:
vercel --prod
```

## Project Structure for Vercel

```
RiskMarkets/
├── index.html          # Landing/splash page
├── terminal.html       # Trading terminal
├── vault.html          # Vault page
├── styles/
│   └── main.css        # Shared styles
├── assets/
│   ├── Video_Brief_for_WARMARKET.mp4
│   └── map-overlay.svg
├── package.json        # Project metadata
└── vercel.json         # Vercel config
```

## Vercel Configuration

The `vercel.json` file includes:

- **Static site detection** - No build step needed
- **Asset caching** - 1 year cache for CSS/assets (faster loads)
- **Clean routing** - All routes serve index.html (for future SPA support)

## Custom Domain

1. Go to your Vercel project settings
2. Click "Domains"
3. Add your custom domain (e.g., `warmarket.com`)
4. Follow DNS setup instructions

## Environment Variables

If you need env vars later (API keys, etc.):
1. Go to Project Settings → Environment Variables
2. Add variables
3. Redeploy

## Important Notes

- **Video file**: The 3MB video will be served via Vercel's CDN (fast globally)
- **No build step**: Pure static HTML/CSS - instant deploys
- **Auto HTTPS**: Vercel handles SSL certificates automatically
- **Preview deployments**: Every push gets a preview URL

## Troubleshooting

**Video not loading?**
- Check file path is correct: `assets/Video_Brief_for_WARMARKET.mp4`
- Check video format is MP4 (should be fine)
- Check browser console for 404 errors

**Styles not loading?**
- Verify `styles/main.css` path is correct
- Clear browser cache
- Check Network tab in dev tools

**Routes not working?**
- All HTML files should be in root directory (✓ already done)
- vercel.json handles routing automatically



