"""빗댄 기록 규칙 — 정해진 일은 가장 가까운 지난 일의 시간을 따른다 (2026-11-03 사용자 결정, CLAUDE.md '빗댄 기록 규칙'). 시험 중.

사용법 (저장소 루트):
  python -m domains.agent_usage.analog             맞춘 범위와 미리 정한 시험
  python -m domains.agent_usage.analog --write     … 그리고 analog.toml의 범위·근거 칸을 seen_until까지의 기록으로 다시 쓴다
  python -m domains.agent_usage.analog <기록 id>    그 기록에서 규칙이 고른 지난 기록과 계산
  python -m domains.agent_usage.analog <상황 파일>   기록을 덧붙이기 전에(파일이 있으면 파일이 먼저: project·date·agent·round·[situation])

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
    """기록 id → (시작, 끝) 시각. 실측 칸 actual.start/end(UTC ISO, 2026-11-04부터 필수)가 먼저이고, 없으면 옛 기록의
    주석에 적힌 'HH:MM:SS → HH:MM:SS'를 원문에서 읽는다(날짜 없는 시각 — 같은 날짜끼리만 견준다)."""
    out = {}
    text = path.read_text(encoding="utf-8")
    for block in re.split(r"\n\[\[dispatch\]\]\n", text):
        rid = re.search(r'^id = "([^"]+)"', block, flags=re.M)
        t = TIME.search(block)
        if rid and t:
            out[rid.group(1)] = (t.group(1), t.group(2))
    for d in tomllib.loads(text).get("dispatch", []):
        a = d.get("actual", {})
        if _iso(a.get("start")) and _iso(a.get("end")):
            out[d["id"]] = (a["start"], a["end"])
    return out


def _iso(x) -> bool:
    return isinstance(x, str) and len(x) == 20 and x.endswith("Z")


def _v(d: dict, k: str) -> str:
    return d.get("situation", {}).get(k, "모름")


def available(c: dict, d: dict, t: dict, order: dict[str, int]) -> bool:
    """후보 c가 기록 d를 보낼 때 이미 끝나 결과가 적혀 있었나."""
    if c["id"] == d["id"] or not dp.done(c) or not dp.measures(c)["minutes"]:
        return False
    if d["id"] not in order:  # 지금 보내는 새 기록(상황 파일): 이미 끝나 결과가 적힌 기록은 다 쓸 수 있다
        return True
    if c["id"] in t and d["id"] in t and _iso(t[c["id"]][1]) and _iso(t[d["id"]][0]):
        return t[c["id"]][1] <= t[d["id"]][0]  # 날짜까지 붙은 시각: 그대로 견준다
    cd, dd = str(c.get("date", "")), str(d.get("date", ""))
    if cd != dd:
        return cd < dd
    if c["id"] in t and d["id"] in t and not _iso(t[c["id"]][1]) and not _iso(t[d["id"]][0]):
        return t[c["id"]][1] <= t[d["id"]][0]
    same_batch = c.get("batch") == d.get("batch") and c.get("project") == d.get("project")
    return not same_batch and order[c["id"]] < order[d["id"]]


def pick(d: dict, records: list[dict], rule: dict, t: dict | None = None) -> tuple[list[dict], str | None]:
    """(고른 기록 묶음, 어떻게 찾았나). 묶음은 맨 앞 열쇠가 같은 동점 기록들. 못 찾으면 ([], None)."""
    t = times() if t is None else t
    order = {r["id"]: i for i, r in enumerate(records)}
    pool = [c for c in records if available(c, d, t, order)]
    agent, rnd = d.get("agent"), d.get("round")
    if rule.get("same_agent_first") and agent and isinstance(rnd, int) and rnd >= 2:
        prev = [c for c in pool if c.get("agent") == agent and isinstance(c.get("round"), int) and c["round"] < rnd
                and _v(c, "S_specified") == _v(d, "S_specified")]
        if prev:
            return [max(prev, key=lambda c: c["round"])], "같은 에이전트의 앞 회차"
    for how, wild in (("반드시 같은 답", False), ("'모름'은 상관없음", True)):
        cands = [c for c in pool if all(_v(c, k) == _v(d, k) or (wild and "모름" in (_v(c, k), _v(d, k)))
                                        for k in rule["hard"])]
        if cands:
            def key(c: dict) -> tuple:
                return (c.get("project") == d.get("project"), sum(_v(c, k) == _v(d, k) for k in rule["soft"]))
            best = max(key(c) for c in cands)
            return [c for c in cands if key(c) == best], how
    return [], None


def decided(group: list[dict], how: str | None, rule: dict) -> bool:
    """규칙이 혼자 답하는가: 같은 에이전트의 앞 회차를 찾았거나, 맨 앞이 한 건이거나, 동점끼리 서로 비슷할 때(최대/최소 ≤
    rule.tie_spread_max). 동점끼리 크게 벌어지면 스위치가 가리지 못한 것이라 손 예측(AI가 빗댄 기록을 고름)으로 넘긴다
    (rule.defer_ties, v2 — 맞추기 쪽 근거는 CLAUDE.md '빗댄 기록 규칙')."""
    if not group:
        return False
    if how == "같은 에이전트의 앞 회차" or len(group) == 1 or not rule.get("defer_ties"):
        return True
    ms = [dp.measures(c)["minutes"] for c in group]  # 동점끼리 비슷하면(최대/최소 ≤ tie_spread_max) 가운데 값으로 답한다
    return max(ms) / min(ms) <= float(rule.get("tie_spread_max", 0))


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


def rule_estimates(rows: list[dict], records: list[dict], rule: dict, t: dict, decided_only: bool = False) -> dict[str, float]:
    """규칙이 고른 분. decided_only면 규칙이 혼자 답하는 기록만(동점이 여럿이면 빠진다 — 손 예측 몫)."""
    out = {}
    for d in rows:
        group, how = pick(d, records, rule, t)
        if decided_only and not decided(group, how, rule):
            continue
        e = estimate(group)
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


def evaluate(rows: list[dict], records: list[dict], rule: dict, kn, t: dict, a_rng) -> dict:
    """같은 기록에서: 규칙(동점이 여럿이면 손 예측으로 넘김) / AI가 고른 빗댄 기록 / 손 예측 / 스위치만 계산기의 말할 구간 적중."""
    rng = tuple(rule["range"]) if rule.get("range") else None
    pieces = pr.live_pieces(kn)
    a_est = ai_estimates(rows, records)
    both = [d for d in rows if d["id"] in a_est]
    out = {"n": len(both), "rule": 0, "decided": 0, "decided_hit": 0, "deferred": 0, "deferred_hit": 0,
           "ai": zone_hits(both, a_est, a_rng)[0], "same_agent": 0}
    for d in both:
        group, how = pick(d, records, rule, t)
        hand = ho.hand_outcome(d)["told_hit"] is True
        if decided(group, how, rule) and rng:
            e = estimate(group)
            hit = dp.say_zone([e * rng[0], e * rng[1]]) == dp.zone(dp.measures(d)["minutes"])
            out["decided"] += 1
            out["decided_hit"] += hit
            out["same_agent"] += how == "같은 에이전트의 앞 회차"
        else:
            hit = hand
            out["deferred"] += 1
            out["deferred_hit"] += hit
        out["rule"] += hit
    out["hand"] = sum(ho.hand_outcome(d)["told_hit"] is True for d in both)
    out["calc"] = sum(pr.outcome(pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn), d)["told_hit"] is True
                      for d in both)
    return out


def _lines(s: dict) -> list[str]:
    n = s["n"]
    return [f"  규칙(동점끼리 크게 벌어지면 손 예측으로): {_pct(s['rule'], n)} — 규칙이 혼자 답함 {s['decided']}건 중 {s['decided_hit']} 맞음"
            f"(같은 에이전트의 앞 회차 {s['same_agent']}) · 손 예측으로 넘김 {s['deferred']}건 중 {s['deferred_hit']} 맞음",
            f"  AI가 고른 빗댄 기록: {_pct(s['ai'], n)} · 손 예측(당시): {_pct(s['hand'], n)} · 스위치만 계산기: {_pct(s['calc'], n)}"]


def report(records: list[dict], rule: dict, kn) -> str:
    t = times()
    max_ratio = float(kn.domain.get("max_ratio", 2))
    train, test = split(records, rule["seen_until"])
    train_s, test_s = [d for d in train if scoped(d)], [d for d in test if scoped(d)]
    rng = tuple(rule["range"]) if rule.get("range") else None
    a_rng, _, _ = fit_range(train_s, ai_estimates(train_s, records), max_ratio)
    need = int(rule.get("min_test", 30))
    lines = [f"빗댄 기록 규칙 v{rule.get('version', 1)} — 맞춘 기록: 파일 순서로 {rule['seen_until']}까지 · 시험 기록: 그 뒤 (바깥 상황 예외는 뺌)",
             f"규칙의 범위(규칙이 혼자 답하는 기록으로 맞춤): ×{rng[0]:g}–{rng[1]:g} ({rule.get('fit', '')})" if rng else "규칙의 범위: 없음",
             f"AI가 고른 빗댄 기록의 범위(같은 쪽 기록으로 맞춤): ×{a_rng[0]:g}–{a_rng[1]:g}" if a_rng else "AI 범위: 없음", ""]
    s = evaluate(test_s, records, rule, kn, t, a_rng)
    lines.append(f"미리 정한 시험 — 시험 기록 중 정해진 일이고 AI가 보내기 전에 빗댄 기록을 적은 {s['n']}건 (판정에 {need}건 필요):")
    if s["n"]:
        lines += _lines(s)
    if s["n"] >= need:
        ok = s["rule"] >= s["ai"] - 0.05 * s["n"]
        lines.append(f"  성공 기준(돌리기 전에 정함): 규칙이 AI보다 5 %p 넘게 낮지 않다 → {'성공' if ok else '실패'}")
    else:
        lines.append(f"  시험 전 ({s['n']}/{need}) — 새 기록이 쌓이면 판정한다")
    ids = [d["id"] for d in records]
    past = [d for d in train_s if ids.index(d["id"]) > ids.index(rule.get("posthoc_from", rule["seen_until"]))]
    if past:
        p = evaluate(past, records, rule, kn, t, a_rng)
        lines.append("")
        lines.append(f"참고(사후 — 이 규칙을 만들며 본 기록이라 판정이 아니다): {rule.get('posthoc_from')} 다음 ~ {rule['seen_until']}의 같은 조건 {p['n']}건")
        lines += _lines(p)
    return "\n".join(lines)


def show(d: dict, records: list[dict], rule: dict) -> str:
    group, how = pick(d, records, rule)
    rng = tuple(rule["range"]) if rule.get("range") else None
    if not group:
        return f"{d['id']}: 비슷한 지난 일 없음 — 손 예측"
    e = estimate(group)
    if not decided(group, how, rule):
        return (f"{d['id']}: 동점 {len(group)}건이 서로 크게 벌어져 규칙이 가리지 못함 — 손 예측(AI가 빗댄 기록을 고름)으로 넘긴다. 동점: "
                + ", ".join(f"{c['id']} {dp.measures(c)['minutes']}분" for c in group[:8]) + (" …" if len(group) > 8 else ""))
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
    head += (f'fit = "{first}–{last}의 정해진 일 중 규칙이 혼자 답하는 기록에서 맞춤: {len(inside)}/{len(matched)}건 범위 안'
             + (f" ({', '.join(inside[:6])}{' …' if len(inside) > 6 else ''})" if inside else "") + '"\n')
    return head


def main(argv: list[str]) -> int:
    kn = pr.load_kn()
    records = dp.load()
    rule = load_rule()
    if argv and not argv[0].startswith("--"):
        arg = argv[0]
        if Path(arg).is_file():  # 기록을 덧붙이기 전: 상황 파일(project, date, agent, round, [situation])
            raw = tomllib.loads(Path(arg).read_text(encoding="utf-8"))
            d = {"id": "(새 기록)", "project": raw.get("project", ""), "date": str(raw.get("date", "")), "batch": None,
                 "agent": raw.get("agent"), "round": raw.get("round"), "situation": raw.get("situation", {}),
                 "predicted": {}, "actual": {"status": "unknown"}}
            print(f"상황 파일 {arg} (project {d['project']}, agent {d['agent']}, round {d['round']})")
            print(show(d, records, rule))
            return 0
        found = [d for d in records if d["id"] == arg]
        if not found:
            print(f"기록 id도 상황 파일도 아님: {arg}")
            return 2
        print(f"기록 {arg} — {found[0].get('task', '')[:70]}")
        print(show(found[0], records, rule))
        return 0
    max_ratio = float(kn.domain.get("max_ratio", 2))
    train, _ = split(records, rule["seen_until"])
    train_s = [d for d in train if scoped(d)]
    rng, matched, inside = fit_range(train_s, rule_estimates(train_s, records, rule, times(), bool(rule.get("defer_ties"))), max_ratio)
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
