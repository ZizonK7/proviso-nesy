"""계산기: 기록 하나의 상황 값(situation)과 프로젝트(project)만 보고 턴·분·토큰 범위와 말할 구간을 계산한다.

사용법 (저장소 루트):
  python -m domains.agent_usage.predict p04            기록 id 하나 (실측이 있으면 맞았는지도)
  python -m domains.agent_usage.predict 상황.toml      상황 값 파일: project = "...", [situation] 상태 = 값, (선택) analog = "기록 id"
  python -m domains.agent_usage.predict --all          끝난 기록 전부를 지금 조각으로 (맞춰 본 것 / 시험 따로)

계산 (2026-10-19, 계산되는 논리):
- 조각 = 효과 칸(effect)이 있는 살아 있는 가설. 효과 하나 = 무엇에(on) · 어떻게(op: 기준값/곱하기/더하기) · 범위 · 언제(when).
- 턴 = 기준값 × 곱하기 조각들, 분당 턴도 같다. 분 = 턴 ÷ 분당 턴 + 더하기 조각(바퀴 몫). 토큰 = 턴 × 턴당 맥락.
  분 기준값 조각이 맞으면(턴이 분을 정하지 않는 일) 그것이 분을 정한다.
- 기준값이 여럿 맞으면 조건이 가장 많은(가장 좁은) 것 하나. 기준값이 없으면 지어내지 않고 '모름'.
- 범위 합치기: 조각마다의 범위를 서로 독립인 불확실성으로 보고 로그 폭을 제곱합 제곱근으로 합친다.
  합친 범위가 분야 상한(max_ratio, 2배)을 넘으면 기하 중심 둘레로 자른다 — 사용자에게는 한 구간을 말해야 한다(장치 G).
- 말할 구간 = 분 범위의 구간, 두 구간에 걸치면 긴 쪽(R_say_numbers_v2).
- 설명: 근거 → 조각 → 조합 → 숫자. 빼도 말할 구간과 토큰 등급이 안 바뀌는 조각은 설명에서 빼고 '쓴 조각' 목록에만 둔다.
- 비유 조각(analog = true)은 빗댄 기록(predicted.analog)의 실측을 쓴다. 보내기 전에 적은 빗댄 기록이 있을 때만 쓰고,
  성적은 '비유'로 따로 낸다.
"""
from __future__ import annotations

import math
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from proviso import schema

from . import dispatches as dp

HERE = Path(__file__).resolve().parent
QUANTITY_LABEL = {"turns": "턴", "turns_per_min": "분당 턴", "add_minutes": "더하는 분",
                  "ctx_k": "턴당 맥락(천 토큰)", "minutes": "분"}
OP_LABEL = {"base": "기준", "mul": "×", "add": "+"}


@dataclass(frozen=True)
class Effect:
    piece: str
    on: str
    op: str
    lo: float
    hi: float
    when: tuple[tuple[str, tuple[str, ...]], ...]
    dir: str | None = None
    analog: bool = False
    reason: str = ""

    @property
    def center(self) -> float:
        return math.sqrt(self.lo * self.hi)


@dataclass
class Piece:
    id: str
    text: str
    reason: str
    effects: list[Effect]
    seen_until: str | None = None
    conditions: tuple[str, ...] = ()
    fit: str | None = None  # 맞춘 기록 범위 설명 (fit.py가 적음)


def _effect(piece_id: str, e: dict) -> Effect:
    rng = e.get("range", [1, 1])
    when = tuple((sid, tuple(vals)) for sid, vals in schema.when_items(e))
    return Effect(piece_id, e["on"], e["op"], float(rng[0]), float(rng[1]), when,
                  e.get("dir"), bool(e.get("analog", False)), e.get("reason", ""))


def piece_of(item: dict) -> Piece:
    """지식 파일의 가설(또는 holdout.toml의 조각) 하나 → Piece."""
    node = schema.Node("hypothesis", item["id"], item)
    return Piece(item["id"], item.get("text", item.get("method", "")), item.get("reason", ""),
                 [_effect(item["id"], e) for e in schema.effects(node)],
                 item.get("seen_until"), tuple(node.refs("conditions")), item.get("fit"))


def live_pieces(kn: schema.Knowledge) -> list[Piece]:
    """지식 파일에서 지금 쓰는 조각: 효과 칸이 있는 살아 있는 가설·규칙 (파일 순서)."""
    return [piece_of(n.data) for n in kn.nodes.values() if schema.alive(n) and schema.effects(n)]


def load_kn() -> schema.Knowledge:
    return schema.load(HERE / "knowledge.toml")


# ---------- 상황 값 ----------
def resolve(situation: dict, project: str, kn: schema.Knowledge) -> dict[str, str]:
    """상태마다 값: 적힌 값 → 프로젝트에서 정해지는 값(from_project) → 기본값(default) → '모름'."""
    out = {}
    for state in kn.of("state"):
        value = situation.get(state.id)
        if value is None:
            value = (state.data.get("from_project") or {}).get(project)
        if value is None:
            value = state.data.get("default")
        out[state.id] = value or "모름"
    return out


def matches(effect: Effect, sit: dict[str, str]) -> bool:
    for sid, vals in effect.when:
        value = sit.get(sid, "모름")
        if not any((value != v[1:]) if v.startswith("!") else (value == v) for v in vals):
            return False
    return True


def specificity(effect: Effect) -> int:
    return len(effect.when)


# ---------- 범위 계산 ----------
def combine(ranges: list[tuple[float, float]]) -> tuple[float, float]:
    """곱하는 범위들을 합친다: 기하 중심의 곱, 로그 반폭의 제곱합 제곱근(독립인 불확실성)."""
    c = sum(math.log(lo * hi) / 2 for lo, hi in ranges)
    w = math.sqrt(sum((math.log(hi / lo) / 2) ** 2 for lo, hi in ranges))
    return math.exp(c - w), math.exp(c + w)


def clamp(rng: tuple[float, float], max_ratio: float) -> tuple[tuple[float, float], bool]:
    """범위가 상한 배를 넘으면 기하 중심 둘레로 자른다. (범위, 잘랐나)."""
    lo, hi = rng
    if hi / lo <= max_ratio * (1 + 1e-9):
        return rng, False
    c, half = math.sqrt(lo * hi), math.sqrt(max_ratio)
    return (c / half, c * half), True


@dataclass
class Quantity:
    """한 값(턴·분당 턴 등)의 계산: 고른 기준값과 곱한 조각들."""
    base: Effect | None = None
    muls: list[Effect] = field(default_factory=list)
    base_value: float | None = None  # 비유 기준값이면 빗댄 기록의 실측

    def factors(self, skip: Effect | None = None) -> list[tuple[float, float]] | None:
        if self.base is None or self.base is skip:
            return None
        if self.base.analog:
            out = [(self.base_value * self.base.lo, self.base_value * self.base.hi)]
        else:
            out = [(self.base.lo, self.base.hi)]
        return out + [(m.lo, m.hi) for m in self.muls if m is not skip]

    def range(self, skip: Effect | None = None) -> tuple[float, float] | None:
        f = self.factors(skip)
        return combine(f) if f else None

    def used(self) -> list[Effect]:
        return ([self.base] if self.base else []) + self.muls


@dataclass
class Prediction:
    sit: dict[str, str]
    q: dict[str, Quantity]
    adds: list[Effect]
    max_ratio: float
    analog: dict | None = None

    def used(self) -> list[Effect]:
        out = []
        for name in ("turns", "turns_per_min", "minutes", "ctx_k"):
            out += self.q[name].used()
        return out + self.adds

    # 계산 (skip = 이 효과를 뺐을 때)
    def turns(self, skip: Effect | None = None, cut: bool = True) -> tuple[float, float] | None:
        r = self.q["turns"].range(skip)
        return (clamp(r, self.max_ratio)[0] if cut else r) if r else None

    def minutes(self, skip: Effect | None = None) -> tuple[tuple[float, float], bool] | None:
        direct = self.q["minutes"].range(skip)
        if direct:
            core = direct
        else:
            turns, rate = self.q["turns"].range(skip), self.q["turns_per_min"].range(skip)
            if not (turns and rate):
                return None
            core = combine([turns, (1 / rate[1], 1 / rate[0])])
        adds = [a for a in self.adds if a is not skip]
        rng = (core[0] + sum(a.lo for a in adds), core[1] + sum(a.hi for a in adds))
        return clamp(rng, self.max_ratio)

    def tokens(self, skip: Effect | None = None) -> tuple[float, float] | None:
        turns, ctx = self.q["turns"].range(skip), self.q["ctx_k"].range(skip)
        if not (turns and ctx):
            return None
        lo, hi = combine([turns, ctx])
        return clamp((lo / 1000, hi / 1000), self.max_ratio)[0]

    def told(self, skip: Effect | None = None) -> str | None:
        m = self.minutes(skip)
        if not m:
            return None
        return dp.zones_of([round(m[0][0], 6), round(m[0][1], 6)])[-1]

    def token_class(self, skip: Effect | None = None) -> str | None:
        t = self.tokens(skip)
        return dp.token_class(math.sqrt(t[0] * t[1])) if t else None

    def decisive(self) -> list[Effect]:
        """빼면 말할 구간이나 토큰 등급이 바뀌는 조각 (설명에 남는 것)."""
        told, tok = self.told(), self.token_class()
        return [e for e in self.used() if self.told(e) != told or self.token_class(e) != tok]


def predict(situation: dict, project: str, pieces: list[Piece], kn: schema.Knowledge,
            analog: dict | None = None) -> Prediction:
    """상황 값과 프로젝트로 계산. analog(빗댄 기록, 끝난 것)를 주면 비유 조각도 쓴다."""
    sit = resolve(situation, project, kn)
    q = {name: Quantity() for name in QUANTITY_LABEL if name != "add_minutes"}
    effects = [e for p in pieces for e in p.effects]
    for name, qty in q.items():
        cands = [e for e in effects if e.on == name and e.op == "base" and matches(e, sit)]
        plain = [e for e in cands if not e.analog]
        analogs = [e for e in cands if e.analog and analog is not None and _actual(analog, name) is not None]
        if analogs:  # 빗댄 기록이 있으면 비유 기준값이 먼저 (가장 좁은 근거)
            qty.base, qty.base_value = analogs[0], _actual(analog, name)
        elif plain:
            qty.base = max(plain, key=specificity)  # 같으면 파일에서 앞선 것
        # 비유 기준값에는 곱하기를 얹지 않는다: 빗댄 기록의 실측이 이미 그 모양을 담고 있다(두 번 세지 않는다)
        if not (qty.base and qty.base.analog):
            qty.muls = [e for e in effects if e.on == name and e.op == "mul" and matches(e, sit)]
    adds = [e for e in effects if e.on == "add_minutes" and e.op == "add" and matches(e, sit)]
    return Prediction(sit, q, adds, float(kn.domain.get("max_ratio", schema.MAX_RATIO)), analog)


def _actual(d: dict, name: str) -> float | None:
    m = dp.measures(d)
    return {"turns": m["turns"], "turns_per_min": m["turns_per_min"], "minutes": m["minutes"],
            "ctx_k": m["ctx_per_turn_k"]}.get(name)


def analog_of(d: dict, records: list[dict]) -> dict | None:
    """보내기 전에 적은 빗댄 기록(predicted.analog)이 끝난 기록이면 그것. (사후에 읽은 것은 쓰지 않는다)"""
    ref = d.get("predicted", {}).get("analog")
    if isinstance(ref, list):
        ref = ref[0] if ref else None
    found = [o for o in records if o["id"] == ref and dp.done(o)]
    return found[0] if found else None


# ---------- 채점 ----------
def outcome(pred: Prediction, d: dict) -> dict:
    """계산 결과와 실측 비교: 말할 구간, 분·턴·토큰 범위, 분 빗나감의 갈래(양/속도)."""
    m = dp.measures(d)
    minutes = pred.minutes()
    turns = pred.turns()
    tokens = pred.tokens()
    told = pred.told()
    out = {"told": told, "minutes": minutes[0] if minutes else None, "turns": turns, "tokens": tokens,
           "zone": dp.zone(m["minutes"]) if m["minutes"] is not None else None}
    out["told_hit"] = (told == out["zone"]) if told and out["zone"] else None
    out["min_hit"] = dp.in_range(m["minutes"], list(minutes[0])) if minutes else None
    out["turn_hit"] = dp.in_range(m["turns"], list(turns)) if turns else None
    out["tok_hit"] = dp.in_range(m["tokens_m"], list(tokens)) if tokens else None
    if out["min_hit"] is False:
        direction = "아래" if m["minutes"] < minutes[0][0] else "위"
        branch = "턴 예측 없음" if out["turn_hit"] is None else ("속도" if out["turn_hit"] else "양")
        out["split"] = (direction, branch)
    else:
        out["split"] = None
    return out


# ---------- 설명 ----------
def _fmt(rng: tuple[float, float] | None, unit: str = "") -> str:
    if not rng:
        return "모름"
    lo, hi = rng

    def f(x: float) -> str:
        return f"{x:.0f}" if x >= 100 else f"{x:.1f}" if x >= 10 else f"{x:.2f}"
    return f"{f(lo)}–{f(hi)}{unit}"


def _piece_line(e: Effect, pieces: dict[str, Piece], value: float | None = None) -> str:
    p = pieces.get(e.piece)
    rng = f"[{e.lo:g}, {e.hi:g}]"
    if e.analog:
        rng = f"빗댄 기록의 실측 {value:g} × {rng}"
    cond = ", ".join(f"{sid}={'/'.join(v)}" for sid, v in e.when) or "조건 없음"
    fit = f" · 근거: {_fit_of(p, e)}" if p and p.fit else ""
    return (f"    {_label(e, pieces)} ({QUANTITY_LABEL[e.on]} {OP_LABEL[e.op]} {rng}; {cond})\n"
            f"      왜: {e.reason}{fit}")


def _fit_of(p: Piece, e: Effect) -> str:
    """조각의 근거 문장(fit.py가 적음: '기간에서 맞춤: 효과1; 효과2')에서 이 효과의 몫만."""
    head, _, rest = (p.fit or "").partition(": ")
    parts = rest.split("; ")
    i = next((k for k, x in enumerate(p.effects) if x == e), None)
    return f"{head}: {parts[i]}" if i is not None and len(parts) == len(p.effects) else (p.fit or "")


def _label(e: Effect, pieces: dict[str, Piece]) -> str:
    p = pieces.get(e.piece)
    return e.piece if not p or len(p.effects) == 1 else f"{e.piece}({QUANTITY_LABEL[e.on]})"


def explain(pred: Prediction, pieces: list[Piece], title: str = "") -> str:
    """근거 → 조각 → 조합 → 숫자. 결과를 바꾸는 조각만 설명에 남긴다."""
    by_id = {p.id: p for p in pieces}
    keep = set(map(id, pred.decisive()))
    lines = [title] if title else []
    told = pred.told()
    minutes = pred.minutes()
    lines.append(f"말할 구간: {told or '모름'}" + (f" ('{dp.ZONE_SAY[told]}')" if told else "")
                 + f" — 분 {_fmt(minutes[0] if minutes else None)}{' (2배 폭으로 자름)' if minutes and minutes[1] else ''}"
                 + f", 턴 {_fmt(pred.turns())}, 토큰 {_fmt(pred.tokens(), 'M')}"
                 + (f" ({pred.token_class()})" if pred.token_class() else ""))
    if not told:
        missing = [QUANTITY_LABEL[n] for n in ("turns", "turns_per_min") if pred.q[n].base is None]
        lines.append(f"  모름: 맞는 기준값 조각이 없음({', '.join(missing) or '분'}) — 지어내지 않는다")
    lines.append("근거 → 조각 → 조합 → 숫자 (빼도 구간·토큰 등급이 안 바뀌는 조각은 뺐다)")
    for name in ("turns", "turns_per_min", "minutes", "ctx_k"):
        qty = pred.q[name]
        shown = [e for e in qty.used() if id(e) in keep]
        if not shown:
            continue
        lines.append(f"  {QUANTITY_LABEL[name]}: 조합 {_fmt(qty.range())}")
        lines += [_piece_line(e, by_id, qty.base_value) for e in shown]
    shown_adds = [a for a in pred.adds if id(a) in keep]
    if shown_adds:
        lines.append("  더하는 분:")
        lines += [_piece_line(a, by_id) for a in shown_adds]
    if minutes:
        how = "분 기준값 조각" if pred.q["minutes"].base else "턴 ÷ 분당 턴"
        lines.append(f"  분 = {how}{' + 더하는 분' if pred.adds else ''} → {_fmt(minutes[0])}")
    used = pred.used()
    lines.append("쓴 조각: " + (", ".join(dict.fromkeys(_label(e, by_id) for e in used)) or "없음")
                 + (f" (설명에서 뺀 것: {', '.join(dict.fromkeys(_label(e, by_id) for e in used if id(e) not in keep))})"
                    if any(id(e) not in keep for e in used) else ""))
    return "\n".join(lines)


def _situation_text(d: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in d.get("situation", {}).items())


def report_record(d: dict, records: list[dict], pieces: list[Piece], kn: schema.Knowledge) -> str:
    lines = [f"{d['id']} — {d.get('task', '')} (project {d.get('project')})",
             f"상황: {_situation_text(d)}"]
    sit = resolve(d.get("situation", {}), d.get("project", ""), kn)
    derived = [f"{s.id}={sit[s.id]}" for s in kn.of("state")
               if s.id not in d.get("situation", {}) and sit[s.id] != "모름"]
    if derived:
        lines.append(f"  (적지 않았지만 정해진 값: {', '.join(derived)})")
    seen = [p.id for p in pieces if p.seen_until and _index(records, d["id"]) <= _index(records, p.seen_until)]
    if seen:
        lines.append(f"  주의: 이 기록은 조각 {len(seen)}개의 seen_until 안쪽이다 — 끝난 기록이면 세울 때 본 것(맞춰 본 것), 시험이 아니다")
    pred = predict(d.get("situation", {}), d.get("project", ""), pieces, kn)
    lines.append("")
    lines.append(explain(pred, pieces))
    if dp.done(d) and d.get("actual", {}).get("minutes") is not None:
        o = outcome(pred, d)
        m = dp.measures(d)
        lines.append("")
        lines.append(f"실측: {m['minutes']}분 ({o['zone']}), {m['turns']}턴, {m['tokens_m']}M → "
                     f"구간 {'맞음' if o['told_hit'] else '모름' if o['told_hit'] is None else '빗나감'}, "
                     f"분 {_hit(o['min_hit'])}, 턴 {_hit(o['turn_hit'])}, 토큰 {_hit(o['tok_hit'])}"
                     + (f" (분 빗나감 갈래: {o['split'][0]}·{o['split'][1]})" if o["split"] else ""))
    analog = analog_of(d, records)
    if analog is not None:
        ap = predict(d.get("situation", {}), d.get("project", ""), pieces, kn, analog)
        if any(e.analog for e in ap.used()):
            lines.append("")
            lines.append(f"비유 계산 (보내기 전에 적은 빗댄 기록 {analog['id']}의 실측을 씀 — 성적은 '비유'로 따로):")
            lines.append(explain(ap, pieces))
            if dp.done(d) and d.get("actual", {}).get("minutes") is not None:
                o = outcome(ap, d)
                lines.append(f"  비유 결과: 구간 {'맞음' if o['told_hit'] else '빗나감'}, 분 {_hit(o['min_hit'])}, 턴 {_hit(o['turn_hit'])}")
    p = d.get("predicted", {})
    if p.get("minutes"):
        hand = p.get("told") or (dp.zones_of(p["minutes"]) or ["–"])[-1]
        lines.append(f"\n당시 손 예측: 분 {dp._bounds(p['minutes'])} (말한/말할 구간 {hand}), 턴 {dp._bounds(p.get('turns', []))}")
    return "\n".join(lines)


def _hit(v: bool | None) -> str:
    return "모름" if v is None else ("안" if v else "밖")


def _index(records: list[dict], rid: str) -> int:
    ids = [r["id"] for r in records]
    return ids.index(rid) if rid in ids else len(ids)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    kn = load_kn()
    records = dp.load()
    pieces = live_pieces(kn)
    arg = argv[0]
    if arg == "--all":
        from . import holdout
        print(holdout.score_table({"지금 조각 (맞춰 본 것: 세울 때 본 기록)": pieces}, [d for d in records if dp.done(d)], kn, records))
        return 0
    found = [d for d in records if d["id"] == arg]
    if found:
        print(report_record(found[0], records, pieces, kn))
        return 0
    path = Path(arg)
    if not path.exists():
        print(f"기록 id나 상황 값 파일이 아님: {arg}")
        return 2
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    d = {"id": path.stem, "project": raw.get("project", ""), "task": raw.get("task", ""),
         "situation": raw.get("situation", {}), "predicted": {"analog": raw.get("analog")}, "actual": {"status": "unknown"}}
    print(report_record(d, records, pieces, kn))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
