"""논리집 데이터를 EDA(탐색적 데이터 분석)용 표(CSV)로 펼친다. 표준 라이브러리만.

사용법 (저장소 루트):
  python -m eda.export [--out out/eda]

읽는 것 (저장소 안의 파일만, 읽기 전용):
  - domains/<분야>/knowledge.toml (+ 나눈 파일 knowledge-*.toml) — proviso.schema.load로
  - domains/agent_usage/dispatches.toml, direct.toml — 하위 에이전트·직접 한 일 기록(예측 → 실측 → 돌아보기)
  - feedback/whitepaper.md, feedback/main/*.md — 피드백 백서와 메인

쓰는 표 (out/eda/, git 제외 — 저장소 파일에서 언제든 다시 만든다):
  nodes.csv            노드 한 줄 = 한 행. 공통 칸 + 분야 칸(있는 것 전부). 목록 칸은 '|'로 잇고 n_<칸>에 개수
  edges.csv            노드 사이 참조 한 개 = 한 행 (src → dst, field = 칸 이름: conditions·evidence·serves …)
  effects.csv          효과 칸 하나 = 한 행 (on·op·range·when·dir)
  judgments.csv        판정 기록 하나 = 한 행
  dispatches.csv       보낸 일 기록 하나 = 한 행. 중첩 칸은 'actual.minutes'처럼 점으로, [하한, 상한]은 _lo·_hi로
  dispatch_rules.csv   기록 × 규칙 (role: predicted.rules · predicted.hypotheses · review.wrong · review.hypotheses)
  dispatch_turns.csv   기록 × 도구 종류별 턴 길이 ([dispatch.turns])
  direct.csv           직접 한 일 기록 (dispatches와 같은 펼침)
  feedback.csv         백서 항목 하나 = 한 행 (출처 종류·날짜는 '출처' 글에서 뽑음)
  feedback_index.csv   항목 × 색인 낱말
  feedback_main.csv    메인 파일 × 항목
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import feedback  # noqa: E402
from proviso import schema  # noqa: E402

DEFAULT_OUT = ROOT / "out" / "eda"
SEP = "|"  # 목록 칸을 한 칸에 넣을 때 쓰는 구분자

# 노드 표에서 앞에 둘 공통 칸 (나머지 분야 칸은 이름 순서로 뒤에)
NODE_FRONT = ("domain", "part", "kind", "id", "alive", "status", "version", "text", "source", "checked", "date",
              "n_checks", "n_judgments", "n_effects", "in_degree", "out_degree")
# 기록 표에서 펼치지 않고 따로 표를 만들거나 버리는 칸
DISPATCH_SKIP = {"turns", "git.dirty_hashes"}


def _cell(value) -> str | int | float | bool:
    """CSV 한 칸으로. 날짜는 ISO, 목록은 '|'로 잇는다."""
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return SEP.join(str(_cell(v)) for v in value)
    if isinstance(value, dict):
        return SEP.join(f"{k}={_cell(v)}" for k, v in value.items())
    return value


def _write(path: Path, rows: list[dict], front: tuple[str, ...] = ()) -> int:
    """행 목록을 CSV로. 칸은 front 순서 + 나머지 이름 순. 엑셀에서 한글이 안 깨지게 utf-8-sig."""
    keys = {k for r in rows for k in r}
    cols = [c for c in front if c in keys] + sorted(keys - set(front))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(v) for k, v in r.items()})
    return len(rows)


# ---------------------------------------------------------------- 논리집 (knowledge)

def domains() -> list[str]:
    return sorted(p.parent.name for p in (ROOT / "domains").glob("*/knowledge.toml"))


def _part_of(domain: str) -> dict[str, str]:
    """노드 id → 그 노드가 든 파일 이름 (나눈 파일이 있는 분야용)."""
    out = {}
    folder = ROOT / "domains" / domain
    for f in [folder / "knowledge.toml", *sorted(folder.glob(schema.PART_GLOB))]:
        raw = tomllib.loads(f.read_text(encoding="utf-8"))
        for kind in schema.KINDS:
            for item in raw.get(kind, []):
                out.setdefault(item.get("id", ""), f.name)
    return out


def knowledge_tables() -> dict[str, list[dict]]:
    nodes, edges, effects, judgments = [], [], [], []
    for domain in domains():
        kn = schema.load(ROOT / "domains" / domain / "knowledge.toml")
        part = _part_of(domain) if len(kn.parts) > 1 else {}
        d_edges = []
        for node in kn.nodes.values():
            for (kind, field), _allowed in schema.REFS.items():
                if kind != node.kind:
                    continue
                for ref in node.refs(field):
                    target = kn.nodes.get(ref)
                    d_edges.append({"domain": domain, "src": node.id, "src_kind": node.kind, "field": field,
                                    "dst": ref, "dst_kind": target.kind if target else ""})
        out_deg, in_deg = {}, {}
        for e in d_edges:
            out_deg[e["src"]] = out_deg.get(e["src"], 0) + 1
            in_deg[e["dst"]] = in_deg.get(e["dst"], 0) + 1
        edges += d_edges

        for node in kn.nodes.values():
            row = {"domain": domain, "part": part.get(node.id, kn.parts[0]), "kind": node.kind, "id": node.id,
                   "text": node.text, "in_degree": in_deg.get(node.id, 0), "out_degree": out_deg.get(node.id, 0)}
            if node.kind in schema.CLAIMS:
                row["alive"] = schema.alive(node)
                row["status"] = node.data.get("status", "hypothesis")
                row["n_checks"] = len(schema.check_names(node))
                row["n_judgments"] = len(kn.judgments_of(node.id))
            for key, value in node.data.items():
                if key in ("id", "text", "effect"):
                    continue
                if isinstance(value, list):
                    row[f"n_{key}"] = len(value)
                if key in row and row[key] == value:
                    continue
                row[key if key not in row else f"data.{key}"] = value
            fx = node.data.get("effect", [])
            row["n_effects"] = len(fx)
            for i, e in enumerate(fx):
                rng = e.get("range", [None, None])
                effects.append({"domain": domain, "node": node.id, "kind": node.kind, "i": i, "on": e.get("on"),
                                "op": e.get("op"), "range_lo": rng[0] if rng else None,
                                "range_hi": rng[1] if rng and len(rng) > 1 else None, "dir": e.get("dir"),
                                "when": e.get("when"), "count": e.get("count"), "analog": e.get("analog"),
                                "reason": e.get("reason")})
            nodes.append(row)
        for j in kn.judgments:
            judgments.append({"domain": domain, **j})
    return {"nodes": nodes, "edges": edges, "effects": effects, "judgments": judgments}


# ---------------------------------------------------------------- 작업 기록 (agent_usage)

def flatten(record: dict, prefix: str = "") -> dict:
    """중첩 칸을 'a.b'로 펴고, 숫자 둘짜리 목록([하한, 상한])은 _lo·_hi로 가른다."""
    out = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if name in DISPATCH_SKIP:
            continue
        if isinstance(value, dict):
            out.update(flatten(value, name + "."))
        elif (isinstance(value, list) and len(value) == 2
              and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)):
            out[name + "_lo"], out[name + "_hi"] = value
        else:
            out[name] = value
    return out


def _hit(rec: dict, what: str):
    """실측이 예측 구간 안에 들었나 (둘 중 하나라도 없으면 None)."""
    pred = rec.get("predicted", {}).get(what)
    act = rec.get("actual", {}).get(what)
    if not (isinstance(pred, list) and len(pred) == 2) or not isinstance(act, (int, float)):
        return None
    return pred[0] <= act <= pred[1]


def dispatch_tables() -> dict[str, list[dict]]:
    folder = ROOT / "domains" / "agent_usage"
    recs = tomllib.loads((folder / "dispatches.toml").read_text(encoding="utf-8")).get("dispatch", [])
    rows, rules, turns = [], [], []
    for r in recs:
        row = {"id": r.get("id"), **flatten(r)}
        for what in ("minutes", "turns", "tokens_m"):
            row[f"hit.{what}"] = _hit(r, what)
        rows.append(row)
        for role in ("predicted.rules", "predicted.hypotheses", "review.wrong", "review.hypotheses"):
            sect, key = role.split(".")
            for rid in r.get(sect, {}).get(key, []) or []:
                rules.append({"id": r.get("id"), "batch": r.get("batch"), "date": r.get("date"), "role": role,
                              "rule": rid})
        for tool, t in (r.get("turns") or {}).items():
            if isinstance(t, dict):
                turns.append({"id": r.get("id"), "tool": tool, **t})
    directs = tomllib.loads((folder / "direct.toml").read_text(encoding="utf-8")).get("direct", [])
    return {"dispatches": rows, "dispatch_rules": rules, "dispatch_turns": turns,
            "direct": [{"id": d.get("id"), **flatten(d)} for d in directs]}


# ---------------------------------------------------------------- 피드백

SOURCE_KINDS = ("사용자", "실측", "AI")
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def feedback_tables() -> dict[str, list[dict]]:
    rows, idx = [], []
    for e in feedback.entries():
        src = e.get("출처", "")
        kind = next((k for k in SOURCE_KINDS if src.startswith(k)), "기타")
        m = DATE.search(src)
        place = e.get("자리", "")
        rows.append({"id": e["id"], "num": int(e["id"][1:]), "title": e["title"], "source_kind": kind,
                     "date": m.group(0) if m else "", "place": place,
                     "place_kind": "메인" if place.startswith("메인") else place,
                     "n_index": len(e.get("색인", [])), **{k: v for k, v in e.items() if k not in ("id", "title")}})
        for w in e.get("색인", []):
            idx.append({"id": e["id"], "word": w})
    main = [{"main": m["stem"], "id": fid, "pos": i} for m in feedback.mains() for i, (fid, _line) in enumerate(m["ids"])]
    return {"feedback": rows, "feedback_index": idx, "feedback_main": main}


FRONTS = {
    "nodes": NODE_FRONT,
    "edges": ("domain", "src", "src_kind", "field", "dst", "dst_kind"),
    "effects": ("domain", "node", "kind", "i", "on", "op", "range_lo", "range_hi", "dir", "when"),
    "judgments": ("domain", "of", "source", "verdict", "date"),
    "dispatches": ("id", "project", "batch", "date", "model", "effort", "agent", "round", "task"),
    "dispatch_rules": ("id", "batch", "date", "role", "rule"),
    "dispatch_turns": ("id", "tool", "n"),
    "direct": ("id", "project", "date", "task"),
    "feedback": ("id", "num", "title", "source_kind", "date", "place_kind", "place"),
}


def export(out: Path = DEFAULT_OUT) -> dict[str, int]:
    """모든 표를 out에 쓰고 {표 이름: 행 수}를 돌려준다. 지난 결과는 지우고 다시 쓴다(F064)."""
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.csv"):
        old.unlink()
    tables = {**knowledge_tables(), **dispatch_tables(), **feedback_tables()}
    return {name: _write(out / f"{name}.csv", rows, FRONTS.get(name, ())) for name, rows in tables.items()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="논리집 데이터를 EDA용 CSV로 펼친다")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="쓸 폴더 (기본 out/eda)")
    args = ap.parse_args(argv)
    counts = export(args.out)
    print(f"{args.out} 에 썼다:")
    for name, n in counts.items():
        print(f"  {name}.csv  {n}행")
    return 0


if __name__ == "__main__":
    sys.exit(main())
