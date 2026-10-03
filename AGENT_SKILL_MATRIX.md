# Agent Skill Matrix

ForexAgents is a professional research operation. Agents do not all receive the same tools.

Core rule:

```text
Code establishes measurable facts.
Agents reason about those facts.
```

Titan, Vega, Sage, Ace, the Risk Board, and NOVA must not fetch their own candles/news independently. They receive the verified evidence snapshot from the specialist layer. This prevents the company from debating two different realities.

## Three skill layers

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

## Agent skill access

| Agent | Core skills | Skill boundary |
|---|---|---|
| 📊 **Atlas** | OHLC candle retrieval, EMA21 calculation, spread, ATR/volatility, price normalization, data freshness validation | Builds market facts only. |
| 🧭 **Orion** | W1/D1/H4 trend classification, multi-timeframe alignment, EMA context, higher-timeframe bias | Reads verified candles, does not create trade plan. |
| 🕒 **Chronos** | Athens timezone, Asian/London/New York sessions, session transitions, allowed watch windows, timing quality | Timing quality only. |
| 📐 **Mason** | Support/resistance, swing highs/lows, HH/HL/LH/LL, break of structure, retest zones | Structure evidence only. |
| 🔎 **Hunter** | Ozzi's two pattern detectors: H4 EMA21 break/retest and H1/H4 pin-bar rejection | Pattern detection only; no trade approval. |
| 📰 **Echo** | Economic calendar, event importance, affected currencies, time-to-news, post-news danger window | News veto/risk only. |
| 🐂 **Titan** | Evidence synthesis, bullish thesis construction, challenge bearish claims | Must not fetch candles/news; argues from snapshot. |
| 🐻 **Vega** | Evidence synthesis, bearish thesis construction, attack weak assumptions and false confirmations | Must not fetch candles/news; argues from snapshot. |
| 🧠 **Sage** | Debate arbitration, contradiction detection, evidence weighting, unresolved-question detection | Rejects unsupported claims; does not force consensus. |
| 🧑‍💼 **Ace** | Entry, stop, invalidation, target, R:R, 1-lot dollar-risk calculation, trade-plan construction | Builds plan only after pattern/evidence gate passes. |
| ⚔️ **Blitz** | Upside/opportunity analysis, continuation potential, aggressive scenario testing | Stress tests upside; no final approval. |
| 🛡️ **Guard** | Capital protection, downside analysis, news exposure, stop vulnerability, veto checks | Protects capital; can recommend veto. |
| ⚖️ **Balance** | Neutral risk/reward assessment, scenario comparison, conflicting-evidence assessment | Independent neutral review. |
| 👑 **NOVA** | Portfolio context, company rules, final evidence review, hard vetoes, candidate classification | Final classifier; deterministic vetoes override LLM confidence. |
| 📲 **Relay** | Telegram receive/send, formatting, commands, threading/case IDs, anti-spam | Presentation only; cannot influence trading conclusion. |
| 🧪 **Ledger** | Case storage, outcome tracking, MFE/MAE, R results, agent scoring, replay/backtesting | Records and evaluates; does not rewrite history. |

## Deterministic skills that are not LLM tasks

These must be Python functions or validated data transformations, not agent opinions:

- EMA21 calculation
- candle math
- pin-bar wick/body ratios
- ATR/volatility
- spread and price normalization
- timestamps and Athens session detection
- stale-data checks
- support/resistance candidate calculation
- break/retest distance
- 1-lot dollar risk
- reward:risk
- case IDs and state transitions
- replay no-future-leak enforcement

Example data path:

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

Sage evaluates disagreement
```

## Planned deterministic skills directory

```text
skills/
  core/
    case_state.py
    evidence_schema.py
    timestamps.py
    audit_log.py
    rules_loader.py
  market_data/
    candles.py
    ema.py
    spread.py
    volatility.py
    freshness.py
  sessions/
    athens_time.py
    market_sessions.py
    watch_windows.py
  structure/
    swings.py
    support_resistance.py
    break_of_structure.py
    retest_zones.py
  patterns/
    ema21_break_retest.py
    pinbar_rejection.py
  news/
    calendar_window.py
    currency_impact.py
  risk/
    one_lot_risk.py
    reward_risk.py
    invalidation.py
  replay/
    replay_runner.py
    no_future_leak.py
```
