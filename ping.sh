#!/bin/bash
# Ping SOSO BTC MAGNET server every 5 min to keep Render awake
while true; do
  curl -s -o /dev/null -w "%{http_code}" "https://btc-trader-e2t9.onrender.com/api/status" >/dev/null 2>&1
  sleep 300
done
