"""이전 실수와 피드백 — 백서(whitepaper.md)와 메인 피드백(main/*.md)을 읽고 모양을 검사한다 (2026-11-05 사용자 결정, CLAUDE.md).

글을 고치지 않는다. 읽고, 모양을 검사하고, 색인 표만 다시 쓴다(`index_write`).
- VOCAB()      색인 낱말 목록 — CLAUDE.md "## 색인 낱말" 바로 아래 쉼표 줄 (코드에 따로 박지 않는다)
- entries()    백서의 `### F012 · 제목` 블록 → {id, title, 색인(목록), 그때, 다시 하면, 왜, 출처, 자리}
- mains()      메인 파일마다 {stem, 키워드(목록), 읽는 때, ids [(F 번호, 줄)]}
- check()      오류 문장 목록 (빈 목록이면 통과)
- index()      색인 표 마크다운, index_write()가 백서의 표지 사이를 바꿔 쓴다
- topics(글)   일 설명에 키워드가 들어 있는 메인 파일 이름(늘 common 포함, 정렬)
- find(낱말)   색인 낱말이 겹치는 백서 항목
- labels()     보낸 기록·직접 한 일마다 읽은 것·찾은 낱말·hit·missed (피드백 찾기의 정답, 2026-11-06 사용자 결정)
"""
from __future__ import annotations

import datetime as dt
import json
import re
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDE = HERE / "CLAUDE.md"
WHITEPAPER = HERE / "whitepaper.md"
MAIN_DIR = HERE / "main"
AGENT_USAGE = HERE.parent / "domains" / "agent_usage"
LABELS_OUT = HERE.parent / "out" / "feedback" / "labels.jsonl"  # out/은 git 제외

FIELDS = ("색인", "그때", "다시 하면", "왜", "출처", "자리")
MAIN_MAX = 10               # 메인 파일마다 최대 항목 수 (CLAUDE.md "메인에 올리는 기준")
COMMON = "common"           # 모든 일에 읽는 메인 파일
PLACE_FIXED = ("검사로 졸업", "백서만")
INDEX_START, INDEX_END = "<!-- index:start -->", "<!-- index:end -->"

HEAD = re.compile(r"^### (F\d+) · (.+?)\s*$")
FIELD = re.compile(r"^- ([^:]+): ?(.*)$")
MAIN_LINE = re.compile(r"^- \*\*(F\d+)\*\* (.+)$")


def VOCAB(path: Path = GUIDE) -> list[str]:
    """CLAUDE.md "## 색인 낱말" 절 바로 아래(빈 줄 건너뜀) 쉼표 줄의 낱말."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## 색인 낱말"):
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return [w.strip() for w in nxt.split(",") if w.strip()]
    raise ValueError(f"{path}: '## 색인 낱말' 절 아래에 낱말 줄이 없음")


def _parse(path: Path) -> tuple[list[dict], list[str]]:
    """백서 → (항목 목록, 모양 문제). 항목은 `### F…` 머리에서 다음 `#` 머리까지."""
    items, problems, cur = [], [], None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("#"):
            cur = None
            m = HEAD.match(line)
            if m:
                cur = {"id": m.group(1), "title": m.group(2), "line": n}
                items.append(cur)
            elif line.startswith("### F"):
                problems.append(f"백서 {n}째 줄: 항목 머리는 '### F012 · 제목' 꼴이어야 함")
            continue
        if cur is None or not line.strip():
            continue
        m = FIELD.match(line)
        if not m or m.group(1) not in FIELDS:
            problems.append(f"{cur['id']}: 칸이 아닌 줄 ({n}째 줄) — 칸은 '- 이름: 내용', 이름은 {'·'.join(FIELDS)}")
            continue
        name, value = m.group(1), m.group(2).strip()
        if name in cur:
            problems.append(f"{cur['id']}: '{name}' 칸이 두 번 있음")
            continue
        cur[name] = [w.strip() for w in value.split(",") if w.strip()] if name == "색인" else value
    return items, problems


def entries(path: Path = WHITEPAPER) -> list[dict]:
    """백서 항목 목록 (파일 순서). 칸 이름은 한글 그대로, 색인은 낱말 목록. 빠진 칸은 키가 없다."""
    return [{k: v for k, v in e.items() if k != "line"} for e in _parse(path)[0]]


def mains(main_dir: Path = MAIN_DIR) -> list[dict]:
    """메인 파일마다 {stem, 키워드, 읽는 때(없으면 None), ids [(F 번호, 줄 글)]} (파일 이름 순)."""
    out = []
    for p in sorted(main_dir.glob("*.md")):
        keys, when, ids = None, None, []
        for line in p.read_text(encoding="utf-8").splitlines():
            if keys is None and line.startswith("키워드:"):
                keys = [w.strip() for w in line[len("키워드:"):].split(",") if w.strip()]
            elif when is None and line.startswith("읽는 때:"):
                when = line[len("읽는 때:"):].strip()
            else:
                m = MAIN_LINE.match(line)
                if m:
                    ids.append((m.group(1), line))
        out.append({"stem": p.stem, "키워드": keys if keys is not None else [], "읽는 때": when,
                    "has_keywords": keys is not None, "ids": ids})
    return out


def index(path: Path = WHITEPAPER, guide: Path = GUIDE) -> str:
    """색인 표: 낱말마다 한 줄(VOCAB 순서, 항목 없는 낱말도 0)."""
    items = entries(path)
    rows = ["| 낱말 | 항목 수 | 항목 |", "|---|---:|---|"]
    for w in VOCAB(guide):
        hit = [e for e in items if w in e.get("색인", [])]
        rows.append(f"| {w} | {len(hit)} | {' · '.join(e['id'] + ' ' + e['title'] for e in hit) or '–'} |")
    return "\n".join(rows)


def _index_span(text: str) -> tuple[int, int] | None:
    a, b = text.find(INDEX_START), text.find(INDEX_END)
    if a < 0 or b < a:
        return None
    return a + len(INDEX_START), b


def index_write(path: Path = WHITEPAPER, guide: Path = GUIDE) -> bool:
    """백서의 표지 사이를 index()로 바꿔 쓴다. 바뀌었으면 True."""
    text = path.read_text(encoding="utf-8")
    span = _index_span(text)
    if span is None:
        raise ValueError(f"{path}: 색인 표지({INDEX_START} … {INDEX_END})가 없음")
    new = text[:span[0]] + "\n" + index(path, guide) + "\n" + text[span[1]:]
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def check(path: Path = WHITEPAPER, main_dir: Path = MAIN_DIR, guide: Path = GUIDE) -> list[str]:
    """백서·메인 모양 검사. 오류 문장 목록(빈 목록이면 통과)."""
    vocab = VOCAB(guide)
    items, errors = _parse(path)
    errors = list(errors)
    for w in {w for w in vocab if vocab.count(w) > 1}:
        errors.append(f"색인 낱말 '{w}'가 목록에 두 번 있음 (CLAUDE.md)")
    ms = mains(main_dir)
    stems = {m["stem"] for m in ms}
    # 항목: 여섯 칸, 색인 낱말, 번호, 자리
    prev = 0
    seen = set()
    for e in items:
        eid = e["id"]
        for f in FIELDS:
            if not e.get(f):
                errors.append(f"{eid}: '{f}' 칸이 없거나 비었음")
        for w in e.get("색인", []):
            if w not in vocab:
                errors.append(f"{eid}: 색인 낱말 '{w}'가 목록에 없음 — CLAUDE.md '색인 낱말'에서 고르거나 목록에 더한다")
        if eid in seen:
            errors.append(f"{eid}: 번호가 겹침")
        seen.add(eid)
        num = int(eid[1:])
        if num <= prev:
            errors.append(f"{eid}: 번호가 파일 순서대로 늘지 않음 (앞 항목 F{prev:03d})")
        prev = max(prev, num)
        place = e.get("자리", "")
        if place and place not in PLACE_FIXED:
            m = re.fullmatch(r"메인 (\S+)", place)
            if not m:
                errors.append(f"{eid}: 자리 '{place}'는 '메인 <파일>' · '검사로 졸업' · '백서만' 중 하나")
            elif m.group(1) not in stems:
                errors.append(f"{eid}: 자리의 메인 파일 main/{m.group(1)}.md가 없음")
    by_id = {e["id"]: e for e in items}
    # 메인 파일: ≤10, 키워드·읽는 때 줄, 줄의 번호가 백서에 있고 자리가 이 파일
    if COMMON not in stems:
        errors.append(f"main/{COMMON}.md가 없음 (모든 일에 읽는 파일)")
    placed: dict[str, set[str]] = {}
    for m in ms:
        name = f"main/{m['stem']}.md"
        if len(m["ids"]) > MAIN_MAX:
            errors.append(f"{name}: 항목 {len(m['ids'])}개 — 최대 {MAIN_MAX}개 (하나를 내리고 백서 자리를 고친다)")
        if not m["has_keywords"] or not m["키워드"]:
            errors.append(f"{name}: '키워드:' 줄이 없거나 비었음")
        if not m["읽는 때"]:
            errors.append(f"{name}: '읽는 때:' 줄이 없거나 비었음")
        ids = [i for i, _ in m["ids"]]
        for i in {i for i in ids if ids.count(i) > 1}:
            errors.append(f"{name}: {i}가 두 번 있음")
        placed[m["stem"]] = set(ids)
        for i in ids:
            e = by_id.get(i)
            if e is None:
                errors.append(f"{name}: {i}가 백서에 없음")
            elif e.get("자리") != f"메인 {m['stem']}":
                errors.append(f"{name}: {i}의 백서 자리가 '{e.get('자리')}' — '메인 {m['stem']}'이어야 함")
    for e in items:
        m = re.fullmatch(r"메인 (\S+)", e.get("자리", ""))
        if m and m.group(1) in placed and e["id"] not in placed[m.group(1)]:
            errors.append(f"{e['id']}: 자리가 '메인 {m.group(1)}'인데 main/{m.group(1)}.md에 없음")
    # 색인 표가 최신인가
    text = path.read_text(encoding="utf-8")
    span = _index_span(text)
    if span is None:
        errors.append(f"백서에 색인 표지({INDEX_START} … {INDEX_END})가 없음")
    elif text[span[0]:span[1]].strip() != index(path, guide).strip():
        errors.append("백서의 색인 표가 최신이 아님 — `python -m feedback index --write`")
    return errors


def topics(text: str, main_dir: Path = MAIN_DIR) -> list[str]:
    """일 설명(task 문장·지시서 글)에 키워드가 하나라도 들어 있는 메인 파일 이름. 늘 common 포함, 정렬.
    매칭은 단순 부분 문자열(대소문자 무시)."""
    low = (text or "").lower()
    out = {COMMON}
    for m in mains(main_dir):
        if any(k.lower() in low for k in m["키워드"]):
            out.add(m["stem"])
    return sorted(out)


def find(words, path: Path = WHITEPAPER) -> list[dict]:
    """색인 낱말이 하나라도 겹치는 백서 항목 (파일 순서)."""
    want = set(words)
    return [e for e in entries(path) if want & set(e.get("색인", []))]


def main_files(main_dir: Path = MAIN_DIR) -> list[str]:
    """메인 파일 이름(stem) 목록."""
    return sorted(p.stem for p in main_dir.glob("*.md"))


def _plain(x):
    """TOML 값 → JSON에 쓸 값 (날짜는 ISO 글)."""
    return x.isoformat() if isinstance(x, (dt.date, dt.datetime)) else x


def labels(dispatch_path: Path = AGENT_USAGE / "dispatches.toml", direct_path: Path = AGENT_USAGE / "direct.toml") -> list[dict]:
    """피드백 찾기의 정답 (2026-11-06 사용자 결정): feedback.hit 칸이 있는 기록마다 한 행.
    {id, kind(dispatch|direct), project, date, task, read, searched, hit, missed}.
    missed는 F 번호 목록 — review.missed가 '없음: 이유'면 [], 아직 안 적었으면(안 끝난 기록) None.
    기록 파일은 tomllib로 바로 읽는다(domains.agent_usage를 불러오면 서로 불러오는 고리가 생긴다)."""
    out = []
    for kind, path in (("dispatch", dispatch_path), ("direct", direct_path)):
        if not path.is_file():
            continue
        for d in tomllib.loads(path.read_text(encoding="utf-8")).get(kind, []):
            f = d.get("feedback")
            if not (isinstance(f, dict) and "hit" in f):
                continue
            missed = d.get("review", {}).get("missed") if isinstance(d.get("review"), dict) else None
            out.append({"id": d.get("id"), "kind": kind, "project": d.get("project"), "date": _plain(d.get("date")),
                        "task": d.get("task"), "read": f.get("read", []), "searched": f.get("searched", []), "hit": f["hit"],
                        "missed": missed if isinstance(missed, list) else ([] if isinstance(missed, str) else None)})
    return out


def labels_write(out: Path = LABELS_OUT, **paths) -> int:
    """labels()를 JSON Lines로 쓴다(한 줄 = 한 기록). 쓴 줄 수."""
    rows = labels(**paths)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return len(rows)
