#!/bin/zsh
set -euo pipefail
cd /Volumes/AI-Brain/n8n-Automation/forexagents
mkdir -p logs
exec >> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-rpc.out.log 2>> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-rpc.err.log
printf '%s starting ForexAgents RPC\n' "$(date -Iseconds)"
exec /usr/local/bin/python3 /Volumes/AI-Brain/n8n-Automation/forexagents/rpc_server.py
