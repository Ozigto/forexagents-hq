"""Persistent case-file storage for ForexAgents."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

try:
    from case_id import build_case_id
except ImportError:  # direct file loading in tests
    import importlib.util
    _case_id_path = Path(__file__).resolve().parent / 'case_id.py'
    _spec = importlib.util.spec_from_file_location('case_id', _case_id_path)
    _mod = importlib.util.module_from_spec(_spec)
    assert _spec and _spec.loader
    _spec.loader.exec_module(_mod)
    build_case_id = _mod.build_case_id


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def append_event(case_dir: Path, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Append an immutable event to a case's audit trail."""
    case_dir.mkdir(parents=True, exist_ok=True)
    events_path = case_dir / 'events.json'
    events = _read_json(events_path, [])
    event = {
        'type': event_type,
        'recorded_at': datetime.now().astimezone().isoformat(timespec='seconds'),
        'payload': payload,
    }
    events.append(event)
    _write_json(events_path, events)
    return event


def read_events(case_dir: Path) -> list[dict[str, Any]]:
    return _read_json(case_dir / 'events.json', [])


def create_case(
    *,
    root: Path,
    symbol: str,
    timestamp: str,
    sequence: int,
    rule_version: int | str,
    snapshot: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    """Create a persistent case folder with standard files."""
    case_id = build_case_id(symbol, timestamp, sequence)
    case_dir = root / 'cases' / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    case = {
        'case_id': case_id,
        'symbol': symbol.upper(),
        'created_at': timestamp,
        'sequence': int(sequence),
        'rule_version': rule_version,
        'status': gate.get('status') or gate.get('decision') or 'DETECTED',
        'snapshot_id': snapshot.get('snapshot_id'),
        'case_dir': str(case_dir),
    }
    _write_json(case_dir / 'case.json', case)
    _write_json(case_dir / 'snapshot.json', snapshot)
    _write_json(case_dir / 'gate.json', gate)
    (case_dir / 'analyst_reports.json').write_text('[]\n', encoding='utf-8')
    (case_dir / 'debate.json').write_text('[]\n', encoding='utf-8')
    (case_dir / 'nova_decision.md').write_text('# NOVA Decision\n\nPending.\n', encoding='utf-8')
    (case_dir / 'ozzi_decision.md').write_text('# Ozzi Decision\n\nPending.\n', encoding='utf-8')
    (case_dir / 'outcome.json').write_text('{}\n', encoding='utf-8')
    (case_dir / 'review.md').write_text('# Review\n\nPending.\n', encoding='utf-8')
    _write_json(case_dir / 'events.json', [])
    append_event(case_dir, 'case_created', {'case_id': case_id, 'status': case['status']})
    return case
