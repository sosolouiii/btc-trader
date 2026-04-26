require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const { initDB, logTrade, getStats, getTrades, getTodayLoss } = require('./database');
const { placeOrder, getBalance, getOpenPositions } = require('./trader');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const MAX_POS = parseFloat(process.env.MAX_POSITION_USDT || 100);
const DAILY_LOSS_LIMIT = parseFloat(process.env.DAILY_LOSS_LIMIT_USDT || 50);
const AUTO_TRADE = process.env.ENABLE_AUTO_TRADE === 'true';
const PAPER_TRADING = process.env.PAPER_TRADING === 'true';

let circuitOpen = false;

initDB();

// Health check
app.get('/api/status', async (req, res) => {
  const balance = await getBalance();
  const positions = await getOpenPositions();
  const stats = await getStats();
  const todayLoss = await getTodayLoss();
  res.json({
    autoTrade: AUTO_TRADE,
    circuitOpen,
    dailyLoss: todayLoss,
    dailyLossLimit: DAILY_LOSS_LIMIT,
    balance,
    openPositions: positions,
    stats
  });
});

// Trade history
app.get('/api/trades', async (req, res) => {
  const limit = parseInt(req.query.limit) || 100;
  const trades = await getTrades(limit);
  res.json(trades);
});

// Webhook from TradingView
app.post('/webhook', async (req, res) => {
  try {
    const payload = req.body;

    // 1. Validate secret
    if (payload.secret !== WEBHOOK_SECRET) {
      console.warn('Invalid webhook secret');
      return res.status(401).json({ error: 'Unauthorized' });
    }

    // 2. Circuit breaker
    const todayLoss = await getTodayLoss();
    if (todayLoss >= DAILY_LOSS_LIMIT) {
      circuitOpen = true;
      console.warn('Circuit breaker triggered. Daily loss limit reached.');
      return res.status(503).json({ error: 'Daily loss limit reached. Trading halted.' });
    }

    // 3. Parse signal
    const { symbol, side, amount, sl, tp, message } = payload;
    if (!symbol || !side) {
      return res.status(400).json({ error: 'Missing symbol or side' });
    }

    console.log(`Signal received: ${side.toUpperCase()} ${symbol}`, { sl, tp, message });

    // 4. Size cap
    const tradeSize = Math.min(parseFloat(amount || 0), MAX_POS);
    if (tradeSize <= 0) {
      return res.status(400).json({ error: 'Invalid trade size' });
    }

    // 5. Execute
    let result = { status: 'simulated', payload };
    if (AUTO_TRADE && !circuitOpen) {
      if (PAPER_TRADING) {
        // Simulate a fill at current market price
        const mockPrice = side.toLowerCase() === 'buy' ? parseFloat(sl) * 1.02 : parseFloat(tp) * 0.98;
        result = {
          status: 'filled',
          orderId: 'PAPER-' + Date.now(),
          symbol,
          side: side.toLowerCase(),
          amount: tradeSize,
          price: mockPrice || 70000
        };
        console.log(`PAPER TRADE: ${side.toUpperCase()} ${tradeSize} USDT of ${symbol} @ ~$${result.price}`);
      } else {
        result = await placeOrder(symbol, side.toLowerCase(), tradeSize);
      }
    }

    // 6. Log
    await logTrade({
      symbol,
      side: side.toLowerCase(),
      amount: tradeSize,
      entryPrice: result.price || 0,
      sl,
      tp,
      message,
      status: result.status || 'filled',
      pnl: 0
    });

    res.json({ success: true, result });
  } catch (err) {
    console.error('Webhook error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Manual kill switch
app.post('/api/kill', (req, res) => {
  circuitOpen = true;
  res.json({ success: true, message: 'Trading halted manually.' });
});

app.listen(PORT, () => {
  console.log(`BTC Trader running on port ${PORT}`);
  console.log(`Auto-trade: ${AUTO_TRADE ? 'ON' : 'OFF'} | Testnet: ${process.env.USE_TESTNET === 'true' ? 'YES' : 'NO'} | Paper: ${PAPER_TRADING ? 'YES' : 'NO'}`);
});
