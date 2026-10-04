# MT5 Autonomous Scanner Setup

ForexAgents HQ can run autonomously from local MT5 candles, but MT5 must first export closed 1H/4H candles.

## What is built

- Project bridge source: `mt5/NovaForexBridgeV2.mq5`
- Copied into MT5 Experts folder:
  - `/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts/NovaForexBridgeV2.mq5`
- Expected MT5 export file:
  - `/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Files/nova_forex_candles.csv`
- Autonomous scanner:
  - `scripts/autonomous_scanner.py`
- MT5 file parser:
  - `skills/market_data/mt5_files.py`

## Safety

`NovaForexBridgeV2.mq5` is read-only:

- no order sending
- no position closing
- no broker actions
- exports market ticks and closed H1/H4 candles only

V1 remains research/signals only. No auto-trading.

## Manual MT5 step required

Headless MetaEditor compile was attempted but did not produce `NovaForexBridgeV2.ex5`, so compile/attach from MT5:

1. Open **MetaTrader 5**.
2. Open **MetaEditor**.
3. In Experts, open:
   - `NovaForexBridgeV2.mq5`
4. Click **Compile**.
5. Return to MT5.
6. Open any chart.
7. Drag **NovaForexBridgeV2** from Navigator → Expert Advisors onto the chart.
8. Allow algo/expert execution if MT5 asks.
   - This EA is read-only and does not trade.
9. Wait 30–60 seconds.
10. Confirm this file appears:
   - `MQL5/Files/nova_forex_candles.csv`

## Verification command

After the file appears, NOVA can run:

```bash
cd /Volumes/AI-Brain/n8n-Automation/forexagents
python3 scripts/autonomous_scanner.py --once --force
```

Expected when MT5 export is working:

- `scanned` greater than `0`
- `errors` reduced or empty
- alerts only if evidence passes the deterministic gates

If no valid setup is found, the scanner stays quiet / WAIT. That is correct.

## Operational mode

Once verified, run autonomous scanner during Ozzi's Athens watch windows:

- 05:00–11:00 Athens
- 18:00–23:00 Athens

Command:

```bash
cd /Volumes/AI-Brain/n8n-Automation/forexagents
python3 scripts/autonomous_scanner.py
```

The scanner reads MT5 candles, calls the RPC brain, lets agents debate only when the evidence gate passes, and alerts Telegram only for alert-worthy cases.
