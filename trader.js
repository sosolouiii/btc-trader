const ccxt = require('ccxt');

const exchangeId = process.env.EXCHANGE || 'bybit';
const isTestnet = process.env.USE_TESTNET === 'true';

const config = {
  apiKey: process.env.API_KEY,
  secret: process.env.API_SECRET,
  enableRateLimit: true,
  options: {
    defaultType: 'swap'
  }
};

// OKX requires passphrase
if (exchangeId === 'okx') {
  config.password = process.env.API_PASSPHRASE || '';
}

// Bybit testnet
if (exchangeId === 'bybit' && isTestnet) {
  config.options.testnet = true;
}

const exchange = new ccxt[exchangeId](config);

if (isTestnet && exchangeId === 'bybit') {
  console.log(`Using ${exchangeId.toUpperCase()} Testnet`);
} else if (exchangeId === 'okx') {
  console.log(`Using ${exchangeId.toUpperCase()} (Demo mode via Paper Trading)`);
} else {
  console.log(`Using ${exchangeId.toUpperCase()} LIVE`);
}

async function getBalance() {
  try {
    const balance = await exchange.fetchBalance();
    return {
      usdt: balance.total?.USDT || 0,
      btc: balance.total?.BTC || 0
    };
  } catch (e) {
    console.error('Balance error:', e.message);
    return { usdt: 0, btc: 0 };
  }
}

async function getOpenPositions() {
  try {
    const positions = await exchange.fetchPositions();
    return positions
      .filter(p => parseFloat(p.contracts) !== 0)
      .map(p => ({
        symbol: p.symbol,
        side: p.side,
        size: p.contracts,
        entryPrice: p.entryPrice,
        unrealizedPnl: p.unrealizedPnl
      }));
  } catch (e) {
    console.error('Positions error:', e.message);
    return [];
  }
}

async function placeOrder(symbol, side, usdtAmount) {
  try {
    // Normalize symbol for CCXT
    // Pine sends BTCUSDT, CCXT expects BTC/USDT:USDT (linear perpetual)
    let formattedSymbol = symbol;
    if (!symbol.includes('/') && !symbol.includes(':')) {
      const base = symbol.replace('USDT', '').replace('USD', '');
      const quote = symbol.includes('USDT') ? 'USDT' : 'USD';
      formattedSymbol = `${base}/${quote}:${quote}`;
    }
    
    // Fetch current price to calculate quantity
    const ticker = await exchange.fetchTicker(formattedSymbol);
    const price = ticker.last;
    const quantity = usdtAmount / price;
    
    // Round to exchange precision
    const amount = exchange.amountToPrecision(formattedSymbol, quantity);

    const order = await exchange.createMarketOrder(formattedSymbol, side, amount);
    
    console.log(`Order placed: ${side.toUpperCase()} ${amount} ${formattedSymbol} @ ~$${price}`);
    
    return {
      status: 'filled',
      orderId: order.id,
      symbol: formattedSymbol,
      side,
      amount,
      price
    };
  } catch (e) {
    console.error('Order error:', e.message);
    throw e;
  }
}

module.exports = { getBalance, getOpenPositions, placeOrder };
