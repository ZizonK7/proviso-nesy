"""보낼까 판단 (2026-11-03 사용자 결정): 하위 에이전트에 맡길지 메인이 직접 할지를 계산으로. decide.py · record.py · direct.toml"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from domains.agent_usage import checks, decide as de, dispatches as dp, predict as pr, record as rc

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "domains" / "agent_usage"


def write_log(path: Path, lines: list[tuple[str, str, int]]) -> None:
    """(시각, 종류, 맥락) → 대화 기록 줄. 종류: user(지시) / assistant(응답) / tool(도구 결과)."""
    out = []
    for i, (ts, kind, ctx) in enumerate(lines):
        if kind == "user":
            out.append({"type": "user", "timestamp": ts, "message": {"content": "지시"}})
        elif kind == "tool":
            out.append({"type": "user", "timestamp": ts, "message": {"content": [{"type": "tool_result", "content": "x"}]}})
        else:
            out.append({"type": "assistant", "timestamp": ts, "message": {"id": f"m{i}", "usage": {
                "cache_read_input_tokens": ctx, "cache_creation_input_tokens": 0, "input_tokens": 0, "output_tokens": 10},
                "content": [{"type": "tool_use", "name": "Read", "input": {}}]}})
    path.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in out), encoding="utf-8")


class Costs(unittest.TestCase):
    def test_direct_pays_for_the_context_it_leaves_behind(self):
        p = {"send_overhead_lines": 10, "report_k": 5, "base_k": 60, "left_responses": 50, "lines_per_response": 2}
        big = de.costs(turns=60, tokens_m=12.0, main_k=800, p=p)   # 큰 일, 큰 메인 맥락 → 보냄
        self.assertEqual(big["cheaper"], "보냄")
        self.assertAlmostEqual(big["added_k"], 2 * (200 - 60))
        small = de.costs(turns=6, tokens_m=0.4, main_k=800, p=p)   # 도구 몇 번 → 직접
        self.assertEqual(small["cheaper"], "직접")
        self.assertGreater(de.costs(60, 12.0, 800, p, left=200)["direct_m"], big["direct_m"])  # 대화가 길게 남을수록 직접이 비싸다

    def test_cost_only_reason_must_match_the_cheaper_side(self):
        dec = {"main_ctx_k": 800, "left": 50, "direct_m": 6.0, "send_m": 9.0, "chose": "보냄", "why": ["비용"]}
        self.assertTrue(any("비용으로는 다른 쪽이 싸다" in e for e in dp.decide_errors("x", dec, "보냄")))
        self.assertEqual(dp.decide_errors("x", {**dec, "why": ["새 눈"]}, "보냄"), [])  # 새 눈이 필요하면 비싸도 보낸다
        self.assertTrue(dp.decide_errors("x", {**dec, "why": ["감"]}, "보냄"))


class Bundle(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copy(HERE / "dispatches.toml", self.tmp / "d.toml")
        shutil.copy(ROOT / "docs" / "AGENT-LOG.md", self.tmp / "log.md")
        (self.tmp / "job.toml").write_text("""project = "exam_grader"
batch = 999
task = "구현(같은 작성 에이전트 14회차, 이어서): 풀이지 한 장 새로 쓰기 + 렌더 확인"
agent = "작성"
round = 14
[situation]
S_resumed = "예"
S_other_model = "아니오"
S_specified = "예"
[predicted]
minutes = [1.5, 3]
turns = [11, 18]
tokens_m = [3, 5.5]
rules = ["R_turns_analogy_v2"]
analog = "p141"
reason = "빗댄 p141"
[decide]
main_ctx_k = 800
why = ["대화 계속"]
""", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_send_then_finish_fills_a_valid_record(self):
        out = rc.send(self.tmp / "job.toml", self.tmp / "d.toml", self.tmp / "log.md")
        rid = dp.load(self.tmp / "d.toml")[-1]["id"]
        self.assertIn(rid, out)
        self.assertIn(999, dp.logged_batches(self.tmp / "log.md"))  # 배치 머리를 붙였다
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual((d["predicted"]["told"], d["decide"]["chose"], d["actual"]["status"]), ("잠깐", "보냄", "unknown"))
        self.assertIn("told", d.get("calc", {}))  # 계산기 답은 그 기록의 상황 값으로
        write_log(self.tmp / "agent.jsonl", [("2026-11-04T01:00:00Z", "user", 0), ("2026-11-04T01:00:20Z", "assistant", 60000),
                                              ("2026-11-04T01:00:21Z", "tool", 0), ("2026-11-04T01:02:00Z", "assistant", 70000)])
        rc.finish(rid, self.tmp / "agent.jsonl", report="docs/worklog/CLAUDE.md", path=self.tmp / "d.toml")
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual((d["actual"]["status"], d["actual"]["start"], d["actual"]["turns"]), ("done", "2026-11-04T01:00:00Z", 2))
        self.assertIn("turns", d)
        self.assertEqual(d["review"]["report"], "docs/worklog/CLAUDE.md")
        errors = [e for e in dp.validate(dp.load(self.tmp / "d.toml"), pr.load_kn()) if e.startswith(rid)]
        self.assertEqual(errors, [f"{rid}: 시간 구간이 빗나갔는데 review.wrong(틀린 조각 id)과 review.why(조건 흐림/이유 틀림/바깥 상황/까닭 모름)가 없음 "
                                  f"(까닭을 못 찾았으면 why = \"까닭 모름\", 이때 wrong은 비워도 된다)"] if d["predicted"]["told"] != dp.zone(d["actual"]["minutes"]) else [])

    def test_direct_work_is_logged_and_measured_from_the_main_log(self):
        (self.tmp / "direct.toml").write_text("# 직접 한 일\n", encoding="utf-8")
        (self.tmp / "dj.toml").write_text('project = "proviso"\ntask = "문서 두 곳 고치기"\n[predicted]\nturns = [4, 8]\ntokens_m = [0.3, 0.6]\n'
                                          '[decide]\nmain_ctx_k = 800\n', encoding="utf-8")
        rc.direct(self.tmp / "dj.toml", self.tmp / "direct.toml")
        write_log(self.tmp / "main.jsonl", [("2026-11-04T02:00:00Z", "user", 0), ("2026-11-04T02:00:10Z", "assistant", 800000),
                                             ("2026-11-04T02:00:11Z", "tool", 0), ("2026-11-04T02:01:00Z", "assistant", 812000),
                                             ("2026-11-04T02:05:00Z", "user", 0), ("2026-11-04T02:05:10Z", "assistant", 815000)])
        out = rc.finish("m001", self.tmp / "main.jsonl", "2026-11-04T02:00:00Z", "2026-11-04T02:01:00Z", path=self.tmp / "direct.toml")
        self.assertIn("m001", out)
        e = dp.load_direct(self.tmp / "direct.toml")[0]
        self.assertEqual((e["decide"]["chose"], e["actual"]["status"], e["actual"]["turns"], e["actual"]["added_k"]), ("직접", "done", 2, 12))
        self.assertEqual(dp.validate_direct(dp.load_direct(self.tmp / "direct.toml")), [])


class Check(unittest.TestCase):
    def test_rule_is_tested_by_decide_cost(self):
        kn = pr.load_kn()
        self.assertIn("decide_cost", kn.nodes["R_send_or_not"].data["check"])
        verdict, _ = checks.decide_cost()
        self.assertTrue(verdict.startswith(("시험 전", "지지됨", "반박됨")))


if __name__ == "__main__":
    unittest.main()
