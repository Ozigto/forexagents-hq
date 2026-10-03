import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


class EvidenceSnapshotTests(unittest.TestCase):
    def test_build_snapshot_has_required_identity_and_completed_candle(self):
        schema = load('evidence_schema', 'skills/core/evidence_schema.py')
        candles = [
            {'time': '2026-10-03T00:00:00+03:00', 'open': 1.10, 'high': 1.11, 'low': 1.09, 'close': 1.105},
            {'time': '2026-10-03T04:00:00+03:00', 'open': 1.105, 'high': 1.12, 'low': 1.10, 'close': 1.118},
        ]
        snap = schema.build_evidence_snapshot('EUR/USD', '4H', candles, data_timestamp='2026-10-03T08:05:00+03:00')
        self.assertEqual(snap['symbol'], 'EUR/USD')
        self.assertEqual(snap['timeframe'], '4H')
        self.assertEqual(snap['data_timestamp'], '2026-10-03T08:05:00+03:00')
        self.assertEqual(snap['completed_candle']['time'], '2026-10-03T04:00:00+03:00')
        self.assertIn('snapshot_id', snap)

    def test_data_quality_waits_on_stale_data(self):
        quality = load('freshness', 'skills/market_data/freshness.py')
        result = quality.check_data_quality(
            {
                'symbol': 'EUR/USD',
                'timeframe': '4H',
                'data_timestamp': '2026-10-03T08:05:00+03:00',
                'completed_candle': {'time': '2026-10-03T00:00:00+03:00'},
                'candles': [{'time': '2026-10-03T00:00:00+03:00'}],
            },
            now='2026-10-03T12:30:00+03:00',
        )
        self.assertEqual(result['decision'], 'WAIT')
        self.assertIn('stale_data', result['vetoes'])

    def test_data_quality_passes_fresh_completed_4h_data(self):
        quality = load('freshness', 'skills/market_data/freshness.py')
        result = quality.check_data_quality(
            {
                'symbol': 'XAU/USD',
                'timeframe': '4H',
                'data_timestamp': '2026-10-03T08:05:00+03:00',
                'completed_candle': {'time': '2026-10-03T04:00:00+03:00'},
                'candles': [
                    {'time': '2026-10-03T00:00:00+03:00'},
                    {'time': '2026-10-03T04:00:00+03:00'},
                ],
            },
            now='2026-10-03T08:10:00+03:00',
        )
        self.assertEqual(result['decision'], 'PASS')
        self.assertEqual(result['vetoes'], [])

if __name__ == '__main__':
    unittest.main()
