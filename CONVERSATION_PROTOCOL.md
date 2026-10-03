# ForexAgents Conversation Protocol

The agents must talk to each other like a professional trading desk, not produce isolated reports.

## Required flow

1. Analyst reports.
2. Cross-questioning.
3. Bull/Bear debate.
4. Research Manager decision.
5. Trader proposal.
6. Risk debate.
7. NOVA Boss final decision.

## Cross-questioning rule

Every debate run must include at least two agent-to-agent questions when there is uncertainty.

Examples:

```text
🐻 Vega -> 🔎 Iris:
Is the pin bar confirmed after close or still forming?

🔎 Iris -> 🐻 Vega:
Still forming. We need candle close; current wick can disappear.
```

```text
🛡 Gaia -> 🧑‍💼 Ava:
Your stop is 28 pips. Does that fit Ozzi's $150-$200 risk with 1 lot?

🧑‍💼 Ava -> 🛡 Gaia:
No, not as written. Proposal must tighten entry or be rejected.
```

## No mistake rule

Agents must challenge each other before NOVA sees a final candidate.

- Pattern Agent must reject unconfirmed patterns.
- News Agent must block dangerous news timing.
- Conservative Risk must try to reject every trade.
- NOVA must reject if the debate is unclear.

## Final output options

NOVA Boss can only output:

- `A+ CANDIDATE — waiting for Ozzi approval`
- `WATCH`
- `WAIT`
- `REJECTED`
- `INVALIDATED`

No auto-trading.

## Professional evidence rules

ForexAgents must behave like a professional trading desk, not like entertainment bots.

### Deterministic pre-check gate

Before any LLM/agent debate starts, deterministic code must check whether either of Ozzi's two allowed strategies is even plausible:

1. 4H 21 EMA break + retest.
2. 1H/4H pin bar rejection.

If neither pattern is plausible, stop immediately with `WAIT` and do not spend LLM calls debating an empty chart.

### Shared evidence layer

Every run must start from one shared, timestamped market snapshot. Agents must not fetch or invent different facts.

Required evidence fields when available:

- symbol
- timeframe
- data timestamp
- completed candle timestamp
- current price
- completed candles used
- 21 EMA value
- structure level(s)
- break condition
- retest condition
- rejection/pin-bar condition
- session window
- spread
- upcoming news risk
- invalidation level

No evidence means no trade. Missing evidence must be stated plainly.

### Claim evidence requirement

Every important claim must carry evidence. Example: Maya cannot say "bullish structure" alone. Maya must include timeframe, level, candle time, break condition, retest condition, and invalidation.

Sage must reject unsupported claims.

### Anti-groupthink rules

- An agent cannot agree without explaining why.
- Bull and Bear must identify the strongest argument against their own position.
- Risk agents must independently evaluate Ava's proposal before seeing each other's conclusions.
- NOVA must not approve because the debate sounds confident; evidence decides.

### Deterministic NOVA vetoes

These conditions block `A+ CANDIDATE` regardless of LLM persuasion:

- dangerous news inside forbidden window
- stale data
- missing completed candles
- invalid or missing stop
- risk above Ozzi's $200 maximum
- wrong pattern
- poor/unsupported evidence
- setup outside rules without explicit downgrade

### Journal chain

Every completed run should preserve this chain:

```text
market snapshot
→ detected pattern
→ analyst reports
→ Bull/Bear claims
→ Sage conclusion
→ Ava proposal
→ risk debate
→ NOVA status
→ Ozzi decision
→ subsequent market outcome
```

### Agent scoring

Do not give agents arbitrary reputation scores early. Score only after enough outcomes exist. Later, track whether agents overcall, reject too much, prevent losses, or identify quality setups.

### Telegram visibility levels

Do not dump every internal message by default. Telegram should have:

1. Short agent status while analysis runs.
2. Selected disagreements worth seeing.
3. One clean NOVA decision card.

A `/full` command can expose the complete debate for inspection.

### Replay mode before trust

Before trusting live signals, replay historical candle snapshots one timestamp at a time. Agents must never see future candles. Test 50, then 100, then hundreds of historical setups before live confidence.

