"""Deterministic 1-lot risk calculations."""

from __future__ import annotations

from typing import Any

JPY_QUOTE = {'USD/JPY'}


def pip_size(symbol: str) -> float:
    symbol = symbol.upper()
    if symbol in JPY_QUOTE or symbol.endswith('/JPY'):
        return 0.01
    if symbol in {'XAU/USD', 'XAUUSD'}:
        return 0.1
    return 0.0001


def pip_value_per_standard_lot(symbol: str) -> float:
    symbol = symbol.upper()
    if symbol in {'XAU/USD', 'XAUUSD'}:
        return 10.0
    # Approximation for USD-quoted major pairs. Later data layer can convert non-USD quote pairs precisely.
    return 10.0


def calculate_one_lot_risk(symbol: str, entry: float, stop: float, max_risk: float = 200.0) -> dict[str, Any]:
    pips = abs(float(entry) - float(stop)) / pip_size(symbol)
    dollar = round(pips * pip_value_per_standard_lot(symbol), 2)
    return {
        'symbol': symbol.upper(),
        'entry': float(entry),
        'stop': float(stop),
        'pip_distance': round(pips, 1),
        'dollar_risk': dollar,
        'max_risk': float(max_risk),
        'fits_ozzi_rule': dollar <= float(max_risk),
    }
