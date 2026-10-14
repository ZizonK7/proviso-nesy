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

    def test_duplicate_id(self):
        kn = load_text('[[goal]]\nid="A"\ntext="a"\n[[state]]\nid="A"\ntext="s"\n')
        self.assertIn("id 중복: A", schema.validate(kn))


if __name__ == "__main__":
    unittest.main()
