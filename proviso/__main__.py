"""사용법 (저장소 루트에서):

  python -m proviso validate flowlog   지식 파일 검사
  python -m proviso graph flowlog      out/flowlog-graph.html, .md 생성
  python -m proviso check flowlog      성적표: 살아 있는 가설(규칙 포함)마다 자동 검사 + 판정 기록, 출처별
  python -m proviso audit flowlog      점검: 오류(목표를 해치는데 받아들인 기록 없음)와
                                       경고(쪼개지 않은 개정, 시험 수단 없음). 오류가 있을 때만 실패
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from . import audit, graph, schema, score

ROOT = Path(__file__).resolve().parent.parent


def _load(domain: str) -> schema.Knowledge:
    return schema.load(ROOT / "domains" / domain / "knowledge.toml")


def cmd_validate(domain: str) -> int:
    kn = _load(domain)
    errors = schema.validate(kn)
    counts = ", ".join(f"{schema.KIND_LABEL[k]} {len(kn.of(k))}" for k in schema.KINDS)
    print(f"[{domain}] {counts}, 판정 기록 {len(kn.judgments)}")
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
    notes = [f"{n.id} ({schema.STATUS[n.data['status']]}): {n.data['note']}"
             for n in kn.of("rule") if n.data.get("note")]
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / f"{domain}-graph.md").write_text(f"```mermaid\n{mermaid}\n```\n", encoding="utf-8")
    html_path = out / f"{domain}-graph.html"
    html_path.write_text(graph.to_html(kn, mermaid, notes), encoding="utf-8")
    print(f"생성: {html_path}")
    return 0


def load_checks(domain: str) -> tuple[dict, str | dict]:
    """분야의 자동 검사 모음과 그 출처(SOURCE, 없으면 'auto'; 검사마다면 {검사 이름: 출처})."""
    module = importlib.import_module(f"domains.{domain}.checks")
    return module.CHECKS, getattr(module, "SOURCE", "auto")


def source_label(source: str | dict) -> str:
    """SOURCE를 사람이 읽을 말로: 하나면 그 이름, 검사마다면 '검사마다 (이름: 출처, …)'."""
    if isinstance(source, dict):
        return "검사마다 (" + ", ".join(f"{k}: {schema.SOURCES.get(v, v)}" for k, v in source.items()) + ")"
    return schema.SOURCES.get(source, source)


def cmd_check(domain: str) -> int:
    kn = _load(domain)
    checks, source = load_checks(domain)
    missing = sorted({c for n in kn.claims() for c in schema.check_names(n)} - set(checks))
    if missing:
        print(f"[{domain}] checks.py에 없는 검사: {', '.join(missing)}")
        return 1
    print(f"[{domain}] 성적표 (자동 검사 출처: {source_label(source)}; ★ = 사용자 판정, 가장 무거움)\n")
    print(score.report(kn, checks, source))
    return 0


def domain_audit(domain: str, kn: schema.Knowledge) -> tuple[list[str], list[str]]:
    """분야 점검: checks.py의 AUDIT(kn) → (오류, 경고). 없으면 빈 것."""
    try:
        module = importlib.import_module(f"domains.{domain}.checks")
    except ModuleNotFoundError:
        return [], []
    hook = getattr(module, "AUDIT", None)
    return hook(kn) if hook else ([], [])


def cmd_audit(domain: str) -> int:
    kn = _load(domain)
    extra = domain_audit(domain, kn)
    print(f"[{domain}] {audit.report(kn, extra)}")
    return 1 if audit.unaccepted_harms(kn) or extra[0] else 0  # 경고만 있으면 통과


def main(argv: list[str]) -> int:
    commands = {"validate": cmd_validate, "graph": cmd_graph, "check": cmd_check, "audit": cmd_audit}
    if len(argv) != 2 or argv[0] not in commands:
        print(__doc__)
        return 2
    return commands[argv[0]](argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
