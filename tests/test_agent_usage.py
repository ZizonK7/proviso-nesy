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


def _a(ts, mid, ctx, *content, think_ms=None):
    """응답 줄 하나(가짜). ctx = 캐시 읽기 토큰. 같은 응답(mid)이 줄 여럿으로 나뉠 수 있다."""
    d = {"type": "assistant", "timestamp": ts, "message": {"id": mid, "usage": {
        "input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": ctx, "output_tokens": 1}, "content": list(content)}}
    if think_ms is not None:
        d["thinkingDurationMs"] = think_ms
    return d


def _use(tid, name, **inp):
    return {"type": "tool_use", "id": tid, "name": name, "input": inp}


def _res(ts, tid, content="ok", error=False):
    return {"type": "user", "timestamp": ts, "message": {"content": [
        {"type": "tool_result", "tool_use_id": tid, "content": content, "is_error": error}]}}


def write_log_fixture(folder: Path) -> Path:
    """[dispatch.log] 시험용 가짜 기록 (내용은 지어낸 것). 1회차 01:00–01:10, 2회차 02:00–02:01."""
    lines = [
        {"type": "user", "timestamp": "2026-11-05T01:00:00Z", "message": {"content": "가짜 지시 첫 줄\n둘째 줄"}},
        {"type": "user", "timestamp": "2026-11-05T01:00:00Z", "isMeta": True, "message": {"content": "붙어 오는 안내"}},
        _a("2026-11-05T01:00:10Z", "m1", 1000, {"type": "thinking", "thinking": ""}, think_ms=1500),
        _a("2026-11-05T01:00:11Z", "m1", 1000, _use("t1", "Write", file_path="/repo/a.py", content="x\ny\n")),
        _res("2026-11-05T01:00:12Z", "t1"),
        _a("2026-11-05T01:00:20Z", "m2", 3000, _use("t2", "Edit", file_path="/repo/a.py", old_string="x", new_string="zz")),
        _res("2026-11-05T01:00:21Z", "t2"),
        _a("2026-11-05T01:00:30Z", "m3", 2000, _use("t3", "Edit", file_path="/repo/b.py", old_string="q", new_string="abc")),
        _res("2026-11-05T01:00:31Z", "t3", "실패", error=True),
        _a("2026-11-05T01:00:40Z", "m4", 5000, _use("t4", "Write", file_path="/tmp/x/scratch.txt", content="임시 메모")),
        _res("2026-11-05T01:00:41Z", "t4"),
        _a("2026-11-05T01:00:42Z", "m4", 5000, _use("t5", "Read", file_path="/repo/a.py")),
        _res("2026-11-05T01:00:43Z", "t5", "1\tx"),
        _a("2026-11-05T01:00:50Z", "m5", 4500, _use("t6", "Read", file_path="/repo/p.png")),
        _res("2026-11-05T01:00:51Z", "t6", [{"type": "image", "source": {}}]),
        _a("2026-11-05T01:01:00Z", "m6", 4500, _use("t7", "Bash", command="cd /repo && python -m y")),
        _res("2026-11-05T01:01:01Z", "t7", "out"),
        _a("2026-11-05T01:01:10Z", "m7", 4500, _use("t8", "Bash", command="cd /repo && python -m y")),
        _res("2026-11-05T01:01:11Z", "t8", [{"type": "text", "text": "out2"}]),
        _a("2026-11-05T01:01:20Z", "m8", 4500, _use("t9", "Grep", pattern="z"), _use("t10", "Glob", pattern="*"),
           _use("t11", "WebSearch", query="q"), _use("t12", "WebFetch", url="u"), _use("t13", "Agent", prompt="p"),
           _use("t14", "ToolSearch", query="q")),
        _a("2026-11-05T01:10:00Z", "m9", 4000, {"type": "text", "text": "끝"}),
        {"type": "user", "timestamp": "2026-11-05T02:00:00Z", "message": {"content": [{"type": "text", "text": "2회차 지시"}]}},
        _a("2026-11-05T02:00:10Z", "m10", 6000, _use("t15", "Write", file_path="/repo/c.md", content="c")),
        _res("2026-11-05T02:00:11Z", "t15"),
        _a("2026-11-05T02:01:00Z", "m11", 6200, {"type": "text", "text": "끝"}),
    ]
    path = folder / "agent-log.jsonl"
    path.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines), encoding="utf-8")
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

    def test_turns_toml_block_pastes_into_a_record(self):
        # 2026-11-02: --turns --toml 출력은 dispatches.toml 기록 끝에 그대로 붙는 [dispatch.turns] 블록이다
        import tomllib
        with tempfile.TemporaryDirectory() as d:
            path = write_transcript(Path(d))
            block = agent_usage.turn_toml(agent_usage.turn_rows(str(path)))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                agent_usage.main([str(path), "--turns", "--toml"])
        turns = tomllib.loads('[[dispatch]]\nid = "x"\n' + block)["dispatch"][0]["turns"]
        self.assertEqual(turns["Read"], {"n": 1, "sum_s": 570.0, "turn_s": 570.0, "tool_s": 30.0, "out_chars": 38, "ctx_k": 1})
        self.assertEqual(turns["글"]["n"], 1)
        self.assertIn("[dispatch.turns]", buf.getvalue())
        self.assertNotIn("파일 내용", block)

    def test_after_keeps_only_the_resumed_round(self):
        # 이어 보낸 회차: 01:05 뒤에 시작한 턴만 (첫 턴 01:00:30은 앞 회차)
        with tempfile.TemporaryDirectory() as d:
            path = str(write_transcript(Path(d)))
            self.assertEqual([r["action"] for r in agent_usage.turn_rows(path, after="01:05:00")], ["글"])
            self.assertEqual(len(agent_usage.turn_rows(path, after="2026-10-14T01:00:00Z")), 2)

    def test_rounds_split_at_new_instructions_and_actual_keeps_one_round(self):
        # 2026-11-03: 이어 보낸 회차는 한 로그에 쌓인다 — 답한 뒤 들어온 지시마다 새 회차, --after로 그 회차만 잰다
        lines = [
            {"type": "user", "timestamp": "2026-11-05T01:00:00Z", "message": {"content": "1회차 지시"}},
            {"type": "user", "timestamp": "2026-11-05T01:00:00Z", "message": {"content": "붙어 오는 안내"}},
            {"type": "assistant", "timestamp": "2026-11-05T01:00:20Z", "message": {"usage": {"input_tokens": 1}, "content": [{"type": "text", "text": "가"}]}},
            {"type": "user", "timestamp": "2026-11-05T01:20:00Z", "message": {"content": [{"type": "text", "text": "2회차 지시"}]}},
            {"type": "assistant", "timestamp": "2026-11-05T01:20:30Z", "message": {"usage": {"input_tokens": 1}, "content": [{"type": "text", "text": "나"}]}},
            {"type": "assistant", "timestamp": "2026-11-05T01:22:00Z", "message": {"usage": {"input_tokens": 1}, "content": [{"type": "text", "text": "다"}]}},
        ]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "agent-r.jsonl"
            path.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines), encoding="utf-8")
            r = agent_usage.rounds(str(path))
            self.assertEqual(len(r), 2)
            self.assertEqual((r[1][0].isoformat(), r[1][2]), ("2026-11-05T01:20:00+00:00", 2))
            s = agent_usage.summarize(str(path), "2026-11-05T01:20:00Z")
            self.assertEqual((s["turns"], s["start_iso"], s["end_iso"]), (2, "2026-11-05T01:20:00Z", "2026-11-05T01:22:00Z"))

    def test_log_numbers_first_round(self):
        # 2026-11-05: 로그에서 싸게 얻는 숫자 — 1회차만(--until)
        with tempfile.TemporaryDirectory() as d:
            path = str(write_log_fixture(Path(d)))
            n = agent_usage.log_numbers(path, until="2026-11-05T01:59:00Z")
            s = agent_usage.summarize(path, until="2026-11-05T01:59:00Z")
        self.assertEqual(tuple(n), agent_usage.LOG_KEYS)
        self.assertEqual((n["responses"], n["blocks"]), (9, 11))      # 응답 m1·m4는 줄이 둘
        self.assertEqual(n["blocks"], s["turns"])                     # 블록 수 = --actual의 turns
        self.assertEqual((n["write"], n["edit"], n["scratch_files"]), (1, 1, 1))  # a.py는 Write+Edit → write, /tmp는 뺌
        self.assertEqual((n["write_chars"], n["edit_chars"], n["write_lines"]), (4, 5, 2))
        self.assertEqual((n["read_calls"], n["read_files"], n["read_chars"], n["images"]), (2, 2, 3, 1))  # 그림은 글자로 안 센다
        self.assertEqual((n["bash_calls"], n["bash_out_chars"], n["repeat_cmds"], n["tool_errors"]), (2, 7, 1, 1))
        self.assertEqual([n[k] for k in ("grep_calls", "glob_calls", "web_search", "web_fetch", "agent_calls", "other_tool_calls")],
                         [1, 1, 1, 1, 1, 1])
        self.assertEqual((n["ctx_start_k"], n["ctx_max_k"], n["ctx_end_k"]), (1, 5, 4))
        self.assertEqual((n["thinking_blocks"], n["thinking_s"]), (1, 1.5))
        self.assertEqual((n["brief_chars"], n["brief_lines"]), (len("가짜 지시 첫 줄\n둘째 줄"), 2))  # 안내 줄(isMeta)은 지시가 아니다

    def test_log_numbers_resumed_round_and_no_text(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_log_fixture(Path(d))
            n = agent_usage.log_numbers(str(path), after="2026-11-05T02:00:00Z")
            whole = agent_usage.log_numbers(str(path))
            buf, whole_buf = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf):
                agent_usage.main([str(path), "--log", "--toml", "--after", "02:00:00"])
            with contextlib.redirect_stdout(whole_buf):
                agent_usage.main([str(path), "--log", "--toml"])
        self.assertEqual((n["responses"], n["blocks"], n["write"], n["edit"], n["write_chars"]), (2, 2, 1, 0, 1))
        self.assertEqual((n["brief_chars"], n["brief_lines"], n["ctx_start_k"], n["ctx_end_k"]), (len("2회차 지시"), 1, 6, 6))
        self.assertEqual((whole["responses"], whole["write"], whole["brief_lines"]), (11, 2, 2))  # 창이 없으면 첫 지시
        import tomllib
        out = buf.getvalue()
        log = tomllib.loads('[[dispatch]]\nid = "x"\n' + out.split("\n", 1)[1])["dispatch"][0]["log"]
        self.assertEqual(log, n)
        for text in ("지시", "/repo", "a.py", "python", "임시 메모", "out2", "scratch.txt", "/tmp"):
            self.assertNotIn(text, whole_buf.getvalue().split("\n", 1)[1])   # 숫자만 (이름 줄 뒤)

    def test_bash_verb_strips_cd_assignments_and_wrappers(self):
        # 2026-11-05: 전에는 첫 낱말이라 `cd /repo && python …`이 'Bash:cd'였다(턴 표 줄의 28 %)
        v = agent_usage.bash_verb
        self.assertEqual(v("cd x && python -m y"), "python")
        self.assertEqual(v("PYTHONPATH=. python3 z"), "python3")
        self.assertEqual(v("time make"), "make")
        self.assertEqual(v("cd /a/b; D=/tmp/o; PYTHONIOENCODING=utf-8 /usr/bin/git log"), "git")
        self.assertEqual(v("cd x"), "cd")                              # cd만이면 cd
        self.assertEqual(agent_usage._action([_use("t", "Bash", command="cd /repo && python -m y")]), "Bash:python")

    def test_bash_action_keeps_only_the_verb(self):
        self.assertEqual(agent_usage._action([{"type": "tool_use", "name": "Bash", "input": {"command": "grep -rn 비밀 src/"}}]),
                         "Bash:grep")
        self.assertEqual(agent_usage._action([{"type": "tool_use", "name": "Grep", "input": {}},
                                              {"type": "tool_use", "name": "Edit", "input": {}}]), "Grep+Edit")


if __name__ == "__main__":
    unittest.main()
