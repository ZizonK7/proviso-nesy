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
            self.assertTrue(h.data["source"].startswith(("AI 생성:", "웹 조사:")), h.id)
            for k in ("field", "rule", "why", "breaks", "confidence"):
                self.assertIn(k, h.data, h.id)

    def test_every_piece_has_ai_judgment_only(self):
        # 전부 AI가 만들거나 모은 재료다: 판정은 가장 가벼운 출처(ai)만 있어야 한다
        judged = {j["of"] for j in self.kn.judgments}
        for h in self.kn.of("hypothesis"):
            self.assertIn(h.id, judged, h.id)
        self.assertEqual({j["source"] for j in self.kn.judgments}, {"ai"})
        self.assertEqual(audit.untested(self.kn), [])

    def test_shapes_are_from_vocabulary(self):
        self.assertEqual({s.id for s in self.kn.of("state")}, set(SHAPES))
        for h in self.kn.of("hypothesis"):
            self.assertTrue(set(h.refs("conditions")) <= set(SHAPES), h.id)

    def test_field_name_leak_is_rare(self):
        _, warnings = checks.AUDIT(self.kn)
        self.assertLess(len(warnings), len(self.kn.of("hypothesis")) * 0.05)


if __name__ == "__main__":
    unittest.main()
