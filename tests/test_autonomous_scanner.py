import importlib.util
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_scanner():
    spec = importlib.util.spec_from_file_location('autonomous_scanner', ROOT / 'scripts' / 'autonomous_scanner.py')
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class AutonomousScannerTests(unittest.TestCase):
    def test_athens_watch_windows(self):
        scanner = load_scanner()
        self.assertTrue(scanner.in_watch_window(datetime.fromisoformat('2026-10-03T06:00:00+03:00')))
        self.assertTrue(scanner.in_watch_window(datetime.fromisoformat('2026-10-03T19:00:00+03:00')))
        self.assertFalse(scanner.in_watch_window(datetime.fromisoformat('2026-10-03T14:00:00+03:00')))

    def test_weekend_market_closed_skips_without_force(self):
        scanner = load_scanner()
        result = scanner.scan_once(now=datetime.fromisoformat('2026-10-04T06:00:00+03:00'))
        self.assertTrue(result['skipped'])
        self.assertEqual(result['reason'], 'market_closed')

    def test_weekday_watch_window_can_scan(self):
        scanner = load_scanner()
        fake_snapshot = {
            'symbol': 'XAU/USD',
            'timeframe': '1H',
            'source': 'mt5_local_file',
            'completed_candle': {'time': '2026-10-05T06:00:00+00:00'},
            'candles': [{'time': '2026-10-05T06:00:00+00:00'}],
        }
        with patch.object(scanner, 'load_mt5_snapshot', return_value=fake_snapshot), \
             patch.object(scanner, 'call_rpc', return_value={'status': 'WAIT', 'gate': {'decision': 'WAIT'}}):
            result = scanner.scan_once(symbols=['XAU/USD'], timeframes=['1H'], now=datetime.fromisoformat('2026-10-05T06:00:00+03:00'))
        self.assertFalse(result['skipped'])
        self.assertEqual(result['scanned'], 1)

    def test_scan_once_calls_rpc_for_mt5_snapshots(self):
        scanner = load_scanner()
        fake_snapshot = {
            'symbol': 'XAU/USD',
            'timeframe': '1H',
            'source': 'mt5_local_file',
            'completed_candle': {'time': '2026-10-03T06:00:00+00:00'},
            'candles': [{'time': '2026-10-03T06:00:00+00:00'}],
        }
        calls = []
        with patch.object(scanner, 'load_mt5_snapshot', return_value=fake_snapshot), \
             patch.object(scanner, 'call_rpc', side_effect=lambda payload: calls.append(payload) or {'status': 'WAIT', 'gate': {'decision': 'WAIT'}}):
            result = scanner.scan_once(symbols=['XAU/USD'], timeframes=['1H'], now=datetime.fromisoformat('2026-10-03T06:00:00+03:00'), force=True)
        self.assertEqual(result['scanned'], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['input_type'], 'mt5_autonomous_scanner')
        self.assertEqual(calls[0]['evidence_snapshot']['source'], 'mt5_local_file')
        self.assertEqual(result['alerts'], [])


if __name__ == '__main__':
    unittest.main()
