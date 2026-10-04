# ForexAgents HQ Control Center

This is the single source of truth for recovering, checking, and operating ForexAgents HQ.

For the whole company identity, departments, agent roles, and trading-desk discipline, read:

```text
FOREXAGENTS_COMPANY_BIBLE.md
```

If chat memory/context breaks, start here first.

## 1. Mission

ForexAgents HQ is NOVA's read-only forex trading-desk system for Ozzi.

Goal: find high-quality setups using Ozzi's exact rules and alert Telegram only when something meaningful appears.

V1 is **research/signals only**. It does **not** auto-trade.

## 2. Current live architecture

```text
MT5 local closed candles
→ scripts/autonomous_scanner.py
→ MT5 health check + Athens watch windows + market-hours guard
→ rpc_server.py /debate/setup
→ deterministic evidence gate
→ agent debate only if evidence passes
→ Telegram alert/status through @ozzi_nova_bot
```

Live services on the Mac:

- `com.ozzi.forexagents.rpc` — local RPC trading brain.
- `com.ozzi.forexagents.scanner` — autonomous scanner every 15 minutes.
- `scripts/telegram_polling_bridge.py` — Telegram command/natural-message bridge.

## 3. User-facing Telegram behavior

Ozzi does not need to remember technical commands.

In the Telegram group he can type natural messages:

```text
NOVA are you here?
anything new?
how is the team going?
team?
status
what should I do now?
next?
```

The bot replies with the team/readiness report.

For `what should I do now?` / `next?`, the bot gives one simple next action instead of a full technical report.

Reliable group commands, even if Telegram privacy blocks normal text:

```text
/status
/team
/next
/nova your question
/voice your question
```

Telegram architecture decision: use one bot only, `@ozzi_nova_bot`, as the ForexAgents + NOVA company door. Do not run a second Telegram poller/gateway against the same bot token at the same time, because two pollers can consume each other's updates.

If Telegram BotFather privacy mode is ON, the bot may only receive slash commands in the group. To make normal group talking work, disable privacy for `@ozzi_nova_bot` in BotFather. The bridge is ready to route normal text to NOVA once Telegram delivers it.

Voice replies: use `/voice your question`. NOVA answers by text and sends a local Kokoro voice audio reply.

Automatic Telegram messages:

- Daily company-awake status report.
- MT5 health warning if live market data is broken.
- Professional trade setup alert only for meaningful setup statuses.

Silent by design:

- `WAIT` results.
- Closed-market weekends.
- Weak/no-pattern scans.

## 4. Trading scope

Watchlist:

- `EUR/USD`
- `GBP/USD`
- `USD/JPY`
- `USD/CHF`
- `AUD/USD`
- `NZD/USD`
- `USD/CAD`
- `XAU/USD`

Timeframes:

- `1H`
- `4H`

That means the scanner checks 16 groups each cycle.

Allowed setup patterns only:

1. 4H 21 EMA Break + Retest.
2. 1H / 4H Pin Bar Rejection.

If neither setup is plausible, the correct result is `WAIT`.

## 5. Timing rules

Timezone: Europe/Athens.

Watch windows:

- 05:00–11:00 Athens time.
- 18:00–23:00 Athens time.

Market-hours guard:

- Saturday: skip.
- Sunday: skip.
- Friday after 23:00 Athens: skip.

`--force` can override this only for testing.

## 6. Risk/safety rules

- V1 never places trades.
- MT5 bridge is read-only.
- Telegram alerts are signal/research only.
- Ozzi makes the final trading decision.
- 1 lot default.
- Risk target: $150–$200 depending on setup quality.
- Weekly target: $1,000–$1,500.
- Weekly shots: 5–7 quality shots.

Professional Telegram alert must tell Ozzi to verify entry, stop, target, spread, and news before acting.

## 7. Important files

Project root:

```text
/Volumes/AI-Brain/n8n-Automation/forexagents
```

Public GitHub mirror:

```text
/Volumes/AI-Brain/n8n-Automation/github/forexagents-hq
https://github.com/Ozigto/forexagents-hq
```

Core files:

- `FOREXAGENTS_COMPANY_BIBLE.md` — whole company master record: mission, agents, departments, rules, and desk behavior.
- `FOREXAGENTS_CONTROL_CENTER.md` — this file.
- `scripts/autonomous_scanner.py` — autonomous scanner, health/status/readiness/Telegram alerts.
- `scripts/telegram_polling_bridge.py` — Telegram bridge, `/status`, `/scan`, natural phrases.
- `rpc_server.py` — evidence gate and agent decision endpoint.
- `skills/market_data/mt5_files.py` — MT5 candle CSV parser.
- `mt5/NovaForexBridgeV2.mq5` — read-only MT5 exporter.
- `MT5_AUTONOMOUS_SETUP.md` — MT5 compile/attach guide.
- `launchd/com.ozzi.forexagents.rpc.plist` — RPC LaunchAgent.
- `launchd/com.ozzi.forexagents.scanner.plist` — scanner LaunchAgent.
- `launchd/run_forexagents_rpc.zsh` — RPC wrapper.
- `launchd/run_forexagents_scanner.zsh` — scanner wrapper.

Local-only runtime files, never push:

- `.env.telegram.local`
- `.telegram_bridge_state.json`
- `.autonomous_scanner_state.json`
- `cases/`
- `logs/`

## 8. MT5 paths

MT5 app folder:

```text
/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5
```

Expert Advisor source copied into MT5:

```text
/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts/NovaForexBridgeV2.mq5
```

MT5 exported candle file:

```text
/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Files/nova_forex_candles.csv
```

MT5 exported market file:

```text
/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Files/nova_forex_market.csv
```

Broker symbols may have suffixes like `EURUSD.` and `XAUUSD.`. The bridge/parser supports suffixes.

## 9. Daily operation checklist

Ozzi should not need to run this daily, but these are the real dependencies:

- Mac awake/logged in.
- `/Volumes/AI-Brain` mounted.
- Internet connected.
- MT5 open.
- `NovaForexBridgeV2` attached/running in MT5.
- LaunchAgents running.

If any of those break, the system may stop watching.

## 10. One-command readiness check

From project root:

```bash
python3 scripts/autonomous_scanner.py --readiness
```

Expected healthy result:

```text
Ready for live test: YES
RPC brain: OK
MT5 health: OK
MT5 groups: 16/16
Scanner service: OK
Auto-trading: OFF
```

Exit codes:

- `0` = ready.
- `2` = blocked/not ready.

## 11. Manual checks

Run these from:

```bash
cd /Volumes/AI-Brain/n8n-Automation/forexagents
```

RPC health:

```bash
curl -s http://127.0.0.1:18765/health
```

Scanner one-shot normal mode:

```bash
python3 scripts/autonomous_scanner.py --once
```

Scanner forced test mode:

```bash
python3 scripts/autonomous_scanner.py --once --force
```

Readiness:

```bash
python3 scripts/autonomous_scanner.py --readiness
```

Tests:

```bash
python3 -m unittest discover -s tests -v
```

Compile check:

```bash
python3 -m py_compile scripts/autonomous_scanner.py scripts/telegram_polling_bridge.py skills/market_data/mt5_files.py rpc_server.py
```

Launch services:

```bash
launchctl list | grep 'com.ozzi.forexagents'
```

Process check:

```bash
ps -axo pid,etime,command | grep -E 'scripts/autonomous_scanner.py|rpc_server.py|telegram_polling_bridge.py' | grep -v grep
```

## 12. Restart commands

Restart RPC LaunchAgent:

```bash
launchctl kickstart -k gui/$UID/com.ozzi.forexagents.rpc
```

Restart scanner LaunchAgent:

```bash
launchctl kickstart -k gui/$UID/com.ozzi.forexagents.scanner
```

Restart Telegram polling bridge manually:

```bash
pkill -f 'telegram_polling_bridge.py' || true
python3 scripts/telegram_polling_bridge.py
```

Use a tracked background process in Hermes when starting the Telegram bridge from NOVA.

## 13. Logs

RPC logs:

```text
logs/launchd-rpc.out.log
logs/launchd-rpc.err.log
```

Scanner logs:

```text
logs/launchd-scanner.out.log
logs/launchd-scanner.err.log
```

Telegram bridge logs if manually redirected:

```text
logs/telegram-bridge.out.log
logs/telegram-bridge.err.log
```

## 14. Recovery after a broken chat/context

Do this in order:

1. Read this file.
2. Run readiness:

   ```bash
   cd /Volumes/AI-Brain/n8n-Automation/forexagents
   python3 scripts/autonomous_scanner.py --readiness
   ```

3. Check git:

   ```bash
   cd /Volumes/AI-Brain/n8n-Automation/github/forexagents-hq
   git log -5 --oneline
   git status --short
   ```

4. If something is broken, inspect the specific service/log instead of guessing.
5. Never expose Telegram tokens or local state files.

## 15. Recovery priorities

If ForexAgents is not working, fix in this order:

1. External drive mounted.
2. MT5 open + EA attached.
3. MT5 candle CSV has 16 groups.
4. RPC brain online.
5. Scanner LaunchAgent online.
6. Telegram bridge online.
7. Telegram group replies.

Do not start changing strategy logic until the operating system/data pipeline is healthy.

## 16. Git / publish safety

Before pushing:

- Run full tests.
- Run compile checks.
- Run secret scan.
- Do not push `.env*`, state files, cases, logs, tokens, credentials, screenshots, or generated runtime files.

GitHub latest important commits when this file was created:

```text
85de1a7 Understand natural Telegram team status phrases
3de55a6 Add live readiness report command
7b9e282 Professional trade alert card format
bf90b84 Add daily ForexAgents status report
5b48b45 Add MT5 health alerts to autonomous scanner
```

## 17. Not finished yet

- First real Monday/open-market live verification.
- First real setup alert observed from live data.
- News/calendar risk filter.
- Replay/shadow performance learning.
- Full n8n dashboard/control-layer decision.
- Broker execution, intentionally not built for V1.

## 18. Final rule

If the system is healthy and there is no valid setup, do nothing. Silence is professional.

The company should protect Ozzi from bad trades, not create noise.
