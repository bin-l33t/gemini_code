#!/bin/bash

# Source environment
source ~/.bashrc

# Kill old processes
kill -9 $(ps aux | grep 'gemini_server' | awk '{print $2}')

# Launch latest version
latest_code_path="/home/ubuntu/gemini_code/gemini_server_v7.py"
port=8080

# Use nohup to detach and redirect stdout/stderr to service_v7.log
nohup python "${latest_code_path}" --port ${port} > service_v7.log 2>&1 &

# Verification
sleep 3
curl -v http://localhost:${port}

