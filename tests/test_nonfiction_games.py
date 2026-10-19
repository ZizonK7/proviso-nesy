import unittest

from domains.nonfiction_games import checks, games
from proviso import schema


class NonfictionGames(unittest.TestCase):
    def setUp(self):
        self.kn = schema.load(games.HERE / "knowledge.toml")

    def test_knowledge_valid(self):
        self.assertEqual(schema.validate(self.kn), [])

    def test_games_valid(self):
        self.assertEqual(games.validate(games.load(), self.kn), [])

    def test_bad_state_is_caught(self):
        bad = [{"id": "g_x", "name": "x", "basis": "x", "basis_kind": "비문학", "facts": ["F_g_simcity"],
                "situation": {"S_nope": "예"}, "outcome": {"judgment": "성공", "judged_by": "public", "basis": "x"}}]
        self.assertTrue(any("S_nope" in e for e in games.validate(bad, self.kn)))

    def test_every_check_runs_and_cut_exists(self):
        ids = [g["id"] for g in games.load()]
        for name, fn in checks.CHECKS.items():
            self.assertIn(checks.SEEN_UNTIL[name], ids)
            verdict, _ = fn()
            self.assertTrue(verdict.startswith(("지지됨", "반박됨", "시험 전")))

    def test_hypothesis_checks_exist(self):
        for node in self.kn.of("hypothesis"):
            name = node.data.get("check")
            if name:
                self.assertIn(name, checks.CHECKS)


if __name__ == "__main__":
    unittest.main()
