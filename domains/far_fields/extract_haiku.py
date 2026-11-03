"""gemmin 저장소의 Haiku 웹 조사 결과(10개 분야 md)를 생성 결과와 같은 모양의 JSON으로 옮긴다.

md 양식이 파일마다 조금씩 달라서 손 파서 대신 API로 칸만 옮긴다(낱말을 바꾸지 말라고 지시). 결과는 out/far_fields/haiku_gen.jsonl.
  python -m domains.far_fields.extract_haiku <md 폴더>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .generate import MODEL, OUT, _append, api, text_of

SCHEMA = {"type": "object", "properties": {"field": {"type": "string"}, "items": {"type": "array", "items": {
    "type": "object", "properties": {
        "rule": {"type": "string"}, "why": {"type": "string"}, "breaks": {"type": "string"},
        "general": {"type": "string"}, "source": {"type": "string"},
        "opened": {"type": "string", "enum": ["열람", "검색 요약", "모델 지식"]},
        "confidence": {"type": "string", "enum": ["높음", "중간", "낮음"]}},
    "required": ["rule", "why", "breaks", "general", "source", "opened", "confidence"], "additionalProperties": False}}},
    "required": ["field", "items"], "additionalProperties": False}

PROMPT = """아래 md는 한 분야의 경험칙 조사 보고서다. 경험칙 항목마다 칸을 옮겨 JSON으로 내라.
- 낱말을 바꾸거나 요약하지 말고 원문 문장을 그대로 옮긴다(줄바꿈·굵게 표시만 뺀다). 제목과 본문 경험칙이 따로 있으면 rule에 둘을 이어 쓴다.
- source: 출처 칸 그대로(주소·이름). opened: [열람 확인]/[열람]이면 "열람", [검색 요약만]/[검색요약]이면 "검색 요약", 출처가 없거나 '모델 지식'이면 "모델 지식". 한 항목에 둘이 섞이면 주장의 핵심 출처를 따른다.
- confidence: "중간~높음"처럼 범위면 낮은 쪽. 
- 경험칙이 아닌 절(가장 의외였던 것, 막힌 사이트, 실측 등)은 빼되, '출처 없음(모델 지식) 추가' 항목은 넣는다.
- field: 분야 이름(한국어, 제목에서).

"""


def main(folder: str) -> None:
    for md in sorted(Path(folder).glob("*.md")):
        if md.name == "README.md":
            continue
        body = {"model": MODEL, "max_tokens": 32000,
                "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                "messages": [{"role": "user", "content": PROMPT + md.read_text(encoding="utf-8")}]}
        r = api.call("POST", "/v1/messages", body)
        data = json.loads(text_of(r))
        _append("haiku_gen", {"custom_id": f"gen-haiku_{md.stem.replace('-', '_')}", "stop_reason": r["stop_reason"],
                              "usage": r["usage"], "data": data})
        print(md.stem, len(data["items"]), f"${api.cost(r['usage']):.3f}")


if __name__ == "__main__":
    main(sys.argv[1])
