"""agent_usage 가설 검사. knowledge.toml의 hypothesis.check 이름으로 찾는다.

판정은 실측 기록(dispatches.toml)으로 한다. 가설은 **세운 뒤에 나온 기록으로만** 시험한다.
세울 때 이미 본 기록은 '맞춰 본 것'(사후 설명)이라 따로 보여 주기만 한다.
판정: "지지됨" / "반박됨" (시험 기록의 80% 이상이 맞으면 지지됨) / "시험 전" (세운 뒤 기록이 아직 없음).
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
}
NEED = 0.8

# 토큰 규칙이 가정한 턴당 맥락(천 토큰). turns_vs_context가 '맥락을 작게 잡았는지' 볼 때 쓴다.
ASSUMED_CTX_K = {"R_tok_v2": 250, "R_tok_v3": 370, "R_tok_long": 350, "R_tok_short": 120}


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


CHECKS = {
    "tokens_per_minute": tokens_per_minute,
    "tokens_per_minute_by_length": tokens_per_minute_by_length,
    "turns_overestimated": turns_overestimated,
    "turns_vs_context": turns_vs_context,
    "check_loop_time": check_loop_time,
    "turn_rate_by_kind": turn_rate_by_kind,
    "mid_notes_longer": mid_notes_longer,
}
