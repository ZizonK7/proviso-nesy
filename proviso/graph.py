"""지식을 Mermaid 그래프로 그린다. 아래(근거·조건) → 가운데(규칙) → 위(목표)."""
from __future__ import annotations

import html

from .schema import RULE_STATUS, Knowledge, Node

# 선 스타일: (Mermaid 화살표, 라벨, 색)
EDGE = {
    "parent": ("==>", "", "#2b7a4b"),
    "serves": ("==>", "", "#2b7a4b"),
    "conditions": ("-->", "", "#7a8494"),
    "evidence": ("-->", "근거", "#7a8494"),
    "against": ("-.-x", "반대", "#c0432e"),
    "results": ("==>", "", "#2d5cae"),
    "side_effects": ("-.->", "부작용", "#b07300"),
    "harms": ("-.-x", "해침", "#c0432e"),
    "accepted_for": ("-.->", "대가로 수용", "#b07300"),
    "replaced_by": ("-.->", "고침", "#c0432e"),
    "exceptions": ("--x", "예외", "#c0432e"),
}

CLASSES = """\
classDef goal fill:#e2f3e8,stroke:#2b7a4b,stroke-width:2px,color:#1b2330
classDef state fill:#ffffff,stroke:#9aa3b1,color:#1b2330
classDef fact fill:#edf0f3,stroke:#5b6676,stroke-dasharray:6 4,color:#1b2330
classDef observation fill:#ffffff,stroke:#1b2330,stroke-width:1.5px,color:#1b2330
classDef hypothesis fill:#efe8f8,stroke:#6a4d9e,stroke-dasharray:8 3,color:#1b2330
classDef rule fill:#e2ebfa,stroke:#2d5cae,stroke-width:1.5px,color:#1b2330
classDef retired fill:#f1f3f6,stroke:#7a8494,stroke-dasharray:5 4,color:#5b6676"""


def _wrap(text: str, width: int = 18) -> str:
    """띄어쓰기 기준으로 줄을 나눈다."""
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return "<br/>".join(_esc(line) for line in lines)


def _esc(text: str) -> str:
    return text.replace('"', "#quot;")


def _label(node: Node) -> str:
    d = node.data
    if node.kind == "goal":
        return f"<b>목표</b><br/>{_wrap(node.text)}"
    if node.kind == "rule":
        head = f"{node.id} · v{d['version']} · {RULE_STATUS[d['status']]}"
        return (
            f"<small>{_esc(head)}</small><br/><b>방법</b> {_wrap(d['method'], 22)}"
            f"<br/><b>이유</b> {_wrap(d['reason'], 22)}"
        )
    if node.kind == "fact":
        return f"<b>사실</b> · {d['checked']}<br/>{_wrap(node.text)}"
    if node.kind == "observation":
        who = "사용자" if d.get("source") == "user" else d.get("source", "")
        return f"<b>관찰</b> · {_esc(who)}<br/>{_wrap(node.text)}"
    if node.kind == "hypothesis":
        return f"<b>가설</b><br/>{_wrap(node.text)}"
    return _wrap(node.text)


def _shape(node: Node) -> str:
    label = _label(node)
    return {
        "goal": f'{node.id}{{{{"{label}"}}}}',
        "state": f'{node.id}(["{label}"])',
        "fact": f'{node.id}[("{label}")]',
        "observation": f'{node.id}[/"{label}"/]',
        "hypothesis": f'{node.id}>"{label}"]',
        "rule": f'{node.id}["{label}"]',
    }[node.kind]


def to_mermaid(kn: Knowledge) -> str:
    out = ["flowchart BT"]
    for node in kn.nodes.values():
        out.append("  " + _shape(node))
    colors = []
    for node in kn.nodes.values():
        for field, (arrow, label, color) in EDGE.items():
            for ref in node.refs(field):
                if ref not in kn.nodes:
                    continue
                # 조건·근거·반대 근거·예외는 그 노드에서 규칙(가설)으로 들어가는 방향
                src, dst = (ref, node.id) if field in ("conditions", "evidence", "against", "exceptions") else (node.id, ref)
                mid = f"|{label}|" if label else ""
                out.append(f"  {src} {arrow}{mid} {dst}")
                colors.append(color)
    out += ["  " + line for line in CLASSES.splitlines()]
    for node in kn.nodes.values():
        cls = "retired" if node.data.get("status") == "retired" else node.kind
        out.append(f"  class {node.id} {cls}")
    for i, color in enumerate(colors):
        out.append(f"  linkStyle {i} stroke:{color},stroke-width:1.6px")
    return "\n".join(out)


def to_html(kn: Knowledge, mermaid: str, notes: list[str]) -> str:
    title = html.escape(kn.domain.get("name", kn.domain.get("id", "지식")))
    note_html = "".join(f"<li>{html.escape(n)}</li>" for n in notes)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 경험 논리 그래프</title>
<style>
body {{ background:#f5f7f9; color:#1b2330; margin:0; padding:24px 16px;
  font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif; }}
h1 {{ font-size:1.4rem; margin:0 0 4px; }}
p, li {{ color:#5b6676; font-size:0.9rem; }}
.graph {{ background:#fff; border:1px solid #b9c1cd; border-radius:8px; padding:12px; overflow-x:auto; }}
</style></head><body>
<h1>{title}</h1>
<p>지식 파일에서 자동으로 그린 그래프입니다. 아래가 근거·조건, 가운데가 규칙, 위가 목표입니다.</p>
<ul>{note_html}</ul>
<div class="graph"><pre class="mermaid">
{html.escape(mermaid)}
</pre></div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad: true, theme: "base" }});</script>
</body></html>
"""
