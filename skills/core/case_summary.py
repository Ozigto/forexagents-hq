"""Readable case summaries for Rhea/Telegram commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def summarize_case(case_dir: Path) -> dict[str, Any]:
    """Read a case folder and return a compact Telegram-ready summary."""
    case = _read_json(case_dir / 'case.json', {})
    snapshot = _read_json(case_dir / 'snapshot.json', {})
    gate = _read_json(case_dir / 'gate.json', {})
    nova_text = (case_dir / 'nova_decision.md').read_text(encoding='utf-8', errors='replace') if (case_dir / 'nova_decision.md').exists() else ''
    case_id = case.get('case_id') or case_dir.name
    status = case.get('status') or gate.get('status') or gate.get('decision') or 'UNKNOWN'
    symbol = case.get('symbol') or snapshot.get('symbol') or gate.get('symbol') or 'UNKNOWN'
    pattern = ', '.join(gate.get('patterns') or []) or 'none'
    evidence_grade = gate.get('evidence_grade', 'unknown')
    snapshot_id = case.get('snapshot_id') or snapshot.get('snapshot_id')
    telegram_text = f"""📁 CASE SUMMARY

Case: {case_id}
Status: {status}
Pair: {symbol}
Pattern: {pattern}
Evidence Grade: {evidence_grade}
Snapshot: {snapshot_id or 'none'}

{nova_text.strip() if nova_text else 'NOVA decision not written yet.'}
""".strip()
    return {
        'case_id': case_id,
        'status': status,
        'symbol': symbol,
        'pattern': pattern,
        'evidence_grade': evidence_grade,
        'snapshot_id': snapshot_id,
        'telegram_text': telegram_text,
    }
