"""Deterministic data-quality checks for ForexAgents."""

from __future__ import annotations

from datetime import datetime
from typing import Any

TIMEFRAME_MINUTES = {
    '1H': 60,
    'H1': 60,
    '4H': 240,
    'H4': 240,
}


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def check_data_quality(snapshot: dict[str, Any], *, now: str, max_lag_factor: float = 1.25) -> dict[str, Any]:
    vetoes: list[str] = []
    warnings: list[str] = []
    timeframe = str(snapshot.get('timeframe', '')).upper()
    tf_minutes = TIMEFRAME_MINUTES.get(timeframe)
    if not snapshot.get('symbol'):
        vetoes.append('missing_symbol')
    if not tf_minutes:
        vetoes.append('unsupported_timeframe')
    candles = snapshot.get('candles') or []
    if not candles:
        vetoes.append('missing_candles')
    completed = snapshot.get('completed_candle') or {}
    if not completed.get('time'):
        vetoes.append('missing_completed_candle')
    times = [c.get('time') for c in candles if c.get('time')]
    if len(times) != len(set(times)):
        vetoes.append('duplicate_candles')
    if tf_minutes and completed.get('time'):
        age_minutes = (parse_iso(now) - parse_iso(completed['time'])).total_seconds() / 60
        if age_minutes > tf_minutes * max_lag_factor:
            vetoes.append('stale_data')
        elif age_minutes < 0:
            vetoes.append('future_candle')
    if snapshot.get('data_timestamp'):
        data_age = (parse_iso(now) - parse_iso(snapshot['data_timestamp'])).total_seconds() / 60
        if data_age < 0:
            vetoes.append('future_data_timestamp')
    else:
        warnings.append('missing_data_timestamp')
    return {
        'decision': 'WAIT' if vetoes else 'PASS',
        'vetoes': vetoes,
        'warnings': warnings,
    }
