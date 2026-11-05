"""피드백 읽기·쓰기 (2026-11-05 사용자 결정: 이 저장소의 목적이 "이전 실수들을 통해 발전한다"로 바뀜, feedback/CLAUDE.md).
백서·메인 모양 검사(feedback) + 보낸 기록·직접 한 일의 feedback.read·review.feedback 검사(dispatches) + record send/finish."""
import shutil
import tempfile
import unittest
from pathlib import Path

import feedback as fb
from domains.agent_usage import dispatches as dp, record as rc
from proviso import schema

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "domains" / "agent_usage"


def copy_feedback(tmp: Path) -> tuple[Path, Path, Path]:
    """feedback/ 문서를 임시 폴더로 (백서, main 폴더, CLAUDE.md)."""
    shutil.copytree(ROOT / "feedback", tmp / "feedback", ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    f = tmp / "feedback"
    return f / "whitepaper.md", f / "main", f / "CLAUDE.md"


class Shape(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.paper, self.main, self.guide = copy_feedback(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def check(self):
        return fb.check(self.paper, self.main, self.guide)

    def test_repository_passes(self):
        self.assertEqual(fb.check(), [])
        self.assertEqual(len(fb.VOCAB()), len(set(fb.VOCAB())))
        e = fb.entries()
        self.assertEqual(e[0]["id"], "F001")
        self.assertEqual(set(e[0]) - {"id", "title"}, set(fb.FIELDS))
        self.assertIsInstance(e[0]["색인"], list)
        self.assertIn("common", {m["stem"] for m in fb.mains()})

    def test_main_file_over_ten_is_an_error(self):
        common = self.main / "common.md"
        extra = "".join(f"- **F{n:03d}** 가짜 줄 — 이유. (AI 판단, 2026-11-05)\n" for n in range(10, 21))
        common.write_text(common.read_text(encoding="utf-8") + extra, encoding="utf-8")
        self.assertTrue(any("main/common.md" in e and "최대 10개" in e for e in self.check()))

    def test_word_outside_the_vocabulary_is_an_error(self):
        text = self.paper.read_text(encoding="utf-8").replace("- 색인: 사용자의도, 앱, 검토", "- 색인: 사용자의도, 앱, 없는낱말", 1)
        self.paper.write_text(text, encoding="utf-8")
        self.assertTrue(any("F001" in e and "없는낱말" in e for e in self.check()))

    def test_missing_field_and_wrong_place_are_errors(self):
        text = self.paper.read_text(encoding="utf-8")
        text = text.replace("- 왜: 과정(테스트가 가짜였다", "- 까닭: 과정(테스트가 가짜였다", 1)   # F001 '왜' 칸 이름이 틀림
        text = text.replace("- 자리: 메인 common\n\n### F002", "- 자리: 백서만\n\n### F002", 1)  # F001이 메인에 있는데 백서만
        self.paper.write_text(text, encoding="utf-8")
        errors = self.check()
        self.assertTrue(any("F001" in e and "'왜'" in e for e in errors), errors)
        self.assertTrue(any("main/common.md" in e and "F001" in e and "백서만" in e for e in errors), errors)

    def test_index_written_then_check_passes(self):
        text = self.paper.read_text(encoding="utf-8")
        a, b = text.index(fb.INDEX_START) + len(fb.INDEX_START), text.index(fb.INDEX_END)
        self.paper.write_text(text[:a] + "\n" + text[b:], encoding="utf-8")  # 빈 표
        self.assertTrue(any("색인 표가 최신이 아님" in e for e in self.check()))
        self.assertTrue(fb.index_write(self.paper, self.guide))
        self.assertEqual(self.check(), [])
        self.assertFalse(fb.index_write(self.paper, self.guide))  # 두 번째는 바뀌지 않는다
        table = fb.index(self.paper, self.guide).splitlines()
        self.assertEqual(len(table), 2 + len(fb.VOCAB(self.guide)))  # 낱말마다 한 줄(0건도)

    def test_topics_and_find(self):
        got = fb.topics("웹 조사 지시서를 쓴다")
        for s in ("common", "research", "brief"):
            self.assertIn(s, got)
        self.assertEqual(got, sorted(got))
        self.assertEqual(fb.topics(""), ["common"])
        hits = fb.find(["웹차단"])
        self.assertTrue(hits and all("웹차단" in e["색인"] for e in hits))


class Enforce(unittest.TestCase):
    base = {"id": "zf1", "project": "proviso", "batch": 99, "date": dp.FEEDBACK_REQUIRED_FROM, "task": "t",
            "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 6, "turns": 10}}

    def errs(self, **kw):
        return dp.feedback_errors({**self.base, **kw})

    def test_records_from_nov_6_need_read_and_review(self):
        e = self.errs()
        self.assertTrue(any("피드백 읽기가 없음" in x for x in e))
        self.assertTrue(any("review.feedback이 없음" in x for x in e))
        # validate()에 끼워져 있다
        self.assertTrue(any(x.startswith("zf1:") and "피드백" in x for x in dp.validate(dp.load() + [dict(self.base)], schema.load(HERE / "knowledge.toml"))))
        ok = {"feedback": {"read": ["common"]}}
        self.assertEqual(self.errs(**ok, review={"feedback": "없음: 새로 알게 된 실수가 없다"}), [])
        self.assertEqual(self.errs(**ok, review={"feedback": ["F001"]}), [])
        self.assertTrue(any("F999" in x for x in self.errs(**ok, review={"feedback": ["F999"]})))
        self.assertTrue(self.errs(**ok, review={"feedback": "없음: 짧"}))           # 이유가 너무 짧다
        self.assertTrue(self.errs(**ok, review={"feedback": "없음"}))
        self.assertTrue(self.errs(**ok, review={"feedback": []}))
        # read에 common이 없거나, 없는 파일이거나, task가 고른 파일이 빠지면 오류
        self.assertTrue(any("common" in x for x in self.errs(feedback={"read": ["brief"]}, review={"feedback": ["F001"]})))
        self.assertTrue(any("없는 파일" in x for x in self.errs(feedback={"read": ["common", "nope"]}, review={"feedback": ["F001"]})))
        miss = self.errs(task="웹 조사 지시서", feedback={"read": ["common", "brief"]}, review={"feedback": ["F001"]})
        self.assertTrue(any("research" in x and "빠짐" in x for x in miss), miss)

    def test_older_records_batman_and_pending_records_are_not_required(self):
        self.assertEqual(self.errs(date="2026-11-05"), [])                                   # 그 전 날짜
        self.assertEqual(self.errs(project="batman"), [])                                    # batman 기록은 batman 쪽
        self.assertEqual(self.errs(feedback={"read": ["common"]}, actual={"status": "unknown"}), [])  # 안 끝난 기록은 review 없어도
        self.assertTrue(self.errs(date="2026-11-05", feedback={"read": "common"}))           # 칸이 있으면 날짜와 상관없이 모양을 본다
        self.assertTrue(self.errs(date="2026-11-05", review={"feedback": ["F999"]}))

    def test_direct_entries_need_the_same_two_fields(self):
        d = {"id": "m999", "project": "proviso", "date": dp.FEEDBACK_REQUIRED_FROM, "task": "t",
             "decide": {"main_ctx_k": 800, "left": 50, "direct_m": 1.0, "send_m": 2.0, "chose": "직접", "why": ["비용"]},
             "actual": {"status": "done", "minutes": 1.0, "turns": 2, "tokens_m": 0.1,
                        "start": "2026-11-06T00:00:00Z", "end": "2026-11-06T00:01:00Z"},
             "log": {"skip": "시험"}}
        errors = dp.validate_direct([d])
        self.assertTrue(any("피드백 읽기" in e for e in errors) and any("review.feedback" in e for e in errors), errors)
        self.assertEqual(dp.validate_direct([{**d, "feedback": {"read": ["common"]}, "review": {"feedback": "없음: 메인이 한 작은 고침"}}]), [])


class Record(unittest.TestCase):
    JOB = """project = "proviso"
batch = 999
date = "{date}"
task = "구현: 기록 검사 하나 더하기"
model = "Opus 5.5"
effort = "high"
agent = "작업"
round = 1
[files]
edit = 1
[situation]
S_specified = "예"
[predicted]
minutes = [5, 9]
turns = [30, 50]
tokens_m = [3, 5]
reason = "시험"
[decide]
main_ctx_k = 800
why = ["대화 계속"]
"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copy(HERE / "dispatches.toml", self.tmp / "d.toml")
        shutil.copy(ROOT / "docs" / "AGENT-LOG.md", self.tmp / "log.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def job(self, name: str, extra: str = "", date: str = dp.FEEDBACK_REQUIRED_FROM) -> Path:
        p = self.tmp / name
        p.write_text(self.JOB.format(date=date) + extra, encoding="utf-8")
        return p

    def send(self, p: Path) -> str:
        return rc.send(p, self.tmp / "d.toml", self.tmp / "log.md")

    def test_send_needs_read_from_nov_6_and_writes_the_table(self):
        n = len(dp.load(self.tmp / "d.toml"))
        with self.assertRaises(SystemExit) as cm:
            self.send(self.job("none.toml"))
        self.assertIn("[feedback] read", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:   # task의 키워드가 고른 파일이 빠지면 막힌다
            self.send(self.job("miss.toml", '[feedback]\nread = ["common"]\n'))
        missing = [s for s in fb.topics("구현: 기록 검사 하나 더하기") if s != fb.COMMON]  # 키워드가 고른 파일(지금은 record)
        self.assertTrue(missing)
        self.assertIn(f"feedback/main/{missing[0]}.md", str(cm.exception))
        self.assertIn("읽고", str(cm.exception))
        self.assertEqual(len(dp.load(self.tmp / "d.toml")), n)  # 막힌 두 번은 아무것도 덧붙이지 않았다
        read = fb.topics("구현: 기록 검사 하나 더하기")
        out = self.send(self.job("ok.toml", f'[feedback]\nread = [{", ".join(chr(34) + s + chr(34) for s in read)}]\n'))
        text = (self.tmp / "d.toml").read_text(encoding="utf-8")
        tail = text[text.rindex("[[dispatch]]"):]
        self.assertLess(tail.index("[dispatch.decide]"), tail.index("[dispatch.feedback]"))   # decide 뒤
        self.assertLess(tail.index("[dispatch.feedback]"), tail.index("[dispatch.actual]"))
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["feedback"]["read"], read)
        self.assertIn("읽은 메인 피드백", out)
        self.assertIn("**F001**", out)  # common의 F 줄을 그대로 찍는다
        self.assertEqual(dp.feedback_errors(d), [])  # 안 끝난 기록이라 review.feedback은 아직

    def test_send_before_nov_6_without_read_is_allowed(self):
        self.send(self.job("early.toml", date="2026-11-05"))
        self.assertNotIn("feedback", dp.load(self.tmp / "d.toml")[-1])

    def test_finish_writes_review_feedback(self):
        from tests.test_decide import write_log
        read = fb.topics("구현: 기록 검사 하나 더하기")
        self.send(self.job("ok.toml", f'[feedback]\nread = [{", ".join(chr(34) + s + chr(34) for s in read)}]\n'))
        rid = dp.load(self.tmp / "d.toml")[-1]["id"]
        write_log(self.tmp / "a.jsonl", [("2026-11-06T01:00:00Z", "user", 0), ("2026-11-06T01:00:20Z", "assistant", 60000),
                                          ("2026-11-06T01:00:21Z", "tool", 0), ("2026-11-06T01:02:00Z", "assistant", 70000)])
        out = rc.finish(rid, self.tmp / "a.jsonl", report="docs/worklog/CLAUDE.md", path=self.tmp / "d.toml")
        self.assertIn("review.feedback", out)  # 안 주면 남은 일에 뜬다
        self.assertTrue(any("review.feedback이 없음" in e for e in dp.feedback_errors(dp.load(self.tmp / "d.toml")[-1])))
        # 다시 주면 review 표에 넣는다 (목록이면 TOML 배열)
        self.assertEqual(rc.feedback_value("F001, F002"), ["F001", "F002"])
        self.assertEqual(rc.feedback_value("없음: 새 실수 없음"), "없음: 새 실수 없음")
        text = (self.tmp / "d.toml").read_text(encoding="utf-8")
        a, b = rc._block(text, "dispatch", rid)
        block = rc._put_review(text[a:b], "dispatch", "feedback", ["F001"])
        block = rc._put_review(block, "dispatch", "feedback", ["F001", "F002"])  # 있으면 바꾼다
        (self.tmp / "d.toml").write_text(text[:a] + block + text[b:], encoding="utf-8")
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual((d["review"]["feedback"], d["review"]["report"]), (["F001", "F002"], "docs/worklog/CLAUDE.md"))
        self.assertEqual(dp.feedback_errors(d), [])


if __name__ == "__main__":
    unittest.main()
