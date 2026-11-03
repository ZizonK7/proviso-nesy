"""하위 에이전트가 쓴 분야 파일(out/far_fields/agent_gen/<slug>.json)의 모양 검사.

  python -m domains.far_fields.check_agent_json [slug ...]     (없으면 폴더 전체)

생성 배치와 같은 JSON 모양(generate.GEN_SCHEMA)인지, 경험칙이 12개인지, 모양 id가 단어장 안인지, 칸이 비지 않았는지 본다.
문제가 있으면 1로 끝난다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .generate import OUT, PER_FIELD
from .shapes import SHAPES

DIR = OUT / "agent_gen"
FIELDS2 = Path(__file__).with_name("fields2.json")
KEYS = ("rule", "why", "breaks", "general", "shapes", "confidence")


def problems(path: Path, ko: str | None) -> list[str]:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"읽기 실패: {e}"]
    out = []
    if set(d) != {"field", "items"}:
        out.append(f"맨 위 칸은 field, items 둘이어야 함: {sorted(d)}")
    if ko and d.get("field") != ko:
        out.append(f"field가 분야 이름과 다름: {d.get('field')!r} ≠ {ko!r}")
    items = d.get("items", [])
    if len(items) != PER_FIELD:
        out.append(f"경험칙 {len(items)}개 (12개여야 함)")
    for i, it in enumerate(items, 1):
        if set(it) != set(KEYS):
            out.append(f"[{i}] 칸이 다름: {sorted(it)}")
            continue
        for k in ("rule", "why", "breaks", "general"):
            if not isinstance(it[k], str) or not it[k].strip():
                out.append(f"[{i}] {k} 비어 있음")
        if not (isinstance(it["shapes"], list) and 1 <= len(it["shapes"]) <= 3 and set(it["shapes"]) <= set(SHAPES)):
            out.append(f"[{i}] shapes는 단어장 id 1~3개: {it['shapes']}")
        if it["confidence"] not in ("높음", "중간", "낮음"):
            out.append(f"[{i}] confidence: {it['confidence']!r}")
    return out


def main(slugs: list[str]) -> int:
    names = {f["slug"]: f["ko"] for f in json.loads(FIELDS2.read_text(encoding="utf-8"))}
    paths = [DIR / f"{s}.json" for s in slugs] if slugs else sorted(DIR.glob("*.json"))
    bad = 0
    for p in paths:
        errs = problems(p, names.get(p.stem))
        if errs:
            bad += 1
            print(f"{p.stem}: " + " / ".join(errs[:5]))
    print(f"{len(paths)}개 파일 검사, 문제 {bad}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
