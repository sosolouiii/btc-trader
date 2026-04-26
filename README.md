# BTC Auto Trader

TradingView webhook → Node.js → Bybit/Binance/OKX API.

## ⚠️ Disclaimer
This is experimental software. A 72% backtest win rate does **not** guarantee live profitability. 
Slippage, latency, and exchange downtime can destroy strategies. Start with **testnet**.

## Quick Start

### 1. Get Bybit Testnet API Keys (Fastest Option)
1. Go to [Bybit Testnet](https://testnet.bybit.com/)
2. Sign up with email (no KYC needed for testnet)
3. Go to **Account & Security** → **API Management**
4. Create API Key:
   - **Read-Write** permissions
   - **Unified Trading Account**
   - Whitelist IP: your server IP (or leave empty for testing)
5. Copy **API Key** and **API Secret**

### 2. Configure Environment
```bash
cd btc-trader
cp .env.example .env
```

Edit `.env`:
```
EXCHANGE=bybit
API_KEY=your_bybit_testnet_api_key
API_SECRET=your_bybit_testnet_secret
WEBHOOK_SECRET=ragnar
USE_TESTNET=true
ENABLE_AUTO_TRADE=true
```

### 3. Install & Run
```bash
npm install
npm start
```

Dashboard: `http://localhost:3000`

### 4. Expose to Internet (for TradingView webhooks)
```bash
npx ngrok http 3000
```
Copy the **HTTPS** URL into your TradingView alert webhook field.

### 5. TradingView Alert Setup
1. Open Alerts panel (clock icon)
2. Create Alert
3. **Condition:** Your indicator → `Alert() function calls`
4. **Message:** Leave BLANK
5. **Webhook URL:** Paste your ngrok HTTPS URL + `/webhook`
6. **Frequency:** Once Per Bar Close
7. Click Create

## Supported Exchanges
| Exchange | Testnet | Notes |
|----------|---------|-------|
| **Bybit** | ✅ Yes | Fastest setup, no KYC for testnet |
| Binance | ✅ Yes | Requires futures account activation |
| OKX | ✅ Yes | Good alternative |

To switch exchanges, change `EXCHANGE=` in `.env`:
- `EXCHANGE=bybit`
- `EXCHANGE=binance`
- `EXCHANGE=okx`

## Safety Features
- **Webhook secret validation** (rejects unauthorized pings)
- **Daily loss circuit breaker** (halts trading automatically)
- **Max position size** (env-controlled cap)
- **Manual kill switch** (dashboard button)
- **Testnet sandbox** (trade fake money first)

## Architecture
```
TradingView Alert (JSON via Webhook)
         ↓
   Express Server (/webhook)
         ↓
   Validate Secret → Circuit Check → Size Check
         ↓
   CCXT → Exchange API (Market Order)
         ↓
   SQLite Log + Dashboard Update
```

## Payload Sent to Server
```json
{
  "secret": "ragnar",
  "symbol": "BTCUSDT",
  "side": "buy",
  "amount": 100,
  "sl": 65000.5,
  "tp": 72000.0,
  "message": "AlgoTrend Long"
}
```

## Next Steps
1. Deploy to a VPS (DigitalOcean, AWS, Railway) for 24/7 uptime
2. Set up PM2: `pm2 start server.js`
3. Add reverse proxy (Nginx/Caddy) with HTTPS
4. Only after 2+ weeks of profitable testnet behavior, switch `USE_TESTNET=false`

## Important
- **Never share your API keys**
- **Start with testnet only**
- **Set conservative position sizes**
- **Monitor the dashboard daily**
