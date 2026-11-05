import tempfile
import unittest
from pathlib import Path

from proviso import graph, schema

ROOT = Path(__file__).resolve().parent.parent


def load_text(text: str) -> schema.Knowledge:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "k.toml"
        path.write_text(text, encoding="utf-8")
        return schema.load(path)


class FlowlogKnowledge(unittest.TestCase):
    def test_flowlog_file_is_valid(self):
        kn = schema.load(ROOT / "domains" / "flowlog" / "knowledge.toml")
        self.assertEqual(schema.validate(kn), [])

    def test_graph_has_every_node_and_goal_edges(self):
        kn = schema.load(ROOT / "domains" / "flowlog" / "knowledge.toml")
        text = graph.to_mermaid(kn)
        for node_id in kn.nodes:
            self.assertIn(f"class {node_id} ", text)
        self.assertIn("G_fast ==> G_record", text)
        self.assertIn("O_slow_recent -->|근거| R_P1b", text)


class Validation(unittest.TestCase):
    def test_missing_reference(self):
        kn = load_text('[[rule]]\nid="R"\nversion=1\nstatus="hypothesis"\nmethod="m"\nreason="r"\nserves=["G_x"]\n')
        self.assertIn("R.serves: 없는 id 'G_x'", schema.validate(kn))

    def test_wrong_reference_kind(self):
        kn = load_text(
            '[[state]]\nid="S"\ntext="s"\n'
            '[[rule]]\nid="R"\nversion=1\nstatus="hypothesis"\nmethod="m"\nreason="r"\nserves=["S"]\n'
        )
        self.assertTrue(any("R.serves" in e and "목표만" in e for e in schema.validate(kn)))

    def test_missing_reason_and_bad_status(self):
        kn = load_text('[[rule]]\nid="R"\nversion=1\nstatus="maybe"\nmethod="m"\n')
        errors = schema.validate(kn)
        self.assertIn("R: 'reason' 칸이 비어 있음", errors)
        self.assertTrue(any("status" in e for e in errors))

    def test_goal_cycle(self):
        kn = load_text('[[goal]]\nid="A"\ntext="a"\nparent="B"\n[[goal]]\nid="B"\ntext="b"\nparent="A"\n')
        self.assertTrue(any("돌고 돎" in e for e in schema.validate(kn)))

    def test_against_points_to_observation_and_draws_into_the_rule(self):
        kn = load_text(
            '[[observation]]\nid="O"\ntext="o"\nsource="measured"\n'
            '[[hypothesis]]\nid="H"\ntext="h"\nsource="ai"\nevidence=["O"]\n'
            '[[rule]]\nid="R"\nversion=1\nstatus="hypothesis"\nmethod="m"\nreason="r"\nagainst=["O"]\n'
        )
        self.assertEqual(schema.validate(kn), [])
        text = graph.to_mermaid(kn)
        self.assertIn("O -.-x|반대| R", text)
        self.assertIn("O -->|근거| H", text)

    def test_against_rejects_a_goal(self):
        kn = load_text(
            '[[goal]]\nid="G"\ntext="g"\n'
            '[[rule]]\nid="R"\nversion=1\nstatus="hypothesis"\nmethod="m"\nreason="r"\nagainst=["G"]\n'
        )
        self.assertTrue(any("R.against" in e for e in schema.validate(kn)))

    def test_duplicate_id(self):
        kn = load_text('[[goal]]\nid="A"\ntext="a"\n[[state]]\nid="A"\ntext="s"\n')
        self.assertIn("id 중복: A", schema.validate(kn))


if __name__ == "__main__":
    unittest.main()


class SplitFilesTest(unittest.TestCase):
    """knowledge.toml 옆의 knowledge-*.toml(나눈 파일)을 같이 읽는다 (2026-11-04)."""

    def _write(self, d, files):
        for name, text in files.items():
            (d / name).write_text(text, encoding="utf-8")
        return schema.load(d / "knowledge.toml")

    def test_parts_are_merged_and_refs_cross_files(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            kn = self._write(d, {
                "knowledge.toml": '[domain]\nid = "x"\n[[state]]\nid = "S_a"\ntext = "상태"\n',
                "knowledge-b.toml": '[[hypothesis]]\nid = "H_1"\ntext = "가설"\nsource = "ai"\nconditions = ["S_a"]\n'
                                    '[[judgment]]\nof = "H_1"\nsource = "ai"\nverdict = "지지"\ndate = 2026-11-04\nnote = "n"\n',
            })
            self.assertEqual(kn.parts, ["knowledge.toml", "knowledge-b.toml"])
            self.assertIn("H_1", kn.nodes)
            self.assertEqual(len(kn.judgments), 1)
            self.assertEqual(schema.validate(kn), [])

    def test_duplicate_id_across_files_and_skeleton_in_part_are_errors(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            h = '[[hypothesis]]\nid = "H_1"\ntext = "가설"\nsource = "ai"\n'
            kn = self._write(d, {
                "knowledge.toml": '[domain]\nid = "x"\n' + h,
                "knowledge-b.toml": h + '[[goal]]\nid = "G_x"\ntext = "목표"\n',
            })
            errors = schema.validate(kn)
            self.assertTrue(any("id 중복: H_1" in e for e in errors), errors)
            self.assertTrue(any("knowledge-b.toml" in e and "[goal]" in e for e in errors), errors)

    def test_other_file_names_are_not_read(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            (d / "notes.toml").write_text('[[hypothesis]]\nid = "H_x"\ntext = "t"\nsource = "s"\n', encoding="utf-8")
            kn = self._write(d, {"knowledge.toml": '[domain]\nid = "x"\n'})
            self.assertNotIn("H_x", kn.nodes)
            self.assertEqual(schema.load(d / "notes.toml").parts, ["notes.toml"])
