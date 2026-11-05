"""eda.export — 논리집 데이터를 CSV로 펼치는 도구 (표준 라이브러리만)."""
import csv
import tempfile
import tomllib
import unittest
from pathlib import Path

from eda import export
from proviso import schema

ROOT = Path(__file__).resolve().parent.parent


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class FlattenTest(unittest.TestCase):
    def test_nested_and_ranges(self):
        rec = {"a": {"b": 1, "r": [2, 5]}, "rules": ["x", "y"], "turns": {"글": {"n": 3}}, "flag": True}
        out = export.flatten(rec)
        self.assertEqual(out["a.b"], 1)
        self.assertEqual((out["a.r_lo"], out["a.r_hi"]), (2, 5))
        self.assertEqual(out["rules"], ["x", "y"])  # 글자 목록은 펼치지 않는다
        self.assertNotIn("turns.글.n", out)  # 턴 표는 따로
        self.assertEqual(export._cell(["x", "y"]), "x|y")


class ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        (cls.out / "stale.csv").write_text("old", encoding="utf-8")
        cls.counts = export.export(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_stale_removed(self):
        self.assertFalse((self.out / "stale.csv").exists())

    def test_node_counts_match_schema(self):
        total = sum(len(schema.load(ROOT / "domains" / d / "knowledge.toml").nodes) for d in export.domains())
        self.assertEqual(self.counts["nodes"], total)

    def test_dispatch_counts_match_file(self):
        raw = tomllib.loads((ROOT / "domains/agent_usage/dispatches.toml").read_text(encoding="utf-8"))
        self.assertEqual(self.counts["dispatches"], len(raw["dispatch"]))
        head = _rows(self.out / "dispatches.csv")[0]
        for col in ("id", "date", "actual.minutes", "predicted.minutes_lo", "hit.minutes"):
            self.assertIn(col, head)

    def test_edges_point_to_known_kinds(self):
        rows = _rows(self.out / "edges.csv")
        self.assertTrue(rows)
        self.assertTrue(all(r["dst_kind"] in schema.KINDS for r in rows))  # validate가 통과하는 데이터면 빈 칸 없음

    def test_feedback(self):
        fb = _rows(self.out / "feedback.csv")
        self.assertTrue(all(r["source_kind"] in (*export.SOURCE_KINDS, "기타") for r in fb))
        self.assertEqual(len(fb), self.counts["feedback"])


if __name__ == "__main__":
    unittest.main()
