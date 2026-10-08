#!/bin/zsh
set -euo pipefail
cd /Volumes/AI-Brain/n8n-Automation/forexagents
export PATH="/Users/ozitzaferi/.hermes/tools/node-26.7.0-darwin-arm64/bin:/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/usr/bin:/bin:/usr/sbin:/sbin"
mkdir -p logs
exec >> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-scanner.out.log 2>> /Volumes/AI-Brain/n8n-Automation/forexagents/logs/launchd-scanner.err.log
printf '%s starting ForexAgents autonomous scanner\n' "$(date -Iseconds)"
exec /usr/local/bin/python3 /Volumes/AI-Brain/n8n-Automation/forexagents/scripts/autonomous_scanner.py --telegram --interval-seconds 900
