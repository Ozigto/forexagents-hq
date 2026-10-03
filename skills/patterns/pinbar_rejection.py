"""Deterministic pin-bar candle measurements."""

from __future__ import annotations

from typing import Any


def detect_pinbar(candle: dict[str, Any], min_wick_ratio: float = 0.6) -> dict[str, Any]:
    open_ = float(candle['open'])
    high = float(candle['high'])
    low = float(candle['low'])
    close = float(candle['close'])
    total_range = high - low
    if total_range <= 0:
        return {'is_pinbar': False, 'direction': 'none', 'reason': 'invalid candle range'}
    body_high = max(open_, close)
    body_low = min(open_, close)
    upper_wick = high - body_high
    lower_wick = body_low - low
    body = abs(close - open_)
    upper_ratio = upper_wick / total_range
    lower_ratio = lower_wick / total_range
    if lower_ratio >= min_wick_ratio and lower_wick > body:
        direction = 'bullish'
        is_pinbar = True
    elif upper_ratio >= min_wick_ratio and upper_wick > body:
        direction = 'bearish'
        is_pinbar = True
    else:
        direction = 'none'
        is_pinbar = False
    return {
        'is_pinbar': is_pinbar,
        'direction': direction,
        'upper_wick': round(upper_wick, 6),
        'lower_wick': round(lower_wick, 6),
        'body': round(body, 6),
        'upper_wick_ratio': round(upper_ratio, 6),
        'lower_wick_ratio': round(lower_ratio, 6),
        'range': round(total_range, 6),
    }
