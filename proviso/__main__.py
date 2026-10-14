"""사용법 (저장소 루트에서):

  python -m proviso validate flowlog   지식 파일 검사
  python -m proviso graph flowlog      out/flowlog-graph.html, .md 생성
  python -m proviso check flowlog      가설을 분야별 검사 함수로 확인
  python -m proviso audit flowlog      점검: 목표를 해치는데 받아들인 기록이 없는 것
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from . import audit, graph, schema

ROOT = Path(__file__).resolve().parent.parent


def _load(domain: str) -> schema.Knowledge:
    return schema.load(ROOT / "domains" / domain / "knowledge.toml")


def cmd_validate(domain: str) -> int:
    kn = _load(domain)
    errors = schema.validate(kn)
    counts = ", ".join(f"{schema.KIND_LABEL[k]} {len(kn.of(k))}" for k in schema.KINDS)
    print(f"[{domain}] {counts}")
    if errors:
        print("문제 발견:")
        for e in errors:
            print("  -", e)
        return 1
    print("문제 없음")
    return 0


def cmd_graph(domain: str) -> int:
    kn = _load(domain)
    errors = schema.validate(kn)
    if errors:
        print("지식 파일에 문제가 있어 그리지 않음. 먼저 validate를 실행하세요.")
        return 1
    mermaid = graph.to_mermaid(kn)
    notes = [f"{n.id} ({schema.RULE_STATUS[n.data['status']]}): {n.data['note']}"
             for n in kn.of("rule") if n.data.get("note")]
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / f"{domain}-graph.md").write_text(f"```mermaid\n{mermaid}\n```\n", encoding="utf-8")
    html_path = out / f"{domain}-graph.html"
    html_path.write_text(graph.to_html(kn, mermaid, notes), encoding="utf-8")
    print(f"생성: {html_path}")
    return 0


def cmd_check(domain: str) -> int:
    kn = _load(domain)
    checks = importlib.import_module(f"domains.{domain}.checks").CHECKS
    for hyp in kn.of("hypothesis"):
        name = hyp.data.get("check")
        if not name:
            print(f"{hyp.id}: 검사 방법 없음 (사용자 확인 필요)")
            continue
        verdict, detail = checks[name]()
        print(f"{hyp.id}: {verdict}\n  가설: {hyp.text}\n{detail}")
    return 0


def cmd_audit(domain: str) -> int:
    kn = _load(domain)
    print(f"[{domain}] {audit.report(kn)}")
    return 1 if audit.unaccepted_harms(kn) else 0


def main(argv: list[str]) -> int:
    commands = {"validate": cmd_validate, "graph": cmd_graph, "check": cmd_check, "audit": cmd_audit}
    if len(argv) != 2 or argv[0] not in commands:
        print(__doc__)
        return 2
    return commands[argv[0]](argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
