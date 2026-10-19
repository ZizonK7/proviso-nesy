"""비문학 기반 게임 가설 검사. knowledge.toml의 hypothesis.check 이름으로 찾는다.

판정은 게임 기록(games.toml)으로 한다. 가설은 **세운 뒤에 덧붙인 기록으로만** 시험한다(agent_usage와 같은 방식).
세울 때 본 기록은 '맞춰 본 것'(사후 설명)이라 따로 보여 주기만 한다.
판정: "지지됨" / "반박됨" (시험 기록의 80% 이상이 맞으면 지지됨) / "시험 전" (세운 뒤 기록이 아직 없음).
반응이 "모름"인 기록은 잘 됐는지를 묻는 가설에서 뺀다.
"""
from __future__ import annotations

from collections.abc import Callable

from . import games as gm

# 가설을 세울 때 본 마지막 기록. 그다음 기록부터가 시험이다.
SEEN_UNTIL = {
    "kind_transfer": "g_wukong",  # 2026-10-19 성공 쪽 첫 묶음(21건)으로 세움
    "model_success": "g_wukong",
    "named_small": "g_wukong",
    "record_people": "g_wukong",
    "one_rule_free": "g_wukong",
}
NEED = 0.8


def _yes(g: dict, state_id: str) -> bool:
    return gm.situation(g, state_id) == "예"


def _known(g: dict) -> bool:
    return gm.judgment(g) != "모름"


def _judge(name: str, applies: Callable[[dict], bool], ok: Callable[[dict], bool],
           show: Callable[[dict], str]) -> tuple[str, str]:
    records = gm.load()
    cut = [g["id"] for g in records].index(SEEN_UNTIL[name]) + 1
    pick = [(i, g) for i, g in enumerate(records) if applies(g)]
    fit, test = [g for i, g in pick if i < cut], [g for i, g in pick if i >= cut]

    def listing(rows: list[dict]) -> str:
        return ", ".join(f"{g['id']} {show(g)}{'' if ok(g) else ' ✗'}" for g in rows) or "없음"

    detail = (f"  세울 때 본 기록 (맞춰 본 것): {listing(fit)}\n"
              f"  시험 기록 ({SEEN_UNTIL[name]} 다음부터): {listing(test)}")
    if not test:
        return "시험 전", detail
    hits = sum(ok(g) for g in test)
    verdict = "지지됨" if hits / len(test) >= NEED else "반박됨"
    return f"{verdict} (시험 {len(test)}건 중 {hits}건 맞음)", detail


def kind_transfer() -> tuple[str, str]:
    """H_ng_kind_transfer: 문학은 이야기가, 비문학은 모형·데이터·기록이 넘어간다."""
    def ok(g: dict) -> bool:
        if g["basis_kind"] == "문학":
            return _yes(g, "S_src_story")
        return any(_yes(g, s) for s in ("S_src_model", "S_src_data", "S_src_record"))

    return _judge("kind_transfer", lambda g: True, ok, lambda g: g["basis_kind"])


def model_success() -> tuple[str, str]:
    """H_ng_model_success: 모형을 규칙으로 옮긴 비문학 게임은 성공 이상."""
    return _judge("model_success",
                  lambda g: g["basis_kind"] == "비문학" and _yes(g, "S_src_model") and _known(g),
                  lambda g: gm.judgment(g) in gm.SUCCESS, gm.judgment)


def named_small() -> tuple[str, str]:
    """H_ng_named_small: 이름을 내건 비문학 게임은 크게 성공하지 못한다."""
    return _judge("named_small",
                  lambda g: g["basis_kind"] == "비문학" and _yes(g, "S_named") and _known(g),
                  lambda g: gm.judgment(g) != "크게 성공", gm.judgment)


def record_people() -> tuple[str, str]:
    """H_ng_record_people: 기록 바탕 + 사람 중심이면 성공 이상."""
    return _judge("record_people",
                  lambda g: _yes(g, "S_src_record") and _yes(g, "S_people_play") and _known(g),
                  lambda g: gm.judgment(g) in gm.SUCCESS, gm.judgment)


def one_rule_free() -> tuple[str, str]:
    """H_ng_one_rule_free: 주장 하나 = 규칙 하나인 게임은 무료·짧고, 크게 성공하지 않는다."""
    def ok(g: dict) -> bool:
        return _yes(g, "S_free_short") and gm.judgment(g) != "크게 성공"

    return _judge("one_rule_free", lambda g: _yes(g, "S_one_rule"), ok,
                  lambda g: f"{gm.judgment(g)}, 무료·짧음={gm.situation(g, 'S_free_short')}")


CHECKS = {
    "kind_transfer": kind_transfer,
    "model_success": model_success,
    "named_small": named_small,
    "record_people": record_people,
    "one_rule_free": one_rule_free,
}
