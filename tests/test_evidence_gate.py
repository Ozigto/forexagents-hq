import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('rpc_server', ROOT / 'rpc_server.py')
rpc_server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rpc_server)


class EvidenceGateTests(unittest.TestCase):
    def test_empty_chart_waits_without_calling_agents(self):
        calls = []
        original = rpc_server.run_hermes_agent
        rpc_server.run_hermes_agent = lambda *args, **kwargs: calls.append(args) or 'SHOULD NOT RUN'
        try:
            result = rpc_server.debate_setup({
                'symbol': 'EUR/USD',
                'timeframe': '4H',
                'chart_notes': 'random sideways candles in the middle of range',
                'max_agents': 2,
            })
        finally:
            rpc_server.run_hermes_agent = original

        self.assertTrue(result['ok'])
        self.assertEqual(result['status'], 'WAIT')
        self.assertEqual(result['gate']['decision'], 'WAIT')
        self.assertEqual(result['gate']['patterns'], [])
        self.assertEqual(calls, [])
        self.assertIn('no plausible allowed pattern', result['telegram_text'].lower())

    def test_break_retest_candidate_passes_gate(self):
        gate = rpc_server.evidence_gate({
            'symbol': 'XAU/USD',
            'timeframe': '4H',
            'chart_notes': '4H bullish break above resistance, pullback retest to 21 EMA, candle close holding support',
        })
        self.assertEqual(gate['decision'], 'DEBATE')
        self.assertIn('4h_21ema_break_retest', gate['patterns'])
        self.assertEqual(gate['evidence_grade'], 'mixed')

    def test_pinbar_candidate_passes_gate(self):
        gate = rpc_server.evidence_gate({
            'symbol': 'GBP/USD',
            'timeframe': '1H',
            'chart_notes': '1H bullish pin bar rejection with long lower wick at support zone',
        })
        self.assertEqual(gate['decision'], 'DEBATE')
        self.assertIn('pinbar_rejection', gate['patterns'])

    def test_stale_evidence_snapshot_waits_without_calling_agents(self):
        calls = []
        original = rpc_server.run_hermes_agent
        rpc_server.run_hermes_agent = lambda *args, **kwargs: calls.append(args) or 'SHOULD NOT RUN'
        try:
            result = rpc_server.debate_setup({
                'symbol': 'XAU/USD',
                'timeframe': '4H',
                'chart_notes': '4H bullish break above resistance and retest to 21 EMA, candle close holding support',
                'evidence_snapshot': {
                    'symbol': 'XAU/USD',
                    'timeframe': '4H',
                    'data_timestamp': '2026-10-03T08:05:00+03:00',
                    'completed_candle': {'time': '2026-10-03T00:00:00+03:00'},
                    'candles': [{'time': '2026-10-03T00:00:00+03:00'}],
                },
                'now': '2026-10-03T12:30:00+03:00',
                'max_agents': 2,
            })
        finally:
            rpc_server.run_hermes_agent = original

        self.assertEqual(result['status'], 'WAIT')
        self.assertIn('stale_data', result['gate']['vetoes'])
        self.assertEqual(calls, [])
        self.assertIn('data quality failed', result['telegram_text'].lower())

    def test_debate_setup_creates_case_file_on_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = rpc_server.debate_setup({
                'symbol': 'EUR/USD',
                'timeframe': '4H',
                'chart_notes': 'random sideways candles in the middle of range',
                'timestamp': '2026-10-03T07:32:57+03:00',
                'case_sequence': 1,
                'case_root': tmp,
                'max_agents': 2,
            })
            self.assertEqual(result['status'], 'WAIT')
            self.assertEqual(result['case_id'], 'EURUSD-20261003-001')
            self.assertTrue(Path(result['case_dir']).exists())
            self.assertTrue((Path(result['case_dir']) / 'case.json').exists())
            self.assertTrue((Path(result['case_dir']) / 'gate.json').exists())


if __name__ == '__main__':
    unittest.main()
