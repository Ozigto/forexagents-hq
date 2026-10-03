# ForexAgents HQ — Operating Playbook

Version: 1.0  
Owner: Ozzi  
Boss / Portfolio Manager: NOVA  
Status: Phase 1 company operating model

---

## 1. Purpose

This playbook explains how ForexAgents HQ should operate day to day.

It turns the company manual into a working routine:

```text
When do we scan?
Who speaks first?
When do we stop?
What does Ozzi see?
What becomes a case?
What is forbidden?
```

ForexAgents HQ should behave like a disciplined trading desk, not a noisy chatroom.

---

## 2. Daily Company Rhythm

The company works around Ozzi's Athens-time watch windows.

Primary watch windows:

```text
05:00–11:00 Athens
18:00–23:00 Athens
```

A normal operating day has four parts:

```text
1. Pre-window readiness
2. Active scan window
3. Candidate review
4. End-of-window journal
```

---

## 3. Pre-Window Readiness

Before an active window, the company should check:

- RPC brain is reachable
- n8n workflow is active
- Telegram Relay is connected
- market data provider is healthy
- news provider is healthy
- rules version is loaded
- no emergency pause is active

If any critical piece is broken:

```text
Status: COMPANY NOT READY
Action: WAIT
```

No agent debate should run from bad infrastructure.

---

## 4. Scan Trigger Types

Scans can be triggered by:

### Manual trigger

Ozzi sends:

```text
/scan EURUSD
/scan XAUUSD
```

### Scheduled trigger

n8n runs scans during allowed windows.

### Watchlist trigger

A previous case is in WATCH status and needs a new evidence snapshot.

### Replay trigger

Ledger feeds historical snapshots during replay mode.

---

## 5. Scan Order

Every scan follows this order:

```text
1. Create or update case
2. Build shared evidence snapshot
3. Run Data Quality Officer checks
4. Run Pattern Gate
5. If no setup: WAIT
6. If plausible setup: specialist reports
7. Controlled challenge/debate
8. Sage arbitration
9. Ava trade plan only if approved
10. Risk Board review
11. NOVA final decision
12. Relay formats output
13. Ledger records everything
```

Important:

```text
No evidence = no debate.
No pattern = WAIT.
Bad data = WAIT.
```

---

## 6. What Ozzi Should See

Ozzi should not see every internal token or noisy agent message.

Telegram should show three layers.

### Layer 1 — Status

Example:

```text
ForexAgents HQ scanning XAU/USD H4...
Evidence snapshot building.
```

### Layer 2 — Important disagreement

Example:

```text
Vega challenges Titan:
Maya has not confirmed a completed H4 break above resistance.
Titan must answer from the shared evidence snapshot.
```

### Layer 3 — NOVA decision card

Example:

```text
👑 NOVA DECISION
Status: WATCH
Pair: XAU/USD
Pattern: 4H EMA21 Break + Retest
Evidence Grade: Mixed
Reason: Retest visible but candle close confirmation missing.
Ozzi Action: Wait for completed H4 close.
```

Full debate only appears if Ozzi asks:

```text
/full CASE_ID
```

---

## 7. Case Status Meanings

### DETECTED

A market condition might matter, but it is early.

### WATCH

A valid idea exists but lacks final confirmation.

### CONFIRMING

A setup is close; the company is waiting for a specific candle or level.

### DEBATE

Evidence is strong enough for controlled agent challenge.

### A+ CANDIDATE

Rare status. All core gates pass and NOVA approves Ozzi review.

### OZZI DECISION

Ozzi must personally decide whether to act.

### ACTIVE

Ozzi entered or is managing the trade manually.

### INVALIDATED

Setup failed before entry or trade thesis broke.

### CLOSED

Trade is finished.

### REVIEW

Ledger reviews the case after outcome.

---

## 8. WAIT Is a Professional Output

WAIT is not failure.

WAIT means:

```text
The company protected Ozzi from weak evidence, bad timing, or unclear structure.
```

Good reasons to WAIT:

- no approved pattern
- stale data
- missing candle
- no completed 4H confirmation
- dangerous news
- risk too high
- stop location unclear
- R:R too weak
- setup is late/chased
- disagreement unresolved

A serious company should produce many WAIT outputs.

---

## 9. A+ Candidate Standard

A+ Candidate requires:

- approved market
- approved pattern
- completed candle evidence
- clean structure
- clear invalidation
- 1-lot risk inside Ozzi's rule
- no high-impact news conflict
- session timing acceptable
- risk board not blocking
- Sage resolves key disagreements
- NOVA approves

If one critical condition fails:

```text
Not A+.
```

---

## 10. Department Speaking Order

Normal order:

```text
Atlas → Aurora → Selena → Maya → Iris → Echo
↓
Titan ↔ Vega
↓
Sage
↓
Ava
↓
Blaze / Gaia / Balance
↓
NOVA
↓
Rhea
↓
Lyra
```

Agents should not skip the evidence team.

Ava should not create a trade plan until Sage allows it.

Risk Board should not review before a concrete plan exists.

---

## 11. Controlled Challenge Rules

Agents can challenge each other only with specific claims.

Good challenge:

```text
Vega → Titan:
You call this a valid bullish retest. Maya reports no completed H4 close above resistance. Which completed candle confirms the break?
```

Bad challenge:

```text
I disagree because it feels weak.
```

Required challenge structure:

```text
Agent challenged
Specific claim
Evidence conflict
Question
Requested proof
```

---

## 12. Evidence Language

Every serious output should use:

```text
FACT
CALCULATION
INTERPRETATION
UNKNOWN
```

Examples:

```text
FACT: H4 candle closed at 1.17482.
CALCULATION: Close is 9.1 pips above EMA21.
INTERPRETATION: Retest is shallow but valid.
UNKNOWN: News source unavailable.
```

Unsupported claims lose authority.

---

## 13. Emergency Controls

NOVA or Ozzi can pause the company.

Suggested Telegram controls:

```text
/pause_company
/resume_company
/no_new_candidates
/status
/rules
```

Emergency pause reasons:

- bot behaving strangely
- wrong data feed
- repeated stale data
- news provider broken
- Telegram posting spam
- unexpected agent outputs
- Ozzi says stop

When paused:

```text
No new candidates.
No alerts except status.
```

---

## 14. End-of-Window Journal

At the end of each watch window, Lyra should summarize:

- scans run
- cases created
- WAIT decisions
- WATCH cases still open
- A+ candidates, if any
- rejected opportunities
- data problems
- agent disagreements worth reviewing

No scoring agents from too little data.

---

## 15. Weekly Review

Once per week, the company should review:

- best rejected setup
- worst accepted setup
- strongest WAIT decision
- missed opportunities
- news warnings
- pattern quality
- whether Ozzi's weekly target was reached
- whether discipline was maintained

The goal is not more trades.
The goal is better decisions.

---

## 16. What n8n Does

n8n is the workflow operator.

It should:

- listen to Telegram commands
- run scheduled scans
- call RPC
- send status messages
- send NOVA decision cards
- route `/case` and `/full`
- handle pauses/resumes

n8n should not:

- invent analysis
- calculate trading math manually
- store secrets in workflow text
- bypass RPC gates
- approve trades

---

## 17. What Telegram Does

Telegram is the trading room.

It should show:

- short status
- selected disagreements
- decision cards
- case summaries
- manual commands

Telegram should not become:

- endless agent roleplay
- noisy internal logs
- secret storage
- trade execution screen

---

## 18. What RPC Does

RPC is the local company brain.

It should own:

- rules loading
- evidence gate
- agent order
- controlled debate
- case creation
- transcript writing
- NOVA decision card
- deterministic vetoes

RPC should be testable and auditable.

---

## 19. What Ledger / Lyra Does

Lyra records the truth.

Lyra should:

- keep original evidence
- store decisions
- store debate
- store Ozzi's decision later
- store outcome later
- support replay mode
- score agents only after enough cases

Lyra must not rewrite history to make agents look better.

---

## 20. Definition of “Company Finished”

The company foundation is finished when these exist:

- company manual
- agent department manual
- operating playbook
- rules constitution
- conversation protocol
- skill matrix
- phase completion document
- architecture decision
- Telegram/n8n role definition
- roadmap for live deployment

That is Phase 1.

Live deployment is Phase 2.

---

## 21. Phase 2 Starts Only After This

Phase 2 begins with operational wiring:

```text
1. n8n import and manual trigger test
2. Telegram credential setup
3. group chat ID and allowlist
4. /scan command
5. /case command
6. /full command
7. market data provider
8. news provider
9. replay mode
10. shadow mode
```

No more company-design ambiguity should remain before Phase 2.

---

## 22. Final Operating Principle

ForexAgents HQ exists to protect Ozzi from bad trades and highlight rare excellent ones.

The company must prefer:

```text
WAIT over weak action
Evidence over opinion
Discipline over excitement
Replay over blind trust
Ozzi's rules over agent creativity
```

This is how ForexAgents HQ should operate.
