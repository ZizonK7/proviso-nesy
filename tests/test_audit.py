import tempfile
import unittest
from pathlib import Path

from proviso import audit, schema

ROOT = Path(__file__).resolve().parent.parent

GOAL = '[[goal]]\nid="G"\ntext="목표"\n[[goal]]\nid="G2"\ntext="다른 목표"\n'
RULE = '[[rule]]\nid="R"\nversion=1\nstatus="{status}"\nmethod="m"\nreason="r"\nside_effects=["S"]\n'


def load_text(text: str) -> schema.Knowledge:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "k.toml"
        path.write_text(text, encoding="utf-8")
        return schema.load(path)


class UnacceptedHarms(unittest.TestCase):
    def test_flowlog_passes_because_harms_are_accepted(self):
        kn = schema.load(ROOT / "domains" / "flowlog" / "knowledge.toml")
        self.assertEqual(audit.unaccepted_harms(kn), [])

    def test_music_player_flags_duplicate_fact(self):
        kn = schema.load(ROOT / "domains" / "music_player" / "knowledge.toml")
        issues = audit.unaccepted_harms(kn)
        self.assertEqual(len(issues), 1)
        self.assertIn("F_dup_window", issues[0])
        self.assertIn("G_diversity", issues[0])

    def test_state_side_effect_of_active_rule_is_flagged(self):
        kn = load_text(GOAL + '[[state]]\nid="S"\ntext="s"\nharms=["G"]\n' + RULE.format(status="hypothesis"))
        self.assertEqual(len(audit.unaccepted_harms(kn)), 1)

    def test_state_side_effect_of_retired_rule_is_past(self):
        kn = load_text(GOAL + '[[state]]\nid="S"\ntext="s"\nharms=["G"]\n' + RULE.format(status="retired"))
        self.assertEqual(audit.unaccepted_harms(kn), [])

    def test_accepted_harm_passes(self):
        kn = load_text(GOAL + '[[state]]\nid="S"\ntext="s"\nharms=["G"]\naccepted_for=["G2"]\n'
                       + RULE.format(status="hypothesis"))
        self.assertEqual(audit.unaccepted_harms(kn), [])


if __name__ == "__main__":
    unittest.main()
