#!/bin/zsh
set -euo pipefail
cd /Volumes/AI-Brain/n8n-Automation/forexagents
mkdir -p logs
exec >> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-scanner.out.log 2>> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-scanner.err.log
printf '%s starting ForexAgents autonomous scanner\n' "$(date -Iseconds)"
exec /usr/local/bin/python3 /Volumes/AI-Brain/n8n-Automation/forexagents/scripts/autonomous_scanner.py --telegram --interval-seconds 900
