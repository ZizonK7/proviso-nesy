"""조각의 숫자를 기록에서 기계적으로 맞춘다 (사람이 고르지 않는다).

사용법 (저장소 루트):
  python -m domains.agent_usage.fit holdout          holdout.toml 조각들을 앞 절반(fit_until까지)으로 맞춘 결과를 보여 준다
  python -m domains.agent_usage.fit holdout --write  … 그리고 holdout.toml의 범위·근거 칸을 다시 쓴다
  python -m domains.agent_usage.fit final            knowledge.toml의 계산 조각을 seen_until까지의 기록으로 맞춘 결과
  python -m domains.agent_usage.fit final --write    … 그리고 knowledge.toml의 계산 조각 구역을 다시 쓴다

조각의 '모양'(무엇에·어떻게·언제·방향·이유)은 사람이(AI가) 적고, 범위 숫자만 여기서 정한다.
- 기준값: 그 기준값이 고른 기록 중 곱하기 조각이 하나도 안 걸린 기록의 실측 값.
- 곱하기: 걸린 기록의 '실측 ÷ (기준값 × 다른 곱하기)'의 가운데들 (세 번 돌려 서로 맞춘다).
- 더하기: 걸린 기록의 '실측 분 − 턴÷분당 턴으로 잡은 분'.
- 비유 기준값: 빗댄 기록이 있는 기록의 '실측 ÷ 빗댄 기록의 실측'. 맞출 때만 사후에 읽은 빗댄 기록(checks.PAST_ANALOG)도 쓴다.
- 범위 = 값들을 상한 배(2배) 폭의 창으로 훑어 가장 많이 담는 창(같으면 값들의 가운데 값에 가까운 창)을, 담긴 값의 최소–최대로 줄인 것.
  값이 하나뿐인 조건(한 건짜리)도 세울 수 있다: 범위는 그 값 둘레의 가장 넓은 창이고 audit이 '근거 1건'으로 경고한다
  (장치 D, 2026-10-19 사용자 결정: 특수한 경우일 수 있고, 기본 논리가 틀린 게 보이면 한 건이라도 고친다. 크기는 다음 기록이 시험한다).
  값이 여럿인데 어느 창도 둘 이상을 못 담으면 세울 수 없다 — 크기가 흩어진 조건은 더 쪼갤 조건이다.
- 곱하기 범위가 주장한 방향(dir)과 어긋나면 dir_ok = False — 방향(논리)이 데이터와 안 맞는 조각이다(장치 A).
"""
from __future__ import annotations

import math
import re
import sys
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

from proviso import schema

from . import checks, dispatches as dp
from . import predict as pr

HERE = Path(__file__).resolve().parent
HOLDOUT = HERE / "holdout.toml"
KNOWLEDGE = HERE / "knowledge.toml"
BLOCK_START = "# ---------- 계산 조각 (fit.py final --write가 range·fit 칸을 다시 쓴다; 모양은 손으로) ----------"
BLOCK_END = "# ---------- 계산 조각 끝 ----------"
PASSES = 3


@dataclass
class Stat:
    matched: list[str] = field(default_factory=list)
    values: list[float] = field(default_factory=list)
    explained: list[str] = field(default_factory=list)
    dir_ok: bool = True


def window(values: list[float], max_ratio: float) -> tuple[float, float] | None:
    """상한 배 폭 창 가운데 값을 가장 많이 담는 창(같으면 가장 좁은 것)의 [최소, 최대].
    값이 하나뿐이면(한 건짜리 조건) 그 값 둘레의 가장 넓은 창(상한 배 폭): 크기는 한 건에서만 나와 아직 모른다는 뜻.
    값이 여럿인데 어느 창도 둘 이상을 못 담으면 None — 크기가 흩어진 조건은 흐린 조건이라 더 쪼개야 한다."""
    v = sorted(x for x in values if x and x > 0)
    if not v:
        return None
    if len(v) == 1:
        half = math.sqrt(max_ratio)
        return v[0] / half, v[0] * half
    mid = math.log(v[len(v) // 2]) if len(v) % 2 else (math.log(v[len(v) // 2 - 1]) + math.log(v[len(v) // 2])) / 2
    best = None
    j = 0
    for i in range(len(v)):
        j = max(j, i)
        while j + 1 < len(v) and v[j + 1] <= v[i] * max_ratio * (1 + 1e-12):
            j += 1
        count = j - i + 1
        off = abs((math.log(v[i]) + math.log(v[j])) / 2 - mid)  # 같으면 가운데 값에 가까운 창
        if best is None or count > best[0] or (count == best[0] and off < best[1]):
            best = (count, off, v[i], v[j])
    if best[0] < 2:
        return None
    return best[2], best[3]


def _sig(x: float, up: bool, digits: int = 3) -> float:
    if x <= 0:
        return x
    e = math.floor(math.log10(x)) - digits + 1
    f = (math.ceil if up else math.floor)(x / 10 ** e - (1e-9 if up else -1e-9))
    return round(f * 10 ** e, max(0, -e))


def rounded(rng: tuple[float, float], max_ratio: float) -> tuple[float, float]:
    lo, hi = _sig(rng[0], False), _sig(rng[1], True)
    if hi / lo > max_ratio:
        hi = _sig(lo * max_ratio, False)
    return lo, hi


def _value(d: dict, name: str) -> float | None:
    return pr._actual(d, name)


def _analog_for_fit(d: dict, records: list[dict]) -> dict | None:
    ref = d.get("predicted", {}).get("analog") or checks.PAST_ANALOG.get(d["id"])
    found = [o for o in records if o["id"] == ref and dp.done(o)]
    return found[0] if found else None


def fit(pieces: list[pr.Piece], records: list[dict], kn: schema.Knowledge,
        all_records: list[dict] | None = None) -> tuple[list[pr.Piece], dict[pr.Effect, Stat]]:
    """records(맞출 기록, 끝난 것)로 조각들의 범위를 정한다. 돌려주는 조각은 새 범위를 가진 복사본."""
    max_ratio = float(kn.domain.get("max_ratio", schema.MAX_RATIO))
    all_records = all_records or records
    recs = [d for d in records if dp.done(d)]
    sits = {d["id"]: pr.resolve(d.get("situation", {}), d.get("project", ""), kn) for d in recs}
    effs = [e for p in pieces for e in p.effects]
    new: dict[pr.Effect, pr.Effect] = {e: e for e in effs}
    stats: dict[pr.Effect, Stat] = {e: Stat() for e in effs}

    def cur(e: pr.Effect) -> pr.Effect:
        return new[e]

    def chosen_base(d: dict, name: str) -> pr.Effect | None:
        cands = [e for e in effs if e.on == name and e.op == "base" and not e.analog and pr.matches(e, sits[d["id"]])]
        return max(cands, key=pr.specificity) if cands else None

    def muls_of(d: dict, name: str) -> list[pr.Effect]:
        return [e for e in effs if e.on == name and e.op == "mul" and pr.matches(e, sits[d["id"]])]

    names = ("turns", "turns_per_min", "ctx_k", "minutes")
    # 1. 기준값
    for name in names:
        for b in [e for e in effs if e.on == name and e.op == "base" and not e.analog]:
            rows = [d for d in recs if chosen_base(d, name) is b and not muls_of(d, name)
                    and _value(d, name) is not None]
            st = stats[b]
            st.matched = [d["id"] for d in rows]
            st.values = [_value(d, name) for d in rows]
            w = window(st.values, max_ratio)
            if w:
                lo, hi = rounded(w, max_ratio)
                new[b] = replace(b, lo=lo, hi=hi)
    # 2. 비유 기준값
    for b in [e for e in effs if e.op == "base" and e.analog]:
        rows = [(d, a) for d in recs if pr.matches(b, sits[d["id"]])
                for a in [_analog_for_fit(d, all_records)] if a is not None
                and _value(d, b.on) is not None and _value(a, b.on)]
        st = stats[b]
        st.matched = [d["id"] for d, _ in rows]
        st.values = [_value(d, b.on) / _value(a, b.on) for d, a in rows]
        w = window(st.values, max_ratio)
        if w:
            new[b] = replace(b, lo=rounded(w, max_ratio)[0], hi=rounded(w, max_ratio)[1])
    # 3. 곱하기 (서로 맞춘다)
    for _ in range(PASSES):
        for name in names:
            for m in [e for e in effs if e.on == name and e.op == "mul"]:
                rows = []
                for d in recs:
                    if not pr.matches(m, sits[d["id"]]):
                        continue
                    b, v = chosen_base(d, name), _value(d, name)
                    if b is None or v is None:
                        continue
                    others = math.prod(cur(o).center for o in muls_of(d, name) if o is not m)
                    rows.append((d, v / (cur(b).center * others)))
                st = stats[m]
                st.matched = [d["id"] for d, _ in rows]
                st.values = [r for _, r in rows]
                w = window(st.values, max_ratio)
                if w:
                    lo, hi = rounded(w, max_ratio)
                    up = m.dir == "up"
                    st.dir_ok = (lo >= 1 and hi > 1) if up else (hi <= 1 and lo < 1)
                    new[m] = replace(m, lo=lo, hi=hi)
    # 4. 더하기: 실측 분 − 턴÷분당 턴(가운데)
    fitted = _rebuild(pieces, new)
    for a in [e for e in effs if e.op == "add"]:
        rows = []
        for d in recs:
            if not pr.matches(a, sits[d["id"]]) or dp.measures(d)["minutes"] is None:
                continue
            p = pr.predict(d.get("situation", {}), d.get("project", ""),
                           [_without(fp, cur(a)) for fp in fitted], kn)
            m = p.minutes()
            if m:
                rows.append((d, dp.measures(d)["minutes"] - math.sqrt(m[0][0] * m[0][1])))
        st = stats[a]
        st.matched = [d["id"] for d, _ in rows]
        st.values = [r for _, r in rows]
        w = window([r for r in st.values if r > 0], max_ratio)
        st.dir_ok = w is not None and sum(r > 0 for r in st.values) * 2 > len(st.values)
        if w:
            new[a] = replace(a, lo=rounded(w, max_ratio)[0], hi=rounded(w, max_ratio)[1])
    # 설명한 기록 (범위 안)
    for e, st in stats.items():
        ne = cur(e)
        st.explained = [i for i, v in zip(st.matched, st.values) if ne.lo * (1 - 1e-9) <= v <= ne.hi * (1 + 1e-9)]
    out = _rebuild(pieces, new)
    first, last = (recs[0]["id"], recs[-1]["id"]) if recs else ("–", "–")
    for p in out:
        parts = []
        for e_old, e_new in zip([e for op in pieces if op.id == p.id for e in op.effects], p.effects):
            st = stats[e_old]
            parts.append(f"{pr.QUANTITY_LABEL[e_new.on]} {len(st.explained)}/{len(st.matched)}건"
                         + (f" ({', '.join(st.explained[:6])}{' …' if len(st.explained) > 6 else ''})" if st.explained else ""))
        p.fit = f"{first}–{last} 끝난 기록에서 맞춤: " + "; ".join(parts)
    return out, {cur(e): stats[e] for e in effs}


def _rebuild(pieces: list[pr.Piece], new: dict) -> list[pr.Piece]:
    return [replace(p, effects=[new[e] for e in p.effects]) for p in pieces]


def _without(p: pr.Piece, e: pr.Effect) -> pr.Piece:
    return replace(p, effects=[x for x in p.effects if x is not e])


# ---------- 세트 읽기·쓰기 ----------
def load_sets(path: Path = HOLDOUT) -> dict[str, dict]:
    """holdout.toml의 세트들: 이름 → {fit_until, note, pieces}."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    return {s["name"]: {"fit_until": s["fit_until"], "note": s.get("note", ""), "raw": s.get("piece", []),
                        "pieces": [pr.piece_of(p) for p in s.get("piece", [])]} for s in raw.get("set", [])}


def records_until(records: list[dict], rid: str) -> list[dict]:
    ids = [d["id"] for d in records]
    return records[: ids.index(rid) + 1]


def _toml(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{v:g}"
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, list):
        return "[" + ", ".join(_toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml(x)}" for k, x in v.items()) + " }"
    raise TypeError(type(v))


def emit_piece(raw: dict, fitted: pr.Piece, prefix: str) -> str:
    """조각 하나를 TOML로 (prefix = 'set.piece' 또는 'hypothesis'). 모양 칸은 그대로, range·fit만 새 값."""
    lines = [f"[[{prefix}]]"]
    for k, v in raw.items():
        if k in ("effect", "fit"):
            continue
        lines.append(f"{k} = {_toml(v)}")
    lines.append(f"fit = {_toml(fitted.fit)}")
    for e_raw, e in zip(raw.get("effect", []), fitted.effects):
        lines.append(f"[[{prefix}.effect]]")
        for k, v in e_raw.items():
            lines.append(f"{k} = {_toml([e.lo, e.hi] if k == 'range' else v)}")
    return "\n".join(lines)


def emit_raw(raw: dict, prefix: str) -> str:
    """맞추지 않는 조각(이전 버전)을 그대로 TOML로."""
    lines = [f"[[{prefix}]]"] + [f"{k} = {_toml(v)}" for k, v in raw.items() if k != "effect"]
    for e in raw.get("effect", []):
        lines.append(f"[[{prefix}.effect]]")
        lines += [f"{k} = {_toml(v)}" for k, v in e.items()]
    return "\n".join(lines)


def write_holdout(kn: schema.Knowledge, records: list[dict]) -> str:
    text = HOLDOUT.read_text(encoding="utf-8")
    head = text.split("[[set]]", 1)[0].rstrip() + "\n"
    raw = tomllib.loads(text)
    blocks = []
    for s in raw["set"]:
        pieces = [pr.piece_of(p) for p in s.get("piece", [])]
        fitted, _ = fit(pieces, records_until(records, s["fit_until"]), kn, records)
        lines = ["[[set]]"] + [f"{k} = {_toml(v)}" for k, v in s.items() if k != "piece"]
        blocks.append("\n".join(lines) + "\n\n" + "\n\n".join(
            emit_piece(r, f, "set.piece") for r, f in zip(s.get("piece", []), fitted)))
    out = head + "\n" + "\n\n".join(blocks) + "\n"
    HOLDOUT.write_text(out, encoding="utf-8")
    return out


def final_raw() -> list[dict]:
    """knowledge.toml 계산 조각 구역의 가설들(원문 칸)."""
    text = KNOWLEDGE.read_text(encoding="utf-8")
    block = text.split(BLOCK_START, 1)[1].split(BLOCK_END, 1)[0]
    return tomllib.loads(block).get("hypothesis", [])


def _alive_raw(r: dict) -> bool:
    return r.get("status", "hypothesis") != "retired"


def fit_final(kn: schema.Knowledge, records: list[dict]) -> tuple[list[pr.Piece], dict]:
    """계산 조각 구역의 살아 있는 가설을 seen_until까지의 기록으로 맞춘다 (이전 버전은 역사로만 남는다)."""
    raws = [r for r in final_raw() if _alive_raw(r)]
    pieces = [pr.piece_of(r) for r in raws]
    cut = {p.seen_until for p in pieces}
    if len(cut) != 1:
        raise ValueError(f"계산 조각의 seen_until이 하나가 아님: {cut}")
    return fit(pieces, records_until(records, cut.pop()), kn, records)


def write_final(kn: schema.Knowledge, records: list[dict]) -> None:
    raws = final_raw()
    fitted = iter(fit_final(kn, records)[0])
    text = KNOWLEDGE.read_text(encoding="utf-8")
    before, rest = text.split(BLOCK_START, 1)
    _, after = rest.split(BLOCK_END, 1)
    body = "\n\n".join(emit_piece(r, next(fitted), "hypothesis") if _alive_raw(r) else emit_raw(r, "hypothesis")
                         for r in raws)
    KNOWLEDGE.write_text(before + BLOCK_START + "\n" + body + "\n" + BLOCK_END + after, encoding="utf-8")


def show(fitted: list[pr.Piece], stats: dict) -> str:
    lines = []
    for p in fitted:
        lines.append(f"{p.id}: {p.text}")
        for e in p.effects:
            st = stats[e]
            flag = "" if st.dir_ok else "  ← 방향이 데이터와 어긋남"
            short = "  ← 근거 1건(크기는 다음 기록이 시험)" if len(st.explained) == 1 else (
                "  ← 설명한 기록 없음(세울 수 없음)" if not st.explained else "")
            lines.append(f"  {pr.QUANTITY_LABEL[e.on]} {pr.OP_LABEL[e.op]} [{e.lo:g}, {e.hi:g}] "
                         f"설명 {len(st.explained)}/{len(st.matched)}{flag}{short}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("holdout", "final"):
        print(__doc__)
        return 2
    kn = pr.load_kn()
    records = dp.load()
    write = "--write" in argv
    if argv[0] == "holdout":
        for name, s in load_sets().items():
            fitted, stats = fit(s["pieces"], records_until(records, s["fit_until"]), kn, records)
            print(f"[{name}] {s['fit_until']}까지 맞춤\n{show(fitted, stats)}\n")
        if write:
            write_holdout(kn, records)
            print("holdout.toml을 다시 썼다")
    else:
        fitted, stats = fit_final(kn, records)
        print(show(fitted, stats))
        if write:
            write_final(kn, records)
            print("knowledge.toml 계산 조각 구역을 다시 썼다")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
