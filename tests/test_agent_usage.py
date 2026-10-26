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

    def test_turns_measure_action_length_and_context_without_content(self):
        # 전제 1 시험(2026-10-26): 턴마다 동작·길이·맥락을 숫자로. 첫 턴은 Read 동작, 다음 응답까지 9.5분(570초), 도구 결과까지 30초
        with tempfile.TemporaryDirectory() as d:
            rows = agent_usage.turn_rows(str(write_transcript(Path(d))))
            table = agent_usage.turn_table(rows)
        self.assertEqual([r["action"] for r in rows], ["Read", "글"])
        self.assertEqual(rows[0]["turn_s"], 570.0)
        self.assertEqual(rows[0]["tool_s"], 30.0)
        self.assertEqual(rows[0]["ctx_k"], 1)
        self.assertIn("| Read | 1 | 570.0 | 30.0 |", table)
        self.assertNotIn("파일 내용", table)

    def test_bash_action_keeps_only_the_verb(self):
        self.assertEqual(agent_usage._action([{"type": "tool_use", "name": "Bash", "input": {"command": "grep -rn 비밀 src/"}}]),
                         "Bash:grep")
        self.assertEqual(agent_usage._action([{"type": "tool_use", "name": "Grep", "input": {}},
                                              {"type": "tool_use", "name": "Edit", "input": {}}]), "Grep+Edit")


if __name__ == "__main__":
    unittest.main()
