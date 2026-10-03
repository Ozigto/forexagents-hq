# ForexAgents HQ — Finished Company Brief

## One-line summary

ForexAgents HQ is a NOVA-led professional forex agent company for Ozzi, built around n8n + Telegram + a local RPC agent brain. It is not a generic signal bot. It is designed to find one A+ setup per week using Ozzi's exact trading process.

---

## Current repo/folder

This is local/private, not on GitHub yet.

```text
/Volumes/AI-Brain/n8n-Automation/forexagents
```

Existing n8n workspace:

```text
/Volumes/AI-Brain/n8n-Automation
```

Existing Telegram bot planned for use:

```text
@ozzi_nova_bot
```

---

## Core architecture

Chosen architecture:

```text
Telegram Group
  ↓
n8n Telegram Trigger / Schedule
  ↓
n8n HTTP Request
  ↓
Local ForexAgents RPC Server
  ↓
Agent functions + tools + journal
  ↓
n8n posts visible agent messages to Telegram
```

### Why this architecture

- n8n handles Telegram, schedules, command routing, and visible workflow control.
- Local RPC server owns the skilled agent brain, agent conversation, rules, journal, and testing.
- Telegram group is the visible trading room.
- NOVA is Boss / Portfolio Manager.
- Ozzi is final human decision maker.

This is inspired by `TauricResearch/TradingAgents`, specifically their workflow style:

```text
Parallel Analysts → Bull/Bear Debate → Research Manager → Trader → Risk Debate → Portfolio Manager
```

ForexAgents adapts that into:

```text
Telegram/Ozzi → n8n → Analyst Team → Bull/Bear Debate → Trader → Risk Debate → NOVA Boss → Telegram + Journal
```

---

## Current built files

Created files include:

```text
README.md
FOREXAGENTS_COMPANY_SPEC.md
RULES.yaml
FLOW.yaml
AGENT_ROSTER.md
TELEGRAM_SETUP.md
CONVERSATION_PROTOCOL.md
ARCHITECTURE_DECISION_001.md
FOREXAGENTS_FINISHED_COMPANY_BRIEF.md
rpc_server.py
run_rpc_server.sh
sample_debate_payload.json
workflows/forexagents_hq_scan_and_debate.n8n.json
agents/*.yaml
prompts/*.md
templates/telegram_messages.md
journal/*.json
```

---

## Agent roster

The company currently has 16 named agents/personas:

1. 📊 **Atlas** — Market Data Analyst  
2. 🧭 **Orion** — Weekly/Daily/4H Bias Analyst  
3. 🕒 **Chronos** — Session Timing Analyst  
4. 📐 **Mason** — Structure Analyst  
5. 🔎 **Hunter** — Pattern Analyst  
6. 📰 **Echo** — News Risk Analyst  
7. 🐂 **Titan** — Bull Researcher  
8. 🐻 **Vega** — Bear Researcher  
9. 🧠 **Sage** — Research Manager  
10. 🧑‍💼 **Ace** — Trader  
11. ⚔️ **Blitz** — Aggressive Risk Agent  
12. 🛡 **Guard** — Conservative Risk Agent  
13. ⚖️ **Balance** — Neutral Risk Agent  
14. 👑 **NOVA** — Boss / Portfolio Manager  
15. 📲 **Relay** — Telegram Manager  
16. 🧪 **Ledger** — Journal / Testing Agent  

Each agent has:

- YAML definition
- prompt file
- role
- tools list
- required output fields
- hard limits
- Telegram display identity

---

## Trading scope

Markets:

```text
EUR/USD
GBP/USD
USD/JPY
USD/CHF
AUD/USD
NZD/USD
USD/CAD
XAU/USD
```

Important rule:

> Any allowed pair can work if the pattern is clean. Do not bias toward screenshot examples.

---

## Trading strategies allowed

Only two patterns are allowed.

### Pattern 1 — 4H 21 EMA Break + Retest

Long setup:

- 4H timeframe.
- Price breaks above important structure/resistance.
- Price is above/reclaiming/supported by 21 EMA.
- Price retests broken level and/or 21 EMA area.
- Bullish confirmation after retest.
- Stop below retest low/invalidation.

Short setup:

- 4H timeframe.
- Price breaks below important structure/support.
- Price is below/losing/rejecting 21 EMA.
- Price retests broken level and/or 21 EMA area.
- Bearish confirmation after retest.
- Stop above retest high/invalidation.

### Pattern 2 — 1H / 4H Pin Bar Rejection

Buy:

- Long lower wick rejects meaningful support/zone/EMA.
- Close shows bullish reaction.
- Stop below wick low.

Sell:

- Long upper wick rejects meaningful resistance/zone/EMA.
- Close shows bearish reaction.
- Stop above wick high.

Reject weak pin bars:

- middle of nowhere
- inside chop
- before dangerous news

---

## Ozzi's operating rules

Timezone:

```text
Europe/Athens
```

Watch windows:

```text
05:00–11:00 Athens time
18:00–23:00 Athens time
```

Management/holding:

```text
19:00–00:00 depending on trade movement
```

Risk model:

```text
Lot size: always 1 lot
Risk: $150–$200 depending on setup quality
Weekly target: $1,000–$1,500
Weekly quality shots: around 5–7
Goal: one A+ entry per week
Second chance: maybe one more if first loses
```

No auto-trading in v1. Research/signals only.

---

## Conversation protocol

The company must produce real conversations, not fake scripted chatter.

Required flow:

```text
1. Analyst reports
2. Agents ask each other questions
3. Bull/Bear debate
4. Research Manager decides
5. Trader proposes
6. Risk team challenges
7. NOVA Boss final decision
```

Cross-questioning is required when uncertainty exists.

Example:

```text
🐻 Vega -> 🔎 Hunter:
Is the pin bar confirmed after close or still forming?

🔎 Hunter -> 🐻 Vega:
Still forming. We need candle close; current wick can disappear.
```

Final NOVA outputs only:

```text
A+ CANDIDATE — waiting for Ozzi approval
WATCH
WAIT
REJECTED
INVALIDATED
```

---

## RPC server status

RPC server file:

```text
rpc_server.py
```

Run script:

```text
run_rpc_server.sh
```

Default local port:

```text
18765
```

Endpoints:

```text
GET  /health
GET  /rules
POST /debate/setup
```

The first attempt on port `8765` failed because the port was already in use. It was changed to `18765`.

Verified:

```text
/health OK
/rules OK
/debate/setup OK with controlled 3-agent smoke test
```

Sample test returned 3 real agent messages from:

- 📊 Atlas
- 🧭 Orion
- 🕒 Chronos

They correctly identified missing data, avoided fake certainty, and asked other agents for confirmation details.

This proves real controlled reasoning works, but full dynamic back-and-forth is not complete yet.

---

## Current quality assessment

| Component | Status | Grade |
|---|---:|---:|
| Project structure | Built | A |
| Agent roster | Built | A |
| Trading rules | Locked | A |
| n8n skeleton | Built | B |
| RPC `/health` | Verified | A |
| RPC `/rules` | Verified | A |
| RPC `/debate/setup` | Verified with controlled input | B |
| Agent questioning | Started | C+ |
| Full dynamic back-and-forth | Not finished | C |
| Journal save | Basic JSON save works | C |
| Agent scoring | Not started | — |
| Telegram live group | Blocked by token/group setup | Blocked |
| Live candle data | Not started | — |
| Broker integration | Not started | — |

---

## Telegram status

Decision:

```text
Use existing @ozzi_nova_bot
```

Telegram group target:

```text
ForexAgents HQ
```

Intended behavior:

- One bot posts as all named agent personas.
- All agents visible in one group.
- Ozzi can watch and challenge the team.
- NOVA acts as Boss.

Current blocker:

- Telegram bot token was not found in checked `.env` files.
- Telegram previously worked, so token may have been removed or stored elsewhere.
- Need to restore/confirm token safely without printing it in chat/logs.
- Need Telegram group chat ID and allowlist.

Do not expose tokens in chat.

---

## What should be built next

### Step 1 — Finish RPC debate engine

Improve `/debate/setup` so it supports full staged conversation:

- all analyst reports
- agent-to-agent questions
- target-agent answers
- Bull/Bear debate
- Research Manager decision
- Trader proposal
- Risk debate
- NOVA final decision

### Step 2 — Connect n8n to RPC

n8n should call:

```text
POST http://127.0.0.1:18765/debate/setup
```

Then post each agent message into Telegram.

### Step 3 — Restore Telegram live group

- Confirm/store bot token safely.
- Add `@ozzi_nova_bot` to group.
- Get group chat ID.
- Allowlist group.
- Test `/status` and `/scan`.

### Step 4 — Add journal/scoring

Ledger should track:

- every candidate
- every rejected setup
- every missed setup
- agent accuracy
- Boss decisions
- weekly performance

### Step 5 — Research and choose data source

Do not rush.

Options to evaluate:

- OANDA API
- MT5
- other forex candle providers
- temporary free prototype data

Live market data comes after the Telegram/RPC pilot works.

---

## Professional build discipline

NOVA must challenge Ozzi and the system when wrong.

Rules:

- Research first before tool/data/architecture decisions.
- Do not agree blindly with Ozzi or another AI.
- Reject weak setups.
- Prefer staged prototypes and verified output.
- No auto-trading in v1.
- Every important claim must be backed by docs, source, tests, or real output.

---

## Short status to send someone

ForexAgents HQ is built as a local/private n8n + RPC prototype. The company structure, 16 named agents, rules, workflow, conversation protocol, n8n skeleton, and RPC server are created. RPC health/rules/debate endpoints were verified on port 18765 with a controlled 3-agent test. Telegram live group is not connected yet because the bot token/group allowlist still needs to be restored safely. Next work is full dynamic agent debate, n8n-to-RPC connection, Telegram group setup, and journal/scoring before live market data.
