MISSION: SYSTEM AUDIT AND PHOENIX DEPLOYMENT

ROLE: Autonomous DevOps Engineer.
CONTEXT: You are operating in a stale environment where old server versions (v3) might be running, but a new version (v7) exists.
GOAL: Audit the system, kill old processes, and deploy the latest server version using the "Phoenix" pattern.

PHASE 1: DISCOVERY & AUDIT
1.  Execute `ls -la bin-l33t/gemini_code/gemini_code-*/gemini_server_*.py` to find all server versions. Identify the file with the highest version number (e.g., v7, v8).
2.  Execute `ps aux | grep gemini_server` to identify currently running server processes and their PIDs.
3.  Analyze the latest server file content using `View`. Check if it requires the `--force` flag to takeover ports.

PHASE 2: REPORTING
1.  Create a file named `audit_report.json` containing:
    -   "latest_version_path": [Path to highest version]
    -   "active_processes": [List of PIDs and ports from ps aux]
    -   "recommended_action": "Kill old PIDs and spawn new version"

PHASE 3: EXECUTION (THE PHOENIX MANEUVER)
1.  Write a bash script named `phoenix_deploy.sh` that does the following:
    -   Reads `audit_report.json`.
    -   Kills the old PIDs found in the report.
    -   Starts the "latest_version_path" found in the report on PORT 8888 (or 8080 if 8888 is strictly unavailable).
    -   Uses `nohup python3 [latest_server_file] --port 8888 --force > server_v7.log 2>&1 &` to detach the process.
2.  Make the script executable: `chmod +x phoenix_deploy.sh`.
3.  Execute the script.

PHASE 4: VERIFICATION
1.  Wait 2 seconds.
2.  Run `ps aux | grep gemini_server` again to verify the new PID is running and the old ones are gone.
3.  Output the final status.
