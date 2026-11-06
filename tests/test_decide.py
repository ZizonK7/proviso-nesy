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
        # 날짜를 박아 둔다: 날짜를 안 적으면 오늘 날짜로 보내서, 날짜로 켜지는 새 검사(예: 2026-11-07부터 피드백 정답 칸)에 내일 깨진다
        (self.tmp / "job.toml").write_text("""project = "exam_grader"
batch = 999
date = "2026-11-06"
task = "구현(같은 작성 에이전트 14회차, 이어서): 풀이지 한 장 새로 쓰기 + 렌더 확인"
model = "Opus 5.5"
effort = "high"
agent = "작성"
round = 14
[files]
write = 1
[situation]
S_resumed = "예"
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
[feedback]
read = ["common", "exam_grader", "images", "parallel", "professor_king"]
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
        # 모델·effort 칸을 옮기고, '기본 설정이 아닌가'(S_other_model)는 두 칸에서 계산해 넣는다
        self.assertEqual((d["model"], d["effort"], d["situation"]["S_other_model"]), ("Opus 5.5", "high", "아니오"))
        write_log(self.tmp / "agent.jsonl", [("2026-11-04T01:00:00Z", "user", 0), ("2026-11-04T01:00:20Z", "assistant", 60000),
                                              ("2026-11-04T01:00:21Z", "tool", 0), ("2026-11-04T01:02:00Z", "assistant", 70000)])
        rc.finish(rid, self.tmp / "agent.jsonl", report="docs/worklog/CLAUDE.md", path=self.tmp / "d.toml", feedback="없음: 시험용 가짜 기록")
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual((d["actual"]["status"], d["actual"]["start"], d["actual"]["turns"]), ("done", "2026-11-04T01:00:00Z", 2))
        self.assertIn("turns", d)
        self.assertEqual((d["log"]["blocks"], d["log"]["responses"], d["log"]["read_calls"]), (2, 2, 2))  # 로그 숫자(2026-11-05)
        self.assertEqual(d["review"]["report"], "docs/worklog/CLAUDE.md")
        # 배치 줄 검사는 저장소의 docs/AGENT-LOG.md를 보므로(임시 복사본이 아님) 여기서는 뺀다
        errors = [e for e in dp.validate(dp.load(self.tmp / "d.toml"), pr.load_kn()) if e.startswith(rid) and "AGENT-LOG" not in e]
        self.assertEqual(errors, [f"{rid}: 시간 구간이 빗나갔는데 review.wrong(틀린 조각 id)과 review.why(조건 흐림/이유 틀림/바깥 상황/까닭 모름)가 없음 "
                                  f"(까닭을 못 찾았으면 why = \"까닭 모름\", 이때 wrong은 비워도 된다)"] if d["predicted"]["told"] != dp.zone(d["actual"]["minutes"]) else [])

    def test_send_needs_the_file_count_from_nov_4(self):
        # 2026-11-04 사용자 결정: 쓰는 파일 수(files)는 실제 지시서에서 세어 보낼 때 적는다 — 2026-11-04부터 없으면 막는다
        job = (self.tmp / "job.toml").read_text(encoding="utf-8")
        no_files = job.replace("[files]\nwrite = 1\n", "")
        (self.tmp / "late.toml").write_text(no_files.replace('date = "2026-11-06"', f'date = "{dp.FILES_REQUIRED_FROM}"'), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            rc.send(self.tmp / "late.toml", self.tmp / "d.toml", self.tmp / "log.md")
        self.assertIn("[files]", str(cm.exception))
        (self.tmp / "early.toml").write_text(no_files.replace('date = "2026-11-06"', 'date = "2026-11-03"'), encoding="utf-8")
        rc.send(self.tmp / "early.toml", self.tmp / "d.toml", self.tmp / "log.md")  # 그 전 날짜는 없어도 된다
        # 정해진 입력(출력 하나)인데 파일이 여럿이면 보낼 때 막는다
        (self.tmp / "clash_files.toml").write_text(job.replace("write = 1", "write = 3").replace('S_resumed = "예"', 'S_resumed = "예"\nS_fixed_input = "예"'),
                                                   encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            rc.send(self.tmp / "clash_files.toml", self.tmp / "d.toml", self.tmp / "log.md")
        self.assertIn("S_fixed_input", str(cm.exception))
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["files"], {"write": 1}) if "files" in d else None

    def test_send_needs_model_and_effort_and_checks_the_default_setup_state(self):
        job = (self.tmp / "job.toml").read_text(encoding="utf-8")
        (self.tmp / "no_model.toml").write_text(job.replace('model = "Opus 5.5"\n', ""), encoding="utf-8")
        with self.assertRaises(SystemExit):
            rc.send(self.tmp / "no_model.toml", self.tmp / "d.toml", self.tmp / "log.md")
        # 상황에 S_other_model을 적었으면 두 칸으로 계산한 값과 같아야 한다 (Opus 5.5 xhigh는 기본 설정이 아니다)
        (self.tmp / "clash.toml").write_text(job.replace('effort = "high"', 'effort = "xhigh"')
                                             .replace('S_resumed = "예"', 'S_resumed = "예"\nS_other_model = "아니오"'), encoding="utf-8")
        with self.assertRaises(SystemExit):
            rc.send(self.tmp / "clash.toml", self.tmp / "d.toml", self.tmp / "log.md")
        (self.tmp / "haiku.toml").write_text(job.replace('model = "Opus 5.5"', 'model = "Haiku 5.5"'), encoding="utf-8")
        rc.send(self.tmp / "haiku.toml", self.tmp / "d.toml", self.tmp / "log.md")
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual((d["model"], d["situation"]["S_other_model"]), ("Haiku 5.5", "예"))
        self.assertEqual(len(dp.load(self.tmp / "d.toml")), len(dp.load()) + 1)  # 막힌 두 번은 아무것도 덧붙이지 않았다

    def test_direct_work_is_logged_and_measured_from_the_main_log(self):
        (self.tmp / "direct.toml").write_text("# 직접 한 일\n", encoding="utf-8")
        (self.tmp / "dj.toml").write_text('project = "proviso"\ndate = "2026-11-06"\ntask = "문서 두 곳 고치기"\n[predicted]\nturns = [4, 8]\ntokens_m = [0.3, 0.6]\n'
                                          '[decide]\nmain_ctx_k = 800\n[feedback]\nread = ["common", "docs"]\n', encoding="utf-8")
        rc.direct(self.tmp / "dj.toml", self.tmp / "direct.toml")
        write_log(self.tmp / "main.jsonl", [("2026-11-04T02:00:00Z", "user", 0), ("2026-11-04T02:00:10Z", "assistant", 800000),
                                             ("2026-11-04T02:00:11Z", "tool", 0), ("2026-11-04T02:01:00Z", "assistant", 812000),
                                             ("2026-11-04T02:05:00Z", "user", 0), ("2026-11-04T02:05:10Z", "assistant", 815000)])
        out = rc.finish("m001", self.tmp / "main.jsonl", "2026-11-04T02:00:00Z", "2026-11-04T02:01:00Z", path=self.tmp / "direct.toml",
                        feedback="없음: 시험용 가짜 기록")
        self.assertIn("m001", out)
        e = dp.load_direct(self.tmp / "direct.toml")[0]
        self.assertEqual((e["decide"]["chose"], e["actual"]["status"], e["actual"]["turns"], e["actual"]["added_k"]), ("직접", "done", 2, 12))
        self.assertEqual((e["log"]["blocks"], e["log"]["ctx_start_k"], e["log"]["ctx_end_k"]), (2, 800, 812))  # 같은 창의 로그 숫자
        self.assertEqual(dp.validate_direct(dp.load_direct(self.tmp / "direct.toml")), [])


    def test_direct_hand_prediction_is_kept_and_compared(self):
        # 2026-11-06 사용자 결정: 직접 하는 작업도 손 예측을 남기고, 끝나면 실측과 견준다. 11-07부터 필수.
        (self.tmp / "direct.toml").write_text("# 직접 한 일\n", encoding="utf-8")
        head = 'project = "proviso"\ndate = "2026-11-07"\ntask = "문서 두 곳 고치기"\n'
        tail = '[decide]\nmain_ctx_k = 800\nwhy = ["대화 맥락"]\n[feedback]\nread = ' + repr(sorted(p.stem for p in (dp.ROOT / "feedback" / "main").glob("*.md"))).replace("'", '"') + \
               '\nsearched = ["문서"]\nhit = []\nhit_none = "시험용 가짜 기록"\n'
        (self.tmp / "no.toml").write_text(head + '[predicted]\nturns = [4, 8]\ntokens_m = [0.3, 0.6]\n' + tail, encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            rc.direct(self.tmp / "no.toml", self.tmp / "direct.toml")
        self.assertIn("predicted.minutes", str(cm.exception))
        (self.tmp / "ok.toml").write_text(head + '[predicted]\nminutes = [0.5, 2]\nturns = [1, 2]\ntokens_m = [0.3, 0.6]\nctx_start_k = 800\n' + tail,
                                          encoding="utf-8")
        rc.direct(self.tmp / "ok.toml", self.tmp / "direct.toml")
        e = dp.load_direct(self.tmp / "direct.toml")[0]
        self.assertEqual((e["predicted"]["minutes"], e["predicted"]["ctx_start_k"], e["predicted"]["written_before"]), ([0.5, 2], 800, True))
        write_log(self.tmp / "main.jsonl", [("2026-11-07T02:00:00Z", "user", 0), ("2026-11-07T02:00:10Z", "assistant", 800000),
                                             ("2026-11-07T02:00:11Z", "tool", 0), ("2026-11-07T02:01:00Z", "assistant", 812000)])
        out = rc.finish("m001", self.tmp / "main.jsonl", "2026-11-07T02:00:00Z", "2026-11-07T02:01:00Z", path=self.tmp / "direct.toml",
                        feedback="없음: 시험용 가짜 기록", missed="없음: 시험용 가짜 기록")
        self.assertIn("손 예측 vs 실측: 분 1.0 (예측 0.5–2, 안) · 줄 2 (예측 1–2, 안)", out)
        self.assertEqual(dp.direct_predicted_errors({"id": "m9", "date": "2026-11-07"})[0][:4], "m9: ")
        self.assertEqual(dp.direct_predicted_errors({"id": "m9", "date": "2026-11-06"}), [])


class Check(unittest.TestCase):
    def test_rule_is_tested_by_decide_cost(self):
        kn = pr.load_kn()
        self.assertIn("decide_cost", kn.nodes["R_send_or_not"].data["check"])
        verdict, _ = checks.decide_cost()
        self.assertTrue(verdict.startswith(("시험 전", "지지됨", "반박됨")))


if __name__ == "__main__":
    unittest.main()
