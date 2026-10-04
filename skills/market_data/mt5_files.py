"""Read-only MT5 local file adapter for ForexAgents.

MT5 writes closed 1H/4H candles to MQL5/Files/nova_forex_candles.csv.
ForexAgents reads that file and builds the shared evidence snapshot.
"""

from __future__ import annotations

import csv
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MT5_CANDLES = Path('/Users/ozitzaferi/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Files/nova_forex_candles.csv')

SYMBOL_MAP = {
    'EURUSD': 'EUR/USD',
    'GBPUSD': 'GBP/USD',
    'USDJPY': 'USD/JPY',
    'USDCHF': 'USD/CHF',
    'AUDUSD': 'AUD/USD',
    'NZDUSD': 'NZD/USD',
    'USDCAD': 'USD/CAD',
    'XAUUSD': 'XAU/USD',
}

TIMEFRAME_MAP = {
    'H1': '1H',
    '1H': '1H',
    'PERIOD_H1': '1H',
    'H4': '4H',
    '4H': '4H',
    'PERIOD_H4': '4H',
}


def _load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_symbol(symbol: str) -> str:
    raw = symbol.strip().upper().replace('/', '')
    if raw not in SYMBOL_MAP:
        raise ValueError(f'unsupported MT5 symbol: {symbol}')
    return SYMBOL_MAP[raw]


def normalize_timeframe(timeframe: str) -> str:
    raw = timeframe.strip().upper()
    if raw not in TIMEFRAME_MAP:
        raise ValueError(f'unsupported MT5 timeframe: {timeframe}')
    return TIMEFRAME_MAP[raw]


def parse_mt5_time(value: str) -> str:
    value = value.strip().replace('.', '-')
    # MT5 bridge exports server time without timezone. Treat as UTC for deterministic
    # file exchange; freshness checks are conservative and fail closed if old.
    dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    return dt.isoformat(timespec='seconds')


def _closed(value: str) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'closed'}


def read_mt5_candles(path: str | Path = DEFAULT_MT5_CANDLES) -> dict[tuple[str, str], list[dict[str, Any]]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'MT5 candle export not found: {path}')
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not _closed(row.get('is_closed', '')):
                continue
            symbol = normalize_symbol(row['symbol'])
            timeframe = normalize_timeframe(row['timeframe'])
            candle = {
                'time': parse_mt5_time(row['time']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'tick_volume': int(float(row.get('tick_volume') or 0)),
            }
            grouped.setdefault((symbol, timeframe), []).append(candle)
    for candles in grouped.values():
        candles.sort(key=lambda c: c['time'])
    return grouped


def build_snapshot_from_candles(symbol: str, timeframe: str, candles: list[dict[str, Any]], *, data_timestamp: str) -> dict[str, Any]:
    if not candles:
        raise ValueError('candles required')
    evidence_schema = _load_module('evidence_schema', 'skills/core/evidence_schema.py')
    ema_mod = _load_module('ema', 'skills/market_data/ema.py')
    pinbar_mod = _load_module('pinbar_rejection', 'skills/patterns/pinbar_rejection.py')
    snapshot = evidence_schema.build_evidence_snapshot(symbol, timeframe, candles, data_timestamp=data_timestamp, source='mt5_local_file')
    closes = [float(c['close']) for c in candles]
    if len(closes) >= 21:
        snapshot['calculations'].append({'name': 'ema21', 'value': ema_mod.ema21(closes), 'period': 21, 'timeframe': timeframe})
    snapshot['calculations'].append({'name': 'pinbar', **pinbar_mod.detect_pinbar(candles[-1])})
    snapshot['facts'].append({'name': 'closed_candle_count', 'value': len(candles)})
    snapshot['facts'].append({'name': 'source_note', 'value': 'MT5 local read-only candle export; no auto-trading.'})
    return snapshot


def load_latest_snapshot(symbol: str, timeframe: str, *, path: str | Path = DEFAULT_MT5_CANDLES, limit: int = 80, data_timestamp: str | None = None) -> dict[str, Any]:
    norm_symbol = normalize_symbol(symbol)
    norm_tf = normalize_timeframe(timeframe)
    grouped = read_mt5_candles(path)
    candles = grouped.get((norm_symbol, norm_tf)) or []
    if not candles:
        raise RuntimeError(f'No MT5 candles for {norm_symbol} {norm_tf}')
    candles = candles[-int(limit):]
    ts = data_timestamp or datetime.now(timezone.utc).isoformat(timespec='seconds')
    return build_snapshot_from_candles(norm_symbol, norm_tf, candles, data_timestamp=ts)
