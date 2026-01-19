#!/bin/bash

# Start Instance A
python3 gemini_server_v3.py --name "Alpha" --port 8080 > alpha.log 2>&1 &  # Redirect output to alpha.log
alpha_pid=$!

# Start Instance B
python3 gemini_server_v3.py --name "Beta" --port 8081 > beta.log 2>&1 &   # Redirect output to beta.log
beta_pid=$!

# Print the PIDs and access URLs
echo "Instance A (Alpha) PID: $alpha_pid"
echo "Instance A (Alpha) URL: http://localhost:8080"
echo "Instance B (Beta) PID: $beta_pid"
echo "Instance B (Beta) URL: http://localhost:8081"

echo "\nLogs are being written to alpha.log and beta.log"

# Optional: Keep the script running (e.g., tail the logs)
tail -f alpha.log beta.log
