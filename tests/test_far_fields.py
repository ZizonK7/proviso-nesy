import unittest
from pathlib import Path

from proviso import audit, schema
from domains.far_fields import checks
from domains.far_fields.shapes import SHAPES

ROOT = Path(__file__).resolve().parent.parent
KN = ROOT / "domains" / "far_fields" / "knowledge.toml"


class FarFieldsTest(unittest.TestCase):
    """먼 분야 조각: 꼭 지킬 것을 검사가 막는다 (루트 CLAUDE.md '꼭 할 단계는 검사가 막게 한다')."""

    @classmethod
    def setUpClass(cls):
        cls.kn = schema.load(KN)

    def test_validates_without_harms(self):
        self.assertEqual(schema.validate(self.kn), [])
        self.assertEqual(audit.unaccepted_harms(self.kn), [])

    def test_every_piece_has_text_source_and_field(self):
        for h in self.kn.of("hypothesis"):
            self.assertTrue(h.data["text"].strip(), h.id)
            self.assertTrue(h.data["source"].startswith(("AI 생성:", "웹 조사:", "AI 생성(Opus 5.5, Claude Code 서브에이전트)")), h.id)
            for k in ("field", "rule", "why", "breaks", "confidence"):
                self.assertIn(k, h.data, h.id)

    def test_judgments_are_ai_only_and_unreviewed_have_plan(self):
        # 전부 AI가 만들거나 모은 재료다: 판정은 가장 가벼운 출처(ai)만 있어야 한다.
        # 1차(API 생성·웹 조사)는 모두 AI 검토 판정이 있고, 2차(서브에이전트 생성)는 검토 없이 test_plan만 있다(사용자 2026-11-03)
        judged = {j["of"] for j in self.kn.judgments}
        self.assertEqual({j["source"] for j in self.kn.judgments}, {"ai"})
        for h in self.kn.of("hypothesis"):
            if "서브에이전트" in h.data["source"]:
                self.assertNotIn(h.id, judged, h.id)
                self.assertIn("검토하지 않은", h.data.get("test_plan", ""), h.id)
            else:
                self.assertIn(h.id, judged, h.id)

    def test_field_lists_do_not_overlap(self):
        # 1·2·3차 분야 목록은 이름·slug가 겹치지 않는다
        import json
        names, slugs = [], []
        for name in ("fields.json", "fields2.json", "fields3.json"):
            for f in json.loads((ROOT / "domains" / "far_fields" / name).read_text(encoding="utf-8")):
                names.append(f["ko"]); slugs.append(f["slug"])
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_split_by_group(self):
        # 묶음별 파일로 나눈다(2026-11-04): 뼈대만 knowledge.toml에, 조각은 묶음 파일에. 파일마다 묶음 하나
        from domains.far_fields.build import GROUP_FILE
        self.assertEqual(len(self.kn.parts), 1 + len(GROUP_FILE))
        main = schema.load.__globals__["tomllib"].loads((KN).read_text(encoding="utf-8"))
        self.assertNotIn("hypothesis", main)
        for h in self.kn.of("hypothesis"):
            self.assertIn(h.data["group"], GROUP_FILE, h.id)

    def test_shapes_are_from_vocabulary(self):
        self.assertEqual({s.id for s in self.kn.of("state")}, set(SHAPES))
        for h in self.kn.of("hypothesis"):
            self.assertTrue(set(h.refs("conditions")) <= set(SHAPES), h.id)

    def test_field_name_leak_is_rare(self):
        _, warnings = checks.AUDIT(self.kn)
        self.assertLess(len(warnings), len(self.kn.of("hypothesis")) * 0.05)


if __name__ == "__main__":
    unittest.main()
