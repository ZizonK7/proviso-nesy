"""논리집을 LLM 도구로 내놓는 MCP 서버 (stdio, 표준 라이브러리만).

Claude Code 등록 예 (저장소 루트를 PYTHONPATH로):
  {"mcpServers": {"proviso": {"command": "<python 경로>", "args": ["-m", "proviso.mcp_server"],
                              "env": {"PYTHONPATH": "<저장소 루트>"}}}}
지금은 읽기 전용. 규칙 기록(commit) 도구는 다음 단계.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from . import audit, query, score

ROOT = Path(__file__).resolve().parent.parent

TOOLS = [
    {
        "name": "list_domains",
        "description": "사용자의 경험 논리집에 있는 분야 목록과 노드 개수.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "goal_tree",
        "description": "한 분야의 목표 위계(큰 목표 ← 하위 목표). 사용자가 무엇을 중요하게 여기는지 보여준다.",
        "inputSchema": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]},
    },
    {
        "name": "search",
        "description": "낱말로 목표·규칙·관찰·가설을 찾는다. 질문의 핵심 낱말을 여러 개 넣는다.",
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    {
        "name": "explain",
        "description": "노드 하나와 연결된 모든 것(조건, 이유, 근거, 부작용, 받아들인 대가, 이전 버전)을 보여준다.",
        "inputSchema": {
            "type": "object",
            "properties": {"domain": {"type": "string"}, "id": {"type": "string"}},
            "required": ["domain", "id"],
        },
    },
    {
        "name": "audit",
        "description": "점검: 오류(목표를 해치는데 사용자가 대가로 받아들인 기록이 없는 것)와 "
                       "경고(조건을 더하지 않은 개정, 시험 수단이 없는 가설)를 찾는다.",
        "inputSchema": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]},
    },
    {
        "name": "scorecard",
        "description": "성적표: 한 분야의 살아 있는 가설(규칙 포함)마다 자동 검사 결과와 판정 기록을 출처별로. "
                       "사용자 실사용 판정이 가장 무겁다. 규칙을 믿기 전에 본다.",
        "inputSchema": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]},
    },
]


def call_tool(name: str, args: dict) -> str:
    if name not in {t["name"] for t in TOOLS}:
        raise KeyError(name)
    kbs = query.load_all(ROOT)
    if name == "list_domains":
        return query.domains_summary(kbs)
    if name == "search":
        return query.search(kbs, args.get("query", ""))
    kn = kbs.get(args.get("domain", ""))
    if kn is None:
        return f"분야 '{args.get('domain')}' 없음. list_domains로 확인하세요."
    if name == "goal_tree":
        return query.goal_tree(kn)
    if name == "audit":
        return audit.report(kn)
    if name == "scorecard":
        module = importlib.import_module(f"domains.{args['domain']}.checks")
        return score.report(kn, module.CHECKS, getattr(module, "SOURCE", "auto"))
    return query.explain(kn, args.get("id", ""))


def handle(msg: dict) -> dict | None:
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:  # 알림은 답하지 않는다
        return None
    if method == "initialize":
        result = {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "proviso", "version": "0.1.0"},
        }
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params", {})
        try:
            text, is_error = call_tool(params.get("name", ""), params.get("arguments") or {}), False
        except KeyError:
            text, is_error = f"모르는 도구: {params.get('name')}", True
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main() -> None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        if not line.strip():
            continue
        reply = handle(json.loads(line))
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
