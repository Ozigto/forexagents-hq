# ForexAgents HQ — Company Manual

Version: 0.1  
Owner: Ozzi  
Boss / Portfolio Manager: NOVA  
Mode: Research and signals only. No auto-trading.

---

## 1. Purpose

ForexAgents HQ is a professional NOVA-led forex research company built around Ozzi's own trading process.

The company exists to find a very small number of high-quality trading opportunities, not to produce constant signals.

The target is:

```text
One A+ forex entry per week.
Maybe a second only if the first loses.
```

ForexAgents must support Ozzi's judgment. It does not replace Ozzi.

---

## 2. North Star

ForexAgents HQ must behave like a disciplined trading desk:

```text
Facts first.
Evidence second.
Debate third.
NOVA decision last.
Ozzi final approval always.
```

The system must avoid:

- fake confidence
- random AI opinions
- endless agent chatter
- forced trades
- unsupported claims
- signals without invalidation
- trading outside Ozzi's process

Most scans should end with:

```text
WAIT
```

A+ candidates must be rare.

---

## 3. Non-Negotiable Company Rules

1. NOVA is Boss / Portfolio Manager.
2. Ozzi is final human authority.
3. No auto-trading in v1.
4. ForexAgents only works on Ozzi's approved setups.
5. The company must challenge weak ideas, including Ozzi's, respectfully.
6. No agent can override `RULES.yaml`.
7. No agent can invent price, candle, news, or risk facts.
8. No setup can become `A+ CANDIDATE` if a deterministic veto is active.
9. Telegram must be readable; it is a trading room, not spam.
10. Every real candidate must become a case file.


---

## 3A. Rule Versioning

`RULES.yaml` is the company constitution.

Every case must record:

- `RULES.yaml` version
- manual version
- workflow version
- prompt/agent version
- deterministic skill version when available

Changing rules creates a new version. Old cases must not be silently re-judged under new rules.

If a rule changes, Ledger must preserve which version produced the original decision.

---

## 4. Trading Scope

### Allowed markets

ForexAgents starts with major forex pairs plus gold:

- EUR/USD
- GBP/USD
- USD/JPY
- USD/CHF
- AUD/USD
- NZD/USD
- USD/CAD
- XAU/USD

The pair name is not the edge. The pattern quality is the edge.

### Approved strategies

Only two strategies are allowed unless Ozzi changes the constitution:

1. **4H 21 EMA Break + Retest**
2. **1H / 4H Pin Bar Rejection**

No random strategies. No pattern drift.

### Timing

Timezone: Europe/Athens.

Primary watch windows:

- 05:00–11:00 Athens time
- 18:00–23:00 Athens time

Management may continue toward 23:00 / midnight depending on the trade.

### Risk style

- Lot size: 1 lot unless Ozzi changes the rule.
- Normal risk: about $150.
- A+ risk ceiling: $200.
- Weekly target: $1,000–$1,500.
- Weekly shots: 5–7 quality shots, not forced daily trades.


### A+ candidate definition

`A+ CANDIDATE` is rare. It requires all of the following:

- approved pattern only: 4H 21 EMA break/retest or 1H/4H pin-bar rejection
- evidence grade is strong or clearly improving from mixed to strong
- no deterministic veto is active
- completed candle evidence supports the setup
- clear invalidation exists
- 1-lot risk fits Ozzi's $150-$200 rule
- entry is not late or chased
- session timing is acceptable or explicitly justified
- no dangerous news window
- Titan/Vega disagreement is resolved or Sage clearly weights the evidence
- NOVA agrees it is worth Ozzi's attention

If any requirement is missing, output `WATCH`, `WAIT`, or `REJECTED`, not `A+ CANDIDATE`.

### WAIT is success

`WAIT` is not failure. `WAIT` means capital protected.

ForexAgents should be proud to wait when evidence is weak, timing is bad, or the setup is not one of Ozzi's two patterns.

---

## 5. Company Structure

```text
                    OZZI
              Final human authority
                       │
                    NOVA
              Portfolio Manager
                       │
          ┌────────────┴────────────┐
          │                         │
      Risk Board                 Ace
 Blitz / Guard / Balance        Trader
          │                         │
          └────────── Sage ─────────┘
                  Research Manager
                       │
                 Titan ↔ Vega
                  Bull   Bear
                       │
    ┌──────────────────┼──────────────────┐
 Atlas  Orion  Chronos  Mason  Hunter  Echo
    └──────────────────┼──────────────────┘
                       │
              Evidence + Pattern Engine
                       │
             Validated Market Snapshot

Relay = communications
Ledger = records, evaluation, replay
n8n = scheduling and orchestration
RPC = company brain/runtime
Telegram = trading room
RULES.yaml = company constitution
```

---

## 6. Department Roles

### Evidence Builders

These agents build and validate the shared evidence snapshot.

| Agent | Role |
|---|---|
| 📊 Atlas | Market Data Analyst |
| 🧭 Orion | Weekly/Daily/4H Bias Analyst |
| 🕒 Chronos | Session Timing Analyst |
| 📐 Mason | Structure Analyst |
| 🔎 Hunter | Pattern Analyst |
| 📰 Echo | News Risk Analyst |

### Debate and Decision Team

These agents reason from the verified evidence. They must not fetch their own separate market data.

| Agent | Role |
|---|---|
| 🐂 Titan | Bull Researcher |
| 🐻 Vega | Bear Researcher |
| 🧠 Sage | Research Manager |
| 🧑‍💼 Ace | Trader |
| ⚔️ Blitz | Aggressive Risk Agent |
| 🛡 Guard | Conservative Risk Agent |
| ⚖️ Balance | Neutral Risk Agent |
| 👑 NOVA | Boss / Portfolio Manager |

### Operations Team

| Agent | Role |
|---|---|
| 📲 Relay | Telegram Manager |
| 🧪 Ledger | Journal / Testing / Replay Agent |

---

## 7. Skill Boundaries

Core rule:

```text
Code establishes measurable facts.
Agents reason about those facts.
```

Do not give every agent every tool.

Titan and Vega must not independently download candles. They receive verified evidence from Atlas, Orion, Chronos, Mason, Hunter, and Echo. Otherwise the company could debate two different realities.

### Three skill layers

```text
SHARED CORE SKILLS
────────────────────
case state
evidence schema
timestamps
audit logging
company rules

        ↓

SPECIALIST SKILLS
────────────────────
Atlas   → market data
Orion   → bias
Chronos → sessions
Mason   → structure
Hunter  → patterns
Echo    → news

        ↓

REASONING SKILLS
────────────────────
Titan/Vega → challenge
Sage       → arbitrate
Ace        → construct plan
Risk Board → stress test
NOVA       → final classification
```

---

## 8. Deterministic Skills vs AI Skills

Some skills must not use an LLM.

Deterministic Python functions should handle:

- EMA21 calculation
- candle mathematics
- wick/body ratios
- ATR/volatility
- spread checks
- stale-data checks
- timezone conversion
- session detection
- 1-lot dollar risk
- reward:risk
- case IDs
- replay no-future-leak checks

AI agents should interpret those measured facts.

Example:

```text
Python:
H4 close       = 1.17482
EMA21          = 1.17391
break level    = 1.17420
retest low     = 1.17417
distance EMA   = 9.1 pips
news in        = 143 minutes

                ↓

Mason:
"Structure break confirmed."

Hunter:
"Break/retest requirements satisfied."

Vega:
"Retest is shallow and London momentum is weakening."

Titan:
"Higher-timeframe alignment supports continuation."

                ↓

Sage evaluates disagreement.
```

---

## 9. Evidence Contract

Every important claim must be marked as one of:

- FACT
- CALCULATION
- INTERPRETATION
- UNKNOWN

Every important price claim must include:

- symbol
- timeframe
- candle timestamp
- source
- level/price
- condition being claimed

Unsupported claims lose authority automatically.

Example of bad output:

```text
Mason: Structure is bullish.
```

Example of professional output:

```text
Mason:
FACT: XAU/USD 4H candle closed above 2342.50 resistance at 2026-10-03 08:00 Athens.
CALCULATION: Retest low is 2342.10, 0.40 below break level.
INTERPRETATION: Structure break is confirmed but retest quality is still mixed.
UNKNOWN: Need next closed 4H candle to confirm continuation.
```


### Screenshot evidence limit

Screenshots can start analysis, but screenshots alone should not create final A+ approval.

Screenshot-only evidence may produce:

- `WATCH`
- `WAIT`
- `REJECTED`

For `A+ CANDIDATE`, the company should eventually require structured candle data or a validated evidence snapshot containing prices, timestamps, candle closes, EMA values, invalidation, and risk calculations.

---

## 10. Data Quality Officer

Before agents debate, deterministic code must check:

- data freshness
- missing candles
- duplicate candles
- correct timezone conversion
- symbol mapping
- spread
- news timestamps
- completed candle availability

Bad input produces:

```text
WAIT — data quality failed.
```

Not AI analysis.

---

## 11. Pattern Engine

The pattern engine checks whether either approved setup is plausible before any expensive or noisy agent debate.

### Gate rule

If neither setup is plausible:

```text
WAIT — no valid setup detected.
```

No Titan/Vega debate. No six-agent discussion over an empty chart.

### Approved pattern checks

1. **4H 21 EMA Break + Retest**
   - 4H timeframe
   - completed candle context
   - 21 EMA value
   - structure break
   - retest zone
   - confirmation/rejection
   - invalidation

2. **1H / 4H Pin Bar Rejection**
   - 1H or 4H timeframe
   - meaningful location
   - wick/body ratio
   - close reaction
   - invalidation beyond wick

AI may judge context after code measures the facts.

---

## 12. Candidate Lifecycle

Every opportunity should move through a case lifecycle:

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

A 4H retest can develop across multiple scans. The company must not forget previous state.

Every opportunity gets a case ID, for example:

```text
EURUSD-20261003-001
```

The case file attaches:

- market snapshot
- detected pattern
- analyst reports
- Bull/Bear claims
- Sage conclusion
- Ace proposal
- risk debate
- NOVA status
- Ozzi decision
- subsequent market outcome


### Case file format

Every real opportunity should eventually be stored as a folder or structured record:

```text
cases/
  EURUSD-20261003-001/
    case.json
    snapshot.json
    evidence.json
    gate.json
    analyst_reports.json
    debate.json
    nova_decision.md
    ozzi_decision.md
    outcome.json
    review.md
```

Minimum case fields:

- case ID
- symbol
- pattern candidate
- status
- timestamps
- rule version
- evidence snapshot ID
- NOVA status
- Ozzi decision
- final outcome when known

Nothing important should live only in Telegram chat.

---

## 13. Debate Protocol

ForexAgents debate must be controlled, not a random group chat.

Required flow:

```text
Market snapshot
→ Analyst reports
→ Cross-questioning
→ Titan vs Vega debate
→ Sage arbitration
→ Ace trade plan
→ Risk Board stress test
→ NOVA decision
```

Rules:

- An agent cannot agree without explaining why.
- Bull and Bear must name the strongest argument against their own position.
- Sage must identify unresolved disagreement instead of forcing consensus.
- Risk agents must independently evaluate Ace's proposal.
- NOVA must reject if the debate is unclear.

---

## 14. NOVA Veto Engine

NOVA has final classification, but deterministic vetoes override persuasive debate.

These block `A+ CANDIDATE`:

- stale data
- dangerous news inside forbidden window
- missing completed candles
- invalid or missing stop
- risk above $200
- wrong pattern
- wrong timeframe
- unsupported structure
- poor evidence
- setup outside rules without explicit downgrade

NOVA final statuses:

- `A+ CANDIDATE — waiting for Ozzi approval`
- `WATCH`
- `WAIT`
- `REJECTED`
- `INVALIDATED`

---

## 15. Telegram Trading Room

Telegram should be readable.

Default Telegram output should have three levels:

1. Short agent status while analysis runs.
2. Selected disagreements worth seeing.
3. One clean NOVA decision card.

The full internal debate should be available by command:

```text
/full CASE_ID
```

Relay handles presentation only. Relay cannot influence trading conclusions.

Suggested commands:

- `/status`
- `/scan`
- `/watch`
- `/case CASE_ID`
- `/debate CASE_ID`
- `/full CASE_ID`
- `/journal`
- `/performance`
- `/rules`
- `/pause_company`
- `/resume_company`
- `/no_new_candidates`

---

## 16. NOVA Decision Card

Final output should be clean and actionable:

```text
👑 NOVA DECISION

Case: EURUSD-20261003-001
Status: WAIT / WATCH / A+ CANDIDATE / REJECTED / INVALIDATED
Pair:
Pattern:
Evidence Grade: strong / mixed / insufficient
Main Reason:
Invalidation:
Risk:
News Risk:
Next Check Time:
Ozzi Action:
```

No hype. No guaranteed profit language.

---

## 17. Ledger and Review

Ledger tracks more than profit.

Each case should eventually record:

- pattern type
- pair
- session
- direction
- analyst disagreements
- MAE
- MFE
- achieved R
- whether original thesis remained valid
- which vetoes helped or hurt
- Ozzi decision
- final outcome

Separate decision quality from trade outcome.

A good decision can lose. A bad decision can win. Ledger must learn the difference.

---

## 18. Replay Laboratory

Replay mode is required before trusting live signals.

The company must receive historical candle snapshots one timestamp at a time. Agents must never see future candles.

Replay milestones:

1. 50 historical setups
2. 100 historical setups
3. Hundreds of cases

Replay tests the whole company, not only an indicator.

---

## 19. Shadow Mode

Before live trust, ForexAgents should run live with zero execution.

Shadow mode records:

- timestamped scan
- evidence snapshot
- company decision
- Ozzi decision if any
- later outcome

This prevents hindsight from making results look better than they were.

---

## 20. Operational Health

NOVA should know the difference between:

```text
No setup.
```

and:

```text
EUR/USD feed stopped 37 minutes ago.
```

Health checks should cover:

- n8n
- RPC server
- market data feed
- news feed
- Telegram
- storage
- journal writing
- replay database

Failures should fail closed:

```text
WAIT — system not clean.
```

---

## 21. Emergency Controls

ForexAgents must support emergency company controls:

- `PAUSE COMPANY`
- `RESUME COMPANY`
- `NO NEW CANDIDATES`

If data, AI, Telegram, or RPC behavior is unsafe, the company pauses or refuses new candidates.

---

## 22. Audit Log

Every decision must record:

- rule version
- model/provider
- prompt version
- agent version
- data snapshot ID
- case ID
- timestamp
- workflow version
- deterministic vetoes
- final NOVA status

When behavior changes later, we must know why.

---

## 23. Roadmap

### Phase 1 — Company foundation

- Company manual
- Agent roster
- Skill matrix
- Rules constitution
- Conversation protocol
- n8n workflow skeleton
- RPC server foundation

### Phase 2 — Deterministic foundation

- Evidence snapshot schema
- Data quality officer
- Pattern engine
- Case lifecycle
- NOVA veto engine

### Phase 3 — Telegram pilot

- Telegram group connection
- `/scan`
- `/status`
- `/full`
- NOVA decision card
- Journal case files

### Phase 4 — Replay and shadow mode

- Historical replay
- No-future-leak enforcement
- Shadow mode live logging
- Agent performance review after enough cases

### Phase 5 — Data integrations

- Market candles
- News calendar
- Spread data
- Broker/paper-trading data if approved later

No auto-trading in v1.

---

## 24. What Is Not Allowed

ForexAgents is not allowed to:

- auto-trade in v1
- invent price data
- force a trade every day
- debate empty charts
- let every agent fetch separate data
- approve a trade without stop/invalidation
- approve risk above $200
- ignore dangerous news
- override Ozzi's final decision
- rewrite case history after outcome
- give agents arbitrary reputation scores before enough cases exist

---

## 25. Current Principle

Do not make ForexAgents bigger until ForexAgents is measurable.

The next level comes from:

- evidence integrity
- controlled disagreement
- persistent cases
- deterministic gates
- replay testing
- auditability
- learning from outcomes

Those pieces turn a collection of AI personas into an engineered research operation.
