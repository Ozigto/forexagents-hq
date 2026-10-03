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

## Important

No auto-trading. Telegram posts are research/signals only. NOVA is Boss, Ozzi is final human decision maker.
