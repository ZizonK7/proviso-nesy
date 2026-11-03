"""일의 크기 모델 (2026-11-03 사용자 결정): 정해진 일은 지시서에서 센 수로 턴을 잡는다. domains/agent_usage/size.py"""
import copy
import unittest
from pathlib import Path

from domains.agent_usage import dispatches as dp, size as sz
from proviso import schema

ROOT = Path(__file__).resolve().parent.parent
KN = ROOT / "domains" / "agent_usage" / "knowledge.toml"


class SizeRecords(unittest.TestCase):
    def test_size_table_is_checked(self):
        kn = schema.load(KN)
        records = dp.load()
        rec = {"id": "zz9", "project": "proviso", "batch": 99, "date": "2026-10-20", "task": "t",
               "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"status": "unknown"},
               "size": {"outputs": 1, "edits": 2, "find_cap": "25 원문"}}
        self.assertEqual(dp.validate(records + [rec], kn), [])
        rec["size"] = {"outputs": -1}
        self.assertTrue(any("size.outputs" in e for e in dp.validate(records + [rec], kn)))
        rec["size"] = {"pages": 3}
        self.assertTrue(any("size의 칸" in e for e in dp.validate(records + [rec], kn)))

    def test_specified_is_a_state_known_before_sending(self):
        # 할 일이 정해져 있나 = 보내기 전에 지시서로 아는 갈림길
        kn = schema.load(KN)
        self.assertIs(kn.nodes["S_specified"].data.get("known_before"), True)


class SizeModel(unittest.TestCase):
    def test_turns_add_up_and_unknown_when_a_term_is_missing(self):
        terms = {"base": (10, 20), "outputs": (30, 50), "edits": (2, 4), "reads": None}
        self.assertEqual(sz.turns_range(terms, {"outputs": 2, "edits": 5}), (10 + 60 + 10, 20 + 100 + 20))
        self.assertIsNone(sz.turns_range(terms, {"reads": 1}))  # 센 수가 있는데 그 몫을 세울 수 없었다 → 모름
        self.assertIsNone(sz.turns_range({"base": None}, {"outputs": 1}))

    def test_only_specified_default_model_records_with_counts_are_used(self):
        base = {"id": "x", "situation": {"S_other_model": "아니오", "S_specified": "예"}, "size": {"outputs": 1},
                "actual": {"minutes": 3, "turns": 20}, "predicted": {}}
        self.assertTrue(sz.usable(base))
        self.assertFalse(sz.usable({**base, "situation": {"S_other_model": "예", "S_specified": "예"}}))
        self.assertFalse(sz.usable({**base, "situation": {"S_other_model": "아니오", "S_specified": "일부"}}))
        self.assertTrue(sz.usable({**base, "situation": {"S_other_model": "아니오", "S_specified": "일부"}}, gate=False))
        self.assertFalse(sz.usable({**base, "size": {"outputs": 0}}))

    def test_numbers_come_only_from_records_up_to_seen_until(self):
        # size.toml의 범위 = seen_until까지로 다시 맞춘 범위. 그 뒤 기록을 바꿔도 맞춘 값은 같다(시험 기록은 맞추는 데 안 쓴다)
        cut, written, _ = sz.load_terms()
        records = dp.load()
        train = sz.split(records, cut)[0]
        fitted = sz.fit_terms(train, 2.0)
        self.assertEqual(written, {k: v["range"] for k, v in fitted.items()})
        changed = copy.deepcopy(records)
        ids = [d["id"] for d in changed]
        for d in changed[ids.index(cut) + 1:]:
            d["actual"] = {**d.get("actual", {}), "turns": 9999}
        again = sz.fit_terms(sz.split(changed, cut)[0], 2.0)
        self.assertEqual({k: v["range"] for k, v in fitted.items()}, {k: v["range"] for k, v in again.items()})


if __name__ == "__main__":
    unittest.main()
