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
🐻 Vega -> 🔎 Hunter:
Is the pin bar confirmed after close or still forming?

🔎 Hunter -> 🐻 Vega:
Still forming. We need candle close; current wick can disappear.
```

```text
🛡 Guard -> 🧑‍💼 Ace:
Your stop is 28 pips. Does that fit Ozzi's $150-$200 risk with 1 lot?

🧑‍💼 Ace -> 🛡 Guard:
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
