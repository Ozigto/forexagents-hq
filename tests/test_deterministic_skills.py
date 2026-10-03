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


class DeterministicSkillTests(unittest.TestCase):
    def test_ema21_calculates_expected_value(self):
        ema = load('ema', 'skills/market_data/ema.py')
        closes = list(range(1, 22))
        self.assertAlmostEqual(ema.ema(closes, 21), 11.0, places=6)
        extended = closes + [22]
        self.assertGreater(ema.ema(extended, 21), 11.0)

    def test_pinbar_ratio_detects_bullish_rejection(self):
        pinbar = load('pinbar', 'skills/patterns/pinbar_rejection.py')
        candle = {'open': 1.1000, 'high': 1.1020, 'low': 1.0900, 'close': 1.1010}
        result = pinbar.detect_pinbar(candle)
        self.assertTrue(result['is_pinbar'])
        self.assertEqual(result['direction'], 'bullish')
        self.assertGreater(result['lower_wick_ratio'], 0.6)

    def test_one_lot_risk_major_pair(self):
        risk = load('one_lot_risk', 'skills/risk/one_lot_risk.py')
        result = risk.calculate_one_lot_risk('EUR/USD', entry=1.1000, stop=1.0980)
        self.assertEqual(result['pip_distance'], 20.0)
        self.assertEqual(result['dollar_risk'], 200.0)
        self.assertTrue(result['fits_ozzi_rule'])

    def test_case_id_is_stable_format(self):
        case_id = load('case_id', 'skills/core/case_id.py')
        cid = case_id.build_case_id('EUR/USD', '2026-10-03T07:32:57+03:00', 1)
        self.assertEqual(cid, 'EURUSD-20261003-001')

if __name__ == '__main__':
    unittest.main()
