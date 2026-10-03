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
import importlib.util
from datetime import datetime
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
    'htf_bias': ('🧭', 'Aurora'),
    'session_timing': ('🕒', 'Selena'),
    'structure': ('📐', 'Maya'),
    'pattern': ('🔎', 'Iris'),
    'news': ('📰', 'Echo'),
    'bull': ('🐂', 'Titan'),
    'bear': ('🐻', 'Vega'),
    'research_manager': ('🧠', 'Sage'),
    'trader': ('🧑‍💼', 'Ava'),
    'aggressive_risk': ('⚔️', 'Blaze'),
    'conservative_risk': ('🛡', 'Gaia'),
    'neutral_risk': ('⚖️', 'Balance'),
    'nova_boss': ('👑', 'NOVA'),
}

DISPLAY_TO_AGENT = {display.lower(): agent_id for agent_id, (_emoji, display) in DISPLAY.items()}

TIMEFRAME_MINUTES = {
    '1H': 60,
    'H1': 60,
    '4H': 240,
    'H4': 240,
}


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def check_snapshot_quality(snapshot: dict[str, Any], now: str | None) -> dict[str, Any]:
    """Fail closed on bad shared evidence before any agent debate."""
    vetoes: list[str] = []
    warnings: list[str] = []
    timeframe = str(snapshot.get('timeframe', '')).upper().replace('H1', '1H').replace('H4', '4H')
    tf_minutes = TIMEFRAME_MINUTES.get(timeframe)
    if not snapshot.get('symbol'):
        vetoes.append('missing_symbol')
    if not tf_minutes:
        vetoes.append('unsupported_timeframe')
    candles = snapshot.get('candles') or []
    if not candles:
        vetoes.append('missing_candles')
    completed = snapshot.get('completed_candle') or {}
    if not completed.get('time'):
        vetoes.append('missing_completed_candle')
    times = [c.get('time') for c in candles if c.get('time')]
    if len(times) != len(set(times)):
        vetoes.append('duplicate_candles')
    if now and tf_minutes and completed.get('time'):
        age_minutes = (_parse_iso(now) - _parse_iso(completed['time'])).total_seconds() / 60
        if age_minutes > tf_minutes * 1.25:
            vetoes.append('stale_data')
        elif age_minutes < 0:
            vetoes.append('future_candle')
    if now and snapshot.get('data_timestamp'):
        data_age = (_parse_iso(now) - _parse_iso(snapshot['data_timestamp'])).total_seconds() / 60
        if data_age < 0:
            vetoes.append('future_data_timestamp')
    elif not snapshot.get('data_timestamp'):
        warnings.append('missing_data_timestamp')
    return {
        'decision': 'WAIT' if vetoes else 'PASS',
        'vetoes': vetoes,
        'warnings': warnings,
    }



def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def _load_case_store():
    path = ROOT / 'skills' / 'core' / 'case_store.py'
    spec = importlib.util.spec_from_file_location('case_store', path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def build_live_evidence_snapshot(symbol: str, timeframe: str, now: str | None = None) -> dict[str, Any]:
    """Fetch live read-only OHLC evidence for the desk.

    Uses the no-key Biquote adapter first. This makes ForexAgents operational
    while still fail-closing if the feed is stale or unavailable.
    """
    path = ROOT / 'skills' / 'market_data' / 'biquote.py'
    spec = importlib.util.spec_from_file_location('biquote', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_live_snapshot(symbol, timeframe, now=now)


def attach_live_snapshot_if_missing(setup: dict[str, Any]) -> dict[str, Any]:
    if isinstance(setup.get('evidence_snapshot'), dict):
        return setup
    if setup.get('input_type') in {'manual_snapshot', 'replay'}:
        return setup
    if not setup.get('use_live_data') and setup.get('input_type') not in {'telegram_polling_bridge', 'n8n', 'live_scan'}:
        return setup
    symbol = str(setup.get('symbol') or '').strip()
    timeframe = str(setup.get('timeframe') or '').strip()
    if not symbol or not timeframe:
        return setup
    try:
        now = setup.get('now') or datetime.now().astimezone().isoformat(timespec='seconds')
        snapshot = build_live_evidence_snapshot(symbol, timeframe, now)
        return {**setup, 'now': now, 'evidence_snapshot': snapshot, 'market_data_source': snapshot.get('source', 'unknown')}
    except Exception as exc:
        return {**setup, 'market_data_error': str(exc)}


def create_rpc_case(setup: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """Create persistent case files for every RPC debate/setup call."""
    store = _load_case_store()
    timestamp = str(setup.get('timestamp') or setup.get('now') or datetime.now().astimezone().isoformat(timespec='seconds'))
    sequence = int(setup.get('case_sequence') or 1)
    root = Path(str(setup.get('case_root') or ROOT))
    snapshot = setup.get('evidence_snapshot') if isinstance(setup.get('evidence_snapshot'), dict) else {
        'snapshot_id': None,
        'symbol': setup.get('symbol', 'UNKNOWN'),
        'timeframe': setup.get('timeframe', 'UNKNOWN'),
        'source': 'manual_notes',
        'chart_notes': setup.get('chart_notes') or setup.get('notes') or setup.get('text') or '',
    }
    return store.create_case(
        root=root,
        symbol=str(setup.get('symbol') or gate.get('symbol') or 'UNKNOWN'),
        timestamp=timestamp,
        sequence=sequence,
        rule_version=setup.get('rule_version', 1),
        snapshot=snapshot,
        gate=gate,
    )


def write_case_transcript(case_dir: str | Path, transcript: list[dict[str, str]]) -> None:
    """Persist agent outputs into the case folder."""
    path = Path(case_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / 'debate.json').write_text(json.dumps(transcript, indent=2, ensure_ascii=False), encoding='utf-8')
    analyst_reports = [m for m in transcript if m.get('stage') == 'analysts']
    (path / 'analyst_reports.json').write_text(json.dumps(analyst_reports, indent=2, ensure_ascii=False), encoding='utf-8')


def build_nova_decision_card(case: dict[str, Any], gate: dict[str, Any], status: str, transcript: list[dict[str, str]] | None = None) -> str:
    """Create the clean decision card Rhea can post to Telegram."""
    reasons = gate.get('reasons') or []
    unknowns = gate.get('unknowns') or []
    vetoes = gate.get('vetoes') or []
    main_reason = reasons[0] if reasons else 'Decision based on current evidence gate and company rules.'
    if vetoes:
        main_reason += f" Vetoes: {', '.join(vetoes)}."
    if unknowns:
        main_reason += f" Unknowns: {', '.join(unknowns)}."
    ozzi_action = 'No trade. Wait for a cleaner setup or better evidence.' if status == 'WAIT' else 'Review the case before any decision.'
    pattern = ', '.join(gate.get('patterns') or []) or 'none'
    return f"""👑 NOVA DECISION

Case: {case.get('case_id')}
Status: {status}
Pair: {gate.get('symbol', case.get('symbol', 'UNKNOWN'))}
Pattern: {pattern}
Evidence Grade: {gate.get('evidence_grade', 'insufficient')}
Main Reason: {main_reason}
Invalidation: not available yet
Risk: not available yet
News Risk: not available yet
Next Check Time: wait for next valid evidence snapshot
Ozzi Action: {ozzi_action}
""".strip() + "\n"


def write_nova_decision_card(case_dir: str | Path, case: dict[str, Any], gate: dict[str, Any], status: str, transcript: list[dict[str, str]] | None = None) -> str:
    card = build_nova_decision_card(case, gate, status, transcript)
    Path(case_dir).mkdir(parents=True, exist_ok=True)
    (Path(case_dir) / 'nova_decision.md').write_text(card, encoding='utf-8')
    return card


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
"{emoji} {display} -> Iris: question"
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
    """Extract simple agent-to-agent questions from lines like 'Atlas -> Iris: ...'."""
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


def evidence_gate(setup: dict[str, Any]) -> dict[str, Any]:
    """Deterministic pre-check before spending LLM calls.

    This is intentionally conservative. It does not approve trades; it only decides
    whether one of Ozzi's two allowed patterns is plausible enough for agent debate.
    """
    notes = ' '.join(str(setup.get(key, '')) for key in ('chart_notes', 'ozzi_notes', 'notes', 'text')).lower()
    timeframe = str(setup.get('timeframe', '')).upper().replace('H1', '1H').replace('H4', '4H')
    symbol = str(setup.get('symbol', 'UNKNOWN'))
    snapshot = setup.get('evidence_snapshot')
    if isinstance(snapshot, dict):
        quality = check_snapshot_quality(snapshot, setup.get('now'))
        if quality['decision'] == 'WAIT':
            return {
                'decision': 'WAIT',
                'status': 'WAIT',
                'symbol': symbol,
                'timeframe': timeframe or 'UNKNOWN',
                'patterns': [],
                'evidence_grade': 'insufficient',
                'reasons': ['Data quality failed before LLM debate.'],
                'unknowns': quality.get('warnings', []),
                'vetoes': quality.get('vetoes', []),
            }
        for calc in snapshot.get('calculations') or []:
            if calc.get('name') == 'pinbar' and calc.get('is_pinbar') is True and timeframe in {'1H', '4H'}:
                direction = calc.get('direction', 'unknown')
                return {
                    'decision': 'DEBATE',
                    'status': 'CANDIDATE_FOR_DEBATE',
                    'symbol': symbol,
                    'timeframe': timeframe or 'UNKNOWN',
                    'patterns': ['pinbar_rejection'],
                    'evidence_grade': 'strong',
                    'reasons': [f'{timeframe} live snapshot contains a deterministic {direction} pin-bar candidate.'],
                    'unknowns': [],
                }
    patterns: list[str] = []
    reasons: list[str] = []
    unknowns: list[str] = []

    has_ema = '21 ema' in notes or 'ema21' in notes or 'ema 21' in notes
    has_break = any(word in notes for word in ('break', 'broke', 'broken'))
    has_retest = any(word in notes for word in ('retest', 'pullback', 'pull back'))
    has_confirm = any(word in notes for word in ('close', 'closed', 'holding', 'reaction', 'reject'))
    if timeframe == '4H' and has_ema and has_break and has_retest:
        patterns.append('4h_21ema_break_retest')
        reasons.append('4H notes mention 21 EMA plus break and retest/pullback.')
        if not has_confirm:
            unknowns.append('closed-candle confirmation not proven')

    has_pinbar = any(term in notes for term in ('pin bar', 'pinbar', 'long wick', 'lower wick', 'upper wick'))
    has_rejection = any(term in notes for term in ('rejection', 'reject', 'wick'))
    has_level = any(term in notes for term in ('support', 'resistance', 'zone', 'level', 'ema'))
    if timeframe in {'1H', '4H'} and has_pinbar and has_rejection and has_level:
        patterns.append('pinbar_rejection')
        reasons.append(f'{timeframe} notes mention pin-bar/wick rejection at a level/zone.')

    if not patterns:
        return {
            'decision': 'WAIT',
            'status': 'WAIT',
            'symbol': symbol,
            'timeframe': timeframe or 'UNKNOWN',
            'patterns': [],
            'evidence_grade': 'insufficient',
            'reasons': ['No plausible allowed pattern detected before LLM debate.'],
            'unknowns': ['No deterministic 4H 21 EMA break/retest or 1H/4H pin-bar rejection candidate found.'],
        }

    has_structured_evidence = bool(setup.get('evidence_snapshot') or setup.get('completed_candles') or setup.get('candles'))
    grade = 'mixed' if unknowns or not has_structured_evidence else 'strong'
    return {
        'decision': 'DEBATE',
        'status': 'CANDIDATE_FOR_DEBATE',
        'symbol': symbol,
        'timeframe': timeframe or 'UNKNOWN',
        'patterns': patterns,
        'evidence_grade': grade,
        'reasons': reasons,
        'unknowns': unknowns,
    }


def format_gate_wait(gate: dict[str, Any]) -> str:
    reasons = '\n'.join(f"- {reason}" for reason in gate.get('reasons', []))
    unknowns = '\n'.join(f"- {item}" for item in gate.get('unknowns', []))
    return f"""👑 NOVA DECISION\n\nStatus: WAIT\nPair: {gate.get('symbol', 'UNKNOWN')}\nTimeframe: {gate.get('timeframe', 'UNKNOWN')}\nEvidence Grade: {gate.get('evidence_grade', 'insufficient')}\n\nReason:\n{reasons}\n\nMissing / Unknown:\n{unknowns}\n\nOzzi Action: No trade. No agent debate spent until one of the two allowed patterns is plausible.""".strip()


def debate_setup(setup: dict[str, Any]) -> dict[str, Any]:
    """Run a real, staged agent conversation over provided setup input."""
    started = time.time()
    setup = attach_live_snapshot_if_missing(setup)
    gate = evidence_gate(setup)
    case = create_rpc_case(setup, gate)
    transcript: list[dict[str, str]] = []
    if gate['decision'] == 'WAIT' and not setup.get('force_debate'):
        journal_id = f"run-{int(started)}"
        journal_path = ROOT / 'journal' / f'{journal_id}.json'
        telegram_text = format_gate_wait(gate)
        decision_card = write_nova_decision_card(case['case_dir'], case, gate, 'WAIT', transcript)
        journal_path.write_text(json.dumps({
            'id': journal_id,
            'case_id': case['case_id'],
            'case_dir': case['case_dir'],
            'setup': setup,
            'gate': gate,
            'status': 'WAIT',
            'transcript': transcript,
            'elapsed_seconds': round(time.time() - started, 2),
        }, indent=2), encoding='utf-8')
        return {
            'ok': True,
            'status': 'WAIT',
            'gate': gate,
            'case_id': case['case_id'],
            'case_dir': case['case_dir'],
            'journal_id': journal_id,
            'journal_path': str(journal_path),
            'elapsed_seconds': round(time.time() - started, 2),
            'setup': setup,
            'transcript': transcript,
            'telegram_text': telegram_text,
        }

    setup = {**setup, 'evidence_gate': gate, 'case_id': case['case_id'], 'case_dir': case['case_dir']}
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
    write_case_transcript(case['case_dir'], transcript)
    decision_status = 'WATCH'
    write_nova_decision_card(case['case_dir'], case, gate, decision_status, transcript)
    journal_path.write_text(json.dumps({
        'id': journal_id,
        'case_id': case['case_id'],
        'case_dir': case['case_dir'],
        'setup': setup,
        'gate': gate,
        'transcript': transcript,
        'elapsed_seconds': round(time.time() - started, 2),
    }, indent=2), encoding='utf-8')
    return {
        'ok': True,
        'case_id': case['case_id'],
        'case_dir': case['case_dir'],
        'gate': gate,
        'journal_id': journal_id,
        'journal_path': str(journal_path),
        'elapsed_seconds': round(time.time() - started, 2),
        'setup': setup,
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
