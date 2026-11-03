"""연결 실험: 조각 두 개를 무작위로 뽑아 연결을 시도한다. 절차는 docs/connection-experiment-v0.md.

  python -m domains.far_fields.connect <쌍 수> <seed>

뽑기는 random.Random(seed)로 재현된다. 두 조각은 서로 다른 묶음(group), 서로 다른 '모양'을 우선한다(같은 모양이면 연결이 뻔하다).
결과는 out/far_fields/connect_<seed>.jsonl(원본)과 docs/experiments/connections/<seed>.md(읽는 기록).
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from proviso import schema

from .generate import MODEL, OUT, _append, api, text_of

ROOT = Path(__file__).resolve().parents[2]
KN = Path(__file__).with_name("knowledge.toml")
DOC = ROOT / "docs" / "experiments" / "connections"

SYSTEM = """두 경험 조각을 받아, 둘을 이은 새 아이디어 카드를 만든다.

배경 (사용자, 2026-11-03): 창의성은 기존 논리를 생각지 못한 방식으로 잇는 것이다. 말도 안 돼 보이는 연결도 쉽게 버리지 않는다. 그래도 안 되면 포기하되, 어디까지 해 봤는지 남긴다.

카드에 들어갈 것:
- ideas: 네 가지 잇는 방식마다 아이디어 하나씩. 방식은 옮기기(한쪽의 방법을 다른 쪽 상황에), 같은 뼈대(이유까지 같은 공통 구조), 부딪히기(둘이 다른 행동을 권하는 상황에서 새로 보이는 것), 잇기(한쪽의 결과가 다른 쪽의 조건이 되는 사슬). 각 아이디어는 한두 문장, 쓸 만한지(worked)와 그 까닭 한 문장.
- outcome: 쓸 만한 아이디어가 있으면 "연결", 넷 다 뻔하거나(한쪽 조각을 다시 말한 것, '균형이 중요하다' 류) 억지면 "포기".
- new_piece: 연결이면 가장 나은 아이디어를 분야 이름 없는 조각 한두 문장으로. 포기면 빈 문자열.
- gave_up_at: 포기면 어디까지 해 봤고 무엇이 막혔는지 한두 문장. 연결이면 빈 문자열.
- test_in_life: 새 조각(포기면 가장 가까웠던 아이디어)을 이 사람의 생활 하나에 대 본 예: 수능 수학 과외, 학원 상담 아르바이트, 데이터 과학 공부, AI 에이전트에게 일 맡기기. 억지면 억지라고.
- novelty·usefulness·forced: 1~5 (새로움, 쓸모, 억지 정도).

한국어 일상어."""

SCHEMA = {"type": "object", "properties": {
    "ideas": {"type": "array", "items": {"type": "object", "properties": {
        "angle": {"type": "string", "enum": ["옮기기", "같은 뼈대", "부딪히기", "잇기"]},
        "idea": {"type": "string"}, "worked": {"type": "boolean"}, "why": {"type": "string"}},
        "required": ["angle", "idea", "worked", "why"], "additionalProperties": False}},
    "outcome": {"type": "string", "enum": ["연결", "포기"]},
    "new_piece": {"type": "string"}, "gave_up_at": {"type": "string"},
    "test_in_life": {"type": "string"},
    "novelty": {"type": "integer"}, "usefulness": {"type": "integer"}, "forced": {"type": "integer"}},
    "required": ["ideas", "outcome", "new_piece", "gave_up_at", "test_in_life",
                 "novelty", "usefulness", "forced"], "additionalProperties": False}


def pick(kn: schema.Knowledge, n: int, seed: int) -> list[tuple]:
    rng = random.Random(seed)
    pieces = [h for h in kn.of("hypothesis") if schema.alive(h) and h.data.get("text")]
    pairs = []
    while len(pairs) < n:
        a, b = rng.sample(pieces, 2)
        if a.data["group"] == b.data["group"] or set(a.refs("conditions")) & set(b.refs("conditions")):
            continue
        pairs.append((a, b))
    return pairs


def _piece(h) -> str:
    return (f"일반화: {h.data['text']}\n  (원래 분야: {h.data['field']} — {h.data['rule']} / 왜: {h.data['why']} / "
            f"깨지는 조건: {h.data['breaks']})")


def run(n: int, seed: int) -> None:
    kn = schema.load(KN)
    DOC.mkdir(parents=True, exist_ok=True)
    md = [f"# 연결 실험 seed {seed} ({n}쌍)\n", "절차: [docs/connection-experiment-v0.md](../../connection-experiment-v0.md). "
          f"연결 모델: {MODEL}(effort high, 거절 시 서버 대체 모델 — 쌍마다 실제 모델을 적는다). 평가 숫자는 모델 자기평가이고, 사용자 판정 칸은 비어 있다.\n"]
    total = 0.0
    for i, (a, b) in enumerate(pick(kn, n, seed), 1):
        user = f"조각 A ({a.id})\n  {_piece(a)}\n\n조각 B ({b.id})\n  {_piece(b)}"
        body = {"model": MODEL, "max_tokens": 32000, "system": SYSTEM, "messages": [{"role": "user", "content": user}],
                "output_config": {"effort": "high", "format": {"type": "json_schema", "schema": SCHEMA}},
                "fallbacks": "default"}  # 분류기 거절(refusal)이면 서버가 다른 모델로 다시 돌린다
        for _ in range(3):  # 거절은 같은 요청에서도 들쭉날쭉했다(2026-11-03: 6쌍 중 4쌍 거절 → 다시 보내면 통과)
            r = api.call("POST", "/v1/messages", body, beta="server-side-fallback-2026-07-01")
            total += api.cost(r["usage"])
            if r["stop_reason"] != "refusal":
                break
            print("  거절:", r.get("stop_details"))
        try:
            d = json.loads(text_of(r))
        except (StopIteration, json.JSONDecodeError):
            _append(f"connect_{seed}", {"pair": [a.id, b.id], "usage": r["usage"], "stop_reason": r["stop_reason"], "data": None})
            md.append(f"## {i}. {a.id} × {b.id}\n\n응답이 끊김(stop_reason={r['stop_reason']}). 기록만 남긴다.\n")
            print(i, a.id, b.id, "끊김", r["stop_reason"])
            continue
        _append(f"connect_{seed}", {"pair": [a.id, b.id], "model": r.get("model"), "usage": r["usage"], "data": d})
        md.append(f"## {i}. {a.id} × {b.id}\n")
        md.append(f"- 답한 모델: {r.get('model')}")
        md.append(f"- A ({a.data['field']}): {a.data['text']}\n- B ({b.data['field']}): {b.data['text']}\n")
        for t in d["ideas"]:
            md.append(f"- **{t['angle']}** {'○' if t['worked'] else '×'}: {t['idea']} — {t['why']}")
        md.append(f"\n**결과: {d['outcome']}**")
        if d["outcome"] == "연결":
            md.append(f"\n- 새 조각: {d['new_piece']}")
        else:
            md.append(f"\n- 어디까지 해 봤나: {d['gave_up_at']}")
        md.append(f"- 사용자 생활에 대 보기: {d['test_in_life']}")
        md.append(f"- 자기평가: 새로움 {d['novelty']} · 쓸모 {d['usefulness']} · 억지 {d['forced']}")
        md.append("- 사용자 판정: (비어 있음)\n")
        print(i, a.id, b.id, d["outcome"], d["novelty"], d["usefulness"], d["forced"])
    md.append(f"\n비용(정가, usage 합): ${total:.2f}\n")
    (DOC / f"seed-{seed}.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]))
