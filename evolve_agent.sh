#!/bin/bash
echo "Killing any process on port 8080..."
fuser -k 8080/tcp || true
sleep 2

echo "Starting Agent_v4..."
nohup python3 gemini_server_v4.py --name "Agent_v4" --port 8080 --force > server_v4.log 2>&1 &

PID=$!
echo "Server launched in background. PID: $PID"
sleep 5
