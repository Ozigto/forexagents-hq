import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BiquoteMarketDataTests(unittest.TestCase):
    def test_symbol_mapping(self):
        biquote = load('biquote', 'skills/market_data/biquote.py')
        self.assertEqual(biquote.to_biquote_symbol('XAU/USD'), 'XAUUSD')
        self.assertEqual(biquote.to_biquote_symbol('EUR/USD'), 'EURUSD')
        self.assertEqual(biquote.to_biquote_symbol('USDJPY'), 'USDJPY')

    def test_bars_to_closed_candles_drops_open_bar(self):
        biquote = load('biquote', 'skills/market_data/biquote.py')
        bars = [
            {'openTime': '2026-10-03T00:00:00Z', 'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'isOpen': False},
            {'openTime': '2026-10-03T01:00:00Z', 'open': 2, 'high': 3, 'low': 1.5, 'close': 2.5, 'isOpen': True},
        ]
        candles = biquote.bars_to_closed_candles(bars)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0]['time'], '2026-10-03T00:00:00+00:00')
        self.assertEqual(candles[0]['close'], 1.5)

    def test_build_live_snapshot_uses_fetcher_and_adds_calculations(self):
        biquote = load('biquote', 'skills/market_data/biquote.py')
        bars = []
        for i in range(25):
            day = 3 + (i // 24)
            hour = i % 24
            bars.append({
                'openTime': f'2026-10-{day:02d}T{hour:02d}:00:00Z',
                'open': 100 + i,
                'high': 101 + i,
                'low': 99 + i,
                'close': 100.5 + i,
                'isOpen': False,
            })
        with patch.object(biquote, 'fetch_bars', return_value=bars):
            snap = biquote.build_live_snapshot('XAU/USD', '1H', limit=25, now='2026-10-04T01:00:00+00:00')
        self.assertEqual(snap['symbol'], 'XAU/USD')
        self.assertEqual(snap['timeframe'], '1H')
        self.assertEqual(snap['source'], 'biquote')
        self.assertEqual(len(snap['candles']), 25)
        self.assertIn('snapshot_id', snap)
        calc_names = {c['name'] for c in snap['calculations']}
        self.assertIn('ema21', calc_names)


if __name__ == '__main__':
    unittest.main()
