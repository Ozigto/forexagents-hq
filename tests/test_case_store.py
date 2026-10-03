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


class CaseStoreTests(unittest.TestCase):
    def test_create_case_writes_required_files(self):
        store = load('case_store', 'skills/core/case_store.py')
        with tempfile.TemporaryDirectory() as tmp:
            case = store.create_case(
                root=Path(tmp),
                symbol='EUR/USD',
                timestamp='2026-10-03T07:32:57+03:00',
                sequence=1,
                rule_version=1,
                snapshot={'snapshot_id': 'snap-test', 'symbol': 'EUR/USD'},
                gate={'decision': 'WAIT', 'vetoes': ['stale_data']},
            )
            case_dir = Path(case['case_dir'])
            self.assertEqual(case['case_id'], 'EURUSD-20261003-001')
            self.assertTrue((case_dir / 'case.json').exists())
            self.assertTrue((case_dir / 'snapshot.json').exists())
            self.assertTrue((case_dir / 'gate.json').exists())
            self.assertTrue((case_dir / 'nova_decision.md').exists())
            self.assertTrue((case_dir / 'review.md').exists())

    def test_append_event_preserves_history(self):
        store = load('case_store', 'skills/core/case_store.py')
        with tempfile.TemporaryDirectory() as tmp:
            case = store.create_case(
                root=Path(tmp),
                symbol='XAU/USD',
                timestamp='2026-10-03T07:32:57+03:00',
                sequence=2,
                rule_version=1,
                snapshot={'snapshot_id': 'snap-gold'},
                gate={'decision': 'DEBATE'},
            )
            store.append_event(Path(case['case_dir']), 'nova_status', {'status': 'WATCH'})
            store.append_event(Path(case['case_dir']), 'ozzi_decision', {'decision': 'WAIT'})
            events = store.read_events(Path(case['case_dir']))
            self.assertEqual([e['type'] for e in events], ['case_created', 'nova_status', 'ozzi_decision'])

if __name__ == '__main__':
    unittest.main()
