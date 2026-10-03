"""Deterministic ForexAgents case IDs."""

from __future__ import annotations

from datetime import datetime


def normalize_symbol(symbol: str) -> str:
    return ''.join(ch for ch in symbol.upper() if ch.isalnum())


def build_case_id(symbol: str, iso_timestamp: str, sequence: int) -> str:
    dt = datetime.fromisoformat(iso_timestamp)
    return f"{normalize_symbol(symbol)}-{dt:%Y%m%d}-{int(sequence):03d}"
