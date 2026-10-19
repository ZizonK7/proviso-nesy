"""하위 에이전트 작업 기록(dispatches.toml)을 읽고, 예측이 맞았는지 계산한다.

사용법 (저장소 루트):
  python -m domains.agent_usage.dispatches     기록 검사 + 예측·실측 비교표 (시간은 세 마디 구간)

기록은 보낸 순서대로 이어 쓴다. 가설 검사(checks.py)는 이 순서로 '가설을 세운 뒤의 기록'을 고른다.
"""
from __future__ import annotations

import sys
import tomllib
from collections import Counter
from pathlib import Path

from proviso import schema

HERE = Path(__file__).resolve().parent

# 시간 구간 세 마디 (사용자 결정 2026-10-19): 사용자가 할 일로 말한다.
#   잠깐 ≤ 10분 "잠깐 기다려" · 다른 일 10–40분 "다른 거 하고 있어" · 신경 끄기 > 40분 "신경 쓰지 말고 있어"
ZONES = ("잠깐", "다른 일", "신경 끄기")
ZONE_EDGES = (10, 40)
ZONE_SAY = {"잠깐": "잠깐 기다려", "다른 일": "다른 거 하고 있어", "신경 끄기": "신경 쓰지 말고 있어"}
OLD_TIME_CLASSES = ("S", "M", "L", "XL")  # 2026-10-19 전의 시간 등급. 옛 기록의 time_class 칸에만 남는다
TOKEN_CLASSES = ("T1", "T2", "T3", "T4")
SITUATION_VALUES = ("예", "아니오", "일부", "모름")
STATUSES = ("done", "stopped", "unknown")
# 돌아보기의 '틀린 조각' 갈래: 조건 흐림 → 쪼갠다 / 이유 틀림 → 새 버전 / 바깥 상황 → 예외
WHY = ("조건 흐림", "이유 틀림", "바깥 상황")
# 이 기록 다음부터(파일 순서) 시간 구간이 빗나가면 review.wrong·review.why가 필수다 (2026-10-19 결정 뒤의 기록)
WRONG_REQUIRED_AFTER = "p03"


def zone(minutes: float) -> str:
    """실제 분의 구간. 잠깐 ≤ 10 · 다른 일 10–40 · 신경 끄기 > 40"""
    for name, upper in zip(ZONES, ZONE_EDGES):
        if minutes <= upper:
            return name
    return ZONES[-1]


def zones_of(bounds: list[float]) -> list[str]:
    """예측 분 범위가 덮는 구간들. 아래 끝이 경계값과 같으면 위 구간에서 시작한다([10, 20] → 다른 일만).
    하나만 있으면 '이상'이라 맨 위 구간까지 덮는다."""
    if not bounds:
        return []
    lo = bounds[0]
    hi = bounds[1] if len(bounds) > 1 else float("inf")
    first = ZONES.index(zone(hi)) if lo == hi else next(i for i, e in enumerate(ZONE_EDGES + (float("inf"),)) if lo < e)
    return list(ZONES[first: ZONES.index(zone(hi)) + 1])


def token_class(tokens_m: float) -> str:
    """T1 < 20M · T2 20–60M · T3 60–120M · T4 > 120M"""
    for name, upper in zip(TOKEN_CLASSES, (20, 60, 120)):
        if tokens_m < upper:
            return name
    return "T4"


def judge(predicted: list[str], actual: str | None, order: tuple[str, ...]) -> str:
    """예측 등급·구간(범위면 여러 개)과 실제를 비교한다."""
    if actual is None or not predicted:
        return "모름"
    if actual in predicted:
        return "맞음"
    highest = max(order.index(p) for p in predicted)
    return "낮게 잡음" if order.index(actual) > highest else "높게 잡음"


def in_range(value: float | None, bounds: list[float]) -> bool | None:
    """실측이 [하한, 상한] 안인가. 하나만 있으면 '이상'. 모르면 None."""
    if value is None or not bounds:
        return None
    return bounds[0] <= value <= (bounds[1] if len(bounds) > 1 else float("inf"))


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


def zone_verdict(d: dict) -> str | None:
    """예측 분 범위의 구간과 실제 구간 비교: 맞음 / 낮게 잡음 / 높게 잡음. 분 범위가 없으면 None."""
    want = zones_of(d["predicted"].get("minutes", []))
    if not want or measures(d)["minutes"] is None:
        return None
    return judge(want, zone(measures(d)["minutes"]), ZONES)


def wrong_required(records: list[dict], d: dict) -> bool:
    """2026-10-19 결정 뒤의 끝난 기록이 시간 구간을 빗나갔나 (그러면 review.wrong·why 필수).
    사용자에게 말한 구간(told)과 실제 구간이 다르면 예측 범위 안이라도 빗나간 것으로 본다(사용자가 받는 것은 told)."""
    order = [r.get("id") for r in records]
    if WRONG_REQUIRED_AFTER not in order or d.get("id") not in order:
        return False
    after = order.index(d["id"]) > order.index(WRONG_REQUIRED_AFTER)
    if not (after and done(d)):
        return False
    told, minutes = d.get("predicted", {}).get("told"), d.get("actual", {}).get("minutes")
    if told and minutes is not None and zone(minutes) != told:
        return True
    return zone_verdict(d) not in (None, "맞음")


def validate(records: list[dict], kn: schema.Knowledge) -> list[str]:
    """기록의 문제 목록. 규칙·상태·가설 id는 지식 파일에 있어야 한다."""
    errors, seen = [], set()

    def expect(did: str, ref: str, kinds: tuple[str, ...]) -> None:
        node = kn.nodes.get(ref)
        if node is None or node.kind not in kinds:
            names = "·".join(schema.KIND_LABEL[k] for k in kinds)
            errors.append(f"{did}: '{ref}'는 지식 파일에 있는 {names}이 아님")

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
            if cls not in OLD_TIME_CLASSES:
                errors.append(f"{did}: 옛 시간 등급 '{cls}'는 {OLD_TIME_CLASSES} 중 하나여야 함")
        if "told" in p and p["told"] not in ZONES:
            errors.append(f"{did}: predicted.told는 {ZONES} 중 하나여야 함")
        for cls in p.get("tokens_class", []):
            if cls not in TOKEN_CLASSES:
                errors.append(f"{did}: 토큰 등급 '{cls}'는 {TOKEN_CLASSES} 중 하나여야 함")
        for rid in p.get("rules", []):
            expect(did, rid, ("rule",))
        for sid, value in d.get("situation", {}).items():
            expect(did, sid, ("state",))
            if value not in SITUATION_VALUES:
                errors.append(f"{did}.{sid}: 값은 {SITUATION_VALUES} 중 하나여야 함")
        review = d.get("review", {})
        for hid in review.get("hypotheses", []):
            expect(did, hid, ("hypothesis",))
        for wid in review.get("wrong", []):
            expect(did, wid, ("rule", "hypothesis", "state"))
        if "why" in review and review["why"] not in WHY:
            errors.append(f"{did}: review.why는 {WHY} 중 하나여야 함")
        if wrong_required(records, d) and not (review.get("wrong") and review.get("why")):
            errors.append(f"{did}: 시간 구간이 빗나갔는데 review.wrong(틀린 조각 id)과 review.why({'/'.join(WHY)})가 없음")
        status = d.get("actual", {}).get("status", "done")
        if status not in STATUSES:
            errors.append(f"{did}: actual.status는 {STATUSES} 중 하나여야 함")
        if done(d) and "minutes" not in d.get("actual", {}):
            errors.append(f"{did}: 끝난 작업인데 실측 시간이 없음")
    return errors


def _num(value: float | None, fmt: str, unit: str = "") -> str:
    return "–" if value is None else format(value, fmt) + unit


def _bounds(b: list[float]) -> str:
    return "–" if not b else (f"{b[0]:g}–{b[1]:g}" if len(b) > 1 else f"{b[0]:g}+")


def miss_split(d: dict) -> tuple[str, str] | None:
    """분이 범위를 빗나간 기록을 기계적으로 가른다: (방향, 갈래). 빗나가지 않았으면 None.
    턴이 범위 안이었으면 '속도'(분당 턴 조각 탓), 밖이었으면 '양'(턴 수 조각 탓), 턴 예측이 없으면 '턴 예측 없음'."""
    p, m = d["predicted"], measures(d)
    hit = in_range(m["minutes"], p.get("minutes", []))
    if hit is None or hit:
        return None
    direction = "아래" if m["minutes"] < p["minutes"][0] else "위"
    turns_hit = in_range(m["turns"], p.get("turns", []))
    branch = "턴 예측 없음" if turns_hit is None else ("속도" if turns_hit else "양")
    return direction, branch


def rescore(records: list[dict]) -> dict:
    """끝난 기록을 새 시간 구간으로 다시 채점한 집계. 기록 파일은 건드리지 않는다."""
    out = {"판정": Counter(), "보내기 전": Counter(), "구간별": {z: Counter() for z in ZONES},
           "걸침": Counter(), "걸침 기록": [], "분 범위 없음": [], "말한 구간": Counter(),
           "분 빗나감": Counter(), "분 범위": Counter(), "양 반대 방향": []}
    for d in records:
        if not done(d):
            continue
        p, m = d["predicted"], measures(d)
        want = zones_of(p.get("minutes", []))
        if not want:
            out["분 범위 없음"].append(d["id"])
            continue
        got = zone(m["minutes"])
        verdict = judge(want, got, ZONES)
        out["판정"][verdict] += 1
        if p.get("written_before", True):
            out["보내기 전"][verdict] += 1
        if len(want) == 1:
            out["구간별"][want[0]][verdict] += 1
        else:
            fell = ("긴 쪽" if got == want[-1] else "짧은 쪽" if got == want[0] else
                    "가운데" if got in want else "밖")
            out["걸침"][fell] += 1
            out["걸침 기록"].append(f"{d['id']} {'/'.join(want)} → {got}")
        if "told" in p:
            out["말한 구간"]["맞음" if p["told"] == got else "빗나감"] += 1
        out["분 범위"]["맞음" if in_range(m["minutes"], p["minutes"]) else "빗나감"] += 1
        split = miss_split(d)
        if split:
            out["분 빗나감"][split] += 1
            if split[1] == "양" and (m["turns"] < p["turns"][0]) != (split[0] == "아래"):
                out["양 반대 방향"].append(d["id"])
    return out


def _tally(c: Counter) -> str:
    return ", ".join(f"{k} {c[k]}" for k in ("맞음", "낮게 잡음", "높게 잡음", "모름") if c[k]) or "없음"


def report(records: list[dict]) -> str:
    """예측·실측 비교표와 맞음/빗나감 집계. 시간은 세 마디 구간으로 (분 숫자로 다시 채점)."""
    head = ("| id | 배치 | 예측 분 | 예측 구간 | 말한 구간 | 실제 | 판정 | 예측 토큰 | 실제 | 판정 | 턴 | 분당 토큰 | 턴당 맥락 |\n"
            "|---|--:|---|---|---|---|---|---|---|---|--:|--:|--:|")
    lines = [head]
    tokens, tokens_before = Counter(), Counter()
    for d in records:
        p = d["predicted"]
        want_m, want_z = _bounds(p.get("minutes", [])), "/".join(zones_of(p.get("minutes", []))) or "–"
        told, want_k = p.get("told", "–"), "–".join(p.get("tokens_class", []))
        if not done(d):
            lines.append(f"| {d['id']} | {d['batch']} | {want_m} | {want_z} | {told} | 판정에서 뺌 "
                         f"({d['actual'].get('status')}) | | {want_k} | | | | | |")
            continue
        m = measures(d)
        got_k = token_class(m["tokens_m"]) if m["tokens_m"] is not None else None
        judged_k = judge(p.get("tokens_class", []), got_k, TOKEN_CLASSES)
        tokens[judged_k] += 1
        if p.get("written_before", True):
            tokens_before[judged_k] += 1
        lines.append(
            f"| {d['id']} | {d['batch']} | {want_m} | {want_z} | {told} | {m['minutes']}분 ({zone(m['minutes'])}) "
            f"| {zone_verdict(d) or '판정에서 뺌 (분 범위 없음)'} "
            f"| {want_k} | {_num(m['tokens_m'], '.1f', 'M')} ({got_k or '–'}) | {judged_k} "
            f"| {m['turns'] or '–'} | {_num(m['tokens_per_min'], '.2f', 'M')} | {_num(m['ctx_per_turn_k'], '.0f', 'k')} |"
        )
    r = rescore(records)
    n = sum(r["판정"].values())
    lines += ["", f"시간 구간 (잠깐 ≤10분 · 다른 일 10–40분 · 신경 끄기 >40분), 분 숫자로 다시 채점한 {n}건",
              f"  전체: {_tally(r['판정'])} · 보내기 전에 적은 것만: {_tally(r['보내기 전'])}"]
    for z in ZONES:
        c = r["구간별"][z]
        lines.append(f"  예측이 '{z}' 하나: {sum(c.values())}건 — {_tally(c)}")
    span = r["걸침"]
    lines.append(f"  걸침(두 구간 이상): {sum(span.values())}건 — 실제 낙하: "
                 + (", ".join(f"{k} {span[k]}" for k in ("짧은 쪽", "가운데", "긴 쪽", "밖") if span[k]) or "없음")
                 + " (긴 쪽으로 말했다면 맞은 것은 '긴 쪽')")
    lines.append(f"  분 범위가 없어 뺀 기록 {len(r['분 범위 없음'])}건: {', '.join(r['분 범위 없음']) or '없음'}")
    lines.append(f"  말한 구간(predicted.told)이 있는 끝난 기록: {sum(r['말한 구간'].values())}건"
                 + (f" — 맞음 {r['말한 구간']['맞음']}, 빗나감 {r['말한 구간']['빗나감']}" if r["말한 구간"] else ""))
    lines.append(f"분 범위 적중(숫자 그대로): 맞음 {r['분 범위']['맞음']}, 빗나감 {r['분 범위']['빗나감']}")
    miss = r["분 빗나감"]
    lines.append("분 빗나감의 갈래 (턴 범위가 맞았으면 속도 조각 탓, 틀렸으면 양 조각 탓):")
    lines.append("| 분 | 속도 | 양 | 턴 예측 없음 | 계 |\n|---|--:|--:|--:|--:|")
    for direction in ("아래", "위"):
        row = [miss[(direction, b)] for b in ("속도", "양", "턴 예측 없음")]
        lines.append(f"| 실제가 범위 {direction} | {' | '.join(map(str, row))} | {sum(row)} |")
    lines.append(f"  '양' 중 턴이 분과 반대로 빗나간 기록(속도도 틀림): {', '.join(r['양 반대 방향']) or '없음'}")
    lines.append(f"토큰 등급 — 전체: {_tally(tokens)} · 보내기 전에 적은 것만: {_tally(tokens_before)}")
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
