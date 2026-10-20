"""규칙·가설 통합(2026-10-19): 상태 둘, 판정 기록, 성적표, 점검 경고."""
import tempfile
import unittest
from pathlib import Path

from proviso import audit, schema, score

ROOT = Path(__file__).resolve().parent.parent


def load_text(text: str) -> schema.Knowledge:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "k.toml"
        path.write_text(text, encoding="utf-8")
        return schema.load(path)


BASE = ('[[goal]]\nid="G"\ntext="g"\n[[state]]\nid="S1"\ntext="s1"\n[[state]]\nid="S2"\ntext="s2"\n'
        '[[observation]]\nid="O"\ntext="o"\nsource="user"\n')


def rule(rid, version, status, method, conds, extra=""):
    return (f'[[rule]]\nid="{rid}"\nversion={version}\nstatus="{status}"\nmethod="{method}"\nreason="r"\n'
            f'serves=["G"]\nconditions={conds}\n{extra}')


class Status(unittest.TestCase):
    def test_verified_is_gone(self):
        kn = load_text(BASE + rule("R", 1, "verified", "m", '["S1"]', 'check="c"\n'))
        self.assertTrue(any("verified" in e for e in schema.validate(kn)))

    def test_retired_needs_replacement_and_hypothesis_can_retire(self):
        kn = load_text(BASE + '[[hypothesis]]\nid="H"\ntext="h"\nsource="ai"\nstatus="retired"\n')
        self.assertTrue(any("replaced_by" in e for e in schema.validate(kn)))
        kn = load_text(BASE + '[[hypothesis]]\nid="H"\ntext="h"\nsource="ai"\nstatus="retired"\nreplaced_by=["H2"]\n'
                       '[[hypothesis]]\nid="H2"\ntext="h2"\nsource="ai"\nconditions=["S1"]\n')
        self.assertEqual(schema.validate(kn), [])
        self.assertFalse(schema.alive(kn.nodes["H"]))
        self.assertTrue(schema.alive(kn.nodes["H2"]))

    def test_superseded_by_is_replaced(self):
        kn = load_text(BASE + '[[hypothesis]]\nid="H"\ntext="h"\nsource="ai"\nsuperseded_by=["H"]\n')
        self.assertTrue(any("superseded_by" in e for e in schema.validate(kn)))

    def test_condition_added_by_new_version_must_be_state_or_fact(self):
        kn = load_text(BASE + rule("R", 1, "retired", "m", '["S1"]', 'replaced_by=["R2"]\n')
                       + rule("R2", 2, "hypothesis", "m2", '["S1", "O"]'))
        self.assertTrue(any("R2" in e and "'O'" in e for e in schema.validate(kn)))

    def test_judgment_fields_are_checked(self):
        good = '[[judgment]]\nof="R"\nsource="user"\nverdict="지지"\ndate=2026-10-19\nnote="써 보니 좋다"\nevidence=["O"]\n'
        kn = load_text(BASE + rule("R", 1, "hypothesis", "m", '["S1"]') + good)
        self.assertEqual(schema.validate(kn), [])
        bad = '[[judgment]]\nof="G"\nsource="friend"\nverdict="좋음"\n'
        errors = schema.validate(load_text(BASE + bad))
        for word in ("of는", "source는", "verdict는", "date와 note"):
            self.assertTrue(any(word in e for e in errors), word)


class Scorecard(unittest.TestCase):
    def test_user_judgment_is_heaviest_and_first(self):
        text = (BASE + rule("R", 1, "hypothesis", "m", '["S1"]', 'check="c"\n')
                + '[[judgment]]\nof="R"\nsource="user"\nverdict="반박"\ndate=2026-10-19\nnote="써 보니 아쉽다"\n')
        kn = load_text(text)
        lines = score.card(kn, kn.nodes["R"], {"c": lambda: ("지지됨 (시험 5건 중 5건 맞음)", "")}, "simulation")
        self.assertEqual([l.source for l in lines], ["user", "simulation"])
        self.assertEqual(score.summary(lines), "사용자 실사용 기준 반박 1 (다른 출처에는 지지도 있음)")
        self.assertIn("★ 사용자 실사용", score.report(kn, {"c": lambda: ("지지됨", "")}, "simulation"))

    def test_check_may_take_the_node_id(self):
        kn = load_text(BASE + rule("R", 1, "hypothesis", "m", '["S1"]', 'check=["used"]\n'))
        lines = score.card(kn, kn.nodes["R"], {"used": lambda rid: (f"반박됨 ({rid})", "")})
        self.assertEqual((lines[0].verdict, lines[0].text), ("반박", "반박됨 (R)"))

    def test_check_may_judge_per_source(self):
        """한 검사가 출처별로 따로 판정한다(2026-10-21, 재생과 실측을 따로 보이기). 이름에 출처가 붙는다."""
        kn = load_text(BASE + rule("R", 1, "hypothesis", "m", '["S1"]', 'check=["c"]\n'))
        both = lambda: [("replay", "반박됨 (시험 9건 중 0건 맞음)", "a"), ("measured", "시험 전", "")]
        lines = score.card(kn, kn.nodes["R"], {"c": both}, "replay")
        self.assertEqual([(l.source, l.name, l.verdict) for l in lines],
                         [("replay", "c·실제 기록 재생", "반박"), ("measured", "c·실측", "시험 전")])
        self.assertEqual(score.summary(lines), "실제 기록 재생 기준 반박 1")
        # 출처 하나만 내면 이름은 그대로
        one = lambda: [("measured", "지지됨 (시험 3건 중 3건 맞음)", "")]
        self.assertEqual(score.card(kn, kn.nodes["R"], {"c": one})[0].name, "c")

    def test_source_may_be_per_check(self):
        kn = load_text(BASE + rule("R", 1, "hypothesis", "m", '["S1"]', 'check=["a", "b", "z"]\n'))
        checks = {k: (lambda: ("지지됨", "")) for k in "abz"}
        lines = score.card(kn, kn.nodes["R"], checks, {"a": "measured", "b": "simulation", "*": "ai"})
        self.assertEqual({l.name: l.source for l in lines}, {"a": "measured", "b": "simulation", "z": "ai"})
        self.assertEqual(score.source_of({"a": "measured"}, "q"), "auto")
        self.assertIn("검사마다", __import__("proviso.__main__", fromlist=["x"]).source_label({"a": "measured"}))

    def test_bad_check_result_shape_is_an_error(self):
        with self.assertRaises(ValueError):
            score.results([("only one",)], "auto")

    def test_no_means_and_not_yet(self):
        self.assertEqual(score.summary([]), "시험 수단 없음")
        self.assertEqual(score.summary([score.Line("measured", "c", "시험 전", "시험 전")]), "시험 전")

    def test_flowlog_r_p1a_keeps_its_old_grounds_as_judgments(self):
        kn = schema.load(ROOT / "domains" / "flowlog" / "knowledge.toml")
        self.assertEqual(kn.nodes["R_P1a"].data["status"], "hypothesis")
        self.assertEqual({j["source"] for j in kn.judgments_of("R_P1a")}, {"user", "replay"})
        self.assertTrue(score.summary(score.card(kn, kn.nodes["R_P1a"], {})).startswith("사용자 실사용 기준 지지"))


class AuditWarnings(unittest.TestCase):
    def test_revision_without_new_condition_is_warned_not_failed(self):
        text = (BASE + rule("R", 1, "retired", "턴 × 25만", '["S1"]', 'replaced_by=["R2"]\n')
                + rule("R2", 2, "hypothesis", "턴 × 35–39만", '["S1"]', 'check="c"\n'))
        kn = load_text(text)
        warns = audit.unsplit_revisions(kn)
        self.assertEqual(len(warns), 1)
        self.assertIn("숫자만 바뀜", warns[0])
        self.assertEqual(audit.unaccepted_harms(kn), [])
        report = audit.report(kn)
        self.assertIn("오류 없음", report)
        self.assertIn("경고 1건", report)

    def test_split_revision_is_quiet(self):
        text = (BASE + rule("R", 1, "retired", "m", '["S1"]', 'replaced_by=["R2"]\n')
                + rule("R2", 2, "hypothesis", "m", '["S1", "S2"]', 'check="c"\n'))
        self.assertEqual(audit.warnings(load_text(text)), [])

    def test_untested_claim_is_warned(self):
        kn = load_text(BASE + rule("R", 1, "hypothesis", "m", '["S1"]', 'test_plan="써 보고 판정"\n'))
        warns = audit.untested(kn)
        self.assertEqual(len(warns), 1)
        self.assertIn("써 보고 판정", warns[0])

    def test_real_domains_have_warnings_but_no_errors(self):
        for domain in ("flowlog", "music_player", "agent_usage"):
            kn = schema.load(ROOT / "domains" / domain / "knowledge.toml")
            self.assertEqual(audit.unaccepted_harms(kn), [], domain)
        kn = schema.load(ROOT / "domains" / "agent_usage" / "knowledge.toml")
        self.assertTrue(any("R_tok_v2 → R_tok_v3" in w and "숫자만" in w for w in audit.unsplit_revisions(kn)))
        self.assertFalse(any(w.startswith("쪼개지 않은 개정: R_tok_long →") for w in audit.unsplit_revisions(kn)))


if __name__ == "__main__":
    unittest.main()
