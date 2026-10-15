"""논리집 조회. LLM이 도구로 쓰는 읽기 기능 (원안의 query_logic_graph).

결과는 LLM이 읽을 한국어 텍스트로 돌려준다.
"""
from __future__ import annotations

from pathlib import Path

from . import schema
from .schema import KIND_LABEL, REFS, RULE_STATUS, Knowledge, Node

# 필드 → (정방향 설명, 역방향 설명)
FIELD_LABEL = {
    "parent": ("상위 목표", "하위 목표"),
    "serves": ("이바지하는 목표", "이 목표를 위한 것"),
    "conditions": ("조건", "이걸 조건으로 쓰는 규칙"),
    "results": ("결과", "이 결과를 내는 규칙"),
    "evidence": ("근거", "이걸 근거로 삼는 것"),
    "against": ("반대 근거", "이걸 반대 근거로 삼는 것"),
    "side_effects": ("부작용", "이 부작용을 낳는 규칙"),
    "exceptions": ("예외", "이걸 예외로 둔 규칙"),
    "replaced_by": ("고친 새 버전", "고치기 전 버전"),
    "harms": ("해치는 목표", "이 목표를 해치는 것"),
    "accepted_for": ("이 목표의 대가로 받아들임", "이 목표를 위해 받아들인 대가"),
}


def load_all(root: Path) -> dict[str, Knowledge]:
    out = {}
    for path in sorted((root / "domains").glob("*/knowledge.toml")):
        kn = schema.load(path)
        out[kn.domain.get("id", path.parent.name)] = kn
    return out


def describe(node: Node) -> str:
    d = node.data
    if node.kind == "rule":
        return (f"[규칙 {node.id} v{d['version']} · {RULE_STATUS[d['status']]}] "
                f"방법: {d['method']} / 이유: {d['reason']}")
    extra = ""
    if node.kind == "fact":
        extra = f" (확인 {d['checked']}, 출처 {d['source']})"
    elif node.kind in ("observation", "hypothesis"):
        extra = f" (출처 {d['source']})"
    return f"[{KIND_LABEL[node.kind]} {node.id}] {node.text}{extra}"


def domains_summary(kbs: dict[str, Knowledge]) -> str:
    lines = []
    for did, kn in kbs.items():
        counts = ", ".join(f"{KIND_LABEL[k]} {len(kn.of(k))}" for k in schema.KINDS if kn.of(k))
        lines.append(f"- {did}: {kn.domain.get('name', '')} ({counts})")
    return "\n".join(lines) or "등록된 분야 없음"


def goal_tree(kn: Knowledge) -> str:
    goals = kn.of("goal")
    children: dict[str | None, list[Node]] = {}
    for g in goals:
        children.setdefault(g.data.get("parent"), []).append(g)
    lines: list[str] = []

    def walk(parent: str | None, depth: int) -> None:
        for g in children.get(parent, []):
            lines.append("  " * depth + f"- {g.id}: {g.text}")
            walk(g.id, depth + 1)

    walk(None, 0)
    return "\n".join(lines) or "목표 없음"


def search(kbs: dict[str, Knowledge], query: str, limit: int = 12) -> str:
    """질문의 낱말이 많이 겹치는 노드부터. 아주 단순한 낱말 겹침 방식."""
    words = [w for w in query.replace(",", " ").split() if len(w) >= 2]
    scored = []
    for did, kn in kbs.items():
        for node in kn.nodes.values():
            hay = " ".join(str(node.data.get(f, "")) for f in ("text", "method", "reason", "note"))
            score = sum(1 for w in words if w in hay or w[:-1] in hay and len(w) > 2)
            if score:
                scored.append((score, did, node))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return "겹치는 노드 없음. goal_tree나 다른 낱말로 다시 찾아보세요."
    return "\n".join(f"- ({did}) {describe(n)}" for _, did, n in scored[:limit])


def explain(kn: Knowledge, node_id: str) -> str:
    node = kn.nodes.get(node_id)
    if node is None:
        return f"'{node_id}' 없음"
    lines = [describe(node)]
    if node.data.get("note"):
        lines.append(f"메모: {node.data['note']}")
    for (kind, field) in REFS:
        if kind == node.kind:
            for ref in node.refs(field):
                if ref in kn.nodes:
                    lines.append(f"- {FIELD_LABEL[field][0]}: {describe(kn.nodes[ref])}")
    for other in kn.nodes.values():
        for (kind, field) in REFS:
            if kind == other.kind and node.id in other.refs(field):
                lines.append(f"- {FIELD_LABEL[field][1]}: {describe(other)}")
    return "\n".join(lines)
