#!/usr/bin/env python3
"""Local Telegram polling bridge for ForexAgents HQ.

Uses the Telegram credential stored in n8n, decrypts it only in memory,
accepts commands only from Ozzi's allowed group/user, and never prints the bot token.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

N8N_ROOT = Path('/Volumes/AI-Brain/n8n-Automation')
N8N_DATA = N8N_ROOT / 'data' / '.n8n'
STATE_FILE = ROOT / '.telegram_bridge_state.json'
LOCAL_ENV = ROOT / '.env.telegram.local'
RPC_URL = 'http://127.0.0.1:18765/debate/setup'


def load_local_env(path: Path = LOCAL_ENV) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        data[key.strip()] = value.strip()
    return data


def evp_bytes_to_key(password: bytes, salt: bytes) -> tuple[bytes, bytes]:
    hash1 = hashlib.md5(password + salt).digest()
    hash2 = hashlib.md5(hash1 + password + salt).digest()
    iv = hashlib.md5(hash2 + password + salt).digest()
    return hash1 + hash2, iv


def get_telegram_token() -> str:
    """Read and decrypt the n8n Telegram credential in memory.

    Node's built-in crypto is used so the bridge does not need a Python
    crypto dependency. The token is returned to this process only and must
    never be printed.
    """
    node_code = r'''
const fs = require('fs');
const crypto = require('crypto');
const sqlite3 = require('sqlite3');
function decryptCBC(data, key) {
  const input = Buffer.from(data, 'base64');
  const salt = input.subarray(8, 16);
  const password = Buffer.concat([Buffer.from(key, 'binary'), salt]);
  const hash1 = crypto.createHash('md5').update(password).digest();
  const hash2 = crypto.createHash('md5').update(Buffer.concat([hash1, password])).digest();
  const iv = crypto.createHash('md5').update(Buffer.concat([hash2, password])).digest();
  const derivedKey = Buffer.concat([hash1, hash2]);
  const decipher = crypto.createDecipheriv('aes-256-cbc', derivedKey, iv);
  return Buffer.concat([decipher.update(input.subarray(16)), decipher.final()]).toString('utf8');
}
const settings = JSON.parse(fs.readFileSync('/Volumes/AI-Brain/n8n-Automation/data/.n8n/config', 'utf8'));
const db = new sqlite3.Database('/Volumes/AI-Brain/n8n-Automation/data/.n8n/database.sqlite');
db.get("select data from credentials_entity where type='telegramApi' order by updatedAt desc limit 1", (err, row) => {
  if (err) { console.error(err.message); process.exit(2); }
  if (!row) { console.error('Telegram credential not found in n8n'); process.exit(3); }
  const decrypted = JSON.parse(decryptCBC(row.data, settings.encryptionKey));
  const token = decrypted.accessToken || decrypted.botToken || decrypted.token;
  if (!token) { console.error('Telegram credential token field not found'); process.exit(4); }
  process.stdout.write(token);
  db.close();
});
'''
    proc = subprocess.run(
        ['node', '-e', node_code],
        cwd=str(N8N_ROOT / 'runtime'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or 'Could not read Telegram credential')
    token = proc.stdout.strip()
    if not token:
        raise RuntimeError('Telegram credential token field not found')
    return token


def telegram_api(token: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f'https://api.telegram.org/bot{token}/{method}'
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def parse_command(text: str | None) -> dict[str, Any] | None:
    if not text or not text.startswith('/'):
        return None
    parts = text.strip().split(maxsplit=1)
    raw = parts[0][1:]
    command = raw.split('@', 1)[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ''
    result: dict[str, Any] = {'command': command, 'args': args}
    if command == 'scan':
        tokens = args.split()
        symbol = 'XAU/USD'
        timeframe = '4H'
        if tokens and (len(tokens[0].replace('/', '')) == 6 or tokens[0].upper().replace('/', '') == 'XAUUSD'):
            symbol = tokens.pop(0).upper().replace('XAUUSD', 'XAU/USD')
            if '/' not in symbol and len(symbol) == 6:
                symbol = symbol[:3] + '/' + symbol[3:]
        if tokens and tokens[0].upper() in {'1H', '4H', 'H1', 'H4'}:
            timeframe = tokens.pop(0).upper().replace('H1', '1H').replace('H4', '4H')
        result.update({'symbol': symbol, 'timeframe': timeframe, 'args': ' '.join(tokens)})
    return result


def is_allowed_update(update: dict[str, Any], allowed_chat_id: int, allowed_user_id: int) -> bool:
    message = update.get('message') or {}
    chat = message.get('chat') or {}
    sender = message.get('from') or {}
    return chat.get('id') == allowed_chat_id and sender.get('id') == allowed_user_id


def build_status_reply(rpc_ok: bool, n8n_note: str = 'local polling bridge') -> str:
    return '\n'.join([
        '👑 ForexAgents HQ status',
        f'RPC brain: {"online" if rpc_ok else "offline"}',
        f'Telegram bridge: {n8n_note}',
        'n8n send path: not enabled for auto-posting yet',
        'Auto-trading: disabled',
    ])


def build_visible_agent_status(symbol: str, timeframe: str) -> str:
    """Natural room-style opening message for a scan.

    This is not fake analysis. It tells Ozzi the desk is opening the case
    and which agents are about to challenge the setup.
    """
    return '\n'.join([
        f'🏢 ForexAgents HQ company room — {symbol} {timeframe}',
        '',
        '📊 👨‍💼 Atlas: I am opening the case. First question: do we have real candles, or only a note?',
        '🧭 👩‍💼 Aurora: I’ll read the higher-timeframe bias, but I need clean structure before I lean bullish or bearish.',
        '🕒 👩‍💼 Selena: I’m watching the session window. Timing matters; a good pattern at bad timing is still danger.',
        '📐 👩‍🏫 Maya: I’ll mark structure — break, retest, support, resistance, invalidation.',
        '🔎 👩‍🔬 Iris: I’ll only pass Ozzi’s two patterns: 4H EMA21 break/retest or 1H/4H pin-bar rejection.',
        '📰 👩‍💻 Echo: I’m checking news risk. If there is red news near the setup, the room slows down.',
        '🐂 👨‍💼 Titan: If evidence passes, I’ll build the bull case — but I won’t force one.',
        '🐻 👩‍💼 Vega: I’ll attack the setup. If it’s weak, I’ll say no before money is at risk.',
        '🧠 🧔 Sage: I’ll judge the debate and separate facts from opinions.',
        '🧑‍💼 👩‍💼 Ava: I’ll think like the trader: entry, stop, target, and whether this is worth Ozzi’s shot.',
        '⚔️ 👨‍✈️ Blaze: I’ll look for opportunity, but only after the gate proves there is a real setup.',
        '🛡 👩‍⚕️ Gaia: I’m protecting capital first. Bad evidence means no trade.',
        '⚖️ 🧑‍⚖️ Balance: I’ll weigh risk versus reward without hype.',
        '📲 👩‍💻 Rhea: I’ll keep the group readable — full room visible, no useless spam.',
        '🧪 👩‍🔬 Lyra: I’ll make sure the case is saved for replay and review.',
        '👑 NOVA: Good. Whole desk is present. If the evidence is weak, we WAIT. If it is real, the debate starts.',
    ])[:3900]


def build_wait_room_summary(rpc: dict[str, Any]) -> str:
    gate = rpc.get('gate') or {}
    reasons = gate.get('reasons') or []
    unknowns = gate.get('unknowns') or []
    reason = reasons[0] if reasons else 'The setup did not pass the first evidence gate.'
    unknown = unknowns[0] if unknowns else 'Required candle/pattern evidence is missing.'
    return '\n\n'.join([
        f"🏢 ForexAgents HQ — {rpc.get('case_id', 'case open')}",
        '📊 👨‍💼 Atlas: I’m not seeing enough verified market evidence here. If this is only a short note, I cannot turn it into candles, EMA values, or structure levels.',
        f'🔎 👩‍🔬 Iris: Pattern gate says WAIT. {reason}',
        f'🐻 👩‍💼 Vega: I agree with stopping early. The strongest objection is: {unknown}',
        '🧠 🧔 Sage: Then we are not spending the full desk on a weak or unclear setup. That is discipline, not failure.',
        f"👑 NOVA: WAIT. Evidence grade: {gate.get('evidence_grade', 'insufficient')}. Ozzi, give me a real setup note or structured candle evidence if you want the full team debate.",
    ])[:3900]


def rpc_health() -> bool:
    try:
        with urllib.request.urlopen('http://127.0.0.1:18765/health', timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return bool(data.get('ok'))
    except Exception:
        return False


def call_rpc_scan(symbol: str, timeframe: str, notes: str) -> dict[str, Any]:
    payload = {
        'symbol': symbol,
        'timeframe': timeframe,
        'input_type': 'telegram_polling_bridge',
        'chart_notes': notes or 'Telegram /scan command with no notes.',
        'ozzi_notes': 'Use Ozzi rules only. No auto-trading. Return WAIT if evidence is insufficient.',
        'max_agents': 8,
        'max_cross_questions': 6,
        'agent_timeout_seconds': 120,
    }
    req = urllib.request.Request(
        RPC_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read().decode('utf-8'))


def format_scan_reply(rpc: dict[str, Any]) -> str:
    gate = rpc.get('gate') or {}
    text = rpc.get('telegram_text') or ''
    header = '\n'.join([
        '🏢 ForexAgents HQ scan complete',
        f"Case: {rpc.get('case_id', 'none')}",
        f"Status: {gate.get('status') or gate.get('decision') or 'UNKNOWN'}",
        f"Evidence: {gate.get('evidence_grade', 'unknown')}",
    ])
    if not rpc.get('transcript') and (gate.get('status') == 'WAIT' or gate.get('decision') == 'WAIT'):
        body = build_wait_room_summary(rpc)
    elif text:
        body = text[:3200]
    else:
        reasons = gate.get('reasons') or []
        body = '\n'.join(reasons) or 'No detailed text returned.'
    return f'{header}\n\n{body}'[:3900]


def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def get_updates(token: str, offset: int | None, timeout: int = 25) -> list[dict[str, Any]]:
    payload = {'timeout': timeout, 'limit': 20, 'allowed_updates': ['message']}
    if offset is not None:
        payload['offset'] = offset
    data = telegram_api(token, 'getUpdates', payload)
    if not data.get('ok'):
        raise RuntimeError(data.get('description') or 'Telegram getUpdates failed')
    return data.get('result') or []


def bridge_once(token: str, allowed_chat_id: int, allowed_user_id: int, state: dict[str, Any]) -> int:
    offset = state.get('offset')
    updates = get_updates(token, offset=offset, timeout=5)
    for update in updates:
        state['offset'] = max(int(state.get('offset') or 0), int(update['update_id']) + 1)
        if not is_allowed_update(update, allowed_chat_id, allowed_user_id):
            continue
        message = update.get('message') or {}
        chat_id = (message.get('chat') or {}).get('id')
        if chat_id is None:
            continue
        cmd = parse_command(message.get('text'))
        if not cmd:
            continue
        if cmd['command'] == 'status':
            telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': build_status_reply(rpc_health())})
        elif cmd['command'] == 'scan':
            telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': build_visible_agent_status(cmd['symbol'], cmd['timeframe'])})
            try:
                rpc = call_rpc_scan(cmd['symbol'], cmd['timeframe'], cmd.get('args', ''))
                telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': format_scan_reply(rpc)})
            except Exception as exc:
                telegram_api(token, 'sendMessage', {'chat_id': chat_id, 'text': f'⚠️ ForexAgents scan failed safely: {exc}'[:3900]})
    save_state(state)
    return len(updates)


def initialize_offset_to_latest(token: str, state: dict[str, Any]) -> None:
    if 'offset' in state:
        return
    updates = get_updates(token, offset=None, timeout=1)
    if updates:
        state['offset'] = max(int(u['update_id']) for u in updates) + 1
    else:
        state['offset'] = 0
    save_state(state)


def main() -> int:
    env = load_local_env()
    allowed_chat_id = int(env.get('FOREXAGENTS_TELEGRAM_GROUP_CHAT_ID', '0'))
    allowed_user_id = int(env.get('FOREXAGENTS_TELEGRAM_OWNER_USER_ID', '0'))
    if not allowed_chat_id or not allowed_user_id:
        raise RuntimeError('Missing local Telegram allowlist in .env.telegram.local')
    token = get_telegram_token()
    state = load_state()
    initialize_offset_to_latest(token, state)
    print('ForexAgents Telegram polling bridge running')
    print(f'allowed_chat_id={allowed_chat_id}')
    print(f'allowed_user_id={allowed_user_id}')
    print('token=REDACTED')
    while True:
        try:
            bridge_once(token, allowed_chat_id, allowed_user_id, state)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            print(f'bridge_error={exc}', file=sys.stderr)
            time.sleep(5)


if __name__ == '__main__':
    raise SystemExit(main())
