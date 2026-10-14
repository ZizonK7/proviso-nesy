"""점검: 엔진이 LLM 없이 그래프만 보고 내리는 판단.

지금은 한 가지: 목표를 해치는데 '대가로 받아들인다'는 기록이 없는 것을 찾는다.
- 사실이 목표를 해치면 항상 문제다 (사실은 지금의 상태).
- 상태·가설이 목표를 해치면, 그걸 부작용으로 낳는 규칙이 모두 이전 버전일 때는 지난 일로 보고 넘어간다.
"""
from __future__ import annotations

from .schema import KIND_LABEL, Knowledge, Node


def _producers(kn: Knowledge, node: Node) -> list[Node]:
    return [r for r in kn.of("rule") if node.id in r.refs("side_effects")]


def unaccepted_harms(kn: Knowledge) -> list[str]:
    issues = []
    for node in kn.nodes.values():
        harmed = node.refs("harms")
        if not harmed or node.refs("accepted_for"):
            continue
        producers = _producers(kn, node)
        if node.kind != "fact" and producers and all(r.data.get("status") == "retired" for r in producers):
            continue
        for gid in harmed:
            goal = kn.nodes.get(gid)
            via = f" (부작용을 낳는 규칙: {', '.join(r.id for r in producers)})" if producers else ""
            issues.append(
                f"[{KIND_LABEL[node.kind]} {node.id}] {node.text}\n"
                f"  → 목표 {gid} '{goal.text if goal else '?'}'를 해치는데, 대가로 받아들인 기록이 없음{via}"
            )
    return issues


def report(kn: Knowledge) -> str:
    issues = unaccepted_harms(kn)
    if not issues:
        return "점검 통과: 목표를 해치는 것은 모두 대가로 받아들인 기록이 있음"
    return f"점검: 문제 {len(issues)}건\n" + "\n".join(issues)
