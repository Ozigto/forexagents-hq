import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_bridge():
    spec = importlib.util.spec_from_file_location('telegram_polling_bridge', ROOT / 'scripts' / 'telegram_polling_bridge.py')
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TelegramPollingBridgeTests(unittest.TestCase):
    def test_parse_status_command(self):
        bridge = load_bridge()
        cmd = bridge.parse_command('/status@ozzi_nova_bot')
        self.assertEqual(cmd['command'], 'status')
        self.assertEqual(cmd['args'], '')

    def test_parse_scan_defaults_symbol_and_timeframe(self):
        bridge = load_bridge()
        cmd = bridge.parse_command('/scan XAU/USD 4H test')
        self.assertEqual(cmd['command'], 'scan')
        self.assertEqual(cmd['symbol'], 'XAU/USD')
        self.assertEqual(cmd['timeframe'], '4H')
        self.assertEqual(cmd['args'], 'test')

    def test_allowlist_requires_group_and_user(self):
        bridge = load_bridge()
        update = {
            'message': {
                'chat': {'id': -5570804166, 'type': 'group', 'title': 'ForexAgents HQ'},
                'from': {'id': 6245975134},
                'text': '/status',
            }
        }
        self.assertTrue(bridge.is_allowed_update(update, allowed_chat_id=-5570804166, allowed_user_id=6245975134))
        self.assertFalse(bridge.is_allowed_update(update, allowed_chat_id=-1, allowed_user_id=6245975134))
        self.assertFalse(bridge.is_allowed_update(update, allowed_chat_id=-5570804166, allowed_user_id=1))

    def test_status_reply_is_safe(self):
        bridge = load_bridge()
        text = bridge.build_status_reply(rpc_ok=True, n8n_note='polling bridge')
        self.assertIn('ForexAgents HQ status', text)
        self.assertIn('RPC brain: online', text)
        self.assertIn('polling bridge', text)
        self.assertNotIn('token', text.lower())


if __name__ == '__main__':
    unittest.main()
