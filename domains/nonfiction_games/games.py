"""게임 기록(games.toml)을 읽고 검사하고, 대 보기 표를 보여 준다.

사용법 (저장소 루트):
  python -m domains.nonfiction_games.games     기록 검사 + 게임별 대 보기 표

기록은 덧붙인 순서대로 둔다. 가설 검사(checks.py)는 이 순서로 '가설을 세운 뒤의 기록'을 고른다.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from proviso import schema

HERE = Path(__file__).resolve().parent
SITUATION_VALUES = ("예", "아니오", "일부", "모름")
JUDGMENTS = ("크게 성공", "성공", "보통", "실패", "모름")
JUDGED_BY = ("user", "public")
BASIS_KINDS = ("비문학", "문학")
SUCCESS = ("크게 성공", "성공")


def load(path: Path = HERE / "games.toml") -> list[dict]:
    return tomllib.loads(path.read_text(encoding="utf-8")).get("game", [])


def situation(g: dict, state_id: str) -> str:
    return g.get("situation", {}).get(state_id, "모름")


def judgment(g: dict) -> str:
    return g.get("outcome", {}).get("judgment", "모름")


def _kind(knowledge: schema.Knowledge, node_id: str) -> str | None:
    node = knowledge.nodes.get(node_id)
    return node.kind if node else None


def validate(records: list[dict], knowledge: schema.Knowledge) -> list[str]:
    """기록의 문제 목록. 상태·사실 id는 지식 파일에 있어야 한다."""
    errors, seen = [], set()
    for g in records:
        gid = g.get("id", "?")
        if gid in seen:
            errors.append(f"id 중복: {gid}")
        seen.add(gid)
        for key in ("name", "basis", "basis_kind", "facts", "situation", "outcome"):
            if not g.get(key):
                errors.append(f"{gid}: '{key}' 칸이 비어 있음")
        if g.get("basis_kind") and g["basis_kind"] not in BASIS_KINDS:
            errors.append(f"{gid}: basis_kind는 {BASIS_KINDS} 중 하나여야 함")
        for fid in g.get("facts", []):
            if _kind(knowledge, fid) != "fact":
                errors.append(f"{gid}: '{fid}'는 지식 파일에 있는 사실이 아님")
        for sid, value in g.get("situation", {}).items():
            if _kind(knowledge, sid) != "state":
                errors.append(f"{gid}: '{sid}'는 지식 파일에 있는 상태가 아님")
            if value not in SITUATION_VALUES:
                errors.append(f"{gid}.{sid}: 값은 {SITUATION_VALUES} 중 하나여야 함")
        o = g.get("outcome", {})
        if o.get("judgment") not in JUDGMENTS:
            errors.append(f"{gid}: outcome.judgment는 {JUDGMENTS} 중 하나여야 함")
        if o.get("judged_by") not in JUDGED_BY:
            errors.append(f"{gid}: outcome.judged_by는 {JUDGED_BY} 중 하나여야 함")
        if not o.get("basis"):
            errors.append(f"{gid}: outcome.basis(판정 근거)가 비어 있음")
    return errors


def table(records: list[dict], states: list[str]) -> str:
    """게임 × 상태 표. 예=●, 일부=◐, 아니오=·, 모름=?"""
    mark = {"예": "●", "일부": "◐", "아니오": "·", "모름": "?"}
    head = "| 게임 | 바탕 | 반응 | " + " | ".join(s.removeprefix("S_") for s in states) + " |"
    rule = "|---|---|---|" + "---|" * len(states)
    rows = [f"| {g['name']} | {g['basis_kind']} | {judgment(g)} | "
            + " | ".join(mark[situation(g, s)] for s in states) + " |" for g in records]
    return "\n".join([head, rule, *rows])


def main() -> int:
    knowledge = schema.load(HERE / "knowledge.toml")
    records = load()
    errors = validate(records, knowledge)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"기록 문제 없음 ({len(records)}건)\n")
    states = [n.id for n in knowledge.of("state")]
    print(table(records, states))
    return 0


if __name__ == "__main__":
    sys.exit(main())
