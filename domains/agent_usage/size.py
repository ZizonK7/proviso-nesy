"""일의 크기 모델 — 정해진 일 (2026-11-03 사용자 결정, CLAUDE.md '일의 크기 모델'). 시험 중이라 지식 파일의 조각이 아니다.

사용법 (저장소 루트):
  python -m domains.agent_usage.size           맞춘 몫, 채운 정도, 미리 정한 시험(시험용 기록에서 견주기)
  python -m domains.agent_usage.size --write   … 그리고 size.toml의 범위·근거 칸을 seen_until까지의 기록으로 다시 쓴다

모델: 할 일이 지시서에 다 적힌 일(S_specified = 예)은
  턴 = 기본 몫 + Σ(센 수 × 하나마다 몫)     센 수 = 기록의 size (dispatches.py SIZE_COUNTS)
  분 = 턴 ÷ 분당 턴 + 더하는 분             분당 턴·더하는 분은 지금 계산기의 조각 그대로 (전제 1이 끝나면 바뀐다)
- 이 모델은 곱하기 조각을 쓰지 않는다: 크기는 센 수가 정한다. 지금 스위치는 하나마다 몫의 조건으로 옮겨 시험할 후보다.
- 기본 설정 모델(S_other_model = 아니오)의 기록만 쓴다 — 숫자 범위는 그 설정에서 잰 것이다.
- 섞인 일(일부)은 두 몫의 합인데 찾는 몫의 모델이 아직 없어 계산하지 않는다(모름). 찾는 일(아니오)도 모름.
맞추기 (fit.py와 같은 정신 — 모양은 손으로, 숫자는 기록에서 기계적으로):
- 가운데 값: 기본 몫과 하나마다 몫을 번갈아 가운데 값(중앙값)으로 맞춘다(PASSES번). 기본 몫 = 실측 − 센 수 몫, 하나마다 몫 = (실측 − 기본 몫 − 다른 몫) ÷ 그 수.
- 범위: 마지막 가운데 값으로 다시 낸 값들을 2배 폭 창으로 훑어 가장 많이 담는 창(fit.window). 값이 흩어져 못 잡으면 그 몫은 '세울 수 없음'.
- 범위 합치기: 더하는 몫이라 하한끼리·상한끼리 더한다(각 몫이 2배 폭 안이면 합도 2배 폭 안).
"""
from __future__ import annotations

import math
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
SIZE_TOML = HERE / "size.toml"
COUNTS = dp.SIZE_COUNTS
PASSES = 30


# ---------- 기록 읽기 ----------
def counts(d: dict) -> dict[str, float] | None:
    """기록의 센 수 (하나라도 0보다 커야 쓴다)."""
    s = d.get("size") or {}
    c = {k: float(s[k]) for k in COUNTS if isinstance(s.get(k), (int, float)) and not isinstance(s.get(k), bool)}
    return c if any(v > 0 for v in c.values()) else None


def specified(d: dict) -> str:
    return d.get("situation", {}).get("S_specified", "모름")


def usable(d: dict, gate: bool = True) -> bool:
    """맞추거나 시험할 수 있는 기록: 끝남, 기본 설정 모델, 센 수가 있음, 턴 실측이 있음, (gate면) 할 일이 정해짐."""
    return (dp.done(d) and d.get("situation", {}).get("S_other_model") == "아니오" and counts(d) is not None
            and bool(dp.measures(d)["turns"]) and (not gate or specified(d) == "예"))


def split(records: list[dict], cut: str) -> tuple[list[dict], list[dict]]:
    """(맞출 기록, 시험 기록): 파일 순서로 cut까지 / 그 뒤. 시험에서는 바깥 상황 예외를 뺀다(checks와 같다)."""
    ids = [d["id"] for d in records]
    i = ids.index(cut) + 1 if cut in ids else len(ids)
    return records[:i], [d for d in records[i:] if not checks.is_exception(d)]


# ---------- 맞추기 ----------
def fit_terms(records: list[dict], max_ratio: float, gate: bool = True) -> dict:
    """{'base': 몫, 'reads': 몫, ...} — 몫 = {'range': (하한, 상한) 또는 None, 'center', 'matched', 'explained'}."""
    rows = [(d["id"], counts(d), float(dp.measures(d)["turns"])) for d in records if usable(d, gate)]
    terms = {"base": {"center": 0.0}} | {k: {"center": 0.0} for k in COUNTS}
    if not rows:
        return {name: {"range": None, "center": None, "matched": [], "explained": []} for name in terms}

    def others(n: dict, skip: str | None) -> float:
        return sum(terms[k]["center"] * n.get(k, 0) for k in COUNTS if k != skip)

    def implied(name: str) -> list[tuple[str, float]]:
        if name == "base":
            return [(i, t - others(n, None)) for i, n, t in rows]
        return [(i, (t - terms["base"]["center"] - others(n, name)) / n[name]) for i, n, t in rows if n.get(name, 0) > 0]

    terms["base"]["center"] = min(t for _, _, t in rows)  # 시작: 가장 작은 일의 턴
    for _ in range(PASSES):
        for name in (*COUNTS, "base"):
            vals = [v for _, v in implied(name) if v > 0]
            if vals:
                terms[name]["center"] = median(vals)
    out = {}
    for name in terms:
        pairs = implied(name)
        w = ft.window([v for _, v in pairs if v > 0], max_ratio)
        rng = ft.rounded(w, max_ratio) if w else None
        explained = [i for i, v in pairs if rng and rng[0] * (1 - 1e-9) <= v <= rng[1] * (1 + 1e-9)]
        out[name] = {"range": rng, "center": math.sqrt(rng[0] * rng[1]) if rng else None,
                     "matched": [i for i, _ in pairs], "explained": explained}
    return out


def load_terms(path: Path = SIZE_TOML) -> tuple[str, dict, list[dict]]:
    """size.toml → (seen_until, {이름: 범위 또는 None}, 원문 칸 목록)."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    terms = {t["count"]: (tuple(t["range"]) if t.get("range") else None) for t in raw.get("term", [])}
    return raw["seen_until"], terms, raw.get("term", [])


# ---------- 계산 ----------
def turns_range(terms: dict, n: dict[str, float]) -> tuple[float, float] | None:
    """기본 몫 + Σ 센 수 × 하나마다 몫. 센 수가 있는데 그 몫이 없으면(세울 수 없음) 모름."""
    base = terms.get("base")
    if not base:
        return None
    lo, hi = base
    for k in COUNTS:
        if n.get(k, 0) > 0:
            r = terms.get(k)
            if not r:
                return None
            lo, hi = lo + r[0] * n[k], hi + r[1] * n[k]
    return lo, hi


def minutes_range(d: dict, turns: tuple[float, float], pieces: list[pr.Piece], kn) -> tuple[float, float] | None:
    """분 = 턴 ÷ 분당 턴 + 더하는 분 — 분당 턴과 더하는 분은 지금 계산기 조각 그대로."""
    pred = pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn)
    rate = pred.q["turns_per_min"].range()
    if not rate:
        return None
    core = pr.combine([turns, (1 / rate[1], 1 / rate[0])])
    rng = (core[0] + sum(a.lo for a in pred.adds), core[1] + sum(a.hi for a in pred.adds))
    return pr.clamp(rng, pred.max_ratio)[0]


def outcome(d: dict, terms: dict, pieces: list[pr.Piece], kn) -> dict:
    m = dp.measures(d)
    t = turns_range(terms, counts(d) or {})
    mins = minutes_range(d, t, pieces, kn) if t else None
    told = dp.zones_of([round(mins[0], 6), round(mins[1], 6)])[-1] if mins else None
    zone = dp.zone(m["minutes"])
    return {"told": told, "zone": zone, "told_hit": (told == zone) if told else None,
            "min_hit": dp.in_range(m["minutes"], list(mins)) if mins else None,
            "turn_hit": dp.in_range(m["turns"], list(t)) if t else None, "turns": t, "minutes": mins}


# ---------- 미리 정한 시험 ----------
def _score(outs: list[dict]) -> str:
    n = len(outs)
    if not n:
        return "–"
    told = sum(o["told_hit"] is True for o in outs)
    unknown = sum(o["told"] is None for o in outs)
    mins = sum(o["min_hit"] is True for o in outs)
    turns = [o["turn_hit"] for o in outs if o["turn_hit"] is not None]
    return (f"{told}/{n} ({100 * told / n:.0f}%)" + (f", 모름 {unknown}" if unknown else "")
            + f" · 분 범위 {mins}/{n} · 턴 범위 {sum(turns)}/{len(turns)}")


def report(records: list[dict], kn, cut: str, terms: dict, open_terms: dict) -> str:
    pieces = pr.live_pieces(kn)
    train, test = split(records, cut)
    lines = [f"맞춘 기록: 파일 순서로 {cut}까지 · 시험 기록: 그 뒤 (바깥 상황 예외는 뺌)"]
    fin = [d for d in train if dp.done(d)]
    lines.append(f"채운 정도 (맞출 쪽 끝난 기록 {len(fin)}건): 할 일이 정해짐 "
                 + ", ".join(f"{v} {sum(specified(d) == v for d in fin)}" for v in ("예", "일부", "아니오", "모름"))
                 + f" · 맞추는 데 쓴 기록(예 + 기본 모델 + 센 수 + 턴) {sum(usable(d) for d in fin)}건")
    lines.append("")
    lines.append("맞춘 몫 (턴):")
    for name in ("base", *COUNTS):
        r = terms.get(name)
        label = "기본 몫" if name == "base" else f"{name} 하나마다"
        lines.append(f"  {label}: " + (f"[{r[0]:g}, {r[1]:g}]" if r else "세울 수 없음(기록이 없거나 값이 흩어짐)"))
    tested = [d for d in test if usable(d)]
    lines.append("")
    lines.append(f"미리 정한 시험 — 시험 기록 중 할 일이 정해진 일(예) + 기본 모델 + 센 수가 있는 끝난 기록 {len(tested)}건, 말할 구간 적중:")
    rows = [
        ("스위치만 (지금 계산기)", [pr.outcome(pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn), d) for d in tested]),
        ("센 수 — 나눈 모델", [outcome(d, terms, pieces, kn) for d in tested]),
        ("센 수 — 안 나눈 모델 (같은 다섯 수, 정해졌나를 안 봄)", [outcome(d, open_terms, pieces, kn) for d in tested]),
        ("손 예측 (당시)", [ho.hand_outcome(d) for d in tested]),
    ]
    for label, outs in rows:
        lines.append(f"  {label}: {_score(outs)}")
    ana = [(d, pr.analog_of(d, records)) for d in tested]
    ana = [pr.outcome(pr.predict(d.get("situation", {}), d.get("project", ""), pieces, kn, a), d) for d, a in ana if a]
    lines.append(f"  빗댄 기록에서 출발 (빗댄 기록이 있는 {len(ana)}건): {_score(ana)}")
    other = [d for d in test if usable(d, gate=False) and specified(d) in ("아니오", "일부")]
    lines.append(f"  참고 — 찾는 일·섞인 일인 시험 기록 {len(other)}건에 안 나눈 모델을 대면: "
                 + _score([outcome(d, open_terms, pieces, kn) for d in other]))
    lines.append("성공 기준 (돌리기 전에 정함, CLAUDE.md): 나눈 모델이 빗댄 기록에서 출발한 성적(2026-11-03 시험 76 %) 가까이 오르면 성공")
    return "\n".join(lines)


# ---------- size.toml 쓰기 ----------
def write(raw_terms: list[dict], fitted: dict, cut: str, records: list[dict]) -> str:
    train = [d for d in split(records, cut)[0] if dp.done(d)]
    first, last = (train[0]["id"], train[-1]["id"]) if train else ("–", "–")
    head = SIZE_TOML.read_text(encoding="utf-8").split("[[term]]", 1)[0]
    parts = [head.rstrip() + "\n"]
    for t in raw_terms:
        f = fitted[t["count"]]
        parts.append("\n[[term]]")
        parts.append(f'count = "{t["count"]}"')
        parts.append(f'reason = "{t["reason"]}"')
        if f["range"]:
            parts.append(f"range = [{f['range'][0]:g}, {f['range'][1]:g}]")
        parts.append(f'fit = "{first}–{last}에서 맞춤: {len(f["explained"])}/{len(f["matched"])}건 범위 안'
                     + (f" ({', '.join(f['explained'][:6])}{' …' if len(f['explained']) > 6 else ''})" if f["explained"] else "")
                     + ('"' if f["range"] else ' — 값이 없거나 흩어져 세울 수 없음"'))
    return "\n".join(parts) + "\n"


def main(argv: list[str]) -> int:
    kn = pr.load_kn()
    records = dp.load()
    max_ratio = float(kn.domain.get("max_ratio", 2))
    cut, written, raw_terms = load_terms()
    train = split(records, cut)[0]
    fitted = fit_terms(train, max_ratio)
    if "--write" in argv:
        SIZE_TOML.write_text(write(raw_terms, fitted, cut, records), encoding="utf-8")
        cut, written, raw_terms = load_terms()
    open_fit = fit_terms(train, max_ratio, gate=False)
    open_terms = {k: v["range"] for k, v in open_fit.items()}
    if written != {k: v["range"] for k, v in fitted.items()}:
        print("주의: size.toml의 범위가 지금 기록으로 맞춘 값과 다르다 — `python -m domains.agent_usage.size --write`로 다시 쓴다\n")
    print(report(records, kn, cut, written, open_terms))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
