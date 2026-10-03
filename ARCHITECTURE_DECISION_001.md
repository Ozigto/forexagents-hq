# Architecture Decision 001 — n8n + Local RPC Agent Server

## Decision

Use **n8n as the workflow/Telegram control layer**, and add a **local ForexAgents RPC server** as the professional agent brain.

## Why

n8n is strong for:

- Telegram integration and sending messages.
- Scheduling watch windows.
- HTTP Request nodes to call APIs/services.
- Code nodes for light transformations.
- AI Agent nodes for workflow AI.

But Ozzi wants a serious professional team where each agent has skills, tools, rules, tests, journal history, and can communicate in a TradingAgents-inspired workflow. That should not become a messy canvas of duplicated prompts.

## Architecture

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

## Roles

### n8n owns

- Telegram command trigger.
- Scheduled scans.
- Posting agent messages into the group.
- Calling RPC endpoints.
- Simple workflow visibility.

### RPC server owns

- Agent skills and prompts.
- Candle/EMA/pattern/news/risk tools.
- TradingAgents-style debate logic.
- Journal/testing records.
- NOVA Boss final decision logic.

## Why not n8n-only

n8n-only is easier at first, but weaker for long-term professionalism:

- agent logic gets duplicated across nodes,
- testing is harder,
- version control is harder,
- agent-to-agent state gets messy,
- journal/scoring is harder to keep strict.

## Build rule

Start with a **small real-conversation RPC pilot**, not fake company chatter.

Endpoints:

1. `/health`
2. `/rules`
3. `/debate/setup`
4. later: `/scan/live`

`/debate/setup` receives one controlled setup: pair, timeframe, screenshot notes or candle snapshot, and optional Ozzi notes. The agents must run a real TradingAgents-style conversation:

1. Analysts report independently.
2. Agents ask each other questions.
3. Bull/Bear debate the evidence.
4. Trader proposes only if research is strong.
5. Risk team challenges the proposal.
6. NOVA Boss makes the final call.

The first pilot can use controlled input, but the agent messages must be genuine reasoning over that input — not hardcoded fake messages.

Only after this works do we connect live candle/news data.

## Safety

No auto-trading. Research/signals only. NOVA Boss must challenge weak setups. Ozzi is final human decision maker.
