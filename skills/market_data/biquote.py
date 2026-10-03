"""No-key Biquote OHLC adapter for ForexAgents live evidence.

This is a read-only market data source. It is useful for making the desk
operational without broker credentials, but broker-grade validation should come
later from OANDA/MT5 before trading trust.
"""

from __future__ import annotations

import importlib.util
import json
import ssl
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = 'https://biquote.io/api'

SUPPORTED_SYMBOLS = {
    'EUR/USD': 'EURUSD',
    'GBP/USD': 'GBPUSD',
    'USD/JPY': 'USDJPY',
    'USD/CHF': 'USDCHF',
    'AUD/USD': 'AUDUSD',
    'NZD/USD': 'NZDUSD',
    'USD/CAD': 'USDCAD',
    'XAU/USD': 'XAUUSD',
}

TIMEFRAME_TO_INTERVAL = {
    '1H': '1h',
    'H1': '1h',
    '4H': '4h',
    'H4': '4h',
}


def _load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def to_biquote_symbol(symbol: str) -> str:
    normalized = symbol.upper().replace(' ', '')
    if '/' not in normalized and len(normalized) == 6:
        normalized = normalized[:3] + '/' + normalized[3:]
    if normalized == 'XAUUSD':
        normalized = 'XAU/USD'
    if normalized not in SUPPORTED_SYMBOLS:
        raise ValueError(f'unsupported symbol for Biquote adapter: {symbol}')
    return SUPPORTED_SYMBOLS[normalized]


def normalize_timeframe(timeframe: str) -> str:
    tf = timeframe.upper().replace('H1', '1H').replace('H4', '4H')
    if tf not in {'1H', '4H'}:
        raise ValueError(f'unsupported timeframe: {timeframe}')
    return tf


def fetch_bars(symbol: str, timeframe: str, *, limit: int = 80, timeout: int = 20) -> list[dict[str, Any]]:
    bq_symbol = to_biquote_symbol(symbol)
    tf = normalize_timeframe(timeframe)
    interval = TIMEFRAME_TO_INTERVAL[tf]
    query = urllib.parse.urlencode({'interval': interval, 'limit': int(limit)})
    url = f'{BASE_URL}/{bq_symbol}/ohlc?{query}'
    request = urllib.request.Request(url, headers={'User-Agent': 'ForexAgents-HQ/0.1'})
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except Exception as first_error:
        proc = subprocess.run(
            ['curl', '-fsSL', '--max-time', str(timeout), url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f'Biquote fetch failed: {first_error}; curl: {proc.stderr.strip()}') from first_error
        payload = json.loads(proc.stdout)
    bars = payload.get('bars') or []
    if not isinstance(bars, list) or not bars:
        raise RuntimeError(f'no bars returned for {symbol} {timeframe}')
    return bars


def _iso_utc(value: str) -> str:
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds')


def bars_to_closed_candles(bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candles: list[dict[str, Any]] = []
    for bar in bars:
        if bar.get('isOpen') is True:
            continue
        candles.append({
            'time': _iso_utc(str(bar['openTime'])),
            'open': float(bar['open']),
            'high': float(bar['high']),
            'low': float(bar['low']),
            'close': float(bar['close']),
            'volume': float(bar.get('volume') or 0),
            'tick_volume': int(bar.get('tickVolume') or 0),
        })
    if not candles:
        raise RuntimeError('no closed candles returned')
    return candles


def build_live_snapshot(symbol: str, timeframe: str, *, limit: int = 80, now: str | None = None) -> dict[str, Any]:
    tf = normalize_timeframe(timeframe)
    bars = fetch_bars(symbol, tf, limit=limit)
    candles = bars_to_closed_candles(bars)
    now_iso = now or datetime.now(timezone.utc).isoformat(timespec='seconds')
    evidence_schema = _load_module('evidence_schema', 'skills/core/evidence_schema.py')
    ema_mod = _load_module('ema', 'skills/market_data/ema.py')
    pinbar_mod = _load_module('pinbar_rejection', 'skills/patterns/pinbar_rejection.py')
    snapshot = evidence_schema.build_evidence_snapshot(symbol.upper(), tf, candles, data_timestamp=now_iso, source='biquote')
    closes = [float(c['close']) for c in candles]
    if len(closes) >= 21:
        snapshot['calculations'].append({'name': 'ema21', 'value': ema_mod.ema21(closes), 'period': 21, 'timeframe': tf})
    snapshot['calculations'].append({'name': 'pinbar', **pinbar_mod.detect_pinbar(candles[-1])})
    snapshot['facts'].append({'name': 'closed_candle_count', 'value': len(candles)})
    snapshot['facts'].append({'name': 'source_note', 'value': 'Biquote no-key OHLC feed; validate with broker feed before live trading trust.'})
    return snapshot
