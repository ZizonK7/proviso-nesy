import unittest
from pathlib import Path

from domains.agent_usage import checks, dispatches as dp
from proviso import audit, schema

ROOT = Path(__file__).resolve().parent.parent
KN = ROOT / "domains" / "agent_usage" / "knowledge.toml"


class Knowledge(unittest.TestCase):
    def test_knowledge_and_records_are_valid(self):
        kn = schema.load(KN)
        self.assertEqual(schema.validate(kn), [])
        self.assertEqual(dp.validate(dp.load(), kn), [])

    def test_every_check_name_exists(self):
        kn = schema.load(KN)
        for hyp in kn.of("hypothesis"):
            self.assertIn(hyp.data["check"], checks.CHECKS)
            self.assertIn(hyp.data["check"], checks.SEEN_UNTIL)

    def test_audit_flags_turn_overestimate(self):
        # 빗대어 잡은 턴 수가 시간 예측을 해치는데, 대가로 받아들인 기록이 없다
        issues = audit.unaccepted_harms(schema.load(KN))
        self.assertEqual(len(issues), 1)
        self.assertIn("H_turns_over", issues[0])


class Classes(unittest.TestCase):
    def test_time_and_token_class_edges(self):
        self.assertEqual([dp.time_class(m) for m in (20, 20.1, 45, 90, 90.1)], ["S", "M", "M", "L", "XL"])
        self.assertEqual([dp.token_class(t) for t in (19.9, 20, 60, 119.9, 120)], ["T1", "T2", "T3", "T3", "T4"])

    def test_judge_range_and_direction(self):
        self.assertEqual(dp.judge(["M", "L"], "L", dp.TIME_CLASSES), "맞음")
        self.assertEqual(dp.judge(["M"], "XL", dp.TIME_CLASSES), "낮게 잡음")
        self.assertEqual(dp.judge(["M", "L"], "S", dp.TIME_CLASSES), "높게 잡음")
        self.assertEqual(dp.judge(["T2"], None, dp.TOKEN_CLASSES), "모름")

    def test_open_ended_bound_uses_lower(self):
        self.assertEqual(dp.midpoint([400]), 400)
        self.assertEqual(dp.midpoint([800, 1200]), 1000)


class Loop(unittest.TestCase):
    def test_stopped_and_unknown_are_not_judged(self):
        ids = {d["id"] for d in dp.load() if not dp.done(d)}
        self.assertEqual(ids, {"d15", "d16"})

    def test_hypothesis_is_tested_only_on_later_records(self):
        # H_tok_per_min은 d12c까지 보고 세웠다 → 배치 10 다섯 건으로만 시험, 네 건이 범위 밖
        verdict, detail = checks.tokens_per_minute()
        self.assertTrue(verdict.startswith("반박됨 (시험 5건 중 1건"))
        self.assertIn("dR1 0.83M ✗", detail.split("시험 기록")[1])

    def test_new_hypotheses_wait_for_new_records(self):
        for name in ("tokens_per_minute_by_length", "turns_overestimated", "check_loop_time"):
            self.assertEqual(checks.CHECKS[name]()[0], "시험 전")


if __name__ == "__main__":
    unittest.main()
