import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def test_text_pinbar_candidate_requires_structure_context(self):
        gate = rpc_server.evidence_gate({
            'symbol': 'GBP/USD',
            'timeframe': '1H',
            'chart_notes': '1H bullish pin bar rejection with long lower wick at support zone',
        })
        self.assertEqual(gate['decision'], 'DEBATE')
        self.assertIn('pinbar_rejection', gate['patterns'])

    def test_snapshot_pinbar_alone_waits_without_clean_structure(self):
        gate = rpc_server.evidence_gate({
            'symbol': 'XAU/USD',
            'timeframe': '4H',
            'now': '2026-10-03T02:00:00+00:00',
            'chart_notes': '',
            'evidence_snapshot': {
                'symbol': 'XAU/USD',
                'timeframe': '4H',
                'source': 'biquote',
                'data_timestamp': '2026-10-03T02:00:00+00:00',
                'completed_candle': {'time': '2026-10-03T00:00:00+00:00'},
                'candles': [
                    {'time': f'2026-10-{i:02d}T00:00:00+00:00', 'open': 1.1000, 'high': 1.1020, 'low': 1.0980, 'close': 1.1005}
                    for i in range(1, 29)
                ],
                'calculations': [
                    {'name': 'ema21', 'value': 1.1000},
                    {'name': 'pinbar', 'is_pinbar': True, 'direction': 'bearish'},
                ],
            },
        })
        self.assertEqual(gate['decision'], 'WAIT')
        self.assertEqual(gate['patterns'], [])
        self.assertIn('Pin-bar-only alert blocked', gate['unknowns'][0])

    def test_snapshot_clean_4h_break_retest_passes_with_levels(self):
        candles = []
        for i in range(20):
            candles.append({'time': f'2026-09-{i+1:02d}T00:00:00+00:00', 'open': 1.1010, 'high': 1.1040, 'low': 1.0950, 'close': 1.1000})
        candles.extend([
            {'time': '2026-09-21T00:00:00+00:00', 'open': 1.1000, 'high': 1.1010, 'low': 1.0940, 'close': 1.0920},
            {'time': '2026-09-22T00:00:00+00:00', 'open': 1.0920, 'high': 1.0940, 'low': 1.0890, 'close': 1.0910},
            {'time': '2026-09-23T00:00:00+00:00', 'open': 1.0910, 'high': 1.0952, 'low': 1.0900, 'close': 1.0948},
            {'time': '2026-09-24T00:00:00+00:00', 'open': 1.0948, 'high': 1.0960, 'low': 1.0920, 'close': 1.0930},
            {'time': '2026-09-25T00:00:00+00:00', 'open': 1.0930, 'high': 1.0940, 'low': 1.0910, 'close': 1.0920},
            {'time': '2026-09-26T00:00:00+00:00', 'open': 1.0920, 'high': 1.0930, 'low': 1.0900, 'close': 1.0905},
            {'time': '2026-09-27T00:00:00+00:00', 'open': 1.0905, 'high': 1.0920, 'low': 1.0890, 'close': 1.0895},
            {'time': '2026-09-28T00:00:00+00:00', 'open': 1.0895, 'high': 1.0910, 'low': 1.0870, 'close': 1.0880},
        ])
        gate = rpc_server.evidence_gate({
            'symbol': 'GBP/USD',
            'timeframe': '4H',
            'now': '2026-09-28T04:00:00+00:00',
            'evidence_snapshot': {
                'symbol': 'GBP/USD',
                'timeframe': '4H',
                'source': 'test',
                'data_timestamp': '2026-09-28T04:00:00+00:00',
                'completed_candle': {'time': '2026-09-28T00:00:00+00:00'},
                'candles': candles,
                'calculations': [{'name': 'ema21', 'value': 1.0960}],
            },
        })
        self.assertEqual(gate['decision'], 'DEBATE')
        self.assertIn('4h_21ema_break_retest', gate['patterns'])
        self.assertEqual(gate['direction'], 'bearish')
        self.assertIn('entry_zone', gate['levels'])

    def test_debate_setup_fetches_live_snapshot_when_missing(self):
        fake_snapshot = {
            'symbol': 'XAU/USD',
            'timeframe': '1H',
            'source': 'biquote',
            'data_timestamp': '2026-10-03T02:00:00+00:00',
            'completed_candle': {'time': '2026-10-03T01:00:00+00:00'},
            'candles': [{'time': '2026-10-03T01:00:00+00:00'}],
            'calculations': [{'name': 'pinbar', 'is_pinbar': True, 'direction': 'bullish'}],
        }
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(rpc_server, 'build_live_evidence_snapshot', return_value=fake_snapshot), \
             patch.object(rpc_server, 'run_hermes_agent', return_value='agent response'):
            result = rpc_server.debate_setup({
                'symbol': 'XAU/USD',
                'timeframe': '1H',
                'input_type': 'live_scan',
                'now': '2026-10-03T02:00:00+00:00',
                'case_root': tmp,
                'max_agents': 0,
            })
        self.assertEqual(result['gate']['decision'], 'WAIT')
        self.assertEqual(result['setup']['evidence_snapshot']['source'], 'biquote')

    def test_live_snapshot_scan_fails_closed_when_feed_is_stale(self):
        stale_snapshot = {
            'symbol': 'XAU/USD',
            'timeframe': '1H',
            'source': 'biquote',
            'data_timestamp': '2026-10-03T12:00:00+00:00',
            'completed_candle': {'time': '2026-10-03T06:00:00+00:00'},
            'candles': [{'time': '2026-10-03T06:00:00+00:00'}],
            'calculations': [{'name': 'pinbar', 'is_pinbar': True, 'direction': 'bullish'}],
        }
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(rpc_server, 'build_live_evidence_snapshot', return_value=stale_snapshot), \
             patch.object(rpc_server, 'run_hermes_agent', return_value='SHOULD NOT RUN'):
            result = rpc_server.debate_setup({
                'symbol': 'XAU/USD',
                'timeframe': '1H',
                'input_type': 'live_scan',
                'now': '2026-10-03T12:00:00+00:00',
                'case_root': tmp,
            })
        self.assertEqual(result['status'], 'WAIT')
        self.assertIn('stale_data', result['gate']['vetoes'])

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

    def test_debate_setup_writes_transcript_to_case_file(self):
        original = rpc_server.run_hermes_agent
        rpc_server.run_hermes_agent = lambda agent_id, *args, **kwargs: f'{agent_id} response'
        try:
            with tempfile.TemporaryDirectory() as tmp:
                result = rpc_server.debate_setup({
                    'symbol': 'XAU/USD',
                    'timeframe': '4H',
                    'chart_notes': '4H bullish break above resistance and retest to 21 EMA, candle close holding support',
                    'timestamp': '2026-10-03T07:32:57+03:00',
                    'case_sequence': 2,
                    'case_root': tmp,
                    'max_agents': 2,
                })
                debate_file = Path(result['case_dir']) / 'debate.json'
                self.assertTrue(debate_file.exists())
                import json
                debate = json.loads(debate_file.read_text())
                self.assertEqual(len(debate), len(result['transcript']))
                self.assertEqual(debate[0]['agent_id'], 'market_data')
        finally:
            rpc_server.run_hermes_agent = original

    def test_debate_setup_writes_nova_decision_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = rpc_server.debate_setup({
                'symbol': 'EUR/USD',
                'timeframe': '4H',
                'chart_notes': 'random sideways candles in the middle of range',
                'timestamp': '2026-10-03T07:32:57+03:00',
                'case_sequence': 3,
                'case_root': tmp,
                'max_agents': 2,
            })
            card = Path(result['case_dir']) / 'nova_decision.md'
            text = card.read_text()
            self.assertIn('👑 NOVA DECISION', text)
            self.assertIn('Case: EURUSD-20261003-003', text)
            self.assertIn('Status: WAIT', text)
            self.assertIn('Evidence Grade: insufficient', text)
            self.assertIn('Ozzi Action:', text)


if __name__ == '__main__':
    unittest.main()
