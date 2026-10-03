import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

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

    def test_visible_agent_status_shows_company_room(self):
        bridge = load_bridge()
        text = bridge.build_visible_agent_status('XAU/USD', '4H')
        self.assertIn('ForexAgents HQ company room', text)
        self.assertIn('📊 Atlas:', text)
        self.assertIn('🧭 Aurora:', text)
        self.assertIn('🕒 Selena:', text)
        self.assertIn('📐 Maya:', text)
        self.assertIn('🔎 Iris:', text)
        self.assertIn('📰 Echo:', text)
        self.assertIn('🐂 Titan:', text)
        self.assertIn('🐻 Vega:', text)
        self.assertIn('🧠 Sage:', text)
        self.assertIn('🧑‍💼 Ava:', text)
        self.assertIn('⚔️ Blaze:', text)
        self.assertIn('🛡 Gaia:', text)
        self.assertIn('⚖️ Balance:', text)
        self.assertIn('👑 NOVA:', text)
        self.assertIn('📲 Rhea:', text)
        self.assertIn('🧪 Lyra:', text)
        self.assertIn('I am opening the case', text)
        self.assertNotIn('checking...', text.lower())

    def test_wait_visibility_summary_shows_agents_even_without_debate(self):
        bridge = load_bridge()
        rpc = {
            'case_id': 'XAUUSD-20261003-001',
            'gate': {
                'status': 'WAIT',
                'evidence_grade': 'insufficient',
                'reasons': ['No plausible allowed pattern detected before LLM debate.'],
                'unknowns': ['No deterministic 4H 21 EMA break/retest candidate found.'],
            },
            'transcript': [],
        }
        text = bridge.format_scan_reply(rpc)
        self.assertIn('📊 Atlas:', text)
        self.assertIn('🔎 Iris:', text)
        self.assertIn('🐻 Vega:', text)
        self.assertIn('👑 NOVA:', text)
        self.assertIn('No plausible allowed pattern detected', text)
        self.assertIn('not spending the full desk', text)

    def test_scan_sends_team_card_before_room_text(self):
        bridge = load_bridge()
        state = {}
        update = {
            'update_id': 100,
            'message': {
                'chat': {'id': -5570804166, 'type': 'group', 'title': 'ForexAgents HQ'},
                'from': {'id': 6245975134},
                'text': '/scan XAU/USD 1H bullish pin bar rejection',
            },
        }
        sent = []

        def fake_api(token, method, payload=None):
            sent.append((method, payload))
            return {'ok': True, 'result': [{'update_id': 100, 'message': update['message']}]} if method == 'getUpdates' else {'ok': True}

        def fake_photo(token, chat_id, photo_path, caption=''):
            sent.append(('sendPhoto', {'chat_id': chat_id, 'photo_path': str(photo_path), 'caption': caption}))
            return {'ok': True}

        with patch.object(bridge, 'get_updates', return_value=[update]), \
             patch.object(bridge, 'telegram_api', side_effect=fake_api), \
             patch.object(bridge, 'telegram_send_photo', side_effect=fake_photo), \
             patch.object(bridge, 'build_team_card_safe', return_value=ROOT / 'assets' / 'generated' / 'test_card.png'), \
             patch.object(bridge, 'call_rpc_scan', return_value={'gate': {'status': 'WAIT', 'evidence_grade': 'insufficient'}, 'transcript': []}), \
             patch.object(bridge, 'save_state'):
            bridge.bridge_once('fake-token', -5570804166, 6245975134, state)

        methods = [item[0] for item in sent]
        self.assertEqual(methods[0], 'sendPhoto')
        self.assertEqual(methods[1], 'sendMessage')
        self.assertIn('company room', sent[1][1]['text'])


if __name__ == '__main__':
    unittest.main()
