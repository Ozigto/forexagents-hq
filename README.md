# ForexAgents HQ

NOVA-led forex agent company for Ozzi.

Start here if anything is forgotten or broken:

➡️ **[`FOREXAGENTS_CONTROL_CENTER.md`](FOREXAGENTS_CONTROL_CENTER.md)**

That file is the single source of truth for:

- What is built.
- How the system works.
- What commands recover it.
- What services should be running.
- What must never be pushed.
- What remains unfinished.

## Mission

Find high-quality forex setups using only Ozzi's rules:

1. 4H 21 EMA break + retest.
2. 1H / 4H pin bar rejection at meaningful levels.

NOVA is the Boss / Portfolio Manager. Ozzi is the final human decision maker.

V1 is **research/signals only** and does **not** auto-trade.

## Current live path

```text
MT5 local candles
→ autonomous scanner
→ RPC evidence gate / debate
→ Telegram status, health, and setup alerts
```

Telegram supports natural status messages like:

```text
anything new?
how is the team going?
team?
```

## Key files

- `FOREXAGENTS_CONTROL_CENTER.md` — main recovery/control file.
- `scripts/autonomous_scanner.py` — scanner, health, status, readiness, Telegram alerts.
- `scripts/telegram_polling_bridge.py` — Telegram commands and natural phrases.
- `rpc_server.py` — evidence gate and agent decision endpoint.
- `mt5/NovaForexBridgeV2.mq5` — read-only MT5 exporter.
- `MT5_AUTONOMOUS_SETUP.md` — MT5 setup guide.
- `RULES.yaml` — Ozzi's trading rules in machine-readable form.
- `AGENT_ROSTER.md` — professional team roster.
- `FOREXAGENTS_HQ_OPERATING_PLAYBOOK.md` — operating playbook.
