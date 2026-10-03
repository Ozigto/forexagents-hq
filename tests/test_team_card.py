import importlib.util
import tempfile
from pathlib import Path
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load_team_card():
    spec = importlib.util.spec_from_file_location('team_card', ROOT / 'scripts' / 'team_card.py')
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TeamCardTests(unittest.TestCase):
    def test_roster_has_all_16_agents(self):
        team_card = load_team_card()
        self.assertEqual(len(team_card.AGENTS), 16)
        names = {agent.name for agent in team_card.AGENTS}
        self.assertEqual(
            names,
            {'Atlas', 'Aurora', 'Selena', 'Maya', 'Iris', 'Echo', 'Titan', 'Vega', 'Sage', 'Ava', 'Blaze', 'Gaia', 'Balance', 'Rhea', 'Lyra', 'NOVA'},
        )

    def test_build_team_card_creates_professional_png(self):
        team_card = load_team_card()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'team_card.png'
            path = team_card.build_team_card('XAU/USD', '1H', out)
            self.assertEqual(path, out)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 10_000)
            with Image.open(path) as img:
                self.assertEqual(img.format, 'PNG')
                self.assertEqual(img.size, (1200, 1500))


if __name__ == '__main__':
    unittest.main()
