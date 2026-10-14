import unittest

from domains.flowlog import checks
from domains.flowlog import simulate as sim


class RecommendV2(unittest.TestCase):
    def test_single_use_title_only_takes_slot_five(self):
        h = sim.History()
        for title in ("공부", "식사", "운동", "휴식"):
            h.log(title, -2.0)
            h.log(title, -1.0)
        h.log("새활동", 0.5)
        shown = sim.recommend_v2(h, 1.0)
        self.assertEqual(len(shown), 5)
        self.assertEqual(shown[4], "새활동")

    def test_slot_five_is_most_recent_outside_top_four(self):
        h = sim.History()
        for title in ("공부", "식사", "운동", "휴식"):
            h.log(title, -2.0)
            h.log(title, -1.0)
        h.log("A", 0.2)
        h.log("B", 0.4)
        self.assertEqual(sim.recommend_v2(h, 1.0)[4], "B")

    def test_score_prefers_recent_and_frequent(self):
        self.assertGreater(sim.score([-1.0, -2.0, -3.0], 0.0), sim.score([-1.0], 0.0))
        self.assertGreater(sim.score([-1.0], 0.0), sim.score([-10.0], 0.0))


class Hypothesis(unittest.TestCase):
    def test_alternate_hypothesis_is_supported_by_simulation(self):
        verdict, _ = checks.alternate_two_new()
        self.assertTrue(verdict.startswith("지지됨"))


if __name__ == "__main__":
    unittest.main()
