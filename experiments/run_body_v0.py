"""본체 실험 v0: 같은 질문을 (A) 논리집 없이 / (B) 논리집 도구(MCP)를 쓰게 해서 Claude에게 묻는다.

저장소 루트에서:  python -m experiments.run_body_v0
- 각 실행은 빈 임시 폴더에서 돈다 (저장소 파일을 직접 못 읽게). 파일·셸·웹 도구는 막는다.
- 원본 출력: out/experiments/body_v0/*.jsonl, 보고서: docs/experiments/2026-10-14-body-v0.md
- Claude Code 구독 사용량을 쓴다 (질문 3개 × 2조건 = 6회).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "out" / "experiments" / "body_v0"
REPORT = ROOT / "docs" / "experiments" / "2026-10-14-body-v0.md"
MODEL = "sonnet"

QUESTIONS = [
    "뮤직 플레이어 앱의 '알아서 틀기'에 최근에 처음 들은 곡을 넣으려고 해. 바로 맨 앞 순서로 틀어 줄까, 아니면 어떻게 넣는 게 좋을까?",
    "Flowlog에서 운동 세트를 기록할 때 운동 종목 이름을 추천하는 칸을 만들려고 해. 몇 칸으로 하고 어떤 순서로 보여 주는 게 좋을까?",
    "Flowlog 제목 추천 칸을 5개에서 8개로 늘리면 어떨까?",
]

COMMON = "당신은 사용자의 개인 앱 설계 질문에 답한다. 한국어로 8줄 이내. 결론을 먼저, 그다음 이유."
SYSTEM = {
    "A": COMMON,
    "B": COMMON + (
        " 사용자의 경험 논리집(proviso 도구)을 쓸 수 있다. 답하기 전에 관련 목표·규칙·관찰·"
        "받아들인 대가를 조회하라. 논리집에 근거한 부분은 노드 id를 괄호로 적고, "
        "논리집에 없는 일반론은 '(일반론)'이라고 표시하라."
    ),
}
BLOCKED = ["Bash", "PowerShell", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch",
           "Task", "Agent", "NotebookEdit", "TodoWrite", "Skill"]
PROVISO_TOOLS = ["mcp__proviso__list_domains", "mcp__proviso__goal_tree",
                 "mcp__proviso__search", "mcp__proviso__explain"]


def mcp_config(tmp: Path) -> Path:
    path = tmp / "mcp.json"
    path.write_text(json.dumps({"mcpServers": {"proviso": {
        "command": sys.executable,
        "args": ["-m", "proviso.mcp_server"],
        "env": {"PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8"},
    }}}), encoding="utf-8")
    return path


def run_one(question: str, cond: str, tag: str) -> dict:
    claude = shutil.which("claude")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        args = [claude, "-p", question, "--output-format", "stream-json", "--verbose",
                "--model", MODEL, "--append-system-prompt", SYSTEM[cond], "--strict-mcp-config"]
        if cond == "B":
            args += ["--mcp-config", str(mcp_config(tmp)), "--allowedTools", *PROVISO_TOOLS]
        args += ["--disallowedTools", *BLOCKED]
        proc = subprocess.run(args, cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=600)
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / f"{tag}-{cond}.jsonl").write_text(proc.stdout + "\n# stderr\n" + proc.stderr, encoding="utf-8")
    tools, answer, cost, turns = [], "", None, None
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for part in ev["message"].get("content", []):
                if part.get("type") == "tool_use":
                    tools.append(f"{part['name'].removeprefix('mcp__proviso__')}({json.dumps(part['input'], ensure_ascii=False)})")
        elif ev.get("type") == "result":
            answer, cost, turns = ev.get("result", ""), ev.get("total_cost_usd"), ev.get("num_turns")
    if not answer:
        answer = f"(실행 실패, 종료 코드 {proc.returncode}) {proc.stderr[-400:]}"
    return {"answer": answer.strip(), "tools": tools, "cost": cost, "turns": turns}


def main() -> None:
    sections = []
    for i, q in enumerate(QUESTIONS, 1):
        a = run_one(q, "A", f"q{i}")
        b = run_one(q, "B", f"q{i}")
        print(f"q{i} 완료: B 도구 호출 {len(b['tools'])}회", flush=True)
        tools = "\n".join(f"  - `{t}`" for t in b["tools"]) or "  - (없음)"
        sections.append(
            f"## 질문 {i}\n\n> {q}\n\n"
            f"### A · 논리집 없이\n\n{a['answer']}\n\n"
            f"### B · 논리집 도구 사용\n\n{b['answer']}\n\n"
            f"<details><summary>B가 호출한 도구 {len(b['tools'])}개 · 비용 A ${a['cost']} / B ${b['cost']}</summary>\n\n{tools}\n\n</details>\n\n"
            f"**사용자 판정:** (A / B / 비슷함) — 이유: \n"
        )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# 본체 실험 v0 — 논리집이 있으면 답이 달라지는가\n\n"
        f"- 날짜: 2026-10-14 · 모델: Claude {MODEL} (Claude Code 헤드리스) · 실행: `python -m experiments.run_body_v0`\n"
        "- A: 논리집 없이. B: proviso MCP 도구(list_domains, goal_tree, search, explain)를 쓰게 함. 둘 다 파일·셸·웹 도구는 막음.\n"
        "- 논리집에는 Flowlog 제목 추천 지식만 있다. 질문 1은 다른 앱(뮤직 플레이어)으로 경험이 옮겨 가는지 본다.\n"
        "- 판정 기준: 사용자의 실제 경험과 판단을 더 잘 반영한 답은 어느 쪽인가.\n\n"
        + "\n---\n\n".join(sections),
        encoding="utf-8",
    )
    print(f"보고서: {REPORT}")


if __name__ == "__main__":
    main()
