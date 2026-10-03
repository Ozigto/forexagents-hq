"""Deterministic EMA calculations for ForexAgents."""

from __future__ import annotations


def ema(values: list[float] | tuple[float, ...], period: int) -> float:
    if period <= 0:
        raise ValueError('period must be positive')
    if len(values) < period:
        raise ValueError('not enough values for EMA period')
    vals = [float(v) for v in values]
    seed = sum(vals[:period]) / period
    multiplier = 2 / (period + 1)
    current = seed
    for value in vals[period:]:
        current = (value - current) * multiplier + current
    return round(current, 6)


def ema21(closes: list[float] | tuple[float, ...]) -> float:
    return ema(closes, 21)
