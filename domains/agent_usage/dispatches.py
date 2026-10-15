"""하위 에이전트 작업 기록(dispatches.toml)을 읽고, 예측이 맞았는지 계산한다.

사용법 (저장소 루트):
  python -m domains.agent_usage.dispatches     기록 검사 + 예측·실측 비교표

기록은 보낸 순서대로 이어 쓴다. 가설 검사(checks.py)는 이 순서로 '가설을 세운 뒤의 기록'을 고른다.
"""
from __future__ import annotations

import sys
import tomllib
from collections import Counter
from pathlib import Path

from proviso import schema

HERE = Path(__file__).resolve().parent
TIME_CLASSES = ("S", "M", "L", "XL")
TOKEN_CLASSES = ("T1", "T2", "T3", "T4")
SITUATION_VALUES = ("예", "아니오", "일부", "모름")
STATUSES = ("done", "stopped", "unknown")


def time_class(minutes: float) -> str:
    """S ≤ 20분 · M 20–45분 · L 45–90분 · XL > 90분"""
    for name, upper in zip(TIME_CLASSES, (20, 45, 90)):
        if minutes <= upper:
            return name
    return "XL"


def token_class(tokens_m: float) -> str:
    """T1 < 20M · T2 20–60M · T3 60–120M · T4 > 120M"""
    for name, upper in zip(TOKEN_CLASSES, (20, 60, 120)):
        if tokens_m < upper:
            return name
    return "T4"


def judge(predicted: list[str], actual: str | None, order: tuple[str, ...]) -> str:
    """예측 등급(범위면 여러 개)과 실제 등급을 비교한다."""
    if actual is None or not predicted:
        return "모름"
    if actual in predicted:
        return "맞음"
    highest = max(order.index(p) for p in predicted)
    return "낮게 잡음" if order.index(actual) > highest else "높게 잡음"


def load(path: Path = HERE / "dispatches.toml") -> list[dict]:
    return tomllib.loads(path.read_text(encoding="utf-8")).get("dispatch", [])


def done(d: dict) -> bool:
    """끝까지 한 작업만 판정에 쓴다."""
    return d.get("actual", {}).get("status", "done") == "done"


def situation(d: dict, state_id: str) -> str:
    return d.get("situation", {}).get(state_id, "모름")


def midpoint(bounds: list[float]) -> float | None:
    """[하한, 상한]의 가운데. 하한만 있으면("이상") 하한."""
    if not bounds:
        return None
    return bounds[0] if len(bounds) == 1 else (bounds[0] + bounds[1]) / 2


def measures(d: dict) -> dict:
    """실측 숫자와 거기서 계산한 값. 없으면 None."""
    a = d.get("actual", {})
    minutes, turns, tokens = a.get("minutes"), a.get("turns"), a.get("tokens_m")
    return {
        "minutes": minutes,
        "turns": turns,
        "tokens_m": tokens,
        "tokens_per_min": tokens / minutes if tokens and minutes else None,
        "ctx_per_turn_k": tokens * 1000 / turns if tokens and turns else None,
        "turns_per_min": turns / minutes if turns and minutes else None,
    }


def validate(records: list[dict], kn: schema.Knowledge) -> list[str]:
    """기록의 문제 목록. 규칙·상태·가설 id는 지식 파일에 있어야 한다."""
    errors, seen = [], set()

    def expect(did: str, ref: str, kind: str) -> None:
        node = kn.nodes.get(ref)
        if node is None or node.kind != kind:
            errors.append(f"{did}: '{ref}'는 지식 파일에 있는 {schema.KIND_LABEL[kind]}이 아님")

    for d in records:
        did = d.get("id", "?")
        if did in seen:
            errors.append(f"id 중복: {did}")
        seen.add(did)
        for key in ("project", "batch", "date", "task", "predicted", "actual"):
            if key not in d:
                errors.append(f"{did}: '{key}' 칸이 비어 있음")
        p = d.get("predicted", {})
        for cls in p.get("time_class", []):
            if cls not in TIME_CLASSES:
                errors.append(f"{did}: 시간 등급 '{cls}'는 {TIME_CLASSES} 중 하나여야 함")
        for cls in p.get("tokens_class", []):
            if cls not in TOKEN_CLASSES:
                errors.append(f"{did}: 토큰 등급 '{cls}'는 {TOKEN_CLASSES} 중 하나여야 함")
        for rid in p.get("rules", []):
            expect(did, rid, "rule")
        for sid, value in d.get("situation", {}).items():
            expect(did, sid, "state")
            if value not in SITUATION_VALUES:
                errors.append(f"{did}.{sid}: 값은 {SITUATION_VALUES} 중 하나여야 함")
        for hid in d.get("review", {}).get("hypotheses", []):
            expect(did, hid, "hypothesis")
        status = d.get("actual", {}).get("status", "done")
        if status not in STATUSES:
            errors.append(f"{did}: actual.status는 {STATUSES} 중 하나여야 함")
        if done(d) and "minutes" not in d.get("actual", {}):
            errors.append(f"{did}: 끝난 작업인데 실측 시간이 없음")
    return errors


def _num(value: float | None, fmt: str, unit: str = "") -> str:
    return "–" if value is None else format(value, fmt) + unit


def report(records: list[dict]) -> str:
    """예측·실측 비교표와 맞음/빗나감 집계."""
    head = ("| id | 배치 | 예측 시간 | 실제 | 판정 | 예측 토큰 | 실제 | 판정 | 턴 | 분당 토큰 | 턴당 맥락 |\n"
            "|---|--:|---|---|---|---|---|---|--:|--:|--:|")
    lines = [head]
    counts = {"시간": Counter(), "토큰": Counter()}
    before = {"시간": Counter(), "토큰": Counter()}
    for d in records:
        p = d["predicted"]
        want_t, want_k = "–".join(p.get("time_class", [])), "–".join(p.get("tokens_class", []))
        if not done(d):
            lines.append(f"| {d['id']} | {d['batch']} | {want_t} | 판정에서 뺌 ({d['actual'].get('status')}) "
                         f"| | {want_k} | | | | | |")
            continue
        m = measures(d)
        got_t = time_class(m["minutes"])
        got_k = token_class(m["tokens_m"]) if m["tokens_m"] is not None else None
        judged = {"시간": judge(p.get("time_class", []), got_t, TIME_CLASSES),
                  "토큰": judge(p.get("tokens_class", []), got_k, TOKEN_CLASSES)}
        for what, verdict in judged.items():
            counts[what][verdict] += 1
            if p.get("written_before", True):
                before[what][verdict] += 1
        lines.append(
            f"| {d['id']} | {d['batch']} | {want_t} | {m['minutes']}분 ({got_t}) | {judged['시간']} "
            f"| {want_k} | {_num(m['tokens_m'], '.1f', 'M')} ({got_k or '–'}) | {judged['토큰']} "
            f"| {m['turns'] or '–'} | {_num(m['tokens_per_min'], '.2f', 'M')} | {_num(m['ctx_per_turn_k'], '.0f', 'k')} |"
        )

    def tally(c: Counter) -> str:
        return ", ".join(f"{k} {c[k]}" for k in ("맞음", "낮게 잡음", "높게 잡음", "모름") if c[k])

    lines.append("")
    for what in ("시간", "토큰"):
        lines.append(f"{what} 등급 — 전체: {tally(counts[what])} · 보내기 전에 적은 것만: {tally(before[what])}")
    return "\n".join(lines)


def main() -> int:
    records = load()
    kn = schema.load(HERE / "knowledge.toml")
    errors = validate(records, kn)
    if errors:
        print("기록에 문제 있음:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"기록 문제 없음 ({len(records)}건)\n")
    print(report(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
