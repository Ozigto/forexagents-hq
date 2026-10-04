#!/usr/bin/env python3
"""Autonomous ForexAgents scanner.

Reads MT5 local candle exports, sends evidence snapshots to RPC, and returns
only alert-worthy cases. No auto-trading.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RPC_URL = 'http://127.0.0.1:18765/debate/setup'
STATE_FILE = ROOT / '.autonomous_scanner_state.json'
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


def _load_telegram_bridge_module():
    path = ROOT / 'scripts' / 'telegram_polling_bridge.py'
    spec = importlib.util.spec_from_file_location('telegram_polling_bridge', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_state(path: Path = STATE_FILE) -> dict[str, Any]:
    if not path.exists():
        return {'sent_alert_keys': [], 'health_alert_keys': []}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {'sent_alert_keys': [], 'health_alert_keys': []}
    data.setdefault('sent_alert_keys', [])
    data.setdefault('health_alert_keys', [])
    return data


def save_state(state: dict[str, Any], path: Path = STATE_FILE) -> None:
    keys = list(dict.fromkeys(state.get('sent_alert_keys', [])))[-500:]
    health_keys = list(dict.fromkeys(state.get('health_alert_keys', [])))[-200:]
    state = {**state, 'sent_alert_keys': keys, 'health_alert_keys': health_keys}
    path.write_text(json.dumps(state, indent=2), encoding='utf-8')


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


def parse_mt5_time(value: str) -> datetime:
    value = str(value).strip().replace('.', '-')
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)


def expected_groups() -> set[tuple[str, str]]:
    return {(symbol, timeframe) for symbol in WATCHLIST for timeframe in TIMEFRAMES}


def _normalize_symbol_loose(symbol: str) -> str:
    raw = str(symbol).strip().upper().replace('/', '')
    for watch_symbol in WATCHLIST:
        base = watch_symbol.replace('/', '')
        if raw.startswith(base):
            return watch_symbol
    return raw


def _normalize_timeframe_loose(timeframe: str) -> str:
    raw = str(timeframe).strip().upper()
    if raw == 'H1':
        return '1H'
    if raw == 'H4':
        return '4H'
    return raw


def check_mt5_health(path: str | Path | None = None, *, now: datetime | None = None) -> dict[str, Any]:
    mt5 = _load_mt5_module()
    path = Path(path or mt5.DEFAULT_MT5_CANDLES)
    moment = now or now_athens()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ATHENS)
    if not path.exists():
        return {'ok': False, 'reason': 'mt5_candle_file_missing', 'path': str(path)}
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    latest_time: datetime | None = None
    latest_server_time: datetime | None = None
    closed_rows = 0
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                if str(row.get('is_closed', '')).strip().lower() not in {'1', 'true', 'yes', 'closed'}:
                    continue
                symbol = _normalize_symbol_loose(row.get('symbol', ''))
                timeframe = _normalize_timeframe_loose(row.get('timeframe', ''))
                key = (symbol, timeframe)
                candle_time = parse_mt5_time(row.get('time', ''))
                server_time = parse_mt5_time(row.get('server_time', row.get('time', '')))
                groups[key] = {'latest_candle_time': candle_time.isoformat(timespec='seconds'), 'server_time': server_time.isoformat(timespec='seconds')}
                latest_time = candle_time if latest_time is None or candle_time > latest_time else latest_time
                latest_server_time = server_time if latest_server_time is None or server_time > latest_server_time else latest_server_time
                closed_rows += 1
    except Exception as exc:
        return {'ok': False, 'reason': 'mt5_candle_file_unreadable', 'path': str(path), 'error': str(exc)}
    missing = sorted([f'{symbol} {tf}' for symbol, tf in expected_groups() if (symbol, tf) not in groups])
    if missing:
        return {'ok': False, 'reason': 'mt5_missing_symbol_timeframes', 'path': str(path), 'closed_groups': len(groups), 'closed_rows': closed_rows, 'missing_groups': missing[:32]}
    if not latest_time:
        return {'ok': False, 'reason': 'mt5_no_closed_candles', 'path': str(path), 'closed_groups': len(groups), 'closed_rows': closed_rows}
    age_hours = (moment.astimezone(timezone.utc) - latest_time).total_seconds() / 3600
    if is_market_open(moment) and age_hours > 6:
        return {
            'ok': False,
            'reason': 'mt5_candles_stale',
            'path': str(path),
            'closed_groups': len(groups),
            'closed_rows': closed_rows,
            'latest_candle_time': latest_time.isoformat(timespec='seconds'),
            'latest_server_time': latest_server_time.isoformat(timespec='seconds') if latest_server_time else None,
            'age_hours': round(age_hours, 2),
        }
    return {
        'ok': True,
        'reason': 'ok',
        'path': str(path),
        'closed_groups': len(groups),
        'closed_rows': closed_rows,
        'latest_candle_time': latest_time.isoformat(timespec='seconds'),
        'latest_server_time': latest_server_time.isoformat(timespec='seconds') if latest_server_time else None,
        'age_hours': round(age_hours, 2),
    }


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


def alert_key(alert: dict[str, Any]) -> str:
    result = alert.get('result') or {}
    snapshot = ((result.get('setup') or {}).get('evidence_snapshot') or {})
    candle_time = (snapshot.get('completed_candle') or {}).get('time') or snapshot.get('data_timestamp') or ''
    case_id = result.get('case_id') or ''
    status = str((result.get('gate') or {}).get('status') or (result.get('gate') or {}).get('decision') or result.get('status') or '')
    return '|'.join([case_id, str(alert.get('symbol')), str(alert.get('timeframe')), status, str(candle_time)])


def format_autonomous_alert(alert: dict[str, Any]) -> str:
    result = alert.get('result') or {}
    gate = result.get('gate') or {}
    symbol = alert.get('symbol')
    timeframe = alert.get('timeframe')
    status = gate.get('status') or gate.get('decision') or result.get('status') or 'WATCH'
    evidence = gate.get('evidence_grade', 'unknown')
    reasons = gate.get('reasons') or []
    transcript = result.get('transcript') or []
    text = result.get('telegram_text') or ''
    lines = [
        '🚨 ForexAgents HQ autonomous alert',
        f'Pair: {symbol}',
        f'Timeframe: {timeframe}',
        f'Status: {status}',
        f'Evidence: {evidence}',
        f"Case: {result.get('case_id', 'none')}",
        '',
    ]
    if text:
        lines.append(text[:2600])
    elif transcript:
        lines.append('Desk summary: evidence gate passed; agents have a case to review.')
    elif reasons:
        lines.extend([f'- {reason}' for reason in reasons[:6]])
    else:
        lines.append('Evidence passed the alert gate. Review before taking any trade.')
    lines.extend([
        '',
        '👑 NOVA: This is a signal/research alert only. No auto-trading. Check entry, stop, target, spread, and news before acting.',
    ])
    return '\n'.join(lines)[:3900]


def _telegram_chat_and_token() -> tuple[Any, int, str]:
    bridge = _load_telegram_bridge_module()
    env = bridge.load_local_env()
    chat_id = int(env.get('FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID', '0'))
    if not chat_id:
        raise RuntimeError('Missing FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID in .env.telegram.local')
    token = bridge.get_telegram_token()
    return bridge, chat_id, token


def format_health_alert(health: dict[str, Any]) -> str:
    lines = [
        '⚠️ ForexAgents HQ health warning',
        '',
        f"Reason: {health.get('reason', 'unknown')}",
    ]
    if health.get('path'):
        lines.append(f"MT5 file: {health.get('path')}")
    if health.get('latest_candle_time'):
        lines.append(f"Latest closed candle: {health.get('latest_candle_time')}")
    if health.get('age_hours') is not None:
        lines.append(f"Candle age: {health.get('age_hours')} hours")
    if health.get('closed_groups') is not None:
        lines.append(f"Closed groups: {health.get('closed_groups')}/16")
    missing = health.get('missing_groups') or []
    if missing:
        lines.append('Missing groups: ' + ', '.join(missing[:8]) + (' ...' if len(missing) > 8 else ''))
    lines.extend([
        '',
        '👑 NOVA: Scanner will not trust bad MT5 evidence. Check MT5 is open, NovaForexBridgeV2 is attached, and candles are updating.',
    ])
    return '\n'.join(lines)[:3900]


def health_alert_key(health: dict[str, Any]) -> str:
    return '|'.join([
        str(health.get('reason', 'unknown')),
        str(health.get('latest_candle_time', '')),
        str(health.get('closed_groups', '')),
    ])


def send_health_alert_if_needed(health: dict[str, Any], *, state: dict[str, Any] | None = None) -> int:
    if health.get('ok'):
        return 0
    state = state if state is not None else load_state()
    sent_keys = set(state.get('health_alert_keys', []))
    key = health_alert_key(health)
    if key in sent_keys:
        return 0
    bridge, chat_id, token = _telegram_chat_and_token()
    bridge.telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': format_health_alert(health)})
    sent_keys.add(key)
    state['health_alert_keys'] = list(sent_keys)
    save_state(state)
    return 1


def send_telegram_alerts(alerts: list[dict[str, Any]], *, state: dict[str, Any] | None = None) -> int:
    if not alerts:
        return 0
    state = state if state is not None else load_state()
    sent_keys = set(state.get('sent_alert_keys', []))
    bridge, chat_id, token = _telegram_chat_and_token()
    sent = 0
    for alert in alerts:
        key = alert_key(alert)
        if key in sent_keys:
            continue
        bridge.telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': format_autonomous_alert(alert)})
        sent_keys.add(key)
        sent += 1
    state['sent_alert_keys'] = list(sent_keys)
    save_state(state)
    return sent


def scan_once(*, symbols: list[str] | None = None, timeframes: list[str] | None = None, now: datetime | None = None, force: bool = False) -> dict[str, Any]:
    moment = now or now_athens()
    health = check_mt5_health(now=moment)
    if not health.get('ok'):
        return {'ok': True, 'skipped': True, 'reason': 'mt5_health_failed', 'health': health, 'alerts': [], 'scanned': 0}
    if not force and not is_market_open(moment):
        return {'ok': True, 'skipped': True, 'reason': 'market_closed', 'health': health, 'alerts': [], 'scanned': 0}
    if not force and not in_watch_window(moment):
        return {'ok': True, 'skipped': True, 'reason': 'outside_watch_window', 'health': health, 'alerts': [], 'scanned': 0}
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
    return {'ok': True, 'skipped': False, 'scanned': scanned, 'alerts': alerts, 'errors': errors, 'health': health, 'timestamp': moment.astimezone(ATHENS).isoformat(timespec='seconds')}


def main() -> int:
    parser = argparse.ArgumentParser(description='ForexAgents autonomous MT5 scanner')
    parser.add_argument('--once', action='store_true', help='run one scan and exit')
    parser.add_argument('--force', action='store_true', help='scan even outside watch windows')
    parser.add_argument('--telegram', action='store_true', help='send alert-worthy cases to the ForexAgents Telegram group')
    parser.add_argument('--interval-seconds', type=int, default=900)
    args = parser.parse_args()
    while True:
        result = scan_once(force=args.force)
        if args.telegram and result.get('health') and not result['health'].get('ok'):
            result['health_alerts_sent'] = send_health_alert_if_needed(result['health'])
        if args.telegram and result.get('alerts'):
            result['telegram_alerts_sent'] = send_telegram_alerts(result['alerts'])
        print(json.dumps(result, ensure_ascii=False, default=str), flush=True)
        if args.once:
            return 0
        time.sleep(max(60, args.interval_seconds))


if __name__ == '__main__':
    raise SystemExit(main())
