#!/bin/bash

report_file="audit_report.json"

latest_version_path=$(sed -n 's/.*latest_version_path": "\(.*\)".*/\1/p' "${report_file}")
#active_processes=$(jq -r .active_processes "${report_file}")

# Kill old processes (currently none)
#echo "Killing old processes: ${active_processes}"
#for pid in $active_processes; do
#  kill -9 $pid
#done

# Start the new version
echo "Starting new version: ${latest_version_path}"
nohup python3 "${latest_version_path}" --port 8888 --force > server_v7.log 2>&1 &

echo "Phoenix deployment completed."
