import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


class CaseSummaryTests(unittest.TestCase):
    def test_case_summary_reads_case_folder(self):
        store = load('case_store', 'skills/core/case_store.py')
        summary = load('case_summary', 'skills/core/case_summary.py')
        with tempfile.TemporaryDirectory() as tmp:
            case = store.create_case(
                root=Path(tmp),
                symbol='EUR/USD',
                timestamp='2026-10-03T07:32:57+03:00',
                sequence=1,
                rule_version=1,
                snapshot={'snapshot_id': 'snap-test', 'symbol': 'EUR/USD', 'timeframe': '4H'},
                gate={'decision': 'WAIT', 'evidence_grade': 'insufficient', 'patterns': []},
            )
            (Path(case['case_dir']) / 'nova_decision.md').write_text('👑 NOVA DECISION\n\nCase: EURUSD-20261003-001\nStatus: WAIT\n', encoding='utf-8')
            result = summary.summarize_case(Path(case['case_dir']))

        self.assertEqual(result['case_id'], 'EURUSD-20261003-001')
        self.assertEqual(result['symbol'], 'EUR/USD')
        self.assertEqual(result['status'], 'WAIT')
        self.assertEqual(result['snapshot_id'], 'snap-test')
        self.assertIn('👑 NOVA DECISION', result['telegram_text'])
        self.assertIn('EURUSD-20261003-001', result['telegram_text'])

if __name__ == '__main__':
    unittest.main()
