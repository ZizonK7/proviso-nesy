"""빗댄 기록 규칙 (2026-11-03 사용자 결정): 정해진 일은 가장 가까운 지난 일의 시간을 따른다. domains/agent_usage/analog.py"""
import copy
import unittest

from domains.agent_usage import analog as an, dispatches as dp


class AnalogRule(unittest.TestCase):
    def setUp(self):
        self.records = dp.load()
        self.rule = an.load_rule()
        self.t = an.times()

    def test_range_comes_only_from_records_up_to_seen_until(self):
        # analog.toml의 범위 = seen_until까지의 정해진 일로 다시 맞춘 범위. 그 뒤 기록의 실측을 바꿔도 같다
        def fitted(records):
            train = [d for d in an.split(records, self.rule["seen_until"])[0] if an.scoped(d)]
            est = an.rule_estimates(train, records, self.rule, self.t, bool(self.rule.get("defer_ties")))
            return an.fit_range(train, est, 2.0)[0]
        self.assertEqual(tuple(self.rule["range"]), fitted(self.records))
        changed = copy.deepcopy(self.records)
        ids = [d["id"] for d in changed]
        for d in changed[ids.index(self.rule["seen_until"]) + 1:]:
            d["actual"] = {**d.get("actual", {}), "minutes": 999.0}
        self.assertEqual(tuple(self.rule["range"]), fitted(changed))

    def test_only_records_finished_before_sending_are_candidates(self):
        order = {d["id"]: i for i, d in enumerate(self.records)}
        for d in self.records[-40:]:
            group, _ = an.pick(d, self.records, self.rule, self.t)
            for c in group:
                self.assertTrue(an.available(c, d, self.t, order), (d["id"], c["id"]))
                self.assertLessEqual(str(c.get("date")), str(d.get("date")), (d["id"], c["id"]))
                if str(c.get("date")) == str(d.get("date")) and c["id"] in self.t and d["id"] in self.t:
                    self.assertLessEqual(self.t[c["id"]][1], self.t[d["id"]][0], (d["id"], c["id"]))

    def test_ties_use_the_middle_value(self):
        # 사용자 제안 '기댓값': 맨 앞이 동점이면 하나를 고르지 않고 그 묶음의 실제 분의 가운데 값
        group = [{"actual": {"minutes": m, "turns": 10}, "predicted": {}} for m in (2.0, 9.0, 4.0)]
        self.assertEqual(an.estimate(group), 4.0)
        self.assertIsNone(an.estimate([]))

    def test_previous_round_of_the_same_agent_comes_first(self):
        # v2: agent·round가 있으면 같은 에이전트의 바로 앞 회차(같은 '할 일이 정해졌나') 하나를 쓴다
        def rec(rid, rnd, minutes, start, end, spec="예"):
            return {"id": rid, "project": "x", "batch": 1, "date": "2026-11-05", "task": "t", "agent": "작성", "round": rnd,
                    "situation": {"S_specified": spec, "S_other_model": "아니오", "S_resumed": "예" if rnd > 1 else "아니오"},
                    "predicted": {}, "actual": {"minutes": minutes, "turns": 10, "start": start, "end": end}}
        r1 = rec("z1", 1, 9.0, "2026-11-05T01:00:00Z", "2026-11-05T01:09:00Z")
        r2 = rec("z2", 2, 2.0, "2026-11-05T01:20:00Z", "2026-11-05T01:22:00Z")
        r3 = rec("z3", 3, 1.5, "2026-11-05T01:30:00Z", "2026-11-05T01:31:30Z")
        t = {r["id"]: (r["actual"]["start"], r["actual"]["end"]) for r in (r1, r2, r3)}
        group, how = an.pick(r3, [r1, r2, r3], self.rule, t)
        self.assertEqual(([c["id"] for c in group], how), (["z2"], "같은 에이전트의 앞 회차"))
        self.assertTrue(an.decided(group, how, self.rule))
        # 앞 회차가 아직 안 끝났으면(끝 시각이 이 회차 시작보다 늦음) 쓰지 않는다
        r2["actual"]["end"] = "2026-11-05T01:35:00Z"
        t["z2"] = (r2["actual"]["start"], r2["actual"]["end"])
        self.assertEqual([c["id"] for c in an.pick(r3, [r1, r2, r3], self.rule, t)[0]], ["z1"])

    def test_ties_go_to_the_hand_prediction(self):
        # v2: 맨 앞이 동점 여럿이면 스위치가 가리지 못한 것 → 규칙은 답하지 않는다(손 예측 몫)
        def r(m):
            return {"id": str(m), "actual": {"minutes": m, "turns": 10}, "predicted": {}}
        one, tight, wide = [r(3.0)], [r(1.4), r(1.7), r(2.4)], [r(2.0), r(9.0)]
        self.assertTrue(an.decided(one, "반드시 같은 답", self.rule))
        self.assertTrue(an.decided(tight, "반드시 같은 답", self.rule))   # 동점끼리 2배 안: 가운데 값으로 답한다
        self.assertFalse(an.decided(wide, "반드시 같은 답", self.rule))   # 크게 벌어지면 손 예측으로
        self.assertTrue(an.decided(wide, "반드시 같은 답", {**self.rule, "defer_ties": False}))
        self.assertFalse(an.decided([], None, self.rule))

    def test_a_new_record_from_a_situation_file_can_use_every_finished_record(self):
        # 기록을 덧붙이기 전(상황 파일): 지금 보내는 일이라 이미 끝난 기록은 모두 후보다
        new = {"id": "(새 기록)", "project": "exam_grader", "date": "", "batch": None,
               "situation": dict(next(d for d in self.records if d["id"] == "p141")["situation"]), "predicted": {}, "actual": {}}
        group, how = an.pick(new, self.records, self.rule, self.t)
        self.assertTrue(group and how)
        self.assertTrue(all(dp.done(c) for c in group))

    def test_same_answers_give_the_same_pick(self):
        # 고르기는 기계가 한다: 같은 기록에 두 번 돌려도 같은 묶음
        d = self.records[-1]
        a, b = an.pick(d, self.records, self.rule, self.t), an.pick(d, self.records, self.rule, self.t)
        self.assertEqual([c["id"] for c in a[0]], [c["id"] for c in b[0]])


if __name__ == "__main__":
    unittest.main()
