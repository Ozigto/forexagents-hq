#!/usr/bin/env python3
"""Generate the ForexAgents HQ pixel roster card for Telegram."""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CARD_DIR = ROOT / 'assets' / 'generated'
CARD_PATH = CARD_DIR / 'forexagents_team_card.png'


class Agent(NamedTuple):
    name: str
    role: str
    icon: str
    color: str
    accent: str


AGENTS: tuple[Agent, ...] = (
    Agent('Atlas', 'Market Data', '📊', '#2F80ED', '#7CC7FF'),
    Agent('Aurora', 'HTF Bias', '🧭', '#9B51E0', '#D7B4FF'),
    Agent('Selena', 'Timing', '🕒', '#27AE60', '#8CF0B0'),
    Agent('Maya', 'Structure', '📐', '#F2994A', '#FFD08A'),
    Agent('Iris', 'Pattern Desk', '🔎', '#EB5757', '#FF9A9A'),
    Agent('Echo', 'News Risk', '📰', '#F2C94C', '#FFF09A'),
    Agent('Titan', 'Bull Case', '🐂', '#00A86B', '#78FFD0'),
    Agent('Vega', 'Bear Case', '🐻', '#6B7280', '#C8D0DD'),
    Agent('Sage', 'Research Manager', '🧠', '#56CCF2', '#B7EEFF'),
    Agent('Ava', 'Trader', '🧑‍💼', '#BB6BD9', '#EAC0FF'),
    Agent('Blaze', 'Aggressive Risk', '⚔️', '#F24E1E', '#FFB199'),
    Agent('Gaia', 'Conservative Risk', '🛡', '#219653', '#9EF0BA'),
    Agent('Balance', 'Neutral Risk', '⚖️', '#BDBDBD', '#FFFFFF'),
    Agent('Rhea', 'Telegram Manager', '📲', '#2D9CDB', '#A8DEFF'),
    Agent('Lyra', 'Journal / Replay', '🧪', '#6FCF97', '#C6FFD9'),
    Agent('NOVA', 'Boss / Portfolio', '👑', '#F7B500', '#FFE38A'),
)


def _font(size: int, bold: bool = False) -> Any:
    candidates = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Supplemental/Helvetica Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Helvetica.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_pixel_avatar(draw: ImageDraw.ImageDraw, x: int, y: int, agent: Agent, scale: int = 7) -> None:
    """Draw a tiny deterministic pixel portrait without external assets."""
    dark = '#0B1020'
    skin = '#F2C6A0' if agent.name not in {'Vega', 'NOVA'} else ('#8E6E53' if agent.name == 'Vega' else '#F6D365')
    hair = agent.color
    shirt = agent.accent
    pixels = [
        '00111100',
        '01111110',
        '11222211',
        '12222221',
        '12022021',
        '12222221',
        '01133110',
        '00333300',
    ]
    palette = {'0': None, '1': hair, '2': skin, '3': shirt}
    for row, line in enumerate(pixels):
        for col, key in enumerate(line):
            color = palette[key]
            if color:
                draw.rectangle([x + col * scale, y + row * scale, x + (col + 1) * scale - 1, y + (row + 1) * scale - 1], fill=color)
    # eyes
    eye = dark
    draw.rectangle([x + 2 * scale, y + 4 * scale, x + 2 * scale + scale - 1, y + 4 * scale + scale - 1], fill=eye)
    draw.rectangle([x + 5 * scale, y + 4 * scale, x + 5 * scale + scale - 1, y + 4 * scale + scale - 1], fill=eye)


def build_team_card(symbol: str = 'XAU/USD', timeframe: str = '4H', output_path: Path = CARD_PATH) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1200, 1500
    img = Image.new('RGB', (width, height), '#090D18')
    draw = ImageDraw.Draw(img)

    # subtle grid background
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill='#111827', width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill='#111827', width=1)

    # header
    draw.rounded_rectangle([44, 38, width - 44, 220], radius=28, fill='#111827', outline='#2F80ED', width=3)
    draw.text((78, 72), 'FOREXAGENTS HQ', font=_font(54, bold=True), fill='#F8FAFC')
    draw.text((80, 137), f'{symbol} {timeframe}  •  Company Room Open', font=_font(29), fill='#9CA3AF')
    draw.text((width - 360, 82), 'NOVA LED', font=_font(34, bold=True), fill='#FFE38A')
    draw.text((width - 360, 132), 'Research only • No auto-trading', font=_font(22), fill='#A7F3D0')

    # cards
    cols = 4
    tile_w, tile_h = 260, 245
    gap_x, gap_y = 24, 26
    start_x, start_y = 58, 270
    name_font = _font(30, bold=True)
    role_font = _font(22)
    icon_font = _font(23, bold=True)

    for i, agent in enumerate(AGENTS):
        col = i % cols
        row = i // cols
        x = start_x + col * (tile_w + gap_x)
        y = start_y + row * (tile_h + gap_y)
        draw.rounded_rectangle([x, y, x + tile_w, y + tile_h], radius=24, fill='#111827', outline=agent.color, width=3)
        draw.rounded_rectangle([x + 14, y + 14, x + tile_w - 14, y + 62], radius=16, fill=agent.color)
        draw.text((x + 28, y + 24), agent.icon, font=icon_font, fill='#FFFFFF')
        draw.text((x + 72, y + 24), agent.name, font=name_font, fill='#FFFFFF')
        _draw_pixel_avatar(draw, x + 92, y + 82, agent, scale=8)
        draw.text((x + 22, y + 158), agent.role, font=role_font, fill='#E5E7EB')
        draw.line([x + 22, y + 194, x + tile_w - 22, y + 194], fill='#263244', width=1)
        status = 'on desk' if agent.name != 'NOVA' else 'final veto'
        draw.text((x + 22, y + 207), status.upper(), font=_font(18, bold=True), fill=agent.accent)

    # footer
    footer_y = height - 115
    draw.rounded_rectangle([44, footer_y, width - 44, height - 38], radius=22, fill='#0F172A', outline='#334155', width=2)
    draw.text((76, footer_y + 25), 'Gate before debate  •  WAIT protects capital  •  One A+ setup per week mindset', font=_font(25), fill='#CBD5E1')

    img.save(output_path, 'PNG', optimize=True)
    return output_path


if __name__ == '__main__':
    print(build_team_card())
