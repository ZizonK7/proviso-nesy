"""agent_usage 가설 검사. knowledge.toml의 hypothesis.check 이름으로 찾는다.

판정은 실측 기록(dispatches.toml)으로 한다. 가설은 **세운 뒤에 나온 기록으로만** 시험한다.
세울 때 이미 본 기록은 '맞춰 본 것'(사후 설명)이라 따로 보여 주기만 한다.
판정: "지지됨" / "반박됨" (시험 기록의 80% 이상이 맞으면 지지됨) / "시험 전" (세운 뒤 기록이 아직 없음).

규칙(방법이 붙은 가설)에는 두 가지 검사를 붙인다 (2026-10-19, 규칙·가설 통합):
- 주장 검사: 규칙의 숫자를 가설과 같은 잣대로 잰다(위 함수들을 그대로 check에 건다).
- 쓴 예측 검사(used_minutes·used_turns·used_tokens): 그 규칙을 predicted.rules에 적은 예측이 실측과 맞았나.
  예측은 보내기 전에 적은 것이라 그 자체가 세운 뒤의 시험이다(SEEN_UNTIL이 필요 없다). 보내기 전에 적지 않은 기록은 뺀다.
  한 예측에 규칙이 여럿 들어가므로 빗나감이 이 규칙 탓인지는 모른다 → review.wrong이 짚은 횟수를 같이 보여 준다.
"""
from __future__ import annotations

from collections.abc import Callable
from statistics import median

from . import dispatches as dp

# 가설을 세울 때 본 마지막 기록. 그다음 기록부터가 시험이다.
SEEN_UNTIL = {
    "tokens_per_minute": "d12c",  # 배치 1–9로 세움 (배치 10 실측을 보기 전)
    "tokens_per_minute_by_length": "d16",
    "turns_overestimated": "d16",
    "turns_vs_context": "d16",
    "check_loop_time": "d16",
    "turn_rate_by_kind": "d16",
    "mid_notes_longer": "d16",
    "tokens_per_minute_long_only": "d26b",  # 배치 1–13으로 세움
    "turn_rate_non_web": "d26b",
    "check_loop_turn_rate": "d26b",
    "research_cap": "dR5D",  # 배치 10·15 조사 여덟 건으로 세움
    "sonnet_max_rate": "d43",  # 배치 19 d42 한 건으로 세움
    "render_turn_rate": "d47",  # 배치 19–22 렌더 작업 네 건(d43·d45·d46·d47)으로 세움
    "model_mult_shape": "d50",  # 배치 23 d49·d50 두 건으로 세움
    "long_lap_turn_rate": "d47",  # 긴 반복 기록(d12b·d12c·d26b)으로 세움
    "given_design_rate": "d71",  # 배치 28 d70·d71 두 건으로 세움
    "given_design_rate2": "d73",  # 배치 29 돌아보기: d70·d72(예)로 세움, d73(일부)을 뺀 근거
    # 2026-10-19 전체 정리(기록 d01–d94를 다 보고 세움). d95부터 시험한다
    "mid_notes_bounded": "d94",
    "sonnet_fixed_floor": "d94",
    "fixed_input_opus": "d94",
    "fix_context": "d94",
    "settled_integration": "d94",
    "build_tools_minutes": "d94",
    "doc_spec_minutes": "d94",
}
NEED = 0.8
SOURCE = "measured"  # 이 분야의 자동 검사는 실측 기록으로 판정한다 (score.py가 출처로 보여 준다)

# 토큰 규칙이 가정한 턴당 맥락(천 토큰). turns_vs_context가 '맥락을 작게 잡았는지' 볼 때 쓴다.
ASSUMED_CTX_K = {"R_tok_v2": 250, "R_tok_v3": 370, "R_tok_long": 350, "R_tok_short": 120, "R_tok_short_v5": 160,
                 "R_tok_long_v5": 355}

# 빗댄 기록. 2026-10-19부터는 보내기 전에 predicted.analog에 적는다. 그 전 기록은 돌아보기 글에서 사후에 읽은 것이라
# '세울 때 본 기록'을 보여 줄 때만 쓴다 (모두 SEEN_UNTIL 앞이라 판정에 들어가지 않는다).
# d68·d87은 글이 비유를 밝히지 않아 가설이 말하는 종류의 직전 기록을 골랐다(d68: 앞 통합, d87: 도구 없이 지은 새 빌더).
PAST_ANALOG = {"d39b": "d26b", "d68": "d39b", "d94": "d68", "d62": "d61", "d87": "d61"}


def _default_setup(d: dict) -> bool:
    """F_setup(Opus 5.5 high) 안의 기록인가. 숫자 범위 가설은 이 설정에서만 시험한다."""
    return dp.situation(d, "S_other_model") != "예"


def _split(name: str, applies: Callable[[dict], bool]) -> tuple[list[dict], list[dict]]:
    """(세울 때 본 기록, 시험 기록). 끝까지 한 작업 중 가설이 다루는 것만."""
    records = dp.load()
    cut = [d["id"] for d in records].index(SEEN_UNTIL[name]) + 1
    pick = [(i, d) for i, d in enumerate(records) if dp.done(d) and applies(d)]
    return [d for i, d in pick if i < cut], [d for i, d in pick if i >= cut]


def _judge(name: str, applies: Callable[[dict], bool], ok: Callable[[dict], bool],
           show: Callable[[dict], str]) -> tuple[str, str]:
    fit, test = _split(name, applies)

    def listing(rows: list[dict]) -> str:
        return ", ".join(f"{d['id']} {show(d)}{'' if ok(d) else ' ✗'}" for d in rows) or "없음"

    detail = (f"  세울 때 본 기록 (맞춰 본 것): {listing(fit)}\n"
              f"  시험 기록 ({SEEN_UNTIL[name]} 다음부터): {listing(test)}")
    if not test:
        return "시험 전", detail
    hits = sum(ok(d) for d in test)
    word = "지지됨" if hits / len(test) >= NEED else "반박됨"
    return f"{word} (시험 {len(test)}건 중 {hits}건 맞음)", detail


def _m(d: dict, key: str) -> float | None:
    return dp.measures(d)[key]


def tokens_per_minute() -> tuple[str, str]:
    """H_tok_per_min: 분당 토큰은 작업 종류와 상관없이 1.2–2.6M."""
    return _judge("tokens_per_minute",
                  lambda d: _m(d, "tokens_per_min") is not None,
                  lambda d: 1.2 <= _m(d, "tokens_per_min") <= 2.6,
                  lambda d: f"{_m(d, 'tokens_per_min'):.2f}M")


def tokens_per_minute_by_length() -> tuple[str, str]:
    """H_tok_per_min_long: 150턴 넘으면 1.1–2.6M, 안쪽이면 0.7–1.2M (긴 글 한 덩어리는 뺌)."""
    def ok(d: dict) -> bool:
        rate = _m(d, "tokens_per_min")
        return 1.1 <= rate <= 2.6 if _m(d, "turns") > 150 else 0.7 <= rate <= 1.2

    return _judge("tokens_per_minute_by_length",
                  lambda d: _m(d, "tokens_per_min") is not None and _m(d, "turns") is not None
                  and dp.situation(d, "S_unsaved_doc") != "예",
                  ok,
                  lambda d: f"{_m(d, 'turns')}턴 {_m(d, 'tokens_per_min'):.2f}M")


def _turn_ratio(d: dict) -> float:
    return _m(d, "turns") / dp.midpoint(d["predicted"]["turns"])


def turns_overestimated() -> tuple[str, str]:
    """H_turns_over: 비슷한 과거 작업에 빗대 잡은 턴 수는 실제보다 크다 (실제/예상 ≤ 0.8)."""
    return _judge("turns_overestimated",
                  lambda d: "R_turns_analogy" in d["predicted"].get("rules", [])
                  and d["predicted"].get("turns") and _m(d, "turns"),
                  lambda d: _turn_ratio(d) <= 0.8,
                  lambda d: f"실제/예상 턴 {_turn_ratio(d):.2f}")


def _assumed_ctx(d: dict) -> float | None:
    for rule in d["predicted"].get("rules", []):
        if rule in ASSUMED_CTX_K:
            return ASSUMED_CTX_K[rule]
    return None


def turns_vs_context() -> tuple[str, str]:
    """H_cancel: 큰 작업(예상 800턴 이상)에서 토큰 등급이 맞았다면, 턴은 크게(≤0.8배) 맥락은 작게(≥1.2배) 잡았다."""
    def applies(d: dict) -> bool:
        p = d["predicted"]
        if not (p.get("turns") and _m(d, "turns") and _m(d, "tokens_m") and _assumed_ctx(d)):
            return False
        hit = dp.token_class(_m(d, "tokens_m")) in p.get("tokens_class", [])
        return hit and dp.midpoint(p["turns"]) >= 800

    def ctx_ratio(d: dict) -> float:
        return _m(d, "ctx_per_turn_k") / _assumed_ctx(d)

    return _judge("turns_vs_context", applies,
                  lambda d: _turn_ratio(d) <= 0.8 and ctx_ratio(d) >= 1.2,
                  lambda d: f"턴 ×{_turn_ratio(d):.2f}, 턴당 맥락 ×{ctx_ratio(d):.2f}")


def _time_ratio(d: dict) -> float | None:
    mid = dp.midpoint(d["predicted"].get("minutes", []))
    return _m(d, "minutes") / mid if mid else None


def check_loop_time() -> tuple[str, str]:
    """H_check_loop: 확인 → 고침을 반복하면 예상(가운데)보다 길고, 확인만 있고 반복이 없으면 예상 안쪽이다."""
    def applies(d: dict) -> bool:
        loop = dp.situation(d, "S_check_loop")
        plain = dp.situation(d, "S_external_check") == "예" and loop == "아니오"
        return _time_ratio(d) is not None and (loop == "예" or plain)

    def ok(d: dict) -> bool:
        longer = _time_ratio(d) > 1.0
        return longer if dp.situation(d, "S_check_loop") == "예" else not longer

    return _judge("check_loop_time", applies, ok,
                  lambda d: f"{'반복' if dp.situation(d, 'S_check_loop') == '예' else '반복 없음'} "
                            f"실제/예상 {_time_ratio(d):.2f}")


def turn_rate_by_kind() -> tuple[str, str]:
    """H_turn_rate: 30분 안쪽에 끝난 작업은 분당 6.5턴 이상."""
    return _judge("turn_rate_by_kind",
                  lambda d: _m(d, "turns_per_min") is not None and _m(d, "minutes") <= 31,
                  lambda d: _m(d, "turns_per_min") >= 6.5,
                  lambda d: f"{_m(d, 'minutes')}분 분당 {_m(d, 'turns_per_min'):.1f}턴")


def mid_notes_longer() -> tuple[str, str]:
    """H_mid_notes: 도중에 추가 지시를 받은 작업은 같은 배치의 다른 작업(가운데 값)보다 1.3배 넘게 길다."""
    records = [d for d in dp.load() if dp.done(d)]

    def ratio(d: dict) -> float | None:
        others = [o["actual"]["minutes"] for o in records
                  if o["project"] == d["project"] and o["batch"] == d["batch"] and o["id"] != d["id"]
                  and dp.situation(o, "S_mid_notes") != "예"]
        return d["actual"]["minutes"] / median(others) if others else None

    return _judge("mid_notes_longer",
                  lambda d: dp.situation(d, "S_mid_notes") == "예" and ratio(d) is not None,
                  lambda d: ratio(d) > 1.3,
                  lambda d: f"같은 배치 가운데 값의 {ratio(d):.2f}배")


def tokens_per_minute_long_only() -> tuple[str, str]:
    """H_tok_rate_long: Opus high로 150턴 넘게 돈 작업은 분당 토큰 1.1–2.6M (긴 글 한 덩어리는 뺌)."""
    return _judge("tokens_per_minute_long_only",
                  lambda d: _m(d, "tokens_per_min") is not None and _m(d, "turns") is not None
                  and _m(d, "turns") > 150 and _default_setup(d)
                  and dp.situation(d, "S_unsaved_doc") != "예",
                  lambda d: 1.1 <= _m(d, "tokens_per_min") <= 2.6,
                  lambda d: f"{_m(d, 'turns')}턴 {_m(d, 'tokens_per_min'):.2f}M")


def turn_rate_non_web() -> tuple[str, str]:
    """H_turn_rate_shape: Opus high, 웹 조사·CI 지켜보기·저장 없는 긴 글이 아닌 작업은 분당 2.5–6.5턴."""
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_web") != "예" and dp.situation(d, "S_ci_warm") != "예"
                and dp.situation(d, "S_ci_cold") != "예" and dp.situation(d, "S_unsaved_doc") != "예"
                and dp.situation(d, "S_render") != "예")

    return _judge("turn_rate_non_web", applies,
                  lambda d: 2.5 <= _m(d, "turns_per_min") <= 6.5,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def render_turn_rate() -> tuple[str, str]:
    """H_render_rate: Opus high로 렌더 한 장(1–2분)을 찍고 보며 고치는 반복(S_long_lap=아니오)이 있는 구현 작업은 분당 5.5–8.5턴."""
    # 2026-10-19 검사 고침: 가설 문장의 조건 '렌더 한 회가 1–2분'은 S_long_lap=아니오다(상태 설명 그대로).
    # 처음 검사는 이 조건을 빼먹어 장 흐름 바퀴(d69 일부, d69c 예)와 한 번 실행(d69b 모름)까지 쟀다.
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_render") == "예" and dp.situation(d, "S_long_lap") == "아니오")

    return _judge("render_turn_rate", applies,
                  lambda d: 5.5 <= _m(d, "turns_per_min") <= 8.5,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def long_lap_turn_rate() -> tuple[str, str]:
    """H_check_loop3: 한 바퀴가 긴 확인 반복(S_long_lap=예)은 분당 2.5–4.5턴."""
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_check_loop") == "예" and dp.situation(d, "S_long_lap") == "예")

    return _judge("long_lap_turn_rate", applies,
                  lambda d: 2.5 <= _m(d, "turns_per_min") <= 4.5,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def check_loop_turn_rate() -> tuple[str, str]:
    """H_check_loop2: 외부 확인이 있는 작업에서 반복하면 분당 턴 < 4, 반복이 없거나 일부면 ≥ 4 (CI 지켜보기는 뺌)."""
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_external_check") == "예"
                and dp.situation(d, "S_check_loop") in ("예", "아니오", "일부")
                and dp.situation(d, "S_ci_warm") != "예" and dp.situation(d, "S_ci_cold") != "예")

    def ok(d: dict) -> bool:
        slow = _m(d, "turns_per_min") < 4.0
        return slow if dp.situation(d, "S_check_loop") == "예" else not slow

    return _judge("check_loop_turn_rate", applies, ok,
                  lambda d: f"{'반복' if dp.situation(d, 'S_check_loop') == '예' else '반복 없음/일부'} "
                            f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def research_cap() -> tuple[str, str]:
    """H_research_cap: 양식·상한이 있는 웹 조사 조각은 넓이와 상관없이 7–14분, 80–140턴 (도중 지시·고정 입력 작업은 뺌)."""
    # 2026-10-19 검사 고침: 문장의 '웹 조사' 조건(S_web=예)을 처음 검사가 빠뜨렸다
    def applies(d: dict) -> bool:
        return (_default_setup(d) and dp.situation(d, "S_research") == "예"
                and dp.situation(d, "S_web") == "예"
                and dp.situation(d, "S_mid_notes") != "예"
                and dp.situation(d, "S_fixed_input") != "예"
                and _m(d, "minutes") is not None and _m(d, "turns") is not None)

    def ok(d: dict) -> bool:
        return 7.0 <= _m(d, "minutes") <= 14.0 and 80 <= _m(d, "turns") <= 140

    return _judge("research_cap", applies, ok,
                  lambda d: f"{_m(d, 'minutes'):.1f}분 {int(_m(d, 'turns'))}턴")


def sonnet_max_rate() -> tuple[str, str]:
    """H_sonnet_max_rate: Sonnet max로 도는 도구 작업(외부 확인이 있는 파일 편집; 순수 추론 풀이는 뺌)은 분당 6.5–9.5턴(Opus high 2.5–6.5보다 빠르다)."""
    def applies(d: dict) -> bool:
        return (dp.situation(d, "S_other_model") == "예" and "Sonnet" in str(d.get("task", ""))
                and dp.situation(d, "S_external_check") == "예"
                and _m(d, "minutes") is not None and _m(d, "turns") is not None)

    def ok(d: dict) -> bool:
        return 6.5 <= _m(d, "turns_per_min") <= 9.5

    return _judge("sonnet_max_rate", applies, ok,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def model_mult_shape() -> tuple[str, str]:
    """H_model_mult_shape: Opus가 아닌 모델의 읽고 쓰는 문서 작업(확인 실행 없음, 고정 입력 아님)은 분당 2.5–5.5턴으로 Opus와 같은 속도다."""
    def applies(d: dict) -> bool:
        return (dp.situation(d, "S_other_model") == "예"
                and dp.situation(d, "S_external_check") == "아니오"
                and dp.situation(d, "S_fixed_input") != "예"
                and _m(d, "minutes") is not None and _m(d, "turns") is not None)

    def ok(d: dict) -> bool:
        return 2.5 <= _m(d, "turns_per_min") <= 5.5

    return _judge("model_mult_shape", applies, ok,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def given_design_rate() -> tuple[str, str]:
    """H_given_design_rate: 원인·설계가 적힌 작은 고침(S_short=예, S_spec_fixed=예/일부, 외부 확인, 짧은 바퀴, 렌더 없음, 첫 회차)은 분당 5.5–8.5턴."""
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_spec_fixed") in ("예", "일부")
                and dp.situation(d, "S_short") == "예"
                and dp.situation(d, "S_external_check") == "예"
                and dp.situation(d, "S_long_lap") != "예"
                and dp.situation(d, "S_render") != "예"
                and dp.situation(d, "S_resumed") != "예"
                and dp.situation(d, "S_web") != "예")

    return _judge("given_design_rate", applies,
                  lambda d: 5.5 <= _m(d, "turns_per_min") <= 8.5,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def given_design_rate2() -> tuple[str, str]:
    """H_given_design_rate2: 원인·설계·글이 전부 적힌 작은 고침(S_short=예, S_spec_fixed=예, 외부 확인, 짧은 바퀴, 렌더 없음, 첫 회차)은 분당 5.5–8.5턴. 말을 쓰는 작업(일부)은 뺀다."""
    def applies(d: dict) -> bool:
        return (_m(d, "turns_per_min") is not None and _default_setup(d)
                and dp.situation(d, "S_spec_fixed") == "예"
                and dp.situation(d, "S_short") == "예"
                and dp.situation(d, "S_external_check") == "예"
                and dp.situation(d, "S_long_lap") != "예"
                and dp.situation(d, "S_render") != "예"
                and dp.situation(d, "S_resumed") != "예"
                and dp.situation(d, "S_web") != "예")

    return _judge("given_design_rate2", applies,
                  lambda d: 5.5 <= _m(d, "turns_per_min") <= 8.5,
                  lambda d: f"분당 {_m(d, 'turns_per_min'):.1f}턴")


def _upper(bounds: list[float]) -> float | None:
    return bounds[1] if bounds and len(bounds) > 1 and bounds[1] else None


def mid_notes_bounded() -> tuple[str, str]:
    """H_mid_notes2: 도중 지시를 받은 작업도 보내기 전 예측 분의 상한 ×1.25 안에서 끝난다."""
    def applies(d: dict) -> bool:
        return (dp.situation(d, "S_mid_notes") == "예" and _m(d, "minutes") is not None
                and _upper(d["predicted"].get("minutes", [])) is not None)

    def ratio(d: dict) -> float:
        return _m(d, "minutes") / _upper(d["predicted"]["minutes"])

    return _judge("mid_notes_bounded", applies, lambda d: ratio(d) <= 1.25,
                  lambda d: f"상한의 {ratio(d):.2f}배")


def sonnet_fixed_floor() -> tuple[str, str]:
    """H_sonnet_floor: Sonnet max의 고정 입력 순수 추론(첫 회차)은 입력 크기와 상관없이 13–28분."""
    def applies(d: dict) -> bool:
        return (dp.situation(d, "S_other_model") == "예" and "Sonnet" in str(d.get("task", ""))
                and dp.situation(d, "S_fixed_input") == "예" and dp.situation(d, "S_resumed") != "예"
                and _m(d, "minutes") is not None)

    return _judge("sonnet_fixed_floor", applies, lambda d: 13.0 <= _m(d, "minutes") <= 28.0,
                  lambda d: f"{_m(d, 'minutes'):.1f}분")


def fixed_input_opus() -> tuple[str, str]:
    """H_fixed_input_opus: Opus high의 고정 입력 순수 추론은 1–7분, 5–20턴 (한 번 읽고 한 번 쓴다)."""
    def applies(d: dict) -> bool:
        return (_default_setup(d) and dp.situation(d, "S_fixed_input") == "예"
                and _m(d, "minutes") is not None and _m(d, "turns") is not None)

    return _judge("fixed_input_opus", applies,
                  lambda d: 1.0 <= _m(d, "minutes") <= 7.0 and 5 <= _m(d, "turns") <= 20,
                  lambda d: f"{_m(d, 'minutes'):.1f}분 {int(_m(d, 'turns'))}턴")


def fix_context() -> tuple[str, str]:
    """H_ctx_fix: Opus high 첫 회차의 고치는 작업(S_fix_existing=예)은 길이와 상관없이 턴당 맥락 13–25만."""
    def applies(d: dict) -> bool:
        return (_default_setup(d) and dp.situation(d, "S_fix_existing") == "예"
                and dp.situation(d, "S_resumed") != "예" and _m(d, "ctx_per_turn_k") is not None)

    return _judge("fix_context", applies, lambda d: 130 <= _m(d, "ctx_per_turn_k") <= 250,
                  lambda d: f"{int(_m(d, 'turns'))}턴 {_m(d, 'ctx_per_turn_k') / 10:.1f}만")


def _analog(d: dict) -> dict | None:
    """빗댄 기록(끝까지 한 것). predicted.analog가 먼저, 없으면 사후에 읽은 PAST_ANALOG."""
    ref = d["predicted"].get("analog") or PAST_ANALOG.get(d["id"])
    if isinstance(ref, list):
        ref = ref[0] if ref else None
    found = [o for o in dp.load() if o["id"] == ref and dp.done(o)]
    return found[0] if found else None


def _analog_ratio(d: dict) -> float:
    return _m(d, "minutes") / _analog(d)["actual"]["minutes"]


def settled_integration() -> tuple[str, str]:
    """H_settled_integration: 통합에서 열린 것이 없으면(S_open_seams=아니오) 전례 통합 분의 ×0.6–0.9, 남아 있으면 ×1.0 이상."""
    def applies(d: dict) -> bool:
        return (_default_setup(d) and dp.situation(d, "S_open_seams") in ("예", "아니오")
                and _m(d, "minutes") is not None and _analog(d) is not None)

    def ok(d: dict) -> bool:
        r = _analog_ratio(d)
        return 0.6 <= r <= 0.9 if dp.situation(d, "S_open_seams") == "아니오" else r >= 1.0

    return _judge("settled_integration", applies, ok,
                  lambda d: f"열린 것 {dp.situation(d, 'S_open_seams')}, {_analog(d)['id']}의 분 ×{_analog_ratio(d):.2f}")


def build_tools_minutes() -> tuple[str, str]:
    """H_build_tools: 확인 도구를 새로 만드는 작업(S_build_tools=예)은 도구 없이 같은 종류를 한 전례 분의 ×1.3–1.7."""
    def applies(d: dict) -> bool:
        if not (_default_setup(d) and dp.situation(d, "S_build_tools") == "예" and _m(d, "minutes") is not None):
            return False
        a = _analog(d)
        return a is not None and dp.situation(a, "S_build_tools") != "예"

    return _judge("build_tools_minutes", applies, lambda d: 1.3 <= _analog_ratio(d) <= 1.7,
                  lambda d: f"{_analog(d)['id']}의 분 ×{_analog_ratio(d):.2f}")


def doc_spec_minutes() -> tuple[str, str]:
    """H_doc_spec_minutes: 설계가 정해진 문서 쓰기(Opus high, 긴 글, 외부 확인 없음, 첫 회차)는 18–45분."""
    def applies(d: dict) -> bool:
        return (_default_setup(d) and dp.situation(d, "S_long_doc") == "예"
                and dp.situation(d, "S_external_check") != "예" and dp.situation(d, "S_resumed") != "예"
                and dp.situation(d, "S_spec_fixed") in ("예", "일부") and dp.situation(d, "S_web") != "예"
                and _m(d, "minutes") is not None)

    return _judge("doc_spec_minutes", applies, lambda d: 18.0 <= _m(d, "minutes") <= 45.0,
                  lambda d: f"{_m(d, 'minutes'):.1f}분")


def _used(rule_id: str, metric: str) -> tuple[str, str]:
    """rule_id를 쓴 예측(보내기 전에 적은 끝난 기록)이 실측과 맞았나. metric: minutes / turns / tokens."""
    rows = []
    for d in dp.load():
        p = d["predicted"]
        if rule_id not in p.get("rules", []) or not dp.done(d) or not p.get("written_before", True):
            continue
        m = dp.measures(d)
        if metric == "tokens":
            if p.get("tokens_m"):
                hit, want = dp.in_range(m["tokens_m"], p["tokens_m"]), f"{dp._bounds(p['tokens_m'])}M"
            elif p.get("tokens_class") and m["tokens_m"] is not None:
                hit, want = dp.token_class(m["tokens_m"]) in p["tokens_class"], "–".join(p["tokens_class"])
            else:
                continue
            got = f"{m['tokens_m']:.1f}M"
        else:
            bounds = p.get(metric, [])
            hit = dp.in_range(m[metric], bounds)
            if hit is None:
                continue
            want, got = dp._bounds(bounds), f"{m[metric]:g}"
        extra = ""
        if metric == "minutes":
            extra = f" [{dp.zone_verdict(d)}]"  # 세 마디 구간으로는
        rows.append((d, hit, f"{d['id']} {got} (예측 {want}){extra}{'' if hit else ' ✗'}"))
    blamed = [d["id"] for d in dp.load() if rule_id in d.get("review", {}).get("wrong", [])]
    word = {"minutes": "분 범위", "turns": "턴 범위", "tokens": "토큰 범위"}[metric]
    detail = f"  쓴 예측: {', '.join(r[2] for r in rows) or '없음'}\n  돌아보기에서 틀린 조각으로 짚힘: {', '.join(blamed) or '없음'}"
    if metric == "minutes" and rows:
        zone_hits = sum(dp.zone_verdict(d) == "맞음" for d, _, _ in rows)
        detail += f"\n  세 마디 구간으로는 {len(rows)}건 중 {zone_hits}건 맞음"
    if not rows:
        return "시험 전 (이 규칙을 쓴 끝난 예측이 없음)", detail
    hits = sum(hit for _, hit, _ in rows)
    verdict = "지지됨" if hits / len(rows) >= NEED else "반박됨"
    return f"{verdict} (쓴 예측 {len(rows)}건 중 {word} {hits}건 맞음)", detail


def used_minutes(rule_id: str) -> tuple[str, str]:
    return _used(rule_id, "minutes")


def used_turns(rule_id: str) -> tuple[str, str]:
    return _used(rule_id, "turns")


def used_tokens(rule_id: str) -> tuple[str, str]:
    return _used(rule_id, "tokens")


def told_zone() -> tuple[str, str]:
    """R_say_numbers_v2: 사용자에게 말한 구간(predicted.told)이 실제 구간과 맞는다."""
    rows = [d for d in dp.load() if dp.done(d) and "told" in d["predicted"]]
    if not rows:
        return "시험 전 (말한 구간을 적은 끝난 기록이 없음)", "  말한 구간: 없음"
    ok = [d for d in rows if d["predicted"]["told"] == dp.zone(d["actual"]["minutes"])]
    detail = "  말한 구간: " + ", ".join(
        f"{d['id']} {d['predicted']['told']} → {dp.zone(d['actual']['minutes'])}{'' if d in ok else ' ✗'}" for d in rows)
    verdict = "지지됨" if len(ok) / len(rows) >= NEED else "반박됨"
    return f"{verdict} (말한 {len(rows)}건 중 {len(ok)}건 맞음)", detail


CHECKS = {
    "tokens_per_minute": tokens_per_minute,
    "tokens_per_minute_by_length": tokens_per_minute_by_length,
    "turns_overestimated": turns_overestimated,
    "turns_vs_context": turns_vs_context,
    "check_loop_time": check_loop_time,
    "turn_rate_by_kind": turn_rate_by_kind,
    "mid_notes_longer": mid_notes_longer,
    "tokens_per_minute_long_only": tokens_per_minute_long_only,
    "turn_rate_non_web": turn_rate_non_web,
    "check_loop_turn_rate": check_loop_turn_rate,
    "research_cap": research_cap,
    "sonnet_max_rate": sonnet_max_rate,
    "model_mult_shape": model_mult_shape,
    "render_turn_rate": render_turn_rate,
    "long_lap_turn_rate": long_lap_turn_rate,
    "given_design_rate": given_design_rate,
    "given_design_rate2": given_design_rate2,
    "mid_notes_bounded": mid_notes_bounded,
    "sonnet_fixed_floor": sonnet_fixed_floor,
    "fixed_input_opus": fixed_input_opus,
    "fix_context": fix_context,
    "settled_integration": settled_integration,
    "build_tools_minutes": build_tools_minutes,
    "doc_spec_minutes": doc_spec_minutes,
    # 규칙에 거는 검사 (노드 id를 받는다)
    "used_minutes": used_minutes,
    "used_turns": used_turns,
    "used_tokens": used_tokens,
    "told_zone": told_zone,
}
# SEEN_UNTIL이 필요 없는 검사: 보내기 전에 적은 예측·말한 구간이 곧 세운 뒤의 시험이다
NO_CUT = ("used_minutes", "used_turns", "used_tokens", "told_zone")
