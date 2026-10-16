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

    def test_audit_passes_after_turn_analogy_revision(self):
        # 빗대어 잡은 턴 수(H_turns_over)를 R_turns_analogy v2가 배수로 고쳤다. v1은 부작용과 함께 보존된다
        kn = schema.load(KN)
        self.assertEqual(audit.unaccepted_harms(kn), [])
        v1 = kn.nodes["R_turns_analogy"].data
        self.assertEqual(v1["status"], "retired")
        self.assertIn("H_turns_over", v1["side_effects"])


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
        # d15 멈춤은 늘 빠진다; 그 밖에 빠진 기록은 아직 끝나지 않은(unknown) 것뿐이어야 한다
        not_done = [d for d in dp.load() if not dp.done(d)]
        ids = {d["id"] for d in not_done}
        self.assertIn("d15", ids)
        for d in not_done:
            if d["id"] != "d15":
                self.assertEqual(d["actual"].get("status"), "unknown", d["id"])

    def test_hypothesis_is_tested_only_on_later_records(self):
        # H_tok_per_min은 d12c까지 보고 세웠다 → 배치 10 이후로만 시험한다. d12c 자신은 맞춰 본 쪽
        verdict, detail = checks.tokens_per_minute()
        self.assertTrue(verdict.startswith("반박됨"))
        fit, test = detail.split("시험 기록")
        test = test.split(":", 1)[1]  # "(d12c 다음부터)" 머리말은 뺀다
        self.assertIn("dR1 0.83M ✗", test)
        self.assertIn("d12c", fit)
        self.assertNotIn("d12c ", test)

    def test_every_check_splits_at_its_cut(self):
        order = [d["id"] for d in dp.load()]
        for name, cut in checks.SEEN_UNTIL.items():
            fit, test = checks._split(name, lambda d: True)
            limit = order.index(cut)
            self.assertTrue(all(order.index(d["id"]) <= limit for d in fit), name)
            self.assertTrue(all(order.index(d["id"]) > limit for d in test), name)

    def test_hypotheses_set_from_batch_13_wait_for_new_records(self):
        for name in ("tokens_per_minute_long_only", "turn_rate_non_web", "check_loop_turn_rate"):
            if order_last_is(checks.SEEN_UNTIL[name]):
                self.assertEqual(checks.CHECKS[name]()[0], "시험 전")


def order_last_is(record_id: str) -> bool:
    return dp.load()[-1]["id"] == record_id


if __name__ == "__main__":
    unittest.main()
