import unittest
from pathlib import Path

from domains.agent_usage import checks, dispatches as dp
from proviso import audit, schema

ROOT = Path(__file__).resolve().parent.parent
KN = ROOT / "domains" / "agent_usage" / "knowledge.toml"


class Knowledge(unittest.TestCase):
    def test_knowledge_and_records_are_valid(self):
        kn = schema.load(KN)
        self.assertEqual(schema.validate(kn), [])
        self.assertEqual(dp.validate(dp.load(), kn), [])

    def test_every_check_name_exists(self):
        # 가설·규칙 모두: 검사 이름이 있고, 세운 뒤 기록으로만 시험하는 검사는 SEEN_UNTIL이 있다
        kn = schema.load(KN)
        for node in kn.claims():
            for name in schema.check_names(node):
                self.assertIn(name, checks.CHECKS, node.id)
                if name in checks.NODE_CUT:  # 계산 조각: 노드가 맞출 때 본 마지막 기록을 적는다
                    self.assertIn("seen_until", node.data, node.id)
                elif name not in checks.NO_CUT:
                    self.assertIn(name, checks.SEEN_UNTIL, node.id)

    def test_prediction_rules_that_are_alive_have_a_test(self):
        # 2026-10-19: 예측에 쓰는 살아 있는 규칙은 자동 검사가 있거나, 못 붙이는 까닭(test_plan)을 적는다
        kn = schema.load(KN)
        for rule in kn.of("rule"):
            if schema.alive(rule):
                self.assertTrue(schema.check_names(rule) or rule.data.get("test_plan"), rule.id)

    def test_no_verified_status_left(self):
        for domain in ("flowlog", "music_player", "agent_usage"):
            kn = schema.load(ROOT / "domains" / domain / "knowledge.toml")
            for node in kn.claims():
                self.assertIn(node.data.get("status", "hypothesis"), ("hypothesis", "retired"), node.id)

    def test_audit_passes_after_turn_analogy_revision(self):
        # 빗대어 잡은 턴 수(H_turns_over)를 R_turns_analogy v2가 배수로 고쳤다. v1은 부작용과 함께 보존된다
        kn = schema.load(KN)
        self.assertEqual(audit.unaccepted_harms(kn), [])
        v1 = kn.nodes["R_turns_analogy"].data
        self.assertEqual(v1["status"], "retired")
        self.assertIn("H_turns_over", v1["side_effects"])


class Classes(unittest.TestCase):
    def test_zone_and_token_class_edges(self):
        self.assertEqual([dp.zone(m) for m in (10, 10.1, 40, 40.1)], ["잠깐", "다른 일", "다른 일", "신경 끄기"])
        self.assertEqual([dp.token_class(t) for t in (19.9, 20, 60, 119.9, 120)], ["T1", "T2", "T3", "T3", "T4"])

    def test_zones_of_prediction_range(self):
        self.assertEqual(dp.zones_of([5, 10]), ["잠깐"])
        self.assertEqual(dp.zones_of([10, 20]), ["다른 일"])  # 아래 끝이 경계값이면 위 구간부터
        self.assertEqual(dp.zones_of([40, 65]), ["신경 끄기"])
        self.assertEqual(dp.zones_of([8, 18]), ["잠깐", "다른 일"])  # 걸침
        self.assertEqual(dp.zones_of([5, 50]), ["잠깐", "다른 일", "신경 끄기"])
        self.assertEqual(dp.zones_of([90]), ["신경 끄기"])  # 하나만 있으면 '이상'
        self.assertEqual(dp.zones_of([]), [])

    def test_say_the_zone_of_the_middle_value(self):
        # 2026-11-03 사용자 결정(R_say_numbers_v3): 걸치면 범위의 가운데 값(√(하한×상한))이 든 구간으로 말한다
        self.assertEqual(dp.say_zone([6, 15]), "잠깐")      # 가운데 9.5분 (p145: 긴 쪽 '다른 일'로 말했는데 7.4분)
        self.assertEqual(dp.say_zone([8, 18]), "다른 일")   # 가운데 12분
        self.assertEqual(dp.say_zone([30, 55]), "신경 끄기")  # 가운데 40.6분
        self.assertEqual(dp.say_zone([5, 50]), "다른 일")   # 세 구간에 걸쳐도 가운데 15.8분
        self.assertEqual(dp.say_zone([5, 9]), "잠깐")       # 걸치지 않으면 그 구간
        self.assertEqual(dp.say_zone([90]), "신경 끄기")    # 열린 범위('이상')는 가운데가 없어 긴 쪽
        self.assertIsNone(dp.say_zone([]))

    def test_judge_range_and_direction(self):
        self.assertEqual(dp.judge(["다른 일", "신경 끄기"], "신경 끄기", dp.ZONES), "맞음")
        self.assertEqual(dp.judge(["잠깐"], "신경 끄기", dp.ZONES), "낮게 잡음")
        self.assertEqual(dp.judge(["다른 일", "신경 끄기"], "잠깐", dp.ZONES), "높게 잡음")
        self.assertEqual(dp.judge(["T2"], None, dp.TOKEN_CLASSES), "모름")


class Rescore20261019(unittest.TestCase):
    """시간 구간 세 마디로 다시 채점 (기록 파일은 고치지 않는다)."""

    def test_rescore_counts_minute_ranges_only(self):
        records = dp.load()
        # 다시 채점한 시점(p03까지)의 기록만: 뒤에 기록이 늘어도 이 숫자는 그대로다
        records = records[: [d["id"] for d in records].index("p03") + 1]
        r = dp.rescore(records)
        self.assertEqual(sorted(r["분 범위 없음"]), sorted(["dR1", "dR2", "dR3", "dR4", "d14", "d16"]))
        self.assertEqual(sum(r["판정"].values()), 118)
        spans = sum(r["걸침"].values())
        singles = sum(sum(c.values()) for c in r["구간별"].values())
        self.assertEqual(spans + singles, 118)

    def test_miss_split_by_turns(self):
        base = {"id": "x", "predicted": {"minutes": [20, 30], "turns": [100, 150]}, "actual": {}}
        speed = {**base, "actual": {"minutes": 10, "turns": 120}}
        amount = {**base, "actual": {"minutes": 10, "turns": 50}}
        none = {"id": "y", "predicted": {"minutes": [20, 30]}, "actual": {"minutes": 50, "turns": 50}}
        self.assertEqual(dp.miss_split(speed), ("아래", "속도"))
        self.assertEqual(dp.miss_split(amount), ("아래", "양"))
        self.assertEqual(dp.miss_split(none), ("위", "턴 예측 없음"))
        self.assertIsNone(dp.miss_split({**base, "actual": {"minutes": 25, "turns": 50}}))

    def test_p04_told_the_long_zone(self):
        p04 = {d["id"]: d for d in dp.load()}["p04"]["predicted"]
        self.assertEqual(p04["told"], "신경 끄기")
        self.assertEqual(dp.zones_of(p04["minutes"])[-1], p04["told"])

    def test_future_zone_miss_needs_wrong_and_why(self):
        kn = schema.load(KN)
        records = dp.load()
        late = {"id": "zz1", "project": "proviso", "batch": 9, "date": "2026-10-20", "task": "t",
                "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 30, "turns": 10}}
        errors = dp.validate(records + [late], kn)
        self.assertTrue(any("zz1" in e and "review.wrong" in e for e in errors))
        late["review"] = {"wrong": ["R_time_turns_v2"], "why": "조건 흐림"}
        self.assertEqual(dp.validate(records + [late], kn), [])
        late["review"]["why"] = "몰라"
        self.assertTrue(any("review.why" in e for e in dp.validate(records + [late], kn)))
        # 2026-11-03 사용자 결정: 까닭을 못 찾으면 '까닭 모름' — 틀린 조각을 몰라도 되고, 사용자에게 넘길 목록에 뜬다
        late["review"] = {"why": "까닭 모름"}
        self.assertEqual(dp.validate(records + [late], kn), [])
        self.assertIn("zz1", dp.for_user(records + [late]))
        late["review"]["user"] = "사용자 답"
        self.assertNotIn("zz1", dp.for_user(records + [late]))
        # 다른 까닭은 여전히 틀린 조각이 있어야 한다
        late["review"] = {"why": "조건 흐림"}
        self.assertTrue(any("zz1" in e and "review.wrong" in e for e in dp.validate(records + [late], kn)))
        # 지난 기록(p03까지)은 빗나가도 요구하지 않는다: p01은 구간을 빗나갔지만 오류가 없다
        self.assertEqual(dp.zone_verdict({d["id"]: d for d in records}["p01"]), "높게 잡음")
        self.assertEqual(dp.validate(records, kn), [])

    def test_records_from_nov_4_need_times_and_agent_round(self):
        # 2026-11-03 사용자 결정: 빗댄 기록 규칙이 '보낼 때 끝나 있던 기록'과 '같은 에이전트의 앞 회차'를 가르려면 필요하다
        kn = schema.load(KN)
        records = dp.load()
        new = {"id": "zz3", "project": "proviso", "batch": 41, "date": "2026-11-04", "task": "t",
               "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 6, "turns": 10},
               "turns": {"글": {"n": 7, "sum_s": 20.0, "turn_s": 2.5}}, "review": {"report": "docs/worklog/CLAUDE.md"}}
        errors = dp.validate(records + [new], kn)
        self.assertTrue(any("zz3" in e and "actual.start" in e for e in errors))
        self.assertTrue(any("zz3" in e and "agent" in e for e in errors))
        new["actual"].update(start="2026-11-04T01:00:00Z", end="2026-11-04T01:06:00Z")
        new.update(agent="작성", round=1)
        self.assertTrue(any("zz3" in e and "decide" in e for e in dp.validate(records + [new], kn)))  # 보낼까 판단도 11-04부터
        new["decide"] = {"main_ctx_k": 300, "left": 50, "direct_m": 20.0, "send_m": 9.0, "chose": "보냄", "why": ["비용"]}
        self.assertTrue(any("zz3" in e and "model·effort" in e for e in dp.validate(records + [new], kn)))  # 모델·effort도 11-04부터
        new.update(model="Opus 5.5", effort="high")
        self.assertEqual(dp.validate(records + [new], kn), [])
        new["actual"]["start"] = "01:00:00"
        self.assertTrue(any("UTC ISO" in e for e in dp.validate(records + [new], kn)))
        new["actual"] = {"minutes": 6, "turns": 10, "time_skip": "클라우드 세션이라 대화 기록이 없음"}
        self.assertEqual(dp.validate(records + [new], kn), [])
        new["situation"] = {"S_resumed": "예"}
        self.assertTrue(any("round" in e for e in dp.validate(records + [new], kn)))
        # 배치 줄이 AGENT-LOG에 없으면 막는다(batman 기록은 batman 쪽이라 뺀다)
        new["situation"] = {}
        new["batch"] = 999
        self.assertTrue(any("배치 999" in e for e in dp.validate(records + [new], kn)))
        self.assertEqual([e for e in dp.validate(records + [{**new, "project": "batman"}], kn) if "배치 999" in e], [])
        # 이어 보낸 회차(round ≥ 2)의 턴 길이 표는 skip하지 않는다 — --rounds로 그 회차를 가른다
        new.update(batch=41, round=2, situation={"S_resumed": "예"}, turns={"skip": "같은 에이전트에 이어 보내 로그가 누적"})
        self.assertTrue(any("skip하지 않는다" in e for e in dp.validate(records + [new], kn)))
        # 11-03까지의 기록은 요구하지 않는다
        self.assertEqual(dp.validate(records, kn), [])

    def test_model_and_effort_decide_the_default_setup_state(self):
        # 2026-11-03 사용자 결정: S_other_model(기본 설정 Opus 5.5 high가 아닌가)은 기록의 model·effort 칸에서 계산한다
        self.assertEqual([dp.other_model(m, e) for m, e in (("Opus 5.5", "high"), ("Opus 5.5", "xhigh"), ("Haiku 5.5", None),
                                                             ("Sonnet 5.5", "max"), ("Opus 5.5", None), (None, None))],
                         ["아니오", "예", "예", "예", None, None])
        # 칸이 없는 옛 기록: S_other_model이 아니오(적지 않으면 기본값)면 기본 설정, 아니면 모름
        self.assertEqual(dp.setup({"situation": {}}), ("Opus 5.5", "high"))
        self.assertEqual(dp.setup({"situation": {"S_other_model": "예"}}), (None, None))
        self.assertEqual(dp.setup({"model": "Haiku 5.5", "situation": {"S_other_model": "예"}}), ("Haiku 5.5", None))
        base = {"id": "zz5", "date": "2026-11-03", "model": "Sonnet 5.5", "effort": "max", "situation": {"S_other_model": "예"}}
        self.assertEqual(dp.model_errors(base), [])
        self.assertTrue(dp.model_errors({**base, "situation": {}}))                        # 적지 않으면 기본값 아니오 → 어긋남
        self.assertTrue(dp.model_errors({**base, "model": "GPT"}))                          # 모르는 모델 이름
        self.assertTrue(dp.model_errors({**base, "effort": "보통"}))
        self.assertTrue(dp.model_errors({**base, "model": None}))                           # effort만 있음
        self.assertEqual(dp.model_errors({"id": "zz6", "date": "2026-11-03", "task": "t"}), [])   # 11-03까지는 칸이 없어도 된다
        self.assertTrue(dp.model_errors({"id": "zz6", "date": "2026-11-04", "task": "t"}))
        # 메인 자신의 일은 세션이 자기 effort를 모를 수 있어 모델만 있어도 된다
        self.assertEqual(dp.model_errors({"id": "zz7", "date": "2026-11-04", "model": "Opus 5.5", "situation": {"S_main_self": "예"}}), [])
        # 지난 기록은 모두 두 칸과 맞는다(채우기 2026-11-03: p139·p142·p169·p170의 '아니오'를 '예'로 고침 — Opus 5.5 xhigh)
        records = {d["id"]: d for d in dp.load()}
        self.assertEqual([e for d in records.values() for e in dp.model_errors(d)], [])
        self.assertEqual([(records[i]["effort"], records[i]["situation"]["S_other_model"]) for i in ("p139", "p142", "p169", "p170")],
                         [("xhigh", "예")] * 4)

    def test_records_from_nov_3_need_turn_table_and_report(self):
        # 2026-11-02 사용자 결정: 문서에만 적힌 단계는 빠지므로 검사가 막는다. 2026-11-03부터의 끝난 기록만
        kn = schema.load(KN)
        records = dp.load()
        new = {"id": "zz2", "project": "proviso", "batch": 99, "date": "2026-11-03", "task": "t",
               "predicted": {"minutes": [5, 9], "told": "잠깐"}, "actual": {"minutes": 6, "turns": 10}}
        errors = dp.validate(records + [new], kn)
        self.assertTrue(any("zz2" in e and "턴 길이 표" in e for e in errors))
        self.assertTrue(any("zz2" in e and "review.report" in e for e in errors))
        # 표를 붙이고 이 저장소에 있는 보고서를 가리키면 통과
        new["turns"] = {"글": {"n": 7, "sum_s": 20.0, "turn_s": 2.5}, "Bash:git": {"n": 3, "turn_s": 4.0}}
        new["review"] = {"report": "docs/worklog/CLAUDE.md"}
        self.assertEqual(dp.validate(records + [new], kn), [])
        # 잴 수 없으면 이유 한 줄, 다른 저장소 보고서는 "저장소:경로"
        new["turns"] = {"skip": "클라우드 세션: 대화 기록 없음"}
        new["review"] = {"report": "movie_game:docs/worklog/2026-11-03-x.md"}
        self.assertEqual(dp.validate(records + [new], kn), [])
        # 없는 파일, 빈 이유, 모양이 틀린 표는 잡는다
        new["review"] = {"report": "docs/worklog/없는-보고서.md"}
        self.assertTrue(any("파일이 없음" in e for e in dp.validate(records + [new], kn)))
        new["review"] = {"report": "docs/worklog/CLAUDE.md"}
        new["turns"] = {"skip": " "}
        self.assertTrue(any("turns.skip" in e for e in dp.validate(records + [new], kn)))
        new["turns"] = {"글": {"turn_s": 2.5}}
        self.assertTrue(any("turns는 동작마다" in e for e in dp.validate(records + [new], kn)))
        # 아직 안 끝난 기록, 11-02까지의 기록은 요구하지 않는다(브랜치에서 합쳐 올 기록 포함)
        pending = {**new, "turns": None, "review": {}, "actual": {"status": "unknown"}}
        del pending["turns"]
        self.assertEqual(dp.form_errors(pending), [])
        old = {**pending, "date": "2026-11-02", "actual": {"minutes": 6}}
        self.assertEqual(dp.form_errors(old), [])

    def test_used_check_reads_predictions_written_before(self):
        verdict, detail = checks.used_minutes("R_time_turns_v2")
        self.assertTrue(verdict.startswith(("지지됨", "반박됨")))
        self.assertNotIn("d32b ", detail)  # 보내기 전에 적지 않은 예측(d32b)은 뺀다
        # R_integration은 2026-10-19엔 시험 전이었다. 2026-10-25에 브랜치 ccr-2a22e640-e8dn8n(10-20 Flowlog 세션)을
        # 병합하며 들어온 p54(원래 p20, 보내기 전에 R_integration으로 예측)가 첫 시험 기록이다 → 이제 판정이 난다
        verdict, detail = checks.used_minutes("R_integration")
        self.assertTrue(verdict.startswith(("지지됨", "반박됨")), verdict)
        self.assertIn("p54", detail)

    def test_telling_check_v3_skips_records_told_with_v2(self):
        # 2026-11-03 병합으로 p145 뒤에 붙은 p147–p167은 v3가 생기기 전에 갈라진 브랜치가 v2(걸치면 긴 쪽)로 말했다 —
        # 파일 순서로는 시험 쪽이지만 v3의 성적에 넣지 않는다(predicted.rules에 R_say_numbers_v2)
        verdict, detail = checks.told_zone_v3()
        test = detail.split("시험 기록")[1]
        self.assertIn("p146", test)
        for rid in ("p147", "p148", "p167"):
            self.assertNotIn(rid + " ", test)

    def test_open_ended_bound_uses_lower(self):
        self.assertEqual(dp.midpoint([400]), 400)
        self.assertEqual(dp.midpoint([800, 1200]), 1000)


class Loop(unittest.TestCase):
    def test_stopped_and_unknown_are_not_judged(self):
        # 빠진 기록은 멈춤(stopped)이나 아직 끝나지 않은(unknown) 것뿐이어야 한다. d15·p08은 멈춤
        not_done = [d for d in dp.load() if not dp.done(d)]
        ids = {d["id"] for d in not_done}
        self.assertIn("d15", ids)
        for d in not_done:
            if d["id"] != "d15":
                self.assertIn(d["actual"].get("status"), ("stopped", "unknown"), d["id"])

    def test_hypothesis_is_tested_only_on_later_records(self):
        # H_tok_per_min은 d12c까지 보고 세웠다 → 배치 10 이후로만 시험한다. d12c 자신은 맞춰 본 쪽
        verdict, detail = checks.tokens_per_minute()
        self.assertTrue(verdict.startswith("반박됨"))
        fit, test = detail.split("시험 기록")
        test = test.split(":", 1)[1]  # "(d12c 다음부터)" 머리말은 뺀다
        self.assertIn("dR1 0.83M ✗", test)
        self.assertIn("d12c", fit)
        self.assertNotIn("d12c ", test)

    def test_every_check_splits_at_its_cut(self):
        order = [d["id"] for d in dp.load()]
        for name, cut in checks.SEEN_UNTIL.items():
            fit, test = checks._split(name, lambda d: True)
            limit = order.index(cut)
            self.assertTrue(all(order.index(d["id"]) <= limit for d in fit), name)
            self.assertTrue(all(order.index(d["id"]) > limit for d in test), name)

    def test_hypotheses_set_from_batch_13_wait_for_new_records(self):
        for name in ("tokens_per_minute_long_only", "turn_rate_non_web", "check_loop_turn_rate"):
            if order_last_is(checks.SEEN_UNTIL[name]):
                self.assertEqual(checks.CHECKS[name]()[0], "시험 전")


def _ids(detail_part: str) -> list[str]:
    """check 설명의 한 줄('...: d01 6.2, d04 2.8 ✗')에서 기록 id만 뽑는다."""
    body = detail_part.split(":", 1)[1].strip()
    return [] if body == "없음" else [item.split()[0] for item in body.split(", ")]


class Cleanup20261019(unittest.TestCase):
    NEW = ("mid_notes_bounded", "sonnet_fixed_floor", "fixed_input_opus", "fix_context",
           "settled_integration", "build_tools_minutes", "doc_spec_minutes")

    def test_new_hypotheses_are_tested_from_d95(self):
        for name in self.NEW:
            self.assertEqual(checks.SEEN_UNTIL[name], "d94", name)

    def test_new_checks_match_the_records_they_were_built_from(self):
        # 세울 때 본 기록에 ✗가 있으면 검사가 가설 문장과 다르게 짜인 것이다 (mid_notes는 보내기 전에 안 적은 d01만 ✗)
        for name in self.NEW:
            fit = checks.CHECKS[name]()[1].split("\n")[0]
            ids = _ids(fit)
            self.assertTrue(ids, name)
            bad = [i for i in ids if f"{i} " in fit and fit.split(f"{i} ", 1)[1].split(",")[0].endswith("✗")]
            self.assertEqual(bad, ["d01"] if name == "mid_notes_bounded" else [], name)

    def test_render_check_keeps_only_short_laps(self):
        # H_render_rate의 조건 '렌더 한 회 1–2분' = S_long_lap=아니오. 장 흐름 바퀴(d69 일부, d69c 예)는 뺀다
        detail = checks.render_turn_rate()[1]
        ids = _ids(detail.split("\n")[0]) + _ids(detail.split("\n")[1])
        self.assertNotIn("d69", ids)
        self.assertNotIn("d69c", ids)
        records = {d["id"]: d for d in dp.load()}
        self.assertTrue(all(dp.situation(records[i], "S_long_lap") == "아니오" for i in ids))

    def test_research_cap_counts_web_research_only(self):
        detail = checks.research_cap()[1]
        records = {d["id"]: d for d in dp.load()}
        for line in detail.split("\n"):
            for i in _ids(line):
                self.assertEqual(dp.situation(records[i], "S_web"), "예", i)

    def test_analog_prefers_prediction_then_past_reading(self):
        self.assertEqual(checks._analog({"id": "d94", "predicted": {}})["id"], "d68")
        self.assertEqual(checks._analog({"id": "x", "predicted": {"analog": "d61"}})["id"], "d61")
        self.assertIsNone(checks._analog({"id": "x", "predicted": {"analog": "없는 id"}}))

    def test_rules_are_tidy(self):
        # 방식 1: 살아 있는 규칙은 이유가 있고 목표를 섬긴다. 물린 규칙은 무엇이 대신하는지 가리킨다
        kn = schema.load(KN)
        for rule in kn.of("rule"):
            if rule.data["status"] == "retired":
                self.assertTrue(rule.refs("replaced_by"), rule.id)
            else:
                self.assertNotIn("기록 없음", rule.data["reason"], rule.id)
                self.assertTrue(rule.refs("serves"), rule.id)


def order_last_is(record_id: str) -> bool:
    return dp.load()[-1]["id"] == record_id


if __name__ == "__main__":
    unittest.main()


class HandVsCalc(unittest.TestCase):
    """손 예측과 계산기를 나란히 적은 기록의 승패 (사용자 결정 2026-10-19: 어느 쪽이 나은지 계속 기록)."""

    def test_counts_only_records_with_both(self):
        recs = [
            {"id": "a", "predicted": {"told": "다른 일"}, "calc": {"told": "신경 끄기"}, "actual": {"minutes": 20}},
            {"id": "b", "predicted": {"told": "잠깐"}, "calc": {"told": "잠깐"}, "actual": {"minutes": 5}},
            {"id": "c", "predicted": {"told": "잠깐"}, "actual": {"minutes": 5}},
        ]
        r = dp.hand_vs_calc(recs)
        self.assertEqual(r["손만 맞음"], 1)
        self.assertEqual(r["둘 다 맞음"], 1)
        self.assertEqual(sum(r.values()), 2)
