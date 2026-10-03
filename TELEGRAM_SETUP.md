# Telegram Setup — Existing NOVA Bot

Decision: use Ozzi's existing Telegram bot for ForexAgents.

Bot handle: `@ozzi_nova_bot`

Group idea: `ForexAgents HQ`

The bot will post as agent personas, not as separate Telegram bots.

## Agent display names

| Agent ID | Display | Role |
|---|---|---|
| `market_data` | 📊 Atlas | Market Data Analyst |
| `htf_bias` | 🧭 Aurora | HTF Bias Analyst |
| `session_timing` | 🕒 Selena | Session Timing Analyst |
| `structure` | 📐 Maya | Structure Analyst |
| `pattern` | 🔎 Iris | Pattern Analyst |
| `news` | 📰 Echo | News Risk Analyst |
| `bull` | 🐂 Titan | Bull Researcher |
| `bear` | 🐻 Vega | Bear Researcher |
| `research_manager` | 🧠 Sage | Research Manager |
| `trader` | 🧑‍💼 Ava | Trader |
| `aggressive_risk` | ⚔️ Blaze | Aggressive Risk Agent |
| `conservative_risk` | 🛡 Gaia | Conservative Risk Agent |
| `neutral_risk` | ⚖️ Balance | Neutral Risk Agent |
| `nova_boss` | 👑 NOVA | Boss / Portfolio Manager |
| `telegram_manager` | 📲 Rhea | Telegram Manager |
| `journal_tester` | 🧪 Lyra | Journal / Testing Agent |


## Required Telegram group setup

1. Create or open the Telegram group where Ozzi wants the team.
2. Add `@ozzi_nova_bot` to the group.
3. Make sure the bot can read messages in the group.
4. Send one message in the group, for example: `/status`.
5. Gateway/logs must reveal the group chat id so we can allowlist it.

## n8n Phase 2 status

Verified on this machine:

```text
RPC brain: running on http://127.0.0.1:18765
n8n UI: running on http://127.0.0.1:5678
n8n database: /Volumes/AI-Brain/n8n-Automation/data/.n8n/database.sqlite
workflow imported: forexagents-hq-rpc-debate-telegram
workflow active: false
manual workflow test: passed
Telegram credentials in n8n: 0
Telegram trigger/send nodes: disabled
```

The workflow file is:

```text
/Volumes/AI-Brain/n8n-Automation/forexagents/workflows/forexagents_hq_scan_and_debate.n8n.json
```

## Safe Telegram activation order

Do not enable the Telegram trigger or Telegram send node until all items below are done.

1. Ozzi opens n8n:

```text
http://127.0.0.1:5678
```

2. Create a Telegram credential inside n8n for `@ozzi_nova_bot`.

Important: the bot token must be typed or pasted only into n8n's credential screen by Ozzi. It must not be pasted into chat, committed to GitHub, or written in project docs.

3. Create/open the `ForexAgents HQ` Telegram group and add `@ozzi_nova_bot`.

4. Get the Telegram group chat ID safely.

5. Add an allowlist so only Ozzi / the intended group can command ForexAgents.

6. Enable `/status` first, not `/scan`.

7. Test `/status`.

8. Then enable `/scan` only after `/status` is stable.

## Current blocker

```text
Blocked on Telegram credential + group chat ID.
```

No credential exists in n8n yet.

## Important

No auto-trading. Telegram posts are research/signals only. NOVA is Boss, Ozzi is final human decision maker.
