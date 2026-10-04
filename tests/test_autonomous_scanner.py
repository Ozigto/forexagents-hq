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
             patch.object(scanner, 'check_mt5_health', return_value={'ok': True, 'reason': 'ok'}), \
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
             patch.object(scanner, 'check_mt5_health', return_value={'ok': True, 'reason': 'ok'}), \
             patch.object(scanner, 'call_rpc', side_effect=lambda payload: calls.append(payload) or {'status': 'WAIT', 'gate': {'decision': 'WAIT'}}):
            result = scanner.scan_once(symbols=['XAU/USD'], timeframes=['1H'], now=datetime.fromisoformat('2026-10-03T06:00:00+03:00'), force=True)
        self.assertEqual(result['scanned'], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['input_type'], 'mt5_autonomous_scanner')
        self.assertEqual(calls[0]['evidence_snapshot']['source'], 'mt5_local_file')
        self.assertEqual(result['alerts'], [])

    def test_autonomous_alert_text_is_safe_and_clear(self):
        scanner = load_scanner()
        alert = {
            'symbol': 'XAU/USD',
            'timeframe': '4H',
            'result': {
                'case_id': 'XAUUSD-20261005-001',
                'gate': {'status': 'WATCH', 'evidence_grade': 'strong'},
                'telegram_text': '📌 21 EMA BREAK + RETEST SETUP\nDecision: WATCH',
            },
        }
        text = scanner.format_autonomous_alert(alert)
        self.assertIn('ForexAgents HQ autonomous alert', text)
        self.assertIn('Pair: XAU/USD', text)
        self.assertIn('No auto-trading', text)

    def test_send_telegram_alerts_deduplicates(self):
        scanner = load_scanner()
        sent = []

        class FakeBridge:
            @staticmethod
            def load_local_env():
                return {'FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID': '-123'}

            @staticmethod
            def get_telegram_token():
                return 'REDACTED_TEST_TOKEN'

            @staticmethod
            def telegram_api(token, method, payload):
                sent.append((token, method, payload))
                return {'ok': True}

        alert = {
            'symbol': 'XAU/USD',
            'timeframe': '4H',
            'result': {
                'case_id': 'XAUUSD-20261005-001',
                'gate': {'status': 'WATCH', 'evidence_grade': 'strong'},
                'setup': {'evidence_snapshot': {'completed_candle': {'time': '2026-10-05T08:00:00+00:00'}}},
            },
        }
        state = {'sent_alert_keys': []}
        with patch.object(scanner, '_load_telegram_bridge_module', return_value=FakeBridge), \
             patch.object(scanner, 'save_state', lambda s: None):
            self.assertEqual(scanner.send_telegram_alerts([alert], state=state), 1)
            self.assertEqual(scanner.send_telegram_alerts([alert], state=state), 0)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0][1], 'sendMessage')

    def test_mt5_health_detects_missing_file(self):
        scanner = load_scanner()
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / 'missing.csv'
            health = scanner.check_mt5_health(path=missing, now=datetime.fromisoformat('2026-10-05T06:00:00+03:00'))
        self.assertFalse(health['ok'])
        self.assertEqual(health['reason'], 'mt5_candle_file_missing')

    def test_mt5_health_detects_missing_groups(self):
        scanner = load_scanner()
        csv_text = 'symbol,timeframe,time,open,high,low,close,tick_volume,is_closed,server_time\nXAUUSD.,H1,2026.10.05 06:00:00,1,2,0.5,1.5,100,true,2026.10.05 06:05:00\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nova_forex_candles.csv'
            path.write_text(csv_text, encoding='utf-8')
            health = scanner.check_mt5_health(path=path, now=datetime.fromisoformat('2026-10-05T06:10:00+03:00'))
        self.assertFalse(health['ok'])
        self.assertEqual(health['reason'], 'mt5_missing_symbol_timeframes')
        self.assertGreater(len(health['missing_groups']), 1)

    def test_mt5_health_ok_on_weekend_with_friday_candles(self):
        scanner = load_scanner()
        rows = ['symbol,timeframe,time,open,high,low,close,tick_volume,is_closed,server_time']
        for symbol in scanner.WATCHLIST:
            broker_symbol = symbol.replace('/', '') + '.'
            for tf in ('H1', 'H4'):
                rows.append(f'{broker_symbol},{tf},2026.10.02 22:00:00,1,2,0.5,1.5,100,true,2026.10.04 04:00:00')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nova_forex_candles.csv'
            path.write_text('\n'.join(rows) + '\n', encoding='utf-8')
            health = scanner.check_mt5_health(path=path, now=datetime.fromisoformat('2026-10-04T06:00:00+03:00'))
        self.assertTrue(health['ok'])
        self.assertEqual(health['closed_groups'], 16)

    def test_mt5_health_detects_stale_open_market_data(self):
        scanner = load_scanner()
        rows = ['symbol,timeframe,time,open,high,low,close,tick_volume,is_closed,server_time']
        for symbol in scanner.WATCHLIST:
            broker_symbol = symbol.replace('/', '') + '.'
            for tf in ('H1', 'H4'):
                rows.append(f'{broker_symbol},{tf},2026.10.02 22:00:00,1,2,0.5,1.5,100,true,2026.10.05 06:00:00')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nova_forex_candles.csv'
            path.write_text('\n'.join(rows) + '\n', encoding='utf-8')
            health = scanner.check_mt5_health(path=path, now=datetime.fromisoformat('2026-10-05T10:00:00+03:00'))
        self.assertFalse(health['ok'])
        self.assertEqual(health['reason'], 'mt5_candles_stale')

    def test_send_health_alert_deduplicates(self):
        scanner = load_scanner()
        sent = []

        class FakeBridge:
            @staticmethod
            def load_local_env():
                return {'FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID': '-123'}

            @staticmethod
            def get_telegram_token():
                return 'REDACTED_TEST_TOKEN'

            @staticmethod
            def telegram_api(token, method, payload):
                sent.append((token, method, payload))
                return {'ok': True}

        state = {'sent_alert_keys': [], 'health_alert_keys': []}
        health = {'ok': False, 'reason': 'mt5_candle_file_missing'}
        with patch.object(scanner, '_load_telegram_bridge_module', return_value=FakeBridge), \
             patch.object(scanner, 'save_state', lambda s: None):
            self.assertEqual(scanner.send_health_alert_if_needed(health, state=state), 1)
            self.assertEqual(scanner.send_health_alert_if_needed(health, state=state), 0)
        self.assertEqual(len(sent), 1)
        self.assertIn('health warning', sent[0][2]['text'])

    def test_status_report_shows_company_awake(self):
        scanner = load_scanner()
        health = {
            'ok': True,
            'closed_groups': 16,
            'closed_rows': 1920,
            'latest_candle_time': '2026-10-02T22:00:00+00:00',
        }
        text = scanner.format_status_report(
            health,
            now=datetime.fromisoformat('2026-10-04T06:00:00+03:00'),
            rpc_ok=True,
        )
        self.assertIn('ForexAgents HQ is awake', text)
        self.assertIn('RPC brain: OK', text)
        self.assertIn('MT5 candles: OK', text)
        self.assertIn('Closed groups: 16/16', text)
        self.assertIn('Auto-trading: OFF', text)

    def test_send_daily_status_report_deduplicates_by_athens_date(self):
        scanner = load_scanner()
        sent = []

        class FakeBridge:
            @staticmethod
            def load_local_env():
                return {'FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID': '-123'}

            @staticmethod
            def get_telegram_token():
                return 'REDACTED_TEST_TOKEN'

            @staticmethod
            def telegram_api(token, method, payload):
                sent.append((token, method, payload))
                return {'ok': True}

        state = {'sent_alert_keys': [], 'health_alert_keys': []}
        health = {'ok': True, 'closed_groups': 16, 'closed_rows': 1920}
        with patch.object(scanner, '_load_telegram_bridge_module', return_value=FakeBridge), \
             patch.object(scanner, 'rpc_health', return_value=True), \
             patch.object(scanner, 'save_state', lambda s: None):
            self.assertEqual(scanner.send_daily_status_report_if_needed(health, now=datetime.fromisoformat('2026-10-04T06:00:00+03:00'), state=state), 1)
            self.assertEqual(scanner.send_daily_status_report_if_needed(health, now=datetime.fromisoformat('2026-10-04T19:00:00+03:00'), state=state), 0)
            self.assertEqual(scanner.send_daily_status_report_if_needed(health, now=datetime.fromisoformat('2026-10-05T06:00:00+03:00'), state=state), 1)
        self.assertEqual(len(sent), 2)
        self.assertIn('ForexAgents HQ is awake', sent[0][2]['text'])


if __name__ == '__main__':
    unittest.main()
