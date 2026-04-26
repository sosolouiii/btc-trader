#!/bin/bash
# Auto-restart localtunnel when it dies

while true; do
    echo "Starting localtunnel at $(date)"
    npx localtunnel --port 3000 --print-requests
    echo "Localtunnel crashed at $(date), restarting in 3 seconds..."
    sleep 3
done
