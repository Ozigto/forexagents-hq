# ForexAgents Company Spec

## North Star

Build a professional NOVA-led forex desk that searches only Ozzi's proven setups, debates them transparently in Telegram, and produces a very small number of high-quality candidate entries.

This is inspired by TauricResearch/TradingAgents' communication structure:

```text
Parallel Analysts -> Bull/Bear Debate -> Research Manager -> Trader -> Risk Debate -> Portfolio Manager
```

For us:

```text
Telegram/Ozzi -> n8n Workflow -> Analyst Team -> Debate -> Trader -> Risk Team -> NOVA Boss -> Telegram + Journal
```

## Non-negotiable rules

- NOVA is Boss / Portfolio Manager.
- Ozzi is final human decision maker.
- No auto-trading in v1.
- Only two patterns:
  1. 4H 21 EMA break + retest.
  2. 1H/4H pin bar rejection.
- Watchlist starts with major pairs + gold.
- Focus on Athens watch windows: 05:00-11:00 and 18:00-23:00.
- Risk uses 1 lot and $150-$200 per trade depending on setup quality.
- Goal is one A+ entry per week; second chance only if first loses.

## n8n-only architecture

n8n handles:

1. Telegram group trigger.
2. Command routing: `/scan`, `/debate`, `/best`, `/watch`, `/rules`, `/status`.
3. Scheduled watch windows.
4. Calling data/news APIs.
5. Running AI agent nodes with strict prompts.
6. Posting every agent message to Telegram in transparent mode.
7. Saving journal records.

## Professional-agent principle

Each agent must have a job, tools, input, output, and hard limits. They are not random bots.

Agents must talk to each other through structured messages. Every later stage can cite earlier reports.

## Telegram modes

### Transparent mode — default during testing

Every agent message is posted so Ozzi can judge capability.

### Quiet mode — later

Only watch alerts, final candidates, invalidations, and summaries are posted.

## Done for v1

v1 is complete when:

- A Telegram group can run `/scan`.
- The workflow posts short status, selected disagreements, and one clean NOVA decision card by default; `/full` can expose the full debate.
- Boss final message says WATCH / WAIT / REJECT / A+ CANDIDATE.
- Journal saves the full run.
- No auto-trade path exists.

## Professional build discipline

This project must be built slowly and correctly. NOVA must not rush architecture decisions.

Rules:

- Research before choosing tools, RPC architecture, data providers, n8n node design, or Telegram setup.
- Challenge Ozzi respectfully when an idea is weak, unsafe, too noisy, or not professional.
- Do not build from hype. Build from verified docs, source inspection, small tests, and real outputs.
- Use staged delivery: spec -> spike -> prototype -> test -> Telegram pilot -> scheduled alerts.
- Every agent must have a real job, tool access, limits, and measurable output.
- No auto-trading in v1. Signals and research only.

## Professional company quality gates

ForexAgents is not allowed to waste calls or produce fake confidence.

- Deterministic code checks whether an allowed setup is plausible before any LLM debate.
- If neither 4H 21 EMA break/retest nor 1H/4H pin-bar rejection is plausible, output `WAIT` immediately.
- All agents work from the same evidence snapshot.
- Important claims require evidence: timeframe, level, candle time, condition, and invalidation.
- NOVA has deterministic vetoes for stale data, missing candles, bad news window, invalid stop, risk over $200, wrong pattern, or weak evidence.
- Telegram output is layered: status, selected disagreements, clean decision card, with `/full` for complete debate.
- Replay mode is required before trusting live signals.

