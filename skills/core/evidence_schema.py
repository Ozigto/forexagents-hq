"""Evidence Snapshot schema helpers for ForexAgents."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def snapshot_id(snapshot: dict[str, Any]) -> str:
    base = {k: v for k, v in snapshot.items() if k != 'snapshot_id'}
    digest = hashlib.sha256(_canonical(base).encode('utf-8')).hexdigest()[:16]
    return f"snap-{digest}"


def build_evidence_snapshot(symbol: str, timeframe: str, candles: list[dict[str, Any]], *, data_timestamp: str, source: str = 'manual_or_replay') -> dict[str, Any]:
    if not candles:
        raise ValueError('candles required')
    completed = candles[-1]
    snapshot = {
        'symbol': symbol.upper(),
        'timeframe': timeframe.upper().replace('H1', '1H').replace('H4', '4H'),
        'source': source,
        'data_timestamp': data_timestamp,
        'completed_candle': completed,
        'candles': candles,
        'facts': [],
        'calculations': [],
        'interpretations': [],
        'unknowns': [],
    }
    snapshot['snapshot_id'] = snapshot_id(snapshot)
    return snapshot
