import importlib.util
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class MT5FilesTests(unittest.TestCase):
    def test_parse_mt5_candles_csv_groups_closed_candles(self):
        mt5 = load('mt5_files', 'skills/market_data/mt5_files.py')
        csv_text = '''symbol,timeframe,time,open,high,low,close,tick_volume,is_closed,server_time\nXAUUSD.,H1,2026.10.03 09:00:00,100,110,95,108,123,true,2026.10.03 10:05:00\nXAUUSD.,H1,2026.10.03 10:00:00,108,111,107,110,88,false,2026.10.03 10:05:00\nEURUSD.,H4,2026.10.03 08:00:00,1.1,1.2,1.0,1.15,99,true,2026.10.03 12:05:00\n'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nova_forex_candles.csv'
            path.write_text(csv_text, encoding='utf-8')
            grouped = mt5.read_mt5_candles(path)
        self.assertIn(('XAU/USD', '1H'), grouped)
        self.assertEqual(len(grouped[('XAU/USD', '1H')]), 1)
        self.assertEqual(grouped[('XAU/USD', '1H')][0]['time'], '2026-10-03T09:00:00+00:00')
        self.assertIn(('EUR/USD', '4H'), grouped)

    def test_build_snapshot_adds_ema_and_pinbar(self):
        mt5 = load('mt5_files', 'skills/market_data/mt5_files.py')
        candles = []
        for i in range(25):
            candles.append({
                'time': f'2026-10-03T{i%24:02d}:00:00+00:00',
                'open': 100 + i,
                'high': 104 + i,
                'low': 99 + i,
                'close': 103 + i,
                'tick_volume': 100 + i,
            })
        snap = mt5.build_snapshot_from_candles('XAU/USD', '1H', candles, data_timestamp='2026-10-04T01:00:00+00:00')
        self.assertEqual(snap['symbol'], 'XAU/USD')
        self.assertEqual(snap['source'], 'mt5_local_file')
        self.assertIn('snapshot_id', snap)
        names = {c['name'] for c in snap['calculations']}
        self.assertIn('ema21', names)
        self.assertIn('pinbar', names)


if __name__ == '__main__':
    unittest.main()
