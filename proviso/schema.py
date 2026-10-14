"""지식 파일(TOML)을 읽고 검사한다.

지식은 노드의 모음이다. 노드 종류: 목표, 상태, 사실, 관찰, 가설, 규칙.
노드끼리는 id로 서로를 가리키고, 그 참조가 그래프의 연결선이 된다.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("goal", "state", "fact", "observation", "hypothesis", "rule")

KIND_LABEL = {
    "goal": "목표",
    "state": "상태",
    "fact": "사실",
    "observation": "관찰",
    "hypothesis": "가설",
    "rule": "규칙",
}

RULE_STATUS = {"hypothesis": "가설", "verified": "검증됨", "retired": "이전 버전"}

REQUIRED = {
    "goal": ("text",),
    "state": ("text",),
    "fact": ("text", "checked", "source"),
    "observation": ("text", "source"),
    "hypothesis": ("text", "source"),
    "rule": ("method", "reason", "status", "version"),
}

# (노드 종류, 필드) → 그 필드가 가리킬 수 있는 노드 종류
REFS = {
    ("goal", "parent"): {"goal"},
    ("state", "serves"): {"goal"},
    ("rule", "serves"): {"goal"},
    ("rule", "conditions"): {"state", "fact", "observation"},
    ("rule", "results"): {"state"},
    ("rule", "evidence"): {"observation", "fact"},
    ("rule", "side_effects"): {"hypothesis", "state"},
    ("rule", "exceptions"): {"state"},
    ("rule", "replaced_by"): {"rule"},
    ("hypothesis", "harms"): {"goal"},
    ("hypothesis", "accepted_for"): {"goal"},
    ("state", "harms"): {"goal"},
    ("state", "accepted_for"): {"goal"},
    ("fact", "harms"): {"goal"},
    ("fact", "accepted_for"): {"goal"},
}


@dataclass
class Node:
    kind: str
    id: str
    data: dict

    @property
    def text(self) -> str:
        return self.data.get("text") or self.data.get("method", "")

    def refs(self, field: str) -> list[str]:
        value = self.data.get(field, [])
        return [value] if isinstance(value, str) else list(value)


@dataclass
class Knowledge:
    domain: dict
    nodes: dict[str, Node]
    duplicates: list[str] = field(default_factory=list)

    def of(self, kind: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]


def load(path: Path) -> Knowledge:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    nodes: dict[str, Node] = {}
    duplicates = []
    for kind in KINDS:
        for item in raw.get(kind, []):
            node = Node(kind, item.get("id", ""), item)
            if node.id in nodes:
                duplicates.append(node.id)
            nodes[node.id] = node
    return Knowledge(raw.get("domain", {}), nodes, duplicates)


def validate(kn: Knowledge) -> list[str]:
    """문제 목록을 돌려준다. 비어 있으면 통과."""
    errors = [f"id 중복: {d}" for d in kn.duplicates]
    for node in kn.nodes.values():
        if not node.id:
            errors.append(f"{KIND_LABEL[node.kind]}에 id가 없음: {node.data}")
        for field in REQUIRED[node.kind]:
            if field not in node.data:
                errors.append(f"{node.id}: '{field}' 칸이 비어 있음")
        if node.kind == "rule" and node.data.get("status") not in RULE_STATUS:
            errors.append(f"{node.id}: status는 {list(RULE_STATUS)} 중 하나여야 함")
        for (kind, field), allowed in REFS.items():
            if kind != node.kind:
                continue
            for ref in node.refs(field):
                target = kn.nodes.get(ref)
                if target is None:
                    errors.append(f"{node.id}.{field}: 없는 id '{ref}'")
                elif target.kind not in allowed:
                    errors.append(
                        f"{node.id}.{field}: '{ref}'는 {KIND_LABEL[target.kind]}인데 "
                        f"{'/'.join(KIND_LABEL[k] for k in allowed)}만 올 수 있음"
                    )
    errors += _goal_cycles(kn)
    return errors


def _goal_cycles(kn: Knowledge) -> list[str]:
    errors = []
    for goal in kn.of("goal"):
        seen, cur = set(), goal
        while cur is not None:
            if cur.id in seen:
                errors.append(f"목표 위계가 돌고 돎: {goal.id}")
                break
            seen.add(cur.id)
            parent = cur.data.get("parent")
            cur = kn.nodes.get(parent) if parent else None
    return errors
