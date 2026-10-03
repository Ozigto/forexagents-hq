# ForexAgents HQ — Roadmap

Version: 1.0  
Owner: Ozzi  
Boss / Portfolio Manager: NOVA  
Status: Phase roadmap for professional rollout

---

## 1. Purpose

This roadmap prevents ForexAgents HQ from becoming messy.

It defines exactly what gets built, in what order, and what must not be rushed.

The company standard is:

```text
Foundation first.
Operational wiring second.
Live data third.
Replay before trust.
Shadow before live reliance.
No auto-trading in v1.
```

---

## 2. Current Status

ForexAgents HQ has completed its professional company foundation.

Completed:

- company manual
- agent department manual
- operating playbook
- phase 1 closeout
- rules constitution
- skill matrix
- conversation protocol
- architecture decision
- n8n workflow skeleton
- local RPC brain foundation
- case file foundation
- balanced agent roster

Not completed yet:

- n8n imported/running live
- Telegram group connected
- real market data feed
- real economic calendar feed
- replay lab
- shadow mode
- long-term performance learning

---

## 3. Phase 1 — Company Foundation

Status:

```text
COMPLETE
```

Goal:

```text
Define ForexAgents HQ as a professional trading research company.
```

Deliverables:

- `FOREXAGENTS_HQ_COMPANY_MANUAL.md`
- `FOREXAGENTS_HQ_AGENT_DEPARTMENT_MANUAL.md`
- `FOREXAGENTS_HQ_OPERATING_PLAYBOOK.md`
- `FOREXAGENTS_HQ_PHASE_1_COMPLETE.md`
- `AGENT_ROSTER.md`
- `AGENT_SKILL_MATRIX.md`
- `RULES.yaml`
- `CONVERSATION_PROTOCOL.md`
- `ARCHITECTURE_DECISION_001.md`

Completion rule:

```text
The company has a clear mission, roles, rules, operating rhythm, and roadmap.
```

Phase 1 does not require live Telegram or live data.

---

## 4. Phase 2 — Operational Command Center

Status:

```text
NEXT
```

Goal:

```text
Make the company controllable through n8n and Telegram.
```

Build order:

1. Confirm RPC server health.
2. Import n8n workflow.
3. Run n8n Manual Test Trigger.
4. Add safe Telegram credential in n8n.
5. Add Telegram group chat ID.
6. Add Telegram allowlist.
7. Enable `/status`.
8. Enable `/scan`.
9. Enable `/case`.
10. Enable `/full`.
11. Add `/pause_company` and `/resume_company`.

Acceptance criteria:

```text
Ozzi can send a Telegram command.
n8n routes it to RPC.
RPC returns a structured result.
Relay posts a clean Telegram message.
No secrets are exposed.
No trade execution exists.
```

Do not move to Phase 3 until Phase 2 works manually and safely.

---

## 5. Phase 3 — Live Evidence Feed

Status:

```text
NOT STARTED
```

Goal:

```text
Give the company reliable market and news evidence.
```

Build order:

1. Choose market data source.
2. Normalize approved symbols.
3. Fetch completed candles only.
4. Calculate EMA21 deterministically.
5. Add spread checks.
6. Add data freshness checks.
7. Add missing/duplicate candle checks.
8. Add economic calendar provider.
9. Add news proximity vetoes.
10. Store every evidence snapshot in case folder.

Acceptance criteria:

```text
All agents use the same timestamped evidence snapshot.
Bad data returns WAIT.
No agent invents prices.
No screenshot-only setup becomes A+.
```

---

## 6. Phase 4 — Replay Lab

Status:

```text
NOT STARTED
```

Goal:

```text
Test the company on historical snapshots without future leaks.
```

Build order:

1. Create replay case format.
2. Feed historical snapshots one timestamp at a time.
3. Block future candles.
4. Run 50 replay cases.
5. Review results.
6. Run 100 replay cases.
7. Review mistakes.
8. Run hundreds later.

Acceptance criteria:

```text
ForexAgents can process old setups as if they were live.
Agents cannot see future candles.
NOVA decisions are recorded before outcomes.
Ledger compares decisions against later candles.
```

No live trust before replay.

---

## 7. Phase 5 — Shadow Mode

Status:

```text
NOT STARTED
```

Goal:

```text
Run ForexAgents live without acting on its signals yet.
```

Build order:

1. Run during Ozzi's watch windows.
2. Record all WAIT/WATCH/A+ decisions.
3. Do not rely on alerts yet.
4. Compare to Ozzi's own manual judgment.
5. Review missed/wrong cases weekly.
6. Tune gates only from evidence.

Acceptance criteria:

```text
System runs live for a meaningful period.
Outputs are stable, readable, and not spammy.
NOVA rejects weak setups often.
Ozzi trusts the process, not blindly the output.
```

---

## 8. Phase 6 — Performance Learning

Status:

```text
NOT STARTED
```

Goal:

```text
Improve the company from outcomes without rewriting history.
```

Track:

- pattern type
- pair
- session
- direction
- evidence grade
- disagreements
- vetoes
- Ozzi decision
- outcome
- MFE
- MAE
- achieved R
- whether thesis remained valid

Agent review examples:

- Did Iris overcall patterns?
- Did Maya mark structure accurately?
- Did Echo catch dangerous news?
- Did Vega reject too many winners?
- Did Titan ignore weak evidence?
- Did Gaia protect capital well?
- Did NOVA classify correctly?

Acceptance criteria:

```text
Agents are evaluated from recorded cases, not opinions.
No arbitrary reputation scores before enough data.
Lessons are evidence-based.
```

---

## 9. Phase 7 — Optional Broker Integration

Status:

```text
FUTURE ONLY
```

Goal:

```text
Maybe support broker/account awareness later.
```

Important:

```text
No auto-trading in v1.
No broker execution until Ozzi explicitly approves a future phase.
```

Possible future broker features:

- account balance awareness
- open-position awareness
- manual trade logging
- FTMO rule reminders
- drawdown tracking

Forbidden for now:

- automatic entries
- automatic exits
- hidden order placement
- credential exposure

---

## 10. Phase Gates

ForexAgents HQ cannot skip phases.

### To enter Phase 2

Must have:

- company foundation complete
- official roster
- operating playbook
- rules constitution

Status:

```text
PASSED
```

### To enter Phase 3

Must have:

- n8n imported
- Telegram commands safe
- `/status`, `/scan`, `/case` working
- secrets protected

Status:

```text
NOT PASSED
```

### To enter Phase 4

Must have:

- structured evidence snapshots
- live data normalization
- deterministic gates working from real data

Status:

```text
NOT PASSED
```

### To enter Phase 5

Must have:

- replay lab results
- stable decision cards
- no major evidence integrity problems

Status:

```text
NOT PASSED
```

### To enter Phase 6

Must have:

- enough recorded cases
- outcomes recorded honestly
- review process working

Status:

```text
NOT PASSED
```

---

## 11. What Not To Do

Do not:

- add more agents before measurement
- connect broker execution now
- trust live signals before replay
- let agents fetch different data
- dump every message to Telegram
- chase every chart
- turn WAIT into failure
- modify risk rules casually
- store secrets in repo or workflow text
- allow auto-trading

---

## 12. Next Immediate Move

The next build move after company finish is Phase 2 step 1:

```text
Confirm RPC health and prepare n8n import/manual test.
```

But only after Ozzi says:

```text
Start Phase 2.
```

Until then, the company design package is the priority.

---

## 13. Final Roadmap Verdict

```text
Phase 1 — Company Foundation: COMPLETE
Phase 2 — Operational Command Center: NEXT
Phase 3 — Live Evidence Feed: NOT STARTED
Phase 4 — Replay Lab: NOT STARTED
Phase 5 — Shadow Mode: NOT STARTED
Phase 6 — Performance Learning: NOT STARTED
Phase 7 — Broker Integration: FUTURE ONLY
```

ForexAgents HQ should move slowly, professionally, and only with verified evidence.
