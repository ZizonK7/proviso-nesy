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
        # 가설·규칙 모두: 검사 이름이 있고, 세운 뒤 기록으로만 시험하는 검사는 SEEN_UNTIL이 있다
        kn = schema.load(KN)
        for node in kn.claims():
            for name in schema.check_names(node):
                self.assertIn(name, checks.CHECKS, node.id)
                if name in checks.NODE_CUT:  # 계산 조각: 노드가 맞출 때 본 마지막 기록을 적는다
                    self.assertIn("seen_until", node.data, node.id)
                elif name not in checks.NO_CUT:
                    self.assertIn(name, checks.SEEN_UNTIL, node.id)

    def test_prediction_rules_that_are_alive_have_a_test(self):
        # 2026-10-19: 예측에 쓰는 살아 있는 규칙은 자동 검사가 있거나, 못 붙이는 까닭(test_plan)을 적는다
        kn = schema.load(KN)
        for rule in kn.of("rule"):
            if schema.alive(rule):
                self.assertTrue(schema.check_names(rule) or rule.data.get("test_plan"), rule.id)

    def test_no_verified_status_left(self):
        for domain in ("flowlog", "music_player", "agent_usage"):
            kn = schema.load(ROOT / "domains" / domain / "knowledge.toml")
            for node in kn.claims():
                self.assertIn(node.data.get("status", "hypothesis"), ("hypothesis", "retired"), node.id)

    def test_audit_passes_after_turn_analogy_revision(self):
        # 빗대어 잡은 턴 수(H_turns_over)를 R_turns_analogy v2가 배수로 고쳤다. v1은 부작용과 함께 보존된다
        kn = schema.load(KN)
        self.assertEqual(audit.unaccepted_harms(kn), [])
        v1 = kn.nodes["R_turns_analogy"].data
        self.assertEqual(v1["status"], "retired")
        self.assertIn("H_turns_over", v1["side_effects"])


class Classes(unittest.TestCase):
    def test_zone_and_token_class_edges(self):
        self.assertEqual([dp.zone(m) for m in (10, 10.1, 40, 40.1)], ["잠깐", "다른 일", "다른 일", "신경 끄기"])
        self.assertEqual([dp.token_class(t) for t in (19.9, 20, 60, 119.9, 120)], ["T1", "T2", "T3", "T3", "T4"])

    def test_zones_of_prediction_range(self):
        self.assertEqual(dp.zones_of([5, 10]), ["잠깐"])
        self.assertEqual(dp.zones_of([10, 20]), ["다른 일"])  # 아래 끝이 경계값이면 위 구간부터
        self.assertEqual(dp.zones_of([40, 65]), ["신경 끄기"])
        self.assertEqual(dp.zones_of([8, 18]), ["잠깐", "다른 일"])  # 걸침
        self.assertEqual(dp.zones_of([5, 50]), ["잠깐", "다른 일", "신경 끄기"])
        self.assertEqual(dp.zones_of([90]), ["신경 끄기"])  # 하나만 있으면 '이상'
        self.assertEqual(dp.zones_of([]), [])

    def test_judge_range_and_direction(self):
        self.assertEqual(dp.judge(["다른 일", "신경 끄기"], "신경 끄기", dp.ZONES), "맞음")
        self.assertEqual(dp.judge(["잠깐"], "신경 끄기", dp.ZONES), "낮게 잡음")
        self.assertEqual(dp.judge(["다른 일", "신경 끄기"], "잠깐", dp.ZONES), "높게 잡음")
        self.assertEqual(dp.judge(["T2"], None, dp.TOKEN_CLASSES), "모름")


class Rescore20261019(unittest.TestCase):
    """시간 구간 세 마디로 다시 채점 (기록 파일은 고치지 않는다)."""

    def test_rescore_counts_minute_ranges_only(self):
        records = dp.load()
        # 다시 채점한 시점(p03까지)의 기록만: 뒤에 기록이 늘어도 이 숫자는 그대로다
        records = records[: [d["id"] for d in records].index("p03") + 1]
        r = dp.rescore(records)
        self.assertEqual(sorted(r["분 범위 없음"]), sorted(["dR1", "dR2", "dR3", "dR4", "d14", "d16"]))
        self.assertEqual(sum(r["판정"].values()), 118)
        spans = sum(r["걸침"].values())
        singles = sum(sum(c.values()) for c in r["구간별"].values())
        self.assertEqual(spans + singles, 118)

    def test_miss_split_by_turns(self):
        base = {"id": "x", "predicted": {"minutes": [20, 30], "turns": [100, 150]}, "actual": {}}
        speed = {**base, "actual": {"minutes": 10, "turns": 120}}
        amount = {**base, "actual": {"minutes": 10, "turns": 50}}
        none = {"id": "y", "predicted": {"minutes": [20, 30]}, "actual": {"minutes": 50, "turns": 50}}
        self.assertEqual(dp.miss_split(speed), ("아래", "속도"))
        self.assertEqual(dp.miss_split(amount), ("아래", "양"))
        self.assertEqual(dp.miss_split(none), ("위", "턴 예측 없음"))
        self.assertIsNone(dp.miss_split({**base, "actual": {"minutes": 25, "turns": 50}}))

    def test_p04_told_the_long_zone(self):
        p04 = {d["id"]: d for d in dp.load()}["p04"]["predicted"]
        self.assertEqual(p04["told"], "신경 끄기")
        self.assertEqual(dp.zones_of(p04["minutes"])[-1], p04["told"])

    def test_future_zone_miss_needs_wrong_and_why(self):
        kn = schema.load(KN)
        records = dp.load()
        late = {"id": "zz1", "project": "proviso", "batch": 9, "date": "2026-10-20", "task": "t",
                "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 30, "turns": 10}}
        errors = dp.validate(records + [late], kn)
        self.assertTrue(any("zz1" in e and "review.wrong" in e for e in errors))
        late["review"] = {"wrong": ["R_time_turns_v2"], "why": "조건 흐림"}
        self.assertEqual(dp.validate(records + [late], kn), [])
        late["review"]["why"] = "몰라"
        self.assertTrue(any("review.why" in e for e in dp.validate(records + [late], kn)))
        # 지난 기록(p03까지)은 빗나가도 요구하지 않는다: p01은 구간을 빗나갔지만 오류가 없다
        self.assertEqual(dp.zone_verdict({d["id"]: d for d in records}["p01"]), "높게 잡음")
        self.assertEqual(dp.validate(records, kn), [])

    def test_used_check_reads_predictions_written_before(self):
        verdict, detail = checks.used_minutes("R_time_turns_v2")
        self.assertTrue(verdict.startswith(("지지됨", "반박됨")))
        self.assertNotIn("d32b ", detail)  # 보내기 전에 적지 않은 예측(d32b)은 뺀다
        self.assertTrue(checks.used_minutes("R_integration")[0].startswith("시험 전"))

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


def _ids(detail_part: str) -> list[str]:
    """check 설명의 한 줄('...: d01 6.2, d04 2.8 ✗')에서 기록 id만 뽑는다."""
    body = detail_part.split(":", 1)[1].strip()
    return [] if body == "없음" else [item.split()[0] for item in body.split(", ")]


class Cleanup20261019(unittest.TestCase):
    NEW = ("mid_notes_bounded", "sonnet_fixed_floor", "fixed_input_opus", "fix_context",
           "settled_integration", "build_tools_minutes", "doc_spec_minutes")

    def test_new_hypotheses_are_tested_from_d95(self):
        for name in self.NEW:
            self.assertEqual(checks.SEEN_UNTIL[name], "d94", name)

    def test_new_checks_match_the_records_they_were_built_from(self):
        # 세울 때 본 기록에 ✗가 있으면 검사가 가설 문장과 다르게 짜인 것이다 (mid_notes는 보내기 전에 안 적은 d01만 ✗)
        for name in self.NEW:
            fit = checks.CHECKS[name]()[1].split("\n")[0]
            ids = _ids(fit)
            self.assertTrue(ids, name)
            bad = [i for i in ids if f"{i} " in fit and fit.split(f"{i} ", 1)[1].split(",")[0].endswith("✗")]
            self.assertEqual(bad, ["d01"] if name == "mid_notes_bounded" else [], name)

    def test_render_check_keeps_only_short_laps(self):
        # H_render_rate의 조건 '렌더 한 회 1–2분' = S_long_lap=아니오. 장 흐름 바퀴(d69 일부, d69c 예)는 뺀다
        detail = checks.render_turn_rate()[1]
        ids = _ids(detail.split("\n")[0]) + _ids(detail.split("\n")[1])
        self.assertNotIn("d69", ids)
        self.assertNotIn("d69c", ids)
        records = {d["id"]: d for d in dp.load()}
        self.assertTrue(all(dp.situation(records[i], "S_long_lap") == "아니오" for i in ids))

    def test_research_cap_counts_web_research_only(self):
        detail = checks.research_cap()[1]
        records = {d["id"]: d for d in dp.load()}
        for line in detail.split("\n"):
            for i in _ids(line):
                self.assertEqual(dp.situation(records[i], "S_web"), "예", i)

    def test_analog_prefers_prediction_then_past_reading(self):
        self.assertEqual(checks._analog({"id": "d94", "predicted": {}})["id"], "d68")
        self.assertEqual(checks._analog({"id": "x", "predicted": {"analog": "d61"}})["id"], "d61")
        self.assertIsNone(checks._analog({"id": "x", "predicted": {"analog": "없는 id"}}))

    def test_rules_are_tidy(self):
        # 방식 1: 살아 있는 규칙은 이유가 있고 목표를 섬긴다. 물린 규칙은 무엇이 대신하는지 가리킨다
        kn = schema.load(KN)
        for rule in kn.of("rule"):
            if rule.data["status"] == "retired":
                self.assertTrue(rule.refs("replaced_by"), rule.id)
            else:
                self.assertNotIn("기록 없음", rule.data["reason"], rule.id)
                self.assertTrue(rule.refs("serves"), rule.id)


def order_last_is(record_id: str) -> bool:
    return dp.load()[-1]["id"] == record_id


if __name__ == "__main__":
    unittest.main()


class HandVsCalc(unittest.TestCase):
    """손 예측과 계산기를 나란히 적은 기록의 승패 (사용자 결정 2026-10-19: 어느 쪽이 나은지 계속 기록)."""

    def test_counts_only_records_with_both(self):
        recs = [
            {"id": "a", "predicted": {"told": "다른 일"}, "calc": {"told": "신경 끄기"}, "actual": {"minutes": 20}},
            {"id": "b", "predicted": {"told": "잠깐"}, "calc": {"told": "잠깐"}, "actual": {"minutes": 5}},
            {"id": "c", "predicted": {"told": "잠깐"}, "actual": {"minutes": 5}},
        ]
        r = dp.hand_vs_calc(recs)
        self.assertEqual(r["손만 맞음"], 1)
        self.assertEqual(r["둘 다 맞음"], 1)
        self.assertEqual(sum(r.values()), 2)
