#!/usr/bin/env python3
"""Autonomous ForexAgents scanner.

Reads MT5 local candle exports, sends evidence snapshots to RPC, and returns
only alert-worthy cases. No auto-trading.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RPC_URL = 'http://127.0.0.1:18765/debate/setup'
ATHENS = ZoneInfo('Europe/Athens')
WATCHLIST = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'XAU/USD']
TIMEFRAMES = ['1H', '4H']
ALERT_STATUSES = {'WATCH', 'A+ CANDIDATE', 'APPROVED', 'CANDIDATE_FOR_DEBATE'}


def _load_mt5_module():
    path = ROOT / 'skills' / 'market_data' / 'mt5_files.py'
    spec = importlib.util.spec_from_file_location('mt5_files', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def now_athens() -> datetime:
    return datetime.now(ATHENS)


def in_watch_window(moment: datetime | None = None) -> bool:
    moment = moment or now_athens()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ATHENS)
    local = moment.astimezone(ATHENS)
    minutes = local.hour * 60 + local.minute
    morning = 5 * 60 <= minutes <= 11 * 60
    evening = 18 * 60 <= minutes <= 23 * 60
    return morning or evening


def is_market_open(moment: datetime | None = None) -> bool:
    """Conservative forex market-hours guard in Athens time.

    Forex is normally closed from Friday night until late Sunday Athens time.
    We use a conservative Sunday 24:00 reopen guard so the scanner does not
    burn agent/RPC calls over the weekend. Manual verification can still use
    --force.
    """
    moment = moment or now_athens()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ATHENS)
    local = moment.astimezone(ATHENS)
    weekday = local.weekday()  # Monday=0, Sunday=6
    if weekday == 5:  # Saturday
        return False
    if weekday == 6:  # Sunday
        return False
    if weekday == 4 and local.hour >= 23:  # Friday late close guard
        return False
    return True


def load_mt5_snapshot(symbol: str, timeframe: str) -> dict[str, Any]:
    mt5 = _load_mt5_module()
    return mt5.load_latest_snapshot(symbol, timeframe)


def call_rpc(payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read().decode('utf-8'))


def is_alert_worthy(result: dict[str, Any]) -> bool:
    status = str(result.get('status') or '').upper()
    gate_status = str((result.get('gate') or {}).get('status') or '').upper()
    decision = str((result.get('gate') or {}).get('decision') or '').upper()
    return status in ALERT_STATUSES or gate_status in ALERT_STATUSES or decision == 'DEBATE'


def scan_once(*, symbols: list[str] | None = None, timeframes: list[str] | None = None, now: datetime | None = None, force: bool = False) -> dict[str, Any]:
    moment = now or now_athens()
    if not force and not is_market_open(moment):
        return {'ok': True, 'skipped': True, 'reason': 'market_closed', 'alerts': [], 'scanned': 0}
    if not force and not in_watch_window(moment):
        return {'ok': True, 'skipped': True, 'reason': 'outside_watch_window', 'alerts': [], 'scanned': 0}
    symbols = symbols or WATCHLIST
    timeframes = timeframes or TIMEFRAMES
    alerts: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    scanned = 0
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                snapshot = load_mt5_snapshot(symbol, timeframe)
                payload = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'input_type': 'mt5_autonomous_scanner',
                    'chart_notes': 'Autonomous MT5 scanner evidence snapshot.',
                    'evidence_snapshot': snapshot,
                    'now': moment.astimezone(ATHENS).isoformat(timespec='seconds'),
                    'max_agents': 8,
                    'max_cross_questions': 6,
                    'agent_timeout_seconds': 120,
                }
                result = call_rpc(payload)
                scanned += 1
                if is_alert_worthy(result):
                    alerts.append({'symbol': symbol, 'timeframe': timeframe, 'result': result})
            except Exception as exc:
                errors.append({'symbol': symbol, 'timeframe': timeframe, 'error': str(exc)})
    return {'ok': True, 'skipped': False, 'scanned': scanned, 'alerts': alerts, 'errors': errors, 'timestamp': moment.astimezone(ATHENS).isoformat(timespec='seconds')}


def main() -> int:
    parser = argparse.ArgumentParser(description='ForexAgents autonomous MT5 scanner')
    parser.add_argument('--once', action='store_true', help='run one scan and exit')
    parser.add_argument('--force', action='store_true', help='scan even outside watch windows')
    parser.add_argument('--interval-seconds', type=int, default=900)
    args = parser.parse_args()
    while True:
        result = scan_once(force=args.force)
        print(json.dumps(result, ensure_ascii=False, default=str), flush=True)
        if args.once:
            return 0
        time.sleep(max(60, args.interval_seconds))


if __name__ == '__main__':
    raise SystemExit(main())
