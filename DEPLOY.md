# Deployment Guide

## Option 1: Railway (Fastest — 2 minutes)

### Step 1: Login to Railway
```bash
railway login
```
This opens a browser tab. Click **Authorize**.

### Step 2: Initialize project
```bash
cd /Users/richytakashi/btc-trader
railway init
```
Choose **Empty Project**, name it `soso-btc-magnet`.

### Step 3: Add environment variables
```bash
railway variables set EXCHANGE=okx
railway variables set API_KEY=your_okx_api_key
railway variables set API_SECRET=your_okx_secret
railway variables set API_PASSPHRASE=your_passphrase
railway variables set WEBHOOK_SECRET=ragnar
railway variables set MAX_POSITION_USDT=100
railway variables set DAILY_LOSS_LIMIT_USDT=50
railway variables set ENABLE_AUTO_TRADE=true
railway variables set USE_TESTNET=false
railway variables set PAPER_TRADING=true
```

### Step 4: Deploy
```bash
railway up
```

### Step 5: Get public URL
```bash
railway domain
```
Copy the URL (e.g., `https://soso-btc-magnet.up.railway.app`).

Your webhook URL will be:
```
https://btc-trader.up.railway.app/webhook
```

**⚠️ CRITICAL: The URL MUST end with `/webhook`.**  
Without `/webhook`, TradingView will show "delivery failed".

---

## Option 2: Render (Also free)

### Step 1: Push to GitHub
```bash
cd /Users/richytakashi/btc-trader
git init
git add .
git commit -m "Initial deploy"
```

Create a new repo on GitHub, then:
```bash
git remote add origin https://github.com/YOUR_USERNAME/soso-btc-magnet.git
git branch -M main
git push -u origin main
```

### Step 2: Connect Render
1. Go to [render.com](https://render.com)
2. Click **New +** → **Blueprint**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`

### Step 3: Add secrets in Render Dashboard
Go to your service → **Environment** → add:
- `API_KEY`
- `API_SECRET`
- `API_PASSPHRASE`

### Step 4: Deploy
Render auto-deploys on every git push.

Your webhook URL will be:
```
https://soso-btc-magnet.onrender.com/webhook
```

**⚠️ CRITICAL: The URL MUST end with `/webhook`.**  
Without `/webhook`, TradingView will show "delivery failed".

---

## After Deployment

1. **Update TradingView alert** with your permanent webhook URL
2. **Test it:** Send a test payload to verify
3. **Dashboard:** Visit `https://your-url.com` to see trades
4. **Logs:** Check Railway/Render dashboard for real-time logs

## Switching from Paper to Live Trading

When you're ready for real money:

1. Set `PAPER_TRADING=false`
2. Set `USE_TESTNET=false`
3. Ensure API keys have **real trading** permissions
4. Restart the service

## Security Checklist

- [ ] Delete all exposed API keys (generate fresh ones)
- [ ] Enable IP whitelist on exchange API keys (whitelist your server IP)
- [ ] Set strong `WEBHOOK_SECRET`
- [ ] Start with small `MAX_POSITION_USDT` ($50-100)
- [ ] Keep `DAILY_LOSS_LIMIT_USDT` tight ($30-50)
