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


class RecordFiles:
    """임시 기록 파일로 record send·finish를 돌리는 준비 (테스트 묶음 둘이 같이 쓴다)."""
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


class Record(RecordFiles, unittest.TestCase):
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


# 피드백 정답 모으기 (2026-11-06 사용자 결정): 2026-11-07부터 메인 파일 전부 읽기 + searched(색인 낱말) + hit(걸린다고 본 항목),
# 끝나면 review.missed(hit에 없던, 알고 보니 걸린 기존 항목). hit + missed = 일마다의 정답(`python -m feedback labels`).
ALL = fb.main_files()
GOOD = {"read": ALL, "searched": ["기록"], "hit": ["F052"]}


class GroundTruth(unittest.TestCase):
    base = {"id": "zg1", "project": "proviso", "batch": 99, "date": dp.FEEDBACK_ALL_FROM, "task": "구현: 기록 검사 하나 더하기",
            "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 6, "turns": 10},
            "review": {"feedback": "없음: 새로 알게 된 실수가 없다", "missed": "없음: 놓친 항목이 없다"}}

    def errs(self, **kw):
        return dp.feedback_errors({**self.base, **kw})

    def test_read_all_main_files_from_nov_7(self):
        self.assertEqual(self.errs(feedback=GOOD), [])
        picked = fb.topics(self.base["task"])
        self.assertLess(len(picked), len(ALL))  # 키워드가 고른 것만으로는
        e = self.errs(feedback={**GOOD, "read": picked})
        self.assertTrue(any("빠짐" in x and "전부" in x for x in e), e)
        # 그 전 날짜는 지금 규칙 그대로: topics가 고른 파일이면 되고 searched·hit·missed도 없어도 된다
        self.assertEqual(self.errs(date="2026-11-06", feedback={"read": picked}, review={"feedback": "없음: 새로 알게 된 실수가 없다"}), [])
        self.assertEqual(self.errs(project="batman", feedback=None, review={}), [])  # batman 기록은 batman 쪽
        # validate()에 끼워져 있다
        bare = {k: v for k, v in self.base.items() if k != "review"}
        self.assertTrue(any(x.startswith("zg1:") and "searched" in x
                            for x in dp.validate(dp.load() + [{**bare, "feedback": {"read": ALL}}], schema.load(HERE / "knowledge.toml"))))

    def test_searched_words_come_from_the_index(self):
        self.assertTrue(any("feedback.searched가 없음" in x for x in self.errs(feedback={"read": ALL, "hit": ["F052"]})))
        self.assertTrue(any("searched" in x for x in self.errs(feedback={**GOOD, "searched": []})))
        bad = self.errs(feedback={**GOOD, "searched": ["기록", "없는낱말"]})
        self.assertTrue(any("없는낱말" in x and "색인 낱말이 아님" in x for x in bad), bad)
        # 칸이 있으면 날짜와 상관없이 모양을 본다
        self.assertTrue(self.errs(date="2026-11-06", feedback={"read": ALL, "searched": ["없는낱말"]}))

    def test_hit_ids_exist_or_hit_none_gives_a_reason(self):
        self.assertTrue(any("feedback.hit가 없음" in x for x in self.errs(feedback={"read": ALL, "searched": ["기록"]})))
        self.assertTrue(any("F999" in x for x in self.errs(feedback={**GOOD, "hit": ["F052", "F999"]})))
        self.assertTrue(any("두 번" in x for x in self.errs(feedback={**GOOD, "hit": ["F052", "F052"]})))
        self.assertTrue(any("hit_none" in x for x in self.errs(feedback={**GOOD, "hit": []})))
        self.assertTrue(self.errs(feedback={**GOOD, "hit": [], "hit_none": "짧"}))
        self.assertEqual(self.errs(feedback={**GOOD, "hit": [], "hit_none": "걸리는 지난 실수가 없는 새 종류의 일"}), [])
        self.assertTrue(any("hit_none" in x for x in self.errs(feedback={**GOOD, "hit_none": "걸리는 지난 실수가 없다"})))  # hit가 있는데
        self.assertTrue(self.errs(feedback={"read": ALL, "searched": ["기록"], "hit_none": "걸리는 지난 실수가 없다"}))  # hit 없이

    def test_missed_format_and_overlap_with_hit(self):
        rev = {"feedback": "없음: 새로 알게 된 실수가 없다"}
        self.assertTrue(any("review.missed" in x and "없음" in x for x in self.errs(feedback=GOOD, review=rev)))
        self.assertEqual(self.errs(feedback=GOOD, review=rev, actual={"status": "unknown"}), [])  # 안 끝난 기록은 아직
        self.assertEqual(self.errs(feedback=GOOD, review={**rev, "missed": ["F001"]}), [])
        self.assertTrue(self.errs(feedback=GOOD, review={**rev, "missed": "없음: 짧"}))
        self.assertTrue(self.errs(feedback=GOOD, review={**rev, "missed": []}))
        self.assertTrue(any("F999" in x for x in self.errs(feedback=GOOD, review={**rev, "missed": ["F999"]})))
        both = self.errs(feedback=GOOD, review={**rev, "missed": ["F001", "F052"]})
        self.assertTrue(any("F052" in x and "hit에도" in x for x in both), both)
        fresh = self.errs(feedback=GOOD, review={"feedback": ["F001"], "missed": ["F001"]})  # 이번에 새로 올린 항목은 missed가 아니다
        self.assertTrue(any("새로 올린" in x for x in fresh), fresh)
        self.assertEqual(self.errs(date="2026-11-06", feedback={"read": ALL}, review=rev), [])  # 그 전 날짜는 없어도

    def test_direct_entries_follow_the_same_rules(self):
        d = {"id": "m998", "project": "proviso", "date": dp.FEEDBACK_ALL_FROM, "task": "t",
             "decide": {"main_ctx_k": 800, "left": 50, "direct_m": 1.0, "send_m": 2.0, "chose": "직접", "why": ["비용"]},
             "actual": {"status": "done", "minutes": 1.0, "turns": 2, "tokens_m": 0.1,
                        "start": "2026-11-07T00:00:00Z", "end": "2026-11-07T00:01:00Z"},
             "log": {"skip": "시험"}, "feedback": {"read": ["common"]}, "review": {"feedback": "없음: 메인이 한 작은 고침"}}
        errors = dp.validate_direct([d])
        for word in ("전부", "searched", "hit", "review.missed"):
            self.assertTrue(any(word in e for e in errors), (word, errors))
        ok = {**d, "feedback": GOOD, "review": {"feedback": "없음: 메인이 한 작은 고침", "missed": "없음: 놓친 항목이 없다"},
              "predicted": {"minutes": [0.5, 2], "turns": [1, 4], "tokens_m": [0.05, 0.2]}}
        self.assertEqual(dp.validate_direct([ok]), [])


class GroundTruthRecord(RecordFiles, unittest.TestCase):
    """record send·direct·finish가 새 칸을 검사하고 옮긴다 (임시 기록 파일로만)."""
    def fb(self, table: dict) -> str:
        return "[feedback]\n" + "".join(f"{k} = {rc._v(v)}\n" for k, v in table.items())

    def test_send_from_nov_7_needs_all_files_searched_and_hit(self):
        n = len(dp.load(self.tmp / "d.toml"))
        late = dp.FEEDBACK_ALL_FROM
        with self.assertRaises(SystemExit) as cm:  # 키워드가 고른 파일만이면 막힌다
            self.send(self.job("pick.toml", self.fb({**GOOD, "read": fb.topics("구현: 기록 검사 하나 더하기")}), date=late))
        self.assertIn("전부", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:
            self.send(self.job("nosearch.toml", self.fb({"read": ALL, "hit": ["F052"]}), date=late))
        self.assertIn("searched", str(cm.exception))
        with self.assertRaises(SystemExit) as cm:
            self.send(self.job("nohit.toml", self.fb({"read": ALL, "searched": ["기록"]}), date=late))
        self.assertIn("hit", str(cm.exception))
        self.assertEqual(len(dp.load(self.tmp / "d.toml")), n)  # 막힌 세 번은 아무것도 덧붙이지 않았다
        out = self.send(self.job("ok.toml", self.fb(GOOD), date=late))
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["feedback"], GOOD)
        self.assertEqual(dp.feedback_errors(d), [])
        self.assertIn("백서에서 찾은 항목 (낱말: 기록)", out)
        for e in fb.find(["기록"]):  # 찾은 항목이 번호 · 제목 · 자리로 메인 맥락을 지나간다
            self.assertIn(f"{e['id']} · {e['title']} — 자리 {e['자리']}", out)
        self.assertIn("키워드가 고른 메인 파일(참고)", out)
        self.assertIn("이번 일에 걸린다고 본 항목(hit): F052", out)
        none = {**GOOD, "hit": [], "hit_none": "걸리는 지난 실수가 없는 새 종류의 일"}
        self.send(self.job("none.toml", self.fb(none), date=late))
        self.assertEqual(dp.load(self.tmp / "d.toml")[-1]["feedback"], none)

    def test_finish_writes_missed_and_refuses_overlap_with_hit(self):
        from tests.test_decide import write_log
        self.send(self.job("ok.toml", self.fb(GOOD), date=dp.FEEDBACK_ALL_FROM))
        rid = dp.load(self.tmp / "d.toml")[-1]["id"]
        write_log(self.tmp / "a.jsonl", [("2026-11-07T01:00:00Z", "user", 0), ("2026-11-07T01:00:20Z", "assistant", 60000),
                                          ("2026-11-07T01:00:21Z", "tool", 0), ("2026-11-07T01:02:00Z", "assistant", 70000)])
        before = (self.tmp / "d.toml").read_text(encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            rc.finish(rid, self.tmp / "a.jsonl", path=self.tmp / "d.toml", feedback="없음: 새 실수 없음", missed="F001, F052")
        self.assertIn("hit에도", str(cm.exception))
        self.assertEqual((self.tmp / "d.toml").read_text(encoding="utf-8"), before)  # 막히면 아무것도 안 쓴다
        out = rc.finish(rid, self.tmp / "a.jsonl", report="docs/worklog/CLAUDE.md", path=self.tmp / "d.toml", feedback="없음: 새 실수 없음")
        self.assertIn("review.missed", out)  # 안 주면 남은 일에 뜬다
        self.assertTrue(any("review.missed이 없음" in e for e in dp.feedback_errors(dp.load(self.tmp / "d.toml")[-1])))
        text = (self.tmp / "d.toml").read_text(encoding="utf-8")
        a, b = rc._block(text, "dispatch", rid)
        (self.tmp / "d.toml").write_text(text[:a] + rc._put_review(text[a:b], "dispatch", "missed", rc.feedback_value("F001, F014")) + text[b:],
                                         encoding="utf-8")
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["review"]["missed"], ["F001", "F014"])
        self.assertEqual(dp.feedback_errors(d), [])

    def test_finish_with_missed_flag(self):
        from tests.test_decide import write_log
        self.send(self.job("ok.toml", self.fb(GOOD), date=dp.FEEDBACK_ALL_FROM))
        rid = dp.load(self.tmp / "d.toml")[-1]["id"]
        write_log(self.tmp / "a.jsonl", [("2026-11-07T01:00:00Z", "user", 0), ("2026-11-07T01:00:20Z", "assistant", 60000)])
        out = rc.finish(rid, self.tmp / "a.jsonl", report="docs/worklog/CLAUDE.md", path=self.tmp / "d.toml",
                        feedback="없음: 새 실수 없음", missed="없음: 놓친 항목이 없다")
        self.assertNotIn("review.missed", out)
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["review"]["missed"], "없음: 놓친 항목이 없다")
        self.assertEqual(dp.feedback_errors(d), [])

    def test_direct_from_nov_7(self):
        (self.tmp / "direct.toml").write_text("# 직접 한 일\n", encoding="utf-8")
        head = (f'project = "proviso"\ndate = "{dp.FEEDBACK_ALL_FROM}"\ntask = "문서 두 곳 고치기"\n[predicted]\nminutes = [1, 3]\nturns = [4, 8]\n'
                'tokens_m = [0.3, 0.6]\n[decide]\nmain_ctx_k = 800\n')
        (self.tmp / "bad.toml").write_text(head + self.fb({"read": ALL, "searched": ["문서"]}), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            rc.direct(self.tmp / "bad.toml", self.tmp / "direct.toml")
        self.assertIn("hit", str(cm.exception))
        table = {"read": ALL, "searched": ["문서"], "hit": ["F078"]}
        (self.tmp / "ok.toml").write_text(head + self.fb(table), encoding="utf-8")
        out = rc.direct(self.tmp / "ok.toml", self.tmp / "direct.toml")
        self.assertIn("백서에서 찾은 항목 (낱말: 문서)", out)
        self.assertEqual(dp.load_direct(self.tmp / "direct.toml")[-1]["feedback"], table)


class Labels(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "d.toml").write_text("""
[[dispatch]]
id = "p901"
project = "proviso"
date = 2026-11-07
task = "구현: 하나"
[dispatch.feedback]
read = ["common"]
searched = ["기록"]
hit = ["F052"]
[dispatch.review]
missed = ["F014"]

[[dispatch]]
id = "p902"
project = "exam_grader"
date = 2026-11-07
task = "풀이지 한 장"
[dispatch.feedback]
read = ["common"]
searched = ["풀이지"]
hit = []
hit_none = "걸리는 지난 실수가 없다"

[[dispatch]]
id = "p903"
project = "proviso"
date = 2026-11-06
task = "옛 기록 (hit 없음)"
[dispatch.feedback]
read = ["common"]
""", encoding="utf-8")
        (self.tmp / "m.toml").write_text("""
[[direct]]
id = "m901"
project = "proviso"
date = 2026-11-07
task = "문서 고치기"
[direct.feedback]
read = ["common", "docs"]
searched = ["문서"]
hit = ["F078"]
[direct.review]
missed = "없음: 놓친 항목이 없다"
""", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_one_line_per_record_with_hit(self):
        import json
        rows = fb.labels(self.tmp / "d.toml", self.tmp / "m.toml")
        self.assertEqual([r["id"] for r in rows], ["p901", "p902", "m901"])  # hit 칸이 없는 p903은 빠진다
        self.assertEqual(rows[0], {"id": "p901", "kind": "dispatch", "project": "proviso", "date": "2026-11-07", "task": "구현: 하나",
                                   "read": ["common"], "searched": ["기록"], "hit": ["F052"], "missed": ["F014"], "brief": None})
        self.assertEqual((rows[1]["hit"], rows[1]["missed"]), ([], None))   # 빈 hit도 정답(걸릴 것 없음), 안 끝났으면 missed None
        self.assertEqual((rows[2]["kind"], rows[2]["missed"]), ("direct", []))  # '없음: 이유'는 빈 목록
        out = self.tmp / "out" / "labels.jsonl"
        self.assertEqual(fb.labels_write(out, dispatch_path=self.tmp / "d.toml", direct_path=self.tmp / "m.toml"), 3)
        lines = out.read_text(encoding="utf-8").splitlines()
        self.assertEqual([json.loads(x) for x in lines], rows)
        self.assertIn("구현: 하나", lines[0])  # 한글을 그대로 (ensure_ascii=False)

    def test_cli_and_real_records(self):
        from feedback.__main__ import main
        import contextlib
        import io
        out = self.tmp / "real.jsonl"
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            self.assertEqual(main(["labels", "--out", str(out)]), 0)
        self.assertIn(str(out), buf.getvalue())
        self.assertEqual(len(out.read_text(encoding="utf-8").splitlines()), len(fb.labels()))
        self.assertTrue(str(fb.LABELS_OUT).replace("\\", "/").endswith("out/feedback/labels.jsonl"))  # 기본은 git 제외 폴더


class Brief(RecordFiles, unittest.TestCase):
    """지시서 경로 brief = "저장소:경로.md" (2026-11-06 사용자 결정): 지시서 글은 이 공개 저장소에 두지 않고 경로만 (임시 파일로만)."""
    PTR = "gemmin:docs/briefs/p901.md"

    def fb(self) -> str:
        return "[feedback]\n" + "".join(f"{k} = {rc._v(v)}\n" for k, v in GOOD.items())

    def brief_job(self, name: str, brief) -> Path:
        p = self.job(name, self.fb(), date=dp.FEEDBACK_ALL_FROM)
        p.write_text(p.read_text(encoding="utf-8").replace("round = 1\n", f"round = 1\nbrief = {rc._v(brief)}\n"), encoding="utf-8")
        return p

    def test_shape(self):
        for ok in (self.PTR, "movie_game:a.md", "x.y-z_1:docs/b c/가.md"):
            self.assertIsNone(fb.brief_error(ok), ok)
        for bad in ("docs/briefs/p901.md", "gemmin:/abs.md", "gemmin:../up.md", "gemmin:a/../b.md", "gemmin:a..b.md",
                    "gemmin:x.txt", "gem min:x.md", ":x.md", "gemmin:", 3, ["gemmin:x.md"]):
            self.assertIsNotNone(fb.brief_error(bad), bad)
        self.assertEqual(dp.brief_errors({"id": "p1"}), [])  # 없어도 된다 (아직 필수 아님)
        self.assertEqual(dp.brief_errors({"id": "p1", "brief": self.PTR}), [])
        self.assertTrue(dp.brief_errors({"id": "p1", "brief": "gemmin:/abs.md"})[0].startswith("p1: brief"))

    def test_checker_rejects_bad_shape_in_records(self):
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertTrue(any("brief" in e for e in dp.validate([{**d, "brief": "../x.md"}], schema.load(HERE / "knowledge.toml"))))
        self.assertTrue(any("brief" in e for e in dp.validate_direct([{"id": "m901", "project": "p", "date": "2026-11-05", "task": "t",
                                                                       "brief": "gemmin:x.txt"}])))

    def test_send_copies_and_refuses_bad_shape(self):
        n = len(dp.load(self.tmp / "d.toml"))
        with self.assertRaises(SystemExit) as cm:
            self.send(self.brief_job("bad.toml", "gemmin:../x.md"))
        self.assertIn("..", str(cm.exception))
        self.assertEqual(len(dp.load(self.tmp / "d.toml")), n)  # 막히면 아무것도 안 덧붙는다
        self.send(self.brief_job("ok.toml", self.PTR))
        d = dp.load(self.tmp / "d.toml")[-1]
        self.assertEqual(d["brief"], self.PTR)
        self.assertEqual(dp.brief_errors(d), [])
        self.send(self.job("plain.toml", self.fb(), date=dp.FEEDBACK_ALL_FROM))
        self.assertNotIn("brief", dp.load(self.tmp / "d.toml")[-1])  # 없으면 칸도 없다

    def test_direct_copies(self):
        (self.tmp / "direct.toml").write_text("# 직접 한 일\n", encoding="utf-8")
        (self.tmp / "ok.toml").write_text(
            f'project = "proviso"\ndate = "{dp.FEEDBACK_ALL_FROM}"\ntask = "문서 두 곳 고치기"\nbrief = "{self.PTR}"\n[predicted]\n'
            'minutes = [1, 3]\nturns = [4, 8]\ntokens_m = [0.3, 0.6]\n[decide]\nmain_ctx_k = 800\n' + self.fb(), encoding="utf-8")
        rc.direct(self.tmp / "ok.toml", self.tmp / "direct.toml")
        self.assertEqual(dp.load_direct(self.tmp / "direct.toml")[-1]["brief"], self.PTR)

    def test_labels_pointer_and_brief_root(self):
        import contextlib
        import io
        import json
        from feedback.__main__ import main
        (self.tmp / "l.toml").write_text(f"""
[[dispatch]]
id = "p901"
project = "proviso"
date = 2026-11-07
task = "하나"
brief = "{self.PTR}"
[dispatch.feedback]
hit = ["F052"]

[[dispatch]]
id = "p902"
project = "proviso"
date = 2026-11-07
task = "둘 (지시서 파일이 없다)"
brief = "gemmin:docs/briefs/p902.md"
[dispatch.feedback]
hit = []

[[dispatch]]
id = "p903"
project = "proviso"
date = 2026-11-07
task = "셋 (경로 칸 없음)"
[dispatch.feedback]
hit = []
""", encoding="utf-8")
        paths = {"dispatch_path": self.tmp / "l.toml", "direct_path": self.tmp / "none.toml"}
        rows = fb.labels(**paths)
        self.assertEqual([r["brief"] for r in rows], [self.PTR, "gemmin:docs/briefs/p902.md", None])
        self.assertTrue(all("brief_text" not in r for r in rows))  # --brief-root 없으면 글 칸도 없다
        repo = self.tmp / "gemmin"
        (repo / "docs" / "briefs").mkdir(parents=True)
        (repo / "docs" / "briefs" / "p901.md").write_text("# 지시서\n할 일 하나", encoding="utf-8")
        missing = []
        rows = fb.labels(**paths, brief_roots={"gemmin": repo}, missing=missing)
        self.assertEqual([r["brief_text"] for r in rows], ["# 지시서\n할 일 하나", None, None])
        self.assertEqual(missing, ["p902", "p903"])
        # CLI: 기본 기록 파일로 돌고(--brief-root 꼴 검사), 잘못된 꼴은 2
        out = self.tmp / "o.jsonl"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["labels", "--out", str(out), "--brief-root", "gemmin"]), 2)
            self.assertEqual(main(["labels", "--out", str(out), "--brief-root", f"gemmin={repo}"]), 0)
        for line in out.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            self.assertIn("brief", row)
            self.assertIn("brief_text", row)


if __name__ == "__main__":
    unittest.main()
