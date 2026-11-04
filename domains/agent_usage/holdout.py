"""다시 돌리기: 끝난 기록을 시간 순서로 앞 절반·뒤 절반으로 나눠, 앞 절반으로 세운 조각을 뒤 절반으로 시험한다.

사용법 (저장소 루트):
  python -m domains.agent_usage.holdout          뒤 절반 성적 비교(쪼개기 전 / 쪼갠 뒤 / 당시 손 예측) + 조각별 방향·크기 성적
  python -m domains.agent_usage.holdout --gaps   앞 절반에서 설명 안 된 기록과 공통 조건 (쪼갤 곳 찾기, 앞 절반만 보여 준다)

성적의 맨 위 줄은 '말할 구간이 맞았나'다(장치 H: 사용자가 받는 것은 한마디). 분 숫자 적중은 그 아래.
방향 성적과 크기 성적은 따로다(장치 A):
- 방향: 조건 조각마다 '조건이 있는 기록'과 '없는 기록'의 (실측 ÷ 그 조각을 뺀 계산) 가운데 값을 비교한다.
  같은 기준값을 고른 기록끼리(비슷한 모양끼리) 비교하고, 그런 짝이 없으면 전체로 — 거친 비교다.
  방향이 틀리면 이유(논리)가 깨진 것 → audit 오류, why = "이유 틀림" 후보.
- 크기: 조건이 있는 기록의 그 비율이 조각 범위 안에 든 몫. 크기만 틀리면 조건이 흐린 것 → 쪼개기 후보.
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from statistics import median

from proviso import schema

from . import dispatches as dp
from . import fit as ft
from . import predict as pr

BOUNDARY = "d38b"  # 앞 절반의 마지막 기록 (holdout.toml의 fit_until과 같다)
HOLDOUT_END = "p05"  # 뒤 절반의 마지막 기록. 홀드아웃은 2026-10-19 실험을 그대로 재생한다(뒤 61건). 그 뒤 기록은 checks.SEEN_UNTIL이 시험한다 (2026-10-22: 새 기록이 뒤 절반에 섞여 성적이 흔들려 고정)
SETS = ("front_v0", "front_split")
SET_LABEL = {"front_v0": "쪼개기 전 계산기", "front_split": "쪼갠 뒤 계산기"}
# 장치 E(회귀 금지): 쪼갠 뒤 설명 안 되게 된 기록과 그래도 쪼갠 까닭. 여기 없는 회귀가 생기면 테스트가 실패한다.
REGRESSION_OK = {
    "front_split": {
        "d15b": "쪼개기 전에는 상쇄로 맞았다: 턴을 실제의 2.3배로 크게 잡고(구현 기준값) 분당 턴도 크게 잡아 구간만 맞았다. "
                "쪼갠 뒤 턴은 가까워졌고(외부 확인 없는 문서 일), 남은 빗나감은 설계부터 하는 새로 쓰기의 느린 분당 턴(2.8) — "
                "그 조건을 가진 기록이 앞 절반에 하나뿐이라 쪼개지 않았다(장치 D)",
    },
    "final": {
        # 2026-11-03 말하기를 가운데 값으로 바꾸자(R_say_numbers_v3) 드러난 회귀. 긴 쪽으로 말하던 때는 범위 위 끝이 '다른 일'에 걸쳐 맞아 보였다
        **{rid: "쪼갠 C_min_light_model(×0.34–0.63)로 Fable xhigh 정해진 입력 풀이의 범위가 6.0–12.1분(가운데 8.5 → 잠깐)인데 "
                "실제 11.6–16.1분(다른 일) — 쪼개기 전 범위는 11.6–19.2분. 쪼개기는 같은 풀이를 두 모델이 한 짝 넷에서 방향이 맞아 남기고, "
                "크기(Fable xhigh 풀이에서 범위 위 끝)는 다음 정리에서 본다(CLAUDE.md 다음 정리 4)"
           for rid in ("d20", "d25", "d57")},
    },
}


def halves(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """끝난 기록의 (앞 절반, 뒤 절반). 경계는 BOUNDARY, 뒤 절반의 끝은 HOLDOUT_END(그 뒤 기록은 홀드아웃에 넣지 않는다)."""
    ids = [d["id"] for d in records]
    cut = ids.index(BOUNDARY) + 1
    end = ids.index(HOLDOUT_END) + 1 if HOLDOUT_END in ids else len(records)
    return [d for d in records[:cut] if dp.done(d)], [d for d in records[cut:end] if dp.done(d)]


def evaluate(pieces: list[pr.Piece], records: list[dict], kn: schema.Knowledge,
             all_records: list[dict], analog: bool = False) -> list[tuple[dict, dict]]:
    out = []
    for d in records:
        a = pr.analog_of(d, all_records) if analog else None
        if analog and a is None:
            continue
        p = pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn, a, pr.counts_of(d))
        if analog and not any(e.analog for e in p.used()):
            continue
        out.append((d, pr.outcome(p, d)))
    return out


def hand_outcome(d: dict) -> dict:
    """당시 메인이 손으로 한 예측. 말한 구간 = predicted.told, 없으면 분 범위의 긴 쪽(R_say_numbers_v2를 지난 기록에 댐)."""
    p, m = d["predicted"], dp.measures(d)
    bounds = p.get("minutes", [])
    if not bounds or max(bounds) <= 0:
        return {"told": None, "told_hit": None, "min_hit": None, "turn_hit": None, "split": None,
                "zone": dp.zone(m["minutes"])}
    told = p.get("told") or dp.zones_of(bounds)[-1]
    turns = p.get("turns", [])
    return {"told": told, "zone": dp.zone(m["minutes"]), "told_hit": told == dp.zone(m["minutes"]),
            "min_hit": dp.in_range(m["minutes"], bounds),
            "turn_hit": dp.in_range(m["turns"], turns) if turns and max(turns) > 0 else None,
            "split": dp.miss_split(d) if turns and max(turns) > 0 else
            (("아래" if m["minutes"] < bounds[0] else "위", "턴 예측 없음") if not dp.in_range(m["minutes"], bounds) else None)}


def summarize(outcomes: list[dict]) -> dict:
    n = len(outcomes)
    c = Counter()
    for o in outcomes:
        c["told"] += o["told_hit"] is True
        c["unknown"] += o["told"] is None
        c["min"] += o["min_hit"] is True
        c["turn"] += o["turn_hit"] is True
        c["turn_n"] += o["turn_hit"] is not None
        if o["split"]:
            c[o["split"]] += 1
    return {"n": n, **c} | {k: c[k] for k in [(a, b) for a in ("아래", "위") for b in ("양", "속도", "턴 예측 없음")]}


def _pct(a: int, n: int) -> str:
    return f"{a}/{n}" + (f" ({100 * a / n:.0f}%)" if n else "")


def score_table(sets: dict[str, list[pr.Piece]], records: list[dict], kn: schema.Knowledge,
                all_records: list[dict], hand: bool = True) -> str:
    """세트별 성적 표. 맨 위 줄 = 말할 구간."""
    rows = [(name, summarize([o for _, o in evaluate(p, records, kn, all_records)])) for name, p in sets.items()]
    if hand:
        rows.append(("당시 손 예측", summarize([hand_outcome(d) for d in records])))
    lines = ["| | " + " | ".join(n for n, _ in rows) + " |", "|---|" + "--:|" * len(rows)]
    lines.append("| **말할 구간 맞음** | " + " | ".join(_pct(s["told"], s["n"]) for _, s in rows) + " |")
    lines.append("| 말할 구간 모름(계산 못 함) | " + " | ".join(str(s["unknown"]) for _, s in rows) + " |")
    lines.append("| 분 범위 맞음 | " + " | ".join(_pct(s["min"], s["n"]) for _, s in rows) + " |")
    lines.append("| 턴 범위 맞음 (턴을 낸 것 중) | " + " | ".join(_pct(s["turn"], s["turn_n"]) for _, s in rows) + " |")
    for direction in ("아래", "위"):
        for branch in ("양", "속도", "턴 예측 없음"):
            lines.append(f"| 분 빗나감: 실제가 {direction}·{branch} | "
                         + " | ".join(str(s[(direction, branch)]) for _, s in rows) + " |")
    return "\n".join(lines)


# ---------- 조각별 방향·크기 ----------
def _ratio_without(e: pr.Effect, pred: pr.Prediction, d: dict) -> float | None:
    """실측 ÷ (이 효과를 뺀 계산의 가운데). 효과가 작용하는 값으로."""
    actual = pr._actual(d, e.on) if e.on != "add_minutes" else dp.measures(d)["minutes"]
    if actual is None:
        return None
    if e.on == "add_minutes":
        m = pred.minutes(e)
        return actual - math.sqrt(m[0][0] * m[0][1]) if m else None
    qty = pred.q[e.on]
    r = qty.range(e)
    if not r:
        return None
    return actual / math.sqrt(r[0] * r[1])


def piece_scores(pieces: list[pr.Piece], records: list[dict], kn: schema.Knowledge,
                 all_records: list[dict] | None = None) -> list[dict]:
    """조건 조각(곱하기·더하기)마다 방향·크기 성적, 기준값은 크기만. records = 시험 기록.
    비율 조각(scale)은 비유 계산에서만 걸리므로 all_records(빗댄 기록을 찾을 전체)가 있어야 성적이 난다."""
    preds = [(d, pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn)) for d in records]
    out = []
    for p in pieces:
        for e in p.effects:
            if e.analog:
                continue
            if e.op == "scale":
                out.append(_scale_scores(p, e, pieces, records, kn, all_records or records))
                continue
            row = {"piece": p.id, "effect": e, "with": [], "without": [], "size_hits": 0, "size_n": 0,
                   "direction": "없음 (기준값)" if e.op == "base" else "시험 전", "rough": ""}
            groups: dict[str, list[list[float]]] = {}
            for d, pred in preds:
                if e.op == "base":
                    if pred.q[e.on].base is e:
                        r = _ratio_without(e, pred, d)  # 기준값을 빼면 계산이 없으므로 직접 잰다
                        actual = pr._actual(d, e.on)
                        muls = math.prod(m.center for m in pred.q[e.on].muls)
                        if actual is not None:
                            v = actual / muls
                            row["size_n"] += 1
                            row["size_hits"] += e.lo <= v <= e.hi
                            row["with"].append(d["id"])
                    continue
                base = pred.q[e.on].base if e.on != "add_minutes" else pred.q["turns"].base
                if base is None:
                    continue
                r = _ratio_without(e, pred, d) if e in pred.used() else None
                if e in pred.used():
                    if r is None:
                        continue
                    row["with"].append(d["id"])
                    row["size_n"] += 1
                    row["size_hits"] += e.lo <= r <= e.hi
                    groups.setdefault(base.piece, [[], []])[0].append(r)
                else:
                    actual = pr._actual(d, e.on) if e.on != "add_minutes" else dp.measures(d)["minutes"]
                    rng = pred.q[e.on].range() if e.on != "add_minutes" else (pred.minutes() or [None])[0]
                    if actual is None or not rng:
                        continue
                    c = math.sqrt(rng[0] * rng[1])
                    groups.setdefault(base.piece, [[], []])[1].append(actual - c if e.on == "add_minutes" else actual / c)
                    row["without"].append(d["id"])
            if e.op != "base":
                row["direction"], row["rough"] = _direction(e, groups)
            out.append(row)
    return out


def _scale_scores(p: pr.Piece, e: pr.Effect, pieces: list[pr.Piece], records: list[dict], kn: schema.Knowledge,
                  all_records: list[dict]) -> dict:
    """비율 조각의 성적 (2026-11-04, 세우기 전에 정한 시험 — CLAUDE.md '파일 수 비율 조각').
    걸리는 기록 = 보내기 전에 적은 빗댄 기록과 count 칸이 둘 다 있는 끝난 기록.
    방향: 비율을 곱한 비유 계산이 곱하지 않은 것보다 실측에 가까운 기록이 절반을 넘으면 지지(둘 다 2건 이상일 때 판정).
    크기: 실측 ÷ (빗댄 기록의 실측 × 비율)이 비유 기준값 조각의 범위 안인 수."""
    row = {"piece": p.id, "effect": e, "with": [], "without": [], "size_hits": 0, "size_n": 0,
           "direction": "시험 전", "rough": "빗댄 기록과 수가 둘 다 있는 기록 없음"}
    closer = 0
    for d in records:
        a = pr.analog_of(d, all_records)
        if a is None:
            continue
        pred = pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn, a, pr.counts_of(d))
        used = [m for m in pred.q[e.on].muls if m.piece == e.piece and m.op == "scale"]
        base = pred.q[e.on].base
        actual = pr._actual(d, e.on)
        if not used or base is None or not base.analog or actual is None:
            continue
        ratio = used[0].lo
        a_val = pred.q[e.on].base_value
        if ratio == 1 or not a_val:
            continue  # 수가 같으면 조각이 아무것도 바꾸지 않는다 — 시험이 아니다
        row["with"].append(d["id"])
        r_with = actual / (a_val * ratio)
        r_without = actual / a_val
        row["size_n"] += 1
        row["size_hits"] += base.lo <= r_with <= base.hi
        closer += abs(math.log(r_with)) < abs(math.log(r_without))
    n = row["size_n"]
    if n >= 2:
        row["direction"] = "지지" if closer * 2 > n else "반박"
        row["rough"] = f"비율을 곱해 실측에 가까워진 기록 {closer}/{n}"
    elif n == 1:
        row["rough"] = f"걸린 기록 1건(가까워짐 {closer}) — 2건부터 판정"
    return row


def _direction(e: pr.Effect, groups: dict[str, list[list[float]]]) -> tuple[str, str]:
    """조건 있음/없음 비교. 같은 기준값 묶음 안에서 비교하고 묶음 수로 무게를 둔다."""
    add = e.op == "add"
    paired = [(w, wo) for w, wo in groups.values() if w and wo]
    note = "같은 기준값끼리 비교"
    if not paired:
        allw = [x for w, _ in groups.values() for x in w]
        allwo = [x for _, wo in groups.values() for x in wo]
        if len(allw) < 2 or len(allwo) < 2:
            return "시험 전", "조건 있음·없음이 둘씩 안 됨"
        paired, note = [(allw, allwo)], "짝이 없어 전체로 비교 (더 거침)"
    if sum(len(w) for w, _ in paired) < 2:
        return "시험 전", "조건 있는 기록이 2건 미만"
    score, weight = 0.0, 0
    for w, wo in paired:
        k = min(len(w), len(wo))
        diff = (median(w) - median(wo)) if add else math.log(median(w) / median(wo))
        score += k * diff
        weight += k
    diff = score / weight
    up = diff > 0
    ok = up if e.dir == "up" else not up
    shown = f"{diff:+.1f}분" if add else f"×{math.exp(diff):.2f}"
    return ("지지" if ok else "반박"), f"거친 비교: 있음/없음 {shown} ({note})"


def piece_table(rows: list[dict]) -> str:
    lines = ["| 조각 | 무엇에 | 어떻게 | 범위 | 방향 주장 | 방향 성적 | 크기 성적 | 비교 |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        e = r["effect"]
        claim = {"up": "늘린다", "down": "줄인다"}.get(e.dir or "", "–")
        if e.op == "scale":
            claim = f"{e.count} 수에 비례"
        size = _pct(r["size_hits"], r["size_n"]) if r["size_n"] else "시험 전"
        rng = f"{e.count} 비" if e.op == "scale" else f"{e.lo:g}–{e.hi:g}"
        lines.append(f"| {r['piece']} | {pr.QUANTITY_LABEL[e.on]} | {pr.OP_LABEL[e.op]} | {rng} | {claim} "
                     f"| {r['direction']} | {size} | {r['rough']} |")
    return "\n".join(lines)


def regressions(before: list[pr.Piece], after: list[pr.Piece], records: list[dict], kn: schema.Knowledge,
                all_records: list[dict]) -> set[str]:
    """쪼개기 전에는 말할 구간이 맞았는데 쪼갠 뒤 틀린 기록 (장치 E)."""
    hit = lambda ps: {d["id"] for d, o in evaluate(ps, records, kn, all_records) if o["told_hit"]}
    return hit(before) - hit(after)


# ---------- 빈틈 ----------
def gaps(pieces: list[pr.Piece], records: list[dict], kn: schema.Knowledge, all_records: list[dict]) -> str:
    """설명 안 된 기록(말할 구간이 틀렸거나 모름)과, 그 기록들에 많은 상황 값."""
    rows = evaluate(pieces, records, kn, all_records)
    bad = [(d, o) for d, o in rows if not o["told_hit"]]
    good = [(d, o) for d, o in rows if o["told_hit"]]
    lines = [f"설명 안 된 기록 {len(bad)}/{len(rows)}:"]
    for d, o in bad:
        m = dp.measures(d)
        p = pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn)
        t, r = p.q["turns"].range(), p.q["turns_per_min"].range()
        tr = f"턴 ×{m['turns'] / math.sqrt(t[0] * t[1]):.2f}" if t and m["turns"] else "턴 –"
        rr = f"분당 턴 ×{m['turns_per_min'] / math.sqrt(r[0] * r[1]):.2f}" if r and m["turns_per_min"] else "분당 턴 –"
        lines.append(f"  {d['id']} 말함 {o['told'] or '모름'} → 실제 {o['zone']} ({m['minutes']}분 {m['turns']}턴; {tr}, {rr}) "
                     f"쓴 조각 {', '.join(dict.fromkeys(e.piece for e in p.used())) or '없음'}")
    sit = lambda d: pr.resolve(d.get("situation", {}), d.get("project", ""), kn)
    cb, cg = Counter(), Counter()
    for d, _ in bad:
        cb.update(f"{k}={v}" for k, v in sit(d).items() if v != "모름")
    for d, _ in good:
        cg.update(f"{k}={v}" for k, v in sit(d).items() if v != "모름")
    common = sorted(cb, key=lambda k: -(cb[k] / max(1, len(bad)) - cg[k] / max(1, len(good))))
    lines.append("설명 안 된 기록에 더 많은 상황 값 (빈틈 몫 − 설명된 몫):")
    for k in common[:12]:
        lines.append(f"  {k}: 빈틈 {cb[k]}/{len(bad)}, 설명됨 {cg[k]}/{len(good)}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    kn = pr.load_kn()
    records = dp.load()
    front, back = halves(records)
    sets = ft.load_sets()
    if "--gaps" in argv:
        for name in SETS:
            print(f"[{SET_LABEL[name]}] 앞 절반({len(front)}건)에서\n{gaps(sets[name]['pieces'], front, kn, records)}\n")
        return 0
    print(f"경계: {BOUNDARY}까지 앞 절반 {len(front)}건(조각을 세우고 쪼갬), 그 뒤 {HOLDOUT_END}까지 뒤 절반 {len(back)}건(시험; 그 뒤 기록은 checks.SEEN_UNTIL이 시험)\n")
    print("뒤 절반 성적 (맨 위 줄이 사용자가 받는 한마디):")
    print(score_table({SET_LABEL[n]: sets[n]["pieces"] for n in SETS}, back, kn, records))
    for name in SETS:
        print(f"\n[{SET_LABEL[name]}] 조각별 방향·크기 성적 (뒤 절반)")
        print(piece_table(piece_scores(sets[name]["pieces"], back, kn)))
    final = pr.live_pieces(kn)
    print("\n[지금 조각 = 전체 기록으로 다시 세운 최종본] 맞춰 본 것 (세울 때 본 기록이라 시험이 아님)")
    done = [d for d in records if dp.done(d)]
    print(score_table({"최종본 (맞춰 봄)": final}, done, kn, records))
    ana = evaluate(final, done, kn, records, analog=True)
    print(f"\n비유 조각 (보내기 전에 적은 빗댄 기록이 있는 끝난 기록 {len(ana)}건, 맞춰 본 것): "
          + (", ".join(f"{d['id']} 구간 {'맞음' if o['told_hit'] else '빗나감'}" for d, o in ana) or "없음"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
