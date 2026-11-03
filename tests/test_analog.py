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
            return an.fit_range(train, an.rule_estimates(train, records, self.rule, self.t), 2.0)[0]
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

    def test_same_answers_give_the_same_pick(self):
        # 고르기는 기계가 한다: 같은 기록에 두 번 돌려도 같은 묶음
        d = self.records[-1]
        a, b = an.pick(d, self.records, self.rule, self.t), an.pick(d, self.records, self.rule, self.t)
        self.assertEqual([c["id"] for c in a[0]], [c["id"] for c in b[0]])


if __name__ == "__main__":
    unittest.main()
