"""빗댄 기록 규칙 — 정해진 일은 가장 가까운 지난 일의 시간을 따른다 (2026-11-03 사용자 결정, CLAUDE.md '빗댄 기록 규칙'). 시험 중.

사용법 (저장소 루트):
  python -m domains.agent_usage.analog             맞춘 범위와 미리 정한 시험
  python -m domains.agent_usage.analog --write     … 그리고 analog.toml의 범위·근거 칸을 seen_until까지의 기록으로 다시 쓴다
  python -m domains.agent_usage.analog <기록 id>    그 기록에서 규칙이 고른 지난 기록과 계산

AI는 지시서를 보고 정해진 질문(상태)에 답만 하고, 고르기는 기계가 한다 — 답이 같으면 누가 돌려도 같은 기록이 나온다.
- 쓸 수 있는 후보: 보낼 때 이미 끝나 있던 기록(날짜가 앞서거나, 같은 날이면 끝 시각 ≤ 이 기록의 시작 시각; 시각을 모르면
  같은 날 다른 배치이고 파일에서 앞선 것만). 시각은 기록 글의 'HH:MM:SS → HH:MM:SS'(주석이라 원문에서 읽는다).
- 반드시 같은 답(HARD, '모름'은 다른 답) → 같은 저장소 → SOFT에서 같은 답이 많은 것. 맨 앞이 동점이면 그 묶음의 실제 분의 가운데 값.
- 못 찾으면 HARD의 '모름'을 상관없음으로 두고 다시 찾는다. 그래도 없으면 모름(손 예측).
- 분 범위 = 고른 분 × 범위(analog.toml). 말할 구간은 가운데 값의 구간(dispatches.say_zone).
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from statistics import median

from . import checks
from . import dispatches as dp
from . import fit as ft
from . import holdout as ho
from . import predict as pr

HERE = Path(__file__).resolve().parent
ANALOG_TOML = HERE / "analog.toml"
TIME = re.compile(r"(\d\d:\d\d:\d\d) → (\d\d:\d\d:\d\d)")


def load_rule(path: Path = ANALOG_TOML) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def times(path: Path = HERE / "dispatches.toml") -> dict[str, tuple[str, str]]:
    """기록 id → (시작, 끝) 시각. 실측 칸의 주석에 적힌 'HH:MM:SS → HH:MM:SS'를 원문에서 읽는다(없으면 빠진다)."""
    out = {}
    for block in re.split(r"\n\[\[dispatch\]\]\n", path.read_text(encoding="utf-8")):
        rid = re.search(r'^id = "([^"]+)"', block, flags=re.M)
        t = TIME.search(block)
        if rid and t:
            out[rid.group(1)] = (t.group(1), t.group(2))
    return out


def _v(d: dict, k: str) -> str:
    return d.get("situation", {}).get(k, "모름")


def available(c: dict, d: dict, t: dict, order: dict[str, int]) -> bool:
    """후보 c가 기록 d를 보낼 때 이미 끝나 결과가 적혀 있었나."""
    if c["id"] == d["id"] or not dp.done(c) or not dp.measures(c)["minutes"]:
        return False
    cd, dd = str(c.get("date", "")), str(d.get("date", ""))
    if cd != dd:
        return cd < dd
    if c["id"] in t and d["id"] in t:
        return t[c["id"]][1] <= t[d["id"]][0]
    same_batch = c.get("batch") == d.get("batch") and c.get("project") == d.get("project")
    return not same_batch and order[c["id"]] < order[d["id"]]


def pick(d: dict, records: list[dict], rule: dict, t: dict | None = None) -> tuple[list[dict], str | None]:
    """(고른 기록 묶음, 어떻게 찾았나). 묶음은 맨 앞 열쇠가 같은 동점 기록들. 못 찾으면 ([], None)."""
    t = times() if t is None else t
    order = {r["id"]: i for i, r in enumerate(records)}
    pool = [c for c in records if available(c, d, t, order)]
    for how, wild in (("반드시 같은 답", False), ("'모름'은 상관없음", True)):
        cands = [c for c in pool if all(_v(c, k) == _v(d, k) or (wild and "모름" in (_v(c, k), _v(d, k)))
                                        for k in rule["hard"])]
        if cands:
            def key(c: dict) -> tuple:
                return (c.get("project") == d.get("project"), sum(_v(c, k) == _v(d, k) for k in rule["soft"]))
            best = max(key(c) for c in cands)
            return [c for c in cands if key(c) == best], how
    return [], None


def estimate(group: list[dict]) -> float | None:
    """동점 묶음의 실제 분의 가운데 값 (사용자 제안 '기댓값')."""
    return median(dp.measures(c)["minutes"] for c in group) if group else None


def scoped(d: dict) -> bool:
    """이 규칙이 다루는 기록: 할 일이 정해진 일(S_specified = 예)."""
    return _v(d, "S_specified") == "예"


def split(records: list[dict], cut: str) -> tuple[list[dict], list[dict]]:
    """(맞출 기록, 시험 기록): 파일 순서로 cut까지 / 그 뒤의 끝난 기록. 시험에서는 바깥 상황 예외를 뺀다."""
    ids = [d["id"] for d in records]
    i = ids.index(cut) + 1 if cut in ids else len(ids)
    return ([d for d in records[:i] if dp.done(d) and dp.measures(d)["minutes"]],
            [d for d in records[i:] if dp.done(d) and dp.measures(d)["minutes"] and not checks.is_exception(d)])


def fit_range(train: list[dict], estimates: dict[str, float], max_ratio: float) -> tuple[tuple[float, float] | None, list[str], list[str]]:
    """(범위, 맞춘 기록, 범위 안 기록) — 실측 분 ÷ 고른 분을 2배 창으로."""
    pairs = [(d["id"], dp.measures(d)["minutes"] / estimates[d["id"]]) for d in train if estimates.get(d["id"])]
    w = ft.window([r for _, r in pairs], max_ratio)
    rng = ft.rounded(w, max_ratio) if w else None
    inside = [i for i, r in pairs if rng and rng[0] * (1 - 1e-9) <= r <= rng[1] * (1 + 1e-9)]
    return rng, [i for i, _ in pairs], inside


def rule_estimates(rows: list[dict], records: list[dict], rule: dict, t: dict) -> dict[str, float]:
    out = {}
    for d in rows:
        e = estimate(pick(d, records, rule, t)[0])
        if e:
            out[d["id"]] = e
    return out


def ai_estimates(rows: list[dict], records: list[dict]) -> dict[str, float]:
    """AI가 보내기 전에 적은 빗댄 기록(predicted.analog)의 실제 분."""
    out = {}
    for d in rows:
        a = pr.analog_of(d, records)
        if a and dp.measures(a)["minutes"]:
            out[d["id"]] = dp.measures(a)["minutes"]
    return out


def zone_hits(rows: list[dict], est: dict[str, float], rng: tuple[float, float] | None) -> tuple[int, int]:
    """(말할 구간 맞음, 분 범위 맞음). 예측이 없는 기록은 틀린 것으로 센다."""
    told = mins = 0
    for d in rows:
        m = dp.measures(d)["minutes"]
        if d["id"] not in est or not rng:
            continue
        lo, hi = est[d["id"]] * rng[0], est[d["id"]] * rng[1]
        told += dp.say_zone([lo, hi]) == dp.zone(m)
        mins += lo <= m <= hi
    return told, mins


def _pct(a: int, n: int) -> str:
    return f"{a}/{n} ({100 * a / n:.0f}%)" if n else "–"


def report(records: list[dict], rule: dict, kn) -> str:
    t = times()
    max_ratio = float(kn.domain.get("max_ratio", 2))
    train, test = split(records, rule["seen_until"])
    train_s, test_s = [d for d in train if scoped(d)], [d for d in test if scoped(d)]
    rng = tuple(rule["range"]) if rule.get("range") else None
    r_est_test = rule_estimates(test_s, records, rule, t)
    a_rng, _, _ = fit_range(train_s, ai_estimates(train_s, records), max_ratio)
    a_est_test = ai_estimates(test_s, records)
    pieces = pr.live_pieces(kn)
    lines = [f"맞춘 기록: 파일 순서로 {rule['seen_until']}까지 · 시험 기록: 그 뒤 (바깥 상황 예외는 뺌)",
             f"규칙의 범위: ×{rng[0]:g}–{rng[1]:g} ({rule.get('fit', '')})" if rng else "규칙의 범위: 없음",
             f"AI가 고른 빗댄 기록의 범위(같은 기록 묶음, 맞추기 쪽으로 맞춤): ×{a_rng[0]:g}–{a_rng[1]:g}" if a_rng else "AI 범위: 없음",
             ""]
    both = [d for d in test_s if d["id"] in a_est_test]
    lines.append(f"미리 정한 시험(주) — 시험 기록 중 정해진 일이고 AI가 보내기 전에 빗댄 기록을 적은 {len(both)}건, 말할 구간 적중:")
    r_told, r_min = zone_hits(both, r_est_test, rng)
    a_told, a_min = zone_hits(both, a_est_test, a_rng)
    lines.append(f"  규칙이 고름: {_pct(r_told, len(both))} · 분 범위 {r_min}/{len(both)} · 기록을 못 찾음 {sum(d['id'] not in r_est_test for d in both)}")
    lines.append(f"  AI가 고름:   {_pct(a_told, len(both))} · 분 범위 {a_min}/{len(both)}")
    hand = [ho.hand_outcome(d) for d in both]
    calc = [pr.outcome(pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn), d) for d in both]
    lines.append(f"  손 예측(당시): {_pct(sum(o['told_hit'] is True for o in hand), len(both))} · 스위치만 계산기: "
                 f"{_pct(sum(o['told_hit'] is True for o in calc), len(both))}")
    same = sum(1 for d in both if any(c["id"] == pr.analog_of(d, records)["id"] for c in pick(d, records, rule, t)[0]))
    lines.append(f"  AI가 고른 기록이 규칙의 동점 묶음 안에 든 것: {same}/{len(both)}")
    ok = r_told >= a_told - 0.05 * len(both)
    lines.append(f"  성공 기준(돌리기 전에 정함): 규칙이 AI보다 5 %p 넘게 낮지 않다 → {'성공' if ok else '실패'}"
                 f" ({100 * r_told / len(both):.0f}% vs {100 * a_told / len(both):.0f}%)" if both else "  비교할 기록 없음")
    lines.append("")
    rt, _ = zone_hits(test_s, r_est_test, rng)
    hows = [pick(d, records, rule, t)[1] for d in test_s]
    lines.append(f"같이 보고 — 정해진 일인 시험 기록 {len(test_s)}건 전체: 규칙 {_pct(rt, len(test_s))} · 기록을 찾음 "
                 f"{sum(h is not None for h in hows)} (반드시 같은 답 {hows.count('반드시 같은 답')}, '모름' 상관없음 {hows.count(chr(39) + '모름' + chr(39) + '은 상관없음')})")
    other = [d for d in test if not scoped(d)]
    o_est = rule_estimates(other, records, rule, t)
    ot, _ = zone_hits(other, o_est, rng)
    lines.append(f"참고 — 찾는 일·섞인 일·모름인 시험 기록 {len(other)}건에 같은 규칙을 대면: {_pct(ot, len(other))}")
    return "\n".join(lines)


def show(d: dict, records: list[dict], rule: dict) -> str:
    group, how = pick(d, records, rule)
    rng = tuple(rule["range"]) if rule.get("range") else None
    if not group:
        return f"{d['id']}: 비슷한 지난 일 없음 — 손 예측"
    e = estimate(group)
    lines = [f"{d['id']}: {how}으로 찾음, 동점 {len(group)}건 — " + ", ".join(f"{c['id']} {dp.measures(c)['minutes']}분" for c in group[:8])
             + (" …" if len(group) > 8 else ""),
             f"  가운데 값 {e:g}분" + (f" × {rng[0]:g}–{rng[1]:g} → {e * rng[0]:.1f}–{e * rng[1]:.1f}분 → 말할 구간 {dp.say_zone([e * rng[0], e * rng[1]])}" if rng else "")]
    if dp.done(d) and dp.measures(d)["minutes"]:
        lines.append(f"  실측 {dp.measures(d)['minutes']}분 ({dp.zone(dp.measures(d)['minutes'])})")
    return "\n".join(lines)


def write(rule_text: str, rng: tuple[float, float] | None, matched: list[str], inside: list[str], first: str, last: str) -> str:
    head = re.sub(r"\n(range|fit) = .*", "", rule_text).rstrip() + "\n"
    if rng:
        head += f"range = [{rng[0]:g}, {rng[1]:g}]\n"
    head += (f'fit = "{first}–{last}의 정해진 일에서 맞춤: {len(inside)}/{len(matched)}건 범위 안'
             + (f" ({', '.join(inside[:6])}{' …' if len(inside) > 6 else ''})" if inside else "") + '"\n')
    return head


def main(argv: list[str]) -> int:
    kn = pr.load_kn()
    records = dp.load()
    rule = load_rule()
    if argv and not argv[0].startswith("--"):
        found = [d for d in records if d["id"] == argv[0]]
        print(show(found[0], records, rule) if found else f"기록 id가 아님: {argv[0]}")
        return 0
    max_ratio = float(kn.domain.get("max_ratio", 2))
    train, _ = split(records, rule["seen_until"])
    train_s = [d for d in train if scoped(d)]
    rng, matched, inside = fit_range(train_s, rule_estimates(train_s, records, rule, times()), max_ratio)
    if "--write" in argv:
        first, last = (train[0]["id"], train[-1]["id"]) if train else ("–", "–")
        ANALOG_TOML.write_text(write(ANALOG_TOML.read_text(encoding="utf-8"), rng, matched, inside, first, last), encoding="utf-8")
        rule = load_rule()
    if (tuple(rule["range"]) if rule.get("range") else None) != rng:
        print("주의: analog.toml의 범위가 지금 기록으로 맞춘 값과 다르다 — `python -m domains.agent_usage.analog --write`\n")
    print(report(records, rule, kn))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
