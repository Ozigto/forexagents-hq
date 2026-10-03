# ForexAgents HQ

NOVA-led forex agent company for Ozzi, implemented in n8n-first style.

## Mission

Find one A+ forex entry per week, maybe a second chance if the first loses, using only Ozzi's rules:

1. 4H 21 EMA break + retest.
2. 1H / 4H pin bar rejection at meaningful levels.

NOVA is the Boss / Portfolio Manager. Ozzi is the final human decision maker.

## Current build status

This folder contains the company blueprint and n8n workflow skeleton. It does not auto-trade.
Next step is connecting Telegram bot/group credentials and choosing the candle/news data source.

## Files

- `FOREXAGENTS_COMPANY_SPEC.md` — full design.
- `RULES.yaml` — Ozzi's trading rules in machine-readable form.
- `AGENT_ROSTER.md` — professional team roster.
- `FLOW.yaml` — TradingAgents-inspired workflow graph.
- `agents/*.yaml` — each agent's job, tools, inputs, outputs, and hard limits.
- `prompts/*.md` — prompts for n8n AI nodes.
- `templates/telegram_messages.md` — group message formats.
- `workflows/forexagents_hq_scan_and_debate.n8n.json` — n8n import skeleton.


## Telegram bot decision

Use existing bot: `@ozzi_nova_bot`. The agents appear as named personas in one group, not separate bots.
