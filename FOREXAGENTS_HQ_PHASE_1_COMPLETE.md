# ForexAgents HQ — Phase 1 Complete

Version: 1.0  
Owner: Ozzi  
Boss / Portfolio Manager: NOVA  
Status: Company foundation complete. Live trading room not yet connected.

---

## 1. What ForexAgents HQ Is

ForexAgents HQ is a professional NOVA-led forex research company built around Ozzi's personal trading process.

It is not a generic signal bot.
It is not an auto-trader.
It is not a random group of AI personalities.

It is a structured trading desk whose job is to search for rare, high-quality forex setups, challenge them, reject weak ones, and present only serious candidates to Ozzi.

North Star:

```text
One A+ forex entry per week.
Maybe a second if the first loses.
Most scans should end in WAIT.
```

---

## 2. Phase 1 Result

Phase 1 created the company foundation.

This means the company now has:

- a mission
- rules
- hierarchy
- departments
- agents
- skill boundaries
- evidence standards
- debate protocol
- Telegram room design
- case lifecycle design
- NOVA veto rules
- roadmap

Phase 1 does **not** mean the live Telegram/n8n/market-data system is fully connected yet.

---

## 3. Company Authority

```text
Ozzi = final human authority
NOVA = Boss / Portfolio Manager
Agents = research departments
n8n = workflow/control layer
RPC = company brain/runtime
Telegram = trading room
Lyra = memory, review, replay, scoring
RULES.yaml = constitution
```

No agent can override Ozzi.
No agent can override `RULES.yaml`.
No LLM can override deterministic vetoes.

---

## 4. Company Constitution

The rules are stored in:

```text
RULES.yaml
FOREXAGENTS_HQ_COMPANY_MANUAL.md
CONVERSATION_PROTOCOL.md
AGENT_SKILL_MATRIX.md
```

Core rules:

1. Research/signals only. No auto-trading in v1.
2. Ozzi gives final approval.
3. Only approved markets are watched.
4. Only Ozzi's two patterns are allowed.
5. Risk must respect 1 lot and $150–$200 rules.
6. Most charts should be rejected or watched.
7. A+ candidates must be rare.
8. WAIT is success when evidence is weak.
9. Every serious opportunity must become a case file.
10. Replay/shadow mode must happen before trust.

---

## 5. Trading Scope Locked

### Markets

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

### Patterns

```text
1. 4H 21 EMA Break + Retest
2. 1H / 4H Pin Bar Rejection
```

### Time

Timezone:

```text
Europe/Athens
```

Watch windows:

```text
05:00–11:00 Athens
18:00–23:00 Athens
```

### Risk

```text
Lot size: 1 lot
Normal risk: about $150
A+ maximum risk: $200
Weekly target: $1,000–$1,500
Weekly shots: 5–7 quality shots
```

---

## 6. Company Departments

### Evidence Builders

These agents build facts and evidence.

| Agent | Department |
|---|---|
| 📊 Atlas | Market Data |
| 🧭 Aurora | Weekly/Daily/4H Bias |
| 🕒 Selena | Session Timing |
| 📐 Maya | Structure |
| 🔎 Iris | Pattern Detection |
| 📰 Echo | News Risk |

### Reasoning and Decision Team

These agents debate and stress-test verified evidence.

| Agent | Department |
|---|---|
| 🐂 Titan | Bull Researcher |
| 🐻 Vega | Bear Researcher |
| 🧠 Sage | Research Manager |
| 🧑‍💼 Ava | Trader |
| ⚔️ Blaze | Aggressive Risk |
| 🛡 Gaia | Conservative Risk |
| ⚖️ Balance | Neutral Risk |
| 👑 NOVA | Boss / Portfolio Manager |

### Operations

| Agent | Department |
|---|---|
| 📲 Rhea | Telegram Manager |
| 🧪 Lyra | Journal / Testing / Replay |

---

## 7. Skill Boundary Rule

ForexAgents does not give every agent every tool.

Rule:

```text
Code establishes measurable facts.
Agents reason about those facts.
```

Important boundary:

```text
Titan and Vega do not fetch candles.
Titan and Vega debate Atlas/Aurora/Selena/Maya/Iris/Echo evidence.
```

This prevents agents from debating different realities.

---

## 8. Operating Flow

Professional flow:

```text
Telegram / n8n command
↓
Evidence Snapshot
↓
Data Quality Officer
↓
Pattern Gate
↓
Specialist Reports
↓
Cross-questioning
↓
Titan vs Vega Debate
↓
Sage Arbitration
↓
Ava Trade Plan
↓
Risk Board
↓
NOVA Final Decision
↓
Ozzi Approval
↓
Lyra / Review
```

If data is bad:

```text
WAIT — data quality failed.
```

If no approved pattern exists:

```text
WAIT — no valid setup detected.
```

No fake debate over empty charts.

---

## 9. Evidence Rules

Every important claim must be marked as:

- FACT
- CALCULATION
- INTERPRETATION
- UNKNOWN

Unsupported claims lose authority.

A screenshot can start analysis, but screenshot-only evidence cannot create a final A+ approval.

For A+ candidate status, the company eventually needs structured evidence:

- candles
- timestamps
- EMA21
- structure levels
- invalidation
- risk calculation
- news risk

---

## 10. A+ Candidate Definition

`A+ CANDIDATE` is rare.

It requires:

- one of Ozzi's two approved patterns
- strong evidence
- no deterministic veto
- completed candle support
- clear invalidation
- risk fits $150–$200
- no dangerous news window
- acceptable session timing
- not late/chased
- debate issues resolved or clearly weighted by Sage
- NOVA approval before Ozzi sees it as a candidate

If anything important is missing:

```text
WATCH / WAIT / REJECTED
```

Not A+.

---

## 11. Telegram Room Design

Telegram should be readable, not spammy.

Default output levels:

1. Short status while analysis runs.
2. Selected disagreements worth seeing.
3. One clean NOVA decision card.

Full debate should be available by command:

```text
/full CASE_ID
```

Suggested commands:

```text
/status
/scan
/watch
/case CASE_ID
/debate CASE_ID
/full CASE_ID
/journal
/performance
/rules
/pause_company
/resume_company
/no_new_candidates
```

---

## 12. n8n Role

n8n is the workflow/control layer.

It should handle:

- Telegram trigger
- schedule/watch windows
- command routing
- RPC calls
- Telegram posting
- workflow visibility

n8n should not become the messy agent brain.

The company brain stays in RPC/Python where we can test, version, and audit it.

Current workflow file:

```text
workflows/forexagents_hq_scan_and_debate.n8n.json
```

Current RPC endpoint:

```text
POST http://127.0.0.1:18765/debate/setup
```

---

## 13. Case Lifecycle

Every opportunity should become a case.

Lifecycle:

```text
DETECTED
→ WATCH
→ CONFIRMING
→ DEBATE
→ A+ CANDIDATE
→ OZZI DECISION
→ ACTIVE
→ INVALIDATED / CLOSED
→ REVIEW
```

Case folder design:

```text
cases/EURUSD-20261003-001/
  case.json
  snapshot.json
  gate.json
  analyst_reports.json
  debate.json
  nova_decision.md
  ozzi_decision.md
  outcome.json
  review.md
  events.json
```

Nothing important should live only in Telegram.

---

## 14. What Is Already Built

### Documents

```text
FOREXAGENTS_HQ_COMPANY_MANUAL.md
FOREXAGENTS_COMPANY_SPEC.md
FOREXAGENTS_HQ_PHASE_1_COMPLETE.md
AGENT_ROSTER.md
AGENT_SKILL_MATRIX.md
CONVERSATION_PROTOCOL.md
RULES.yaml
FLOW.yaml
ARCHITECTURE_DECISION_001.md
TELEGRAM_SETUP.md
```

### Agents

```text
agents/*.yaml
prompts/*.md
```

### Workflow

```text
workflows/forexagents_hq_scan_and_debate.n8n.json
```

### Local brain

```text
rpc_server.py
run_rpc_server.sh
```

### Deterministic foundation started

```text
skills/core/case_id.py
skills/core/evidence_schema.py
skills/core/case_store.py
skills/market_data/ema.py
skills/market_data/freshness.py
skills/patterns/pinbar_rejection.py
skills/risk/one_lot_risk.py
```

### Tests

The project has automated tests covering:

- case store
- case IDs
- EMA21
- 1-lot risk
- pin-bar detection
- evidence snapshot
- data quality
- evidence gate
- RPC case creation
- debate transcript persistence
- NOVA decision card persistence

---

## 15. What Is Not Live Yet

Not done yet:

- Telegram group live connection
- n8n workflow imported and activated
- Telegram bot credential in n8n
- group chat ID / allowlist
- real market candle data feed
- economic calendar/news feed
- replay lab
- shadow mode
- agent performance scoring

These are later phases.

---

## 16. Phase 1 Completion Definition

Phase 1 is complete because the company now has:

- clear mission
- clear chain of command
- complete agent roster
- company constitution
- agent skill boundaries
- operating flow
- debate protocol
- evidence rules
- Telegram room design
- case lifecycle design
- n8n/RPC architecture
- no-auto-trading boundary
- professional roadmap

Phase 1 does not require live Telegram or market data.

---

## 17. Next Phase Starts Here

The next phase should not add more agents.

The next phase is:

```text
Make the company operational.
```

Correct next build order:

1. Finish `/case` summary output.
2. Import n8n workflow manually and run Manual Test Trigger.
3. Restore/configure Telegram credential safely.
4. Add Telegram group chat ID and allowlist.
5. Enable `/scan`, `/status`, `/case`, `/full`.
6. Add real market data provider.
7. Add news calendar provider.
8. Build replay lab.
9. Run shadow mode before trusting live alerts.

---

## 18. Final Phase 1 Verdict

```text
ForexAgents HQ company foundation: COMPLETE.
Live company deployment: NOT COMPLETE YET.
```

The company is now designed seriously enough to build from.

From this point forward, new work should follow the company manual, not random ideas.

NOVA must continue to challenge weak designs and protect the professional standard.
