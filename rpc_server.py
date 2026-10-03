#!/usr/bin/env python3
"""ForexAgents local RPC server.

n8n calls this server over HTTP. The server owns the skilled-agent brain:
- loads Ozzi's trading rules
- runs TradingAgents-style conversation stages
- calls Hermes/NOVA for real agent reasoning
- returns agent messages for Telegram

No auto-trading. Signals/research only.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
HERMES_BIN = Path('/Volumes/AI-Brain/hermes/hermes-agent/.hermes/bin/hermes')
HERMES_HOME = Path('/Volumes/AI-Brain/hermes')

AGENT_ORDER = {
    'analysts': ['market_data', 'htf_bias', 'session_timing', 'structure', 'pattern', 'news'],
    'research_debate': ['bull', 'bear', 'bull', 'bear', 'research_manager'],
    'trader': ['trader'],
    'risk_debate': ['aggressive_risk', 'conservative_risk', 'neutral_risk'],
    'boss': ['nova_boss'],
}

DISPLAY = {
    'market_data': ('📊', 'Atlas'),
    'htf_bias': ('🧭', 'Orion'),
    'session_timing': ('🕒', 'Chronos'),
    'structure': ('📐', 'Mason'),
    'pattern': ('🔎', 'Hunter'),
    'news': ('📰', 'Echo'),
    'bull': ('🐂', 'Titan'),
    'bear': ('🐻', 'Vega'),
    'research_manager': ('🧠', 'Sage'),
    'trader': ('🧑‍💼', 'Ace'),
    'aggressive_risk': ('⚔️', 'Blitz'),
    'conservative_risk': ('🛡', 'Guard'),
    'neutral_risk': ('⚖️', 'Balance'),
    'nova_boss': ('👑', 'NOVA'),
}

DISPLAY_TO_AGENT = {display.lower(): agent_id for agent_id, (_emoji, display) in DISPLAY.items()}



def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def load_agent(agent_id: str) -> dict[str, str]:
    return {
        'id': agent_id,
        'yaml': read_text(ROOT / 'agents' / f'{agent_id}.yaml'),
        'prompt': read_text(ROOT / 'prompts' / f'{agent_id}.md'),
    }


def run_hermes_agent(agent_id: str, setup: dict[str, Any], transcript: list[dict[str, str]], extra_task: str | None = None) -> str:
    """Call Hermes for one agent response."""
    emoji, display = DISPLAY.get(agent_id, ('🤖', agent_id))
    agent = load_agent(agent_id)
    rules = read_text(ROOT / 'RULES.yaml')
    protocol = read_text(ROOT / 'CONVERSATION_PROTOCOL.md')

    prior = '\n'.join(
        f"{m['emoji']} {m['display']} ({m['agent_id']}): {m['message']}"
        for m in transcript[-12:]
    ) or 'No prior messages yet.'

    prompt = f"""
You are {emoji} {display}, agent id `{agent_id}`, inside ForexAgents HQ.
NOVA is the Boss / Portfolio Manager. Ozzi is final human decision maker.

AGENT DEFINITION:
{agent['yaml']}

BASE PROMPT:
{agent['prompt']}

OZZI RULES:
{rules}

CONVERSATION PROTOCOL:
{protocol}

CURRENT SETUP INPUT JSON:
{json.dumps(setup, indent=2)}

PREVIOUS AGENT MESSAGES:
{prior}

TASK:
{extra_task or f'Respond as {emoji} {display} only. Be concise, professional, and specific.'}
If you need to question another agent, include a line like:
"{emoji} {display} -> Hunter: question"
Do not pretend to have live data if it was not provided. Say what is missing.
Output 3-8 short bullet lines max.
""".strip()

    env = os.environ.copy()
    env['HERMES_HOME'] = str(HERMES_HOME)
    tmp_dir = ROOT / 'journal' / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.txt', dir=tmp_dir, delete=False) as fh:
        fh.write(prompt)
        prompt_file = fh.name
    try:
        proc = subprocess.run(
            [str(HERMES_BIN), 'chat', '-Q', '--oneshot', '--query-file', prompt_file],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=int(setup.get('agent_timeout_seconds', 180)),
        )
        out = (proc.stdout or '').strip()
        if proc.returncode != 0:
            return f"ERROR: Hermes call failed for {display}: {out[-800:]}"
        # Strip Hermes CLI noise/trailing session_id, keep agent content.
        lines = []
        for ln in out.splitlines():
            if ln.startswith('session_id:'):
                continue
            if ln.startswith('Warning: Unknown toolsets:'):
                continue
            lines.append(ln)
        return '\n'.join(lines).strip() or 'No response.'
    except subprocess.TimeoutExpired:
        return f"ERROR: {display} timed out."
    finally:
        try:
            Path(prompt_file).unlink()
        except OSError:
            pass



def extract_agent_questions(message: str) -> list[tuple[str, str]]:
    """Extract simple agent-to-agent questions from lines like 'Atlas -> Hunter: ...'."""
    questions: list[tuple[str, str]] = []
    for raw in message.splitlines():
        line = raw.strip().lstrip('-• ').strip()
        if '->' not in line or ':' not in line:
            continue
        left, rest = line.split('->', 1)
        target_part, question = rest.split(':', 1)
        # Remove emoji/brackets and keep the last word-ish display name.
        target = target_part.replace('[', ' ').replace(']', ' ').strip()
        target_tokens = [tok.strip(' ,.:;') for tok in target.split() if tok.strip(' ,.:;')]
        for tok in reversed(target_tokens):
            agent_id = DISPLAY_TO_AGENT.get(tok.lower())
            if agent_id:
                q = question.strip()
                if q.endswith('?') or len(q) > 12:
                    questions.append((agent_id, q))
                break
    return questions


def answer_cross_questions(setup: dict[str, Any], transcript: list[dict[str, str]], new_message: str, asked: set[tuple[str, str]]) -> list[dict[str, str]]:
    """Let targeted agents answer direct questions, bounded to avoid loops/spam."""
    max_q = int(setup.get('max_cross_questions', 4))
    answers: list[dict[str, str]] = []
    for target_agent, question in extract_agent_questions(new_message):
        key = (target_agent, question.lower()[:120])
        if key in asked or len(asked) >= max_q:
            continue
        asked.add(key)
        emoji, display = DISPLAY.get(target_agent, ('🤖', target_agent))
        task = f"Answer this direct question from another ForexAgents agent. Question: {question}\nUse the setup input and previous transcript. If data is missing, say so. Do not invent facts."
        msg = run_hermes_agent(target_agent, setup, transcript, extra_task=task)
        answers.append({
            'stage': 'cross_question',
            'agent_id': target_agent,
            'emoji': emoji,
            'display': display,
            'message': msg,
        })
        transcript.append(answers[-1])
    return answers


def debate_setup(setup: dict[str, Any]) -> dict[str, Any]:
    """Run a real, staged agent conversation over provided setup input."""
    started = time.time()
    transcript: list[dict[str, str]] = []
    asked_questions: set[tuple[str, str]] = set()
    # Allow smoke tests to run only part of the company, but default is the professional flow.
    max_agents = setup.get('max_agents')
    count = 0
    for stage, agents in AGENT_ORDER.items():
        for agent_id in agents:
            if max_agents is not None and count >= int(max_agents):
                break
            emoji, display = DISPLAY.get(agent_id, ('🤖', agent_id))
            msg = run_hermes_agent(agent_id, setup, transcript)
            entry = {
                'stage': stage,
                'agent_id': agent_id,
                'emoji': emoji,
                'display': display,
                'message': msg,
            }
            transcript.append(entry)
            count += 1
            for _answer in answer_cross_questions(setup, transcript, msg, asked_questions):
                pass
        if max_agents is not None and count >= int(max_agents):
            break
    journal_id = f"run-{int(started)}"
    journal_path = ROOT / 'journal' / f'{journal_id}.json'
    journal_path.write_text(json.dumps({
        'id': journal_id,
        'setup': setup,
        'transcript': transcript,
        'elapsed_seconds': round(time.time() - started, 2),
    }, indent=2), encoding='utf-8')
    return {
        'ok': True,
        'journal_id': journal_id,
        'journal_path': str(journal_path),
        'elapsed_seconds': round(time.time() - started, 2),
        'transcript': transcript,
        'telegram_text': format_for_telegram(transcript),
    }


def format_for_telegram(transcript: list[dict[str, str]]) -> str:
    chunks = ['🏢 ForexAgents HQ — Team Debate']
    for m in transcript:
        chunks.append(f"\n{m['emoji']} {m['display']}:\n{m['message']}")
    return '\n'.join(chunks)


class Handler(BaseHTTPRequestHandler):
    server_version = 'ForexAgentsRPC/0.1'

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict[str, Any]:
        length = int(self.headers.get('Content-Length') or '0')
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode('utf-8'))

    def do_GET(self) -> None:  # noqa: N802
        if self.path == '/health':
            self._json(200, {
                'ok': True,
                'service': 'forexagents-rpc',
                'version': '0.1',
                'root': str(ROOT),
                'hermes_bin_exists': HERMES_BIN.exists(),
            })
        elif self.path == '/rules':
            self._json(200, {'ok': True, 'rules_yaml': read_text(ROOT / 'RULES.yaml')})
        else:
            self._json(404, {'ok': False, 'error': 'not found'})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._read_body()
            if self.path == '/debate/setup':
                self._json(200, debate_setup(payload))
            else:
                self._json(404, {'ok': False, 'error': 'not found'})
        except Exception as exc:  # noqa: BLE001
            self._json(500, {'ok': False, 'error': f'{type(exc).__name__}: {exc}'})


def main() -> None:
    host = os.environ.get('FOREXAGENTS_HOST', '127.0.0.1')
    port = int(os.environ.get('FOREXAGENTS_PORT', '18765'))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f'ForexAgents RPC listening on http://{host}:{port}', flush=True)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
