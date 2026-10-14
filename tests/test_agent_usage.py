import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import agent_usage


def write_transcript(folder: Path) -> Path:
    lines = [
        {"type": "user", "timestamp": "2026-10-14T01:00:00Z", "message": {"content": "지시서"}},
        {"type": "assistant", "timestamp": "2026-10-14T01:00:30Z", "message": {
            "usage": {"input_tokens": 10, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 0, "output_tokens": 5},
            "content": [{"type": "text", "text": "가" * 36}, {"type": "tool_use", "name": "Read", "input": {}}]}},
        {"type": "user", "timestamp": "2026-10-14T01:01:00Z", "message": {
            "content": [{"type": "tool_result", "content": "파일 내용"}]}},
        {"type": "assistant", "timestamp": "2026-10-14T01:10:00Z", "message": {
            "usage": {"input_tokens": 2, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1000, "output_tokens": 3},
            "content": [{"type": "text", "text": "끝"}]}},
    ]
    path = folder / "agent-abc123.jsonl"
    path.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines), encoding="utf-8")
    (folder / "agent-abc123.meta.json").write_text(json.dumps({"description": "조각 스키마 구현"}, ensure_ascii=False),
                                                   encoding="utf-8")
    return path


class AgentUsage(unittest.TestCase):
    def test_summarize_counts_without_content(self):
        with tempfile.TemporaryDirectory() as d:
            s = agent_usage.summarize(str(write_transcript(Path(d))))
        self.assertEqual(s["turns"], 2)
        self.assertEqual(s["tool_calls"], 1)
        self.assertEqual(s["duration_min"], 10.0)
        self.assertEqual(s["cache_creation"], 1000)
        self.assertEqual(s["cache_read"], 1000)
        self.assertEqual(s["description"], "조각 스키마 구현")
        self.assertNotIn("파일 내용", json.dumps(s, ensure_ascii=False))

    def test_markdown_uses_meta_description_as_name(self):
        with tempfile.TemporaryDirectory() as d:
            write_transcript(Path(d))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                agent_usage.main([str(Path(d) / "agent-*.jsonl"), "--md"])
        self.assertIn("| 조각 스키마 구현 |", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
