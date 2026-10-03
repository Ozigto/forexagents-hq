# ForexAgents Roster

## 📊 Market Data Analyst

Fetch candles, 21 EMA, current price, spread, candle close time. No trade opinions.

Tools: candles_1h, candles_4h, candles_daily, candles_weekly, ema21, spread

Outputs: symbol, timeframe, price, ema21, candle_close_time, spread_status

## 🧭 HTF Bias Analyst

Identify weekly, daily, and 4H direction and whether they align.

Tools: weekly_candles, daily_candles, h4_candles, structure

Outputs: weekly_bias, daily_bias, h4_bias, alignment, preferred_direction

## 🕒 Session Timing Analyst

Judge Athens time windows and daily candle move context.

Tools: clock, session_calendar, daily_open

Outputs: current_window, timing_quality, daily_candle_context

## 📐 Structure Analyst

Find support/resistance, break levels, retest zones, liquidity highs/lows.

Tools: swing_high_low, support_resistance, liquidity_levels

Outputs: key_levels, break_level, retest_zone, invalidation_zone

## 🔎 Pattern Analyst

Detect only Ozzi's two patterns.

Tools: ema21, break_retest_detector, pinbar_detector

Outputs: pattern_name, status, direction, entry_zone, stop_zone, target_zone, confidence

## 📰 News Risk Analyst

Check high-impact macro risk and block bad timing.

Tools: economic_calendar

Outputs: news_risk, next_event, block_status

## 🐂 Bull Researcher

Build the strongest buy/long case from evidence and question Bear/Pattern when needed.

Tools: analyst_reports

Outputs: buy_case, evidence, questions, weakness

## 🐻 Bear Researcher

Build the strongest sell/short case from evidence and challenge weak buy ideas.

Tools: analyst_reports

Outputs: sell_case, evidence, questions, weakness

## 🧠 Research Manager

Stop debate, reject messy setups early, or pass clean idea to Trader.

Tools: analyst_reports, bull_bear_debate

Outputs: decision, reason, next_step

## 🧑‍💼 Trader

Create concrete trade plan only after research approval.

Tools: research_manager_decision

Outputs: direction, entry, stop_loss, targets, invalidation, confidence

## ⚔️ Aggressive Risk Agent

Argue if opportunity is worth taking earlier while respecting max risk.

Tools: trade_plan, rules

Outputs: opportunity_case, acceptable_risk, objection

## 🛡 Conservative Risk Agent

Try to reject weak trades and protect account rules.

Tools: trade_plan, rules

Outputs: reject_reasons, required_confirmation, risk_status

## ⚖️ Neutral Risk Agent

Balance opportunity and protection.

Tools: aggressive_risk, conservative_risk, trade_plan

Outputs: balanced_view, risk_grade, approve_watch_reject

## 👑 NOVA Boss / Portfolio Manager

Final decision-maker before Ozzi. Enforces rules and decides what reaches Telegram as candidate.

Tools: all_reports, risk_debate, journal_history

Outputs: final_decision, alert_type, reason, ozzi_action

## 📲 Telegram Manager

Format transparent debate and final alerts for the Telegram group.

Tools: all_agent_messages

Outputs: telegram_messages

## 🧪 Journal / Testing Agent

Save every scan, debate, decision, result, and agent quality score.

Tools: all_run_data

Outputs: journal_id, saved_fields, follow_up_check
