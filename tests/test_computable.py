"""계산되는 논리 (2026-10-19): 효과 칸, 계산기, 시간 순서 홀드아웃, 지킬 장치 A–H."""
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from domains.agent_usage import checks, dispatches as dp, fit as ft, holdout as ho, predict as pr
from proviso import schema

ROOT = Path(__file__).resolve().parent.parent

DOMAIN = '[domain]\nid="x"\nquantities=["turns","turns_per_min"]\nsituation_values=["예","아니오","일부","모름"]\nmax_ratio=2\n'
STATE = '[[state]]\nid="S_a"\ntext="a"\nknown_before=true\n[[state]]\nid="S_after"\ntext="끝나고 아는 값"\nknown_before=false\n'


def load_text(text: str) -> schema.Knowledge:
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "k.toml"
        path.write_text(text, encoding="utf-8")
        return schema.load(path)


def piece_toml(effect: str, reason: str = 'reason="r"', conds: str = '["S_a"]') -> str:
    return (DOMAIN + STATE + f'[[hypothesis]]\nid="C_x"\ntext="t"\nsource="ai"\n{reason}\nconditions={conds}\n'
            f'[[hypothesis.effect]]\n{effect}\n')


GOOD = 'on="turns"\nop="mul"\nrange=[0.5,0.8]\ndir="down"\nwhen={S_a="예"}\nreason="왜"'


class EffectSchema(unittest.TestCase):
    def test_good_effect_passes(self):
        self.assertEqual(schema.validate(load_text(piece_toml(GOOD))), [])

    def test_A_condition_piece_needs_a_direction_that_matches_its_range(self):
        errs = schema.validate(load_text(piece_toml(GOOD.replace('dir="down"\n', ''))))
        self.assertTrue(any("방향 주장" in e for e in errs), errs)
        errs = schema.validate(load_text(piece_toml(GOOD.replace("[0.5,0.8]", "[0.8,1.2]"))))
        self.assertTrue(any("넘나들면 방향이 없다" in e for e in errs), errs)
        errs = schema.validate(load_text(piece_toml(GOOD.replace('dir="down"', 'dir="up"'))))
        self.assertTrue(any("어긋남" in e for e in errs), errs)

    def test_B_no_number_without_a_reason(self):
        errs = schema.validate(load_text(piece_toml(GOOD, reason='reason=""')))
        self.assertTrue(any("이유 없는 숫자" in e for e in errs), errs)
        errs = schema.validate(load_text(piece_toml(GOOD.replace('reason="왜"', 'reason=""'))))
        self.assertTrue(any("왜 이 조건이" in e for e in errs), errs)

    def test_C_conditions_must_be_known_before_sending(self):
        errs = schema.validate(load_text(piece_toml(GOOD.replace("S_a=", "S_after="), conds='["S_after"]')))
        self.assertTrue(any("보내기 전에 알 수 있는 상태가 아님" in e for e in errs), errs)

    def test_C_real_states_after_the_fact_are_marked(self):
        kn = pr.load_kn()
        for sid in ("S_short", "S_mid_notes", "S_unsaved_doc", "S_impl_hour", "S_turns"):
            self.assertIs(kn.nodes[sid].data["known_before"], False, sid)
        for p in pr.live_pieces(kn):
            for e in p.effects:
                for sid, _ in e.when:
                    self.assertIs(kn.nodes[sid].data.get("known_before"), True, (p.id, sid))

    def test_C_new_split_states_are_known_before(self):
        kn = pr.load_kn()
        for sid in ("S_small_codebase", "S_integration", "S_many_turn_model"):
            self.assertIs(kn.nodes[sid].data["known_before"], True)

    def test_G_range_width_cap(self):
        errs = schema.validate(load_text(piece_toml(GOOD.replace("[0.5,0.8]", "[0.2,0.8]"))))
        self.assertTrue(any("상한 2배를 넘음" in e for e in errs), errs)

    def test_condition_must_be_in_node_conditions(self):
        errs = schema.validate(load_text(piece_toml(GOOD, conds='[]')))
        self.assertTrue(any("conditions에 없음" in e for e in errs), errs)


class Calculator(unittest.TestCase):
    def setUp(self):
        self.kn = pr.load_kn()
        self.records = dp.load()
        self.pieces = pr.live_pieces(self.kn)

    def rec(self, rid):
        return next(d for d in self.records if d["id"] == rid)

    def test_p04_explains_evidence_pieces_numbers(self):
        out = pr.report_record(self.rec("p04"), self.records, self.pieces, self.kn)
        self.assertIn("말할 구간: 다른 일", out)
        self.assertIn("근거 → 조각 → 조합 → 숫자", out)
        self.assertIn("C_fix_existing_v2(턴)", out)
        self.assertIn("근거: d01–p05 끝난 기록에서 맞춤", out)
        self.assertIn("쓴 조각:", out)
        self.assertIn("맞춰 본 것", out)  # p04는 조각을 세울 때 본 기록이다

    def test_explanation_drops_pieces_that_do_not_change_the_result(self):
        d = self.rec("p04")
        p = pr.predict(d["situation"], d["project"], self.pieces, self.kn)
        decisive = p.decisive()
        for e in p.used():
            changed = p.told(e) != p.told() or p.token_class(e) != p.token_class()
            self.assertEqual(changed, e in decisive, e.piece)
        # 고치는 일의 분당 턴 효과를 뺀 뒤(C_fix_existing_v2, 2026-10-27) p04에는 안 바꾸는 조각이 없다.
        # d18에서는 정해진 입력의 턴당 맥락이 구간·토큰 등급을 안 바꾼다
        d = self.rec("d18")
        p = pr.predict(d["situation"], d["project"], self.pieces, self.kn)
        self.assertTrue(any(e not in p.decisive() for e in p.used()))

    def test_unknown_when_no_base_piece_matches(self):
        # 기본이 아닌 모델의 문서 일: 맞는 기준값이 없으면 지어내지 않는다
        p = pr.predict({"S_other_model": "예", "S_external_check": "아니오"}, "batman", self.pieces, self.kn)
        self.assertIsNone(p.told())
        self.assertIn("모름", pr.explain(p, self.pieces))

    def test_project_fills_a_general_state(self):
        sit = pr.resolve({}, "proviso", self.kn)
        self.assertEqual(sit["S_small_codebase"], "예")
        self.assertEqual(pr.resolve({}, "batman", self.kn)["S_small_codebase"], "아니오")
        self.assertEqual(sit["S_other_model"], "아니오")  # F_setup 기본값

    def test_G_outputs_are_one_narrow_range(self):
        for d in self.records:
            p = pr.predict(d.get("situation", {}), d.get("project", ""), self.pieces, self.kn)
            m = p.minutes()
            if m:
                self.assertLessEqual(m[0][1] / m[0][0], 2 * (1 + 1e-9), d["id"])
                self.assertLessEqual(len(dp.zones_of(list(m[0]))), 2, d["id"])

    def test_analog_is_used_only_when_written_before_and_skips_multipliers(self):
        d = self.rec("p04")
        a = pr.analog_of(d, self.records)
        self.assertEqual(a["id"], "p01")
        p = pr.predict(d["situation"], d["project"], self.pieces, self.kn, a)
        self.assertTrue(p.q["turns"].base.analog)
        self.assertEqual(p.q["turns"].muls, [])
        self.assertIsNone(pr.analog_of(self.rec("d39b"), self.records))  # 사후에 읽은 빗댄 기록은 쓰지 않는다

    def test_situation_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.toml"
            path.write_text('project = "proviso"\n[situation]\nS_fix_existing = "예"\nS_external_check = "예"\n', encoding="utf-8")
            with mock.patch("sys.stdout") as out:
                self.assertEqual(pr.main([str(path)]), 0)
            text = "".join(c.args[0] for c in out.write.call_args_list)
            self.assertIn("말할 구간", text)


class Holdout(unittest.TestCase):
    def setUp(self):
        self.kn = pr.load_kn()
        self.records = dp.load()
        self.front, self.back = ho.halves(self.records)
        self.sets = ft.load_sets()

    def test_boundary_and_halves(self):
        self.assertEqual(ho.BOUNDARY, "d38b")
        self.assertEqual(len(self.front), 64)
        self.assertEqual(self.front[-1]["id"], "d38b")
        for s in self.sets.values():
            self.assertEqual(s["fit_until"], ho.BOUNDARY)

    def test_holdout_numbers_come_only_from_the_front_half(self):
        # 앞 절반만 보고 세웠다: 저장된 범위 = 앞 절반으로 다시 맞춘 범위. 뒤 절반을 지워도 같다
        front_only = ft.records_until(self.records, ho.BOUNDARY)
        for name, s in self.sets.items():
            fitted, _ = ft.fit(s["pieces"], front_only, self.kn, front_only)
            for stored, again in zip(s["pieces"], fitted):
                self.assertEqual([(e.lo, e.hi) for e in stored.effects], [(e.lo, e.hi) for e in again.effects],
                                 (name, stored.id))

    def test_H_top_line_is_the_told_zone(self):
        table = ho.score_table({"x": self.sets["front_split"]["pieces"]}, self.back, self.kn, self.records)
        self.assertTrue(table.splitlines()[2].startswith("| **말할 구간 맞음**"))
        out = pr.explain(pr.predict({}, "batman", pr.live_pieces(self.kn), self.kn), pr.live_pieces(self.kn))
        self.assertTrue(out.startswith("말할 구간"))

    def test_back_half_comparison_is_reported_three_ways(self):
        table = ho.score_table({ho.SET_LABEL[n]: self.sets[n]["pieces"] for n in ho.SETS}, self.back, self.kn, self.records)
        head = table.splitlines()[0]
        for label in ("쪼개기 전 계산기", "쪼갠 뒤 계산기", "당시 손 예측"):
            self.assertIn(label, head)

    def test_hand_prediction_uses_told_or_the_longer_zone(self):
        d = next(r for r in self.records if r["id"] == "d39")  # [45, 80] → 신경 끄기
        self.assertEqual(ho.hand_outcome(d)["told"], "신경 끄기")
        d88 = next(r for r in self.records if r["id"] == "d88")  # 예측 없이 보냄
        self.assertIsNone(ho.hand_outcome(d88)["told"])

    def test_E_no_unexplained_regression_from_splitting(self):
        lost = ho.regressions(self.sets["front_v0"]["pieces"], self.sets["front_split"]["pieces"], self.front, self.kn, self.records)
        self.assertLessEqual(lost, set(ho.REGRESSION_OK["front_split"]), lost)
        # 최종본: 쪼갠 세트의 모양을 전체 기록으로 다시 맞춘 것보다 잃은 기록이 없다
        # 맞춘 기간(p05까지)의 기록만 본다. 세운 뒤의 기록은 시험 몫이라 회귀 비교에 넣지 않는다
        cut = [d["id"] for d in self.records].index("p05")
        done = [d for d in self.records[: cut + 1] if dp.done(d)]
        until = ft.records_until(self.records, "p04")
        before, _ = ft.fit(self.sets["front_split"]["pieces"], until, self.kn, self.records)
        lost = ho.regressions(before, pr.live_pieces(self.kn), done, self.kn, self.records)
        self.assertLessEqual(lost, set(ho.REGRESSION_OK["final"]), lost)


class Devices(unittest.TestCase):
    def setUp(self):
        self.kn = pr.load_kn()
        self.records = dp.load()

    def test_outside_situation_records_are_excepted_but_shown(self):
        # 돌아보기 까닭이 '바깥 상황'인 기록은 계산 조각 시험에서 빠지되, 성적표와 audit에 늘 보인다
        ex = [d["id"] for d in self.records if checks.is_exception(d)]
        self.assertTrue(ex)
        _, test = checks._cut_split(self.records, "p05")
        self.assertFalse({d["id"] for d in test} & set(ex))
        _, detail = checks.piece_direction("C_rate_web")
        self.assertIn("예외로 뺀 기록(바깥 상황)", detail)
        _, warns = checks.audit_pieces(self.kn)
        self.assertTrue(any("바깥 상황 예외" in w for w in warns), warns)

    def test_A_direction_and_size_are_separate_scores(self):
        down = pr.Effect("C_t", "turns", "mul", 0.5, 0.8, (("S_a", ("예",)),), "down")
        verdict, _ = ho._direction(down, {"B": [[1.2, 1.4], [1.0, 0.9]]})  # 조건이 있는 쪽이 더 크다 → 줄인다는 주장은 틀림
        self.assertEqual(verdict, "반박")
        verdict, _ = ho._direction(down, {"B": [[0.6, 0.7], [1.0, 1.1]]})
        self.assertEqual(verdict, "지지")
        rows = ho.piece_scores(ft.load_sets()["front_split"]["pieces"], ho.halves(self.records)[1], self.kn)
        self.assertTrue(all("direction" in r and "size_n" in r for r in rows))
        self.assertIn("방향 성적", ho.piece_table(rows).splitlines()[0])
        self.assertIn("크기 성적", ho.piece_table(rows).splitlines()[0])

    def test_A_found_a_wrong_direction_in_the_holdout(self):
        # 앞 절반으로 세운 '설계가 정해지면 턴이 준다'가 뒤 절반에서 방향이 틀렸다 → 최종본에서 물림(이유 틀림)
        rows = ho.piece_scores(ft.load_sets()["front_v0"]["pieces"], ho.halves(self.records)[1], self.kn)
        spec = next(r for r in rows if r["piece"] == "C_turns_spec_fixed")
        self.assertEqual(spec["direction"], "반박")
        node = self.kn.nodes["C_turns_spec_fixed"]
        self.assertEqual(node.data["status"], "retired")
        self.assertIn("이유 틀림", node.data["note"])

    def test_A_wrong_direction_is_an_audit_error(self):
        fake = [{"piece": "C_x", "direction": "반박", "rough": "있음/없음 ×1.3"}]
        with mock.patch.object(ho, "piece_scores", return_value=fake):
            errors, _ = checks.audit_pieces(self.kn)
        self.assertTrue(any("이유 틀림" in e for e in errors), errors)

    def test_audit_has_no_errors_now(self):
        errors, _ = checks.audit_pieces(self.kn)
        self.assertEqual(errors, [])

    def test_D_one_record_piece_is_allowed_with_the_widest_range(self):
        # 2026-10-19 사용자 결정: 한 건이라도 기본 논리가 틀린 게 보이면 고친다. 크기는 모르므로 가장 넓은 창
        lo, hi = ft.window([3.0], 2)
        self.assertAlmostEqual(lo * hi, 9.0)
        self.assertAlmostEqual(hi / lo, 2.0)
        self.assertIsNone(ft.window([], 2))
        # 값이 여럿인데 흩어져 어느 창도 둘을 못 담으면 세우지 않는다 (흐린 조건)
        self.assertIsNone(ft.window([1.0, 5.0, 30.0], 2))
        _, stats = ft.fit_final(self.kn, self.records)
        for e, st in stats.items():
            self.assertGreaterEqual(len(st.explained), 1, e.piece)

    def test_F_effect_count_cap(self):
        pieces = pr.live_pieces(self.kn)
        fit_recs, _ = checks._cut_split(self.records, pieces[0].seen_until)
        explained = sum(1 for _, o in ho.evaluate(pieces, fit_recs, self.kn, self.records) if o["told_hit"])
        n_eff = sum(len(p.effects) for p in pieces)
        self.assertLessEqual(n_eff * checks.EFFECT_PER_RECORDS, explained)
        with mock.patch.object(checks, "EFFECT_PER_RECORDS", 100):
            errors, _ = checks.audit_pieces(self.kn)
        self.assertTrue(any("외워서" in e for e in errors), errors)

    def test_G_numbers_are_fitted_not_hand_widened(self):
        node = self.kn.nodes["C_turns_base"]
        old = node.data["effect"][0]["range"]
        try:
            node.data["effect"][0]["range"] = [old[0] * 0.8, old[1]]
            errors, _ = checks.audit_pieces(self.kn)
        finally:
            node.data["effect"][0]["range"] = old
        self.assertTrue(any("손으로 넣거나 넓히지" in e for e in errors), errors)

    def test_G_widening_revisions_still_warned(self):
        from proviso import audit
        self.assertTrue(any("R_tok_v2 → R_tok_v3" in w for w in audit.unsplit_revisions(self.kn)))

    def test_seen_until_principle_final_pieces_are_untested_now(self):
        # 세운 시점은 p05다. p05까지의 기록은 '맞춰 본 것'일 뿐 시험에 들어가지 않는다(시험은 p06부터 쌓인다)
        for p in pr.live_pieces(self.kn):
            self.assertEqual(p.seen_until, "p05", p.id)
            verdict, detail = checks.piece_size(p.id)
            self.assertTrue(verdict.startswith("시험 전") or "시험(p05 다음부터)" in detail, (p.id, verdict, detail))

    def test_split_pieces_say_why_the_condition_matters(self):
        for pid in ("C_turns_research_v2", "C_turns_resumed_v2", "C_turns_no_check", "C_fix_existing_v2",
                    "C_small_codebase", "C_min_light_model"):
            self.assertTrue(self.kn.nodes[pid].data.get("why_condition", "").strip(), pid)
        node = self.kn.nodes["C_fix_existing_v2"]
        saved = node.data.pop("why_condition")
        try:
            errors, _ = checks.audit_pieces(self.kn)
        finally:
            node.data["why_condition"] = saved
        self.assertTrue(any("why_condition" in e for e in errors), errors)
        for old, new in (("C_turns_research", "C_turns_research_v2"), ("C_turns_resumed", "C_turns_resumed_v2")):
            o, n = self.kn.nodes[old].data, self.kn.nodes[new].data
            self.assertEqual(o["status"], "retired")
            self.assertEqual(o["replaced_by"], [new])
            self.assertTrue(set(n["conditions"]) - set(o["conditions"]), new)

    def test_pieces_name_no_project_or_app(self):
        names = ("proviso", "batman", "flowlog", "music", "godot", "sonnet", "fable", "opus")
        for p in pr.live_pieces(self.kn) + [p for s in ft.load_sets().values() for p in s["pieces"]]:
            text = " ".join([p.id, p.text, p.reason] + [e.reason for e in p.effects]).lower()
            for n in names:
                self.assertNotIn(n, text, p.id)


if __name__ == "__main__":
    unittest.main()
