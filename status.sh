#!/bin/bash
# Get current webhook URL

echo "=== BTC Trader Status ==="
echo ""

# Check if server is running
if pgrep -f "node server.js" > /dev/null; then
    echo "Server: ✅ Running"
else
    echo "Server: ❌ Not running"
fi

# Check if tunnel is running
if pgrep -f "localtunnel" > /dev/null; then
    echo "Tunnel: ✅ Running"
else
    echo "Tunnel: ❌ Not running"
fi

echo ""
echo "=== Current Webhook URL ==="
grep -o "https://[^[:space:]]*\.loca\.lt" /Users/richytakashi/btc-trader/tunnel-daemon.log 2>/dev/null | tail -1

echo ""
echo "=== Recent Trades ==="
curl -s http://localhost:3000/api/trades?limit=3 2>/dev/null | grep -o '"side":"[^"]*"' | head -3

echo ""
echo "=== To get a NEW URL if this one expires ==="
echo "Run: pkill -f localtunnel && sleep 2 && /Users/richytakashi/btc-trader/tunnel.sh"
echo ""
echo "Last updated: $(date)"
