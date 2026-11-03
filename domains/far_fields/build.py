"""생성·검토 결과(out/far_fields/*.jsonl)를 knowledge.toml로 바꾼다.

  python -m domains.far_fields.build

읽는 것: gen_*.jsonl·test_gen.jsonl·haiku_gen.jsonl(생성), rev_*.jsonl(검토). 같은 custom_id는 뒤 파일이 이긴다.
조각 하나 = 가설 노드 하나. text는 분야 이름 없는 일반화, 분야 칸(field·rule·why·breaks·confidence)에 구체 경험칙.
검토 판정은 [[judgment]] source = "ai"로 붙는다(가장 가벼운 출처).
"""
from __future__ import annotations

import json
from pathlib import Path

from .shapes import SHAPES

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "out" / "far_fields"
GEN_DATE = "2026-11-03"

HEADER = '''# 먼 분야 경험 논리 — 창의 연결의 재료
# 자동 생성 파일: 손으로 고치지 말고 build.py를 다시 돌린다(python -m domains.far_fields.build). 설명은 같은 폴더 CLAUDE.md.
# 전부 AI가 만들거나 모은 것이다. 사용자 경험이 아니고, 진료·안전 지침이 아니다.
# 조각(가설)의 text는 분야 이름이 없는 일반화. field·rule·why·breaks·confidence는 이 분야 칸(구체 경험칙).

[domain]
id = "far_fields"
name = "먼 분야 경험 논리 (창의 연결 재료)"

[[goal]]
id = "G_creative"
text = "생각지 못한 연결로 새 생각을 낸다: 기존 논리를 생각지 못한 방식으로 잇는다"
note = "사용자 2026-11-03 '창의성은 기존 논리를 생각지 못한 방식으로 연결하는 과정이다'"

[[goal]]
id = "G_far_material"
text = "사용자가 전혀 모르거나 하지도 않을 분야의 논리를 연결 재료로 쌓아 둔다. 나중에 그 분야를 실제로 하게 되면 지우거나 그 위에서 시작한다"
parent = "G_creative"
note = "사용자 2026-11-03"

[[goal]]
id = "G_try_absurd"
text = "말도 안 돼 보이는 연결도 충분히 고민한다. 충분히 고민해도 안 되면 포기하되, 어디까지 해 봤는지 남긴다"
parent = "G_creative"
note = "사용자 2026-11-03 (기록을 남기는 부분은 부모 세션 제안)"
'''


UNREVIEWED_PLAN = ("검토하지 않은 AI 생성분(사용자 2026-11-03: 구조만 정확하면 나중에 하나씩 고친다). "
                   "쓰거나 연결에 뽑힐 때 판정을 붙이고, 그 분야를 실제로 하게 되면 사용자 실사용으로 판정한다")


# 묶음(fields*.json의 group) → 나눈 파일 이름 knowledge-<이름>.toml
GROUP_FILE = {
    "바다": "sea", "물·강": "river", "땅·농사": "farm", "숲·산·눈": "forest", "하늘": "sky", "지하·광물": "under",
    "불·금속": "fire", "공예·섬유": "craft", "음식·발효": "food", "동물": "animal", "사람 다루기": "people",
    "의례·전통": "rite", "공연·예술": "stage", "기계·현대기술": "machine", "건설": "build", "스포츠": "sport",
    "웹 조사 10개 분야": "web", "학문": "academia", "IT": "it", "금융": "finance",
}
PART_HEADER = """# 먼 분야 경험 논리 — 묶음 '{group}'의 조각과 판정
# 자동 생성 파일: 손으로 고치지 말고 build.py를 다시 돌린다. 분야 뼈대(domain·목표·모양)는 knowledge.toml, 설명은 같은 폴더 CLAUDE.md.

"""


def q(s: str) -> str:
    """TOML 기본 문자열 (JSON 문자열 표기는 TOML에서도 유효하다)."""
    return json.dumps(s, ensure_ascii=False)


def _read(pattern: str) -> dict[str, dict]:
    recs = {}
    for path in sorted(OUT.glob(pattern)):
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("data"):
                recs[r["custom_id"].split("-", 1)[1]] = r["data"]
    return recs


AGENT_SLUGS: set[str] = set()
THIRD = {f["slug"] for f in json.loads((HERE / "fields3.json").read_text(encoding="utf-8"))}  # 3차: 학문·IT·금융 (2026-11-04)


def _read_agent() -> dict[str, dict]:
    """2차: Claude Code 하위 에이전트가 쓴 분야 파일(out/far_fields/agent_gen/<slug>.json). 검토 없음(사용자 지시 2026-11-03)."""
    recs = {}
    for path in sorted((OUT / "agent_gen").glob("*.json")):
        recs[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    AGENT_SLUGS.update(recs)
    return recs


def _source(slug: str, it: dict) -> str:
    if slug in AGENT_SLUGS:
        if slug in THIRD:
            return "AI 생성(Opus 5.5, Claude Code 서브에이전트) 3차 2026-11-04, 출처 없음(모델 지식), 검토 없음"
        return f"AI 생성(Opus 5.5, Claude Code 서브에이전트) {GEN_DATE}, 출처 없음(모델 지식), 검토 없음"
    if not slug.startswith("haiku_"):
        return f"AI 생성: claude-opus-5-5 배치 {GEN_DATE}, 출처 없음(모델 지식)"
    kind = {"열람": "원문 열람", "검색 요약": "검색 요약만", "모델 지식": "출처 없음(모델 지식)"}[it["opened"]]
    return f"웹 조사: Haiku 5.5 'searching' {GEN_DATE}, {kind} — {it['source']}"


def build() -> tuple[str, dict]:
    gens = _read("test_gen.jsonl") | _read("gen_*.jsonl") | _read("haiku_gen.jsonl") | _read_agent()
    revs = _read("rev_*.jsonl")
    fields = {f["slug"]: f for name in ("fields.json", "fields2.json", "fields3.json")
              for f in json.loads((HERE / name).read_text(encoding="utf-8"))}
    out = [HEADER, "\n# ---------- 모양 (조각이 조건으로 공유하는 상황) ----------"]
    for sid, text in SHAPES.items():
        out.append(f"[[state]]\nid = {q(sid)}\ntext = {q(text)}\n")
    out.append("# 조각과 판정은 묶음별 파일 knowledge-<묶음>.toml에 있다 (2026-11-04 사용자 결정 '분야 별로 나누는 게 좋을거 같아'). 코어가 같이 읽는다")
    parts: dict[str, list[str]] = {}  # 파일 이름 → 조각 줄
    part_j: dict[str, list[str]] = {}  # 파일 이름 → 판정 줄
    judgments, stats = [], {"fields": 0, "agent_fields": 0, "pieces": 0, "reviewed": 0, "verdict": {}, "general_bad": 0, "no_review": []}
    order = [s for s in fields if s in gens] + sorted(s for s in gens if s not in fields)
    for slug in order:
        data = gens[slug]
        group = fields[slug]["group"] if slug in fields else "웹 조사 10개 분야"
        rev = {r["n"]: r for r in (revs.get(slug) or {}).get("reviews", [])}
        if slug not in revs and slug not in AGENT_SLUGS:
            stats["no_review"].append(slug)
        stats["fields"] += 1
        stats["agent_fields"] += slug in AGENT_SLUGS
        fname = f"knowledge-{GROUP_FILE[group]}.toml"
        out_p = parts.setdefault(fname, [])
        judgments = part_j.setdefault(fname, [])
        out_p.append(f"# {data['field']} ({group})")
        for n, it in enumerate(data["items"], 1):
            nid = f"H_{slug}_{n:02d}"
            r = rev.get(n)
            shapes = [s for s in ((r or {}).get("shapes") or it.get("shapes") or []) if s in SHAPES]  # 검토가 고친 목록이 먼저
            text = it["general"]
            fixed = (r or {}).get("general_fix", "").strip()
            if fixed and (not r["general_ok"] or not text.strip()):
                text = fixed
            lines = [
                "[[hypothesis]]", f"id = {q(nid)}", f"text = {q(text)}", f"source = {q(_source(slug, it))}",
                f"field = {q(data['field'])}", f"group = {q(group)}", f"rule = {q(it['rule'])}",
                f"why = {q(it['why'])}", f"breaks = {q(it['breaks'])}", f"confidence = {q(it['confidence'])}",
            ]
            if slug in AGENT_SLUGS:
                lines.append(f"test_plan = {q(UNREVIEWED_PLAN)}")
            if text != it["general"]:
                lines.append(f"general_original = {q(it['general'])}")
            if shapes:
                lines.append("conditions = [" + ", ".join(q(s) for s in shapes) + "]")
            out_p.append("\n".join(lines) + "\n")
            stats["pieces"] += 1
            if r:
                stats["reviewed"] += 1
                stats["verdict"][r["verdict"]] = stats["verdict"].get(r["verdict"], 0) + 1
                note = f"Opus 5.5 검토 배치: {r['note']}"
                if not r["general_ok"]:
                    stats["general_bad"] += 1
                    note += " [일반화 문장 문제 있음]"
                judgments.append(f"[[judgment]]\nof = {q(nid)}\nsource = \"ai\"\nverdict = {q(r['verdict'])}\n"
                                 f"date = {GEN_DATE}\nnote = {q(note)}\n")
    files = {"knowledge.toml": "\n".join(out) + "\n"}
    for fname in sorted(parts):
        head = PART_HEADER.format(group=next(g for g, c in GROUP_FILE.items() if f"knowledge-{c}.toml" == fname))
        body = parts[fname] + (["# ---------- 판정 기록 (AI 검토) ----------"] + part_j[fname] if part_j[fname] else [])
        files[fname] = head + "\n".join(body)
    return files, stats


if __name__ == "__main__":
    files, stats = build()
    for old in HERE.glob("knowledge-*.toml"):  # 묶음이 바뀌어도 낡은 파일이 남지 않게
        if old.name not in files:
            old.unlink()
    for fname, text in files.items():
        (HERE / fname).write_text(text, encoding="utf-8")
    stats["files"] = len(files)
    print(json.dumps(stats, ensure_ascii=False))
