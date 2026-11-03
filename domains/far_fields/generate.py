"""먼 분야 경험칙을 Claude API로 만든다 (생성 → 검토 두 단계). 표준 라이브러리만.

키는 환경 변수 `API`에서만 읽는다(scripts/claude_http.py). 원본 응답은 out/far_fields/(git 제외)에만 둔다.

  python -m domains.far_fields.generate test <slug> [<slug> ...]   동기 호출로 시험 생성 (정가)
  python -m domains.far_fields.generate submit-gen [--limit N]     생성 배치 제출 (정가의 절반)
  python -m domains.far_fields.generate submit-review <이름> [...]     검토 배치 제출 (생성 결과·웹 조사 결과에)
  python -m domains.far_fields.generate status <배치 id>
  python -m domains.far_fields.generate fetch <배치 id> <이름>     결과를 out/far_fields/<이름>.jsonl로
  python -m domains.far_fields.generate cost <이름> [--batch]      usage 합으로 비용 집계
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import claude_http as api  # noqa: E402

from .shapes import SHAPES  # noqa: E402

OUT = ROOT / "out" / "far_fields"
FIELDS = Path(__file__).with_name("fields.json")
MODEL = "claude-opus-5-5"
PER_FIELD = 12

_shape_lines = "\n".join(f"- {k}: {v}" for k, v in SHAPES.items())

GEN_SYSTEM = f"""너는 여러 현장 분야의 숙련자가 실제로 쓰는 경험칙을 모아 정리하는 사람이다.

## 목적
한 사람의 '논리집'에, 그 사람이 전혀 모르고 앞으로도 하지 않을 분야의 경험 논리를 넣어 둔다. 나중에 조각 두 개를 무작위로 뽑아 생각지 못한 연결을 시도하는 재료로 쓴다(창의성 = 기존 논리를 생각지 못한 방식으로 잇기). 그래서 가장 중요한 칸은 분야 이름을 뺀 일반화 문장(general)이다.

## 무엇을 쓰나
분야 하나에 경험칙 {PER_FIELD}개. 각 경험칙:
- rule: 그 분야 말로 쓴 구체적인 경험칙. 현장 사람이 후배에게 해 주는 말처럼. 숫자·감각·신호가 있으면 넣는다. 교과서 정의나 '안전이 중요하다' 같은 뻔한 말은 안 된다.
- why: 왜 통하는가 (원리나 이유). 짧게.
- breaks: 깨지는 조건·예외. 이 경험칙을 믿으면 안 되는 상황, 또는 반대로 하는 게 맞는 상황.
- general: 분야·직업·도구·재료·동물 이름이 하나도 없는 일반화 한 문장(길어도 두 문장). 그 분야를 모르는 사람이 읽어도 뜻이 통해야 하고, 다른 분야에 대 볼 수 있어야 한다. "~하면 ~한다", "~일 때는 ~부터 본다"처럼 조건과 결론이 보이게. rule을 그대로 추상명사로 바꾼 말장난은 안 된다 — 왜 통하는지가 일반화에 남아야 한다.
- shapes: 아래 모양 단어장에서 이 경험칙이 기대는 상황 1~3개 (id).
- confidence: 이 경험칙이 그 분야 현장에서 실제로 통용된다고 네가 얼마나 확신하는지. 높음 / 중간 / 낮음. 지역·시대·유파마다 다르거나 네 기억이 흐리면 낮춘다. 모르는 것을 지어내지 말고, 확신이 낮으면 낮음으로 적는다.

## 고르는 기준
- {PER_FIELD}개가 서로 다른 면을 다루게: 시기·순서 판단, 재료·대상 읽기, 몸 쓰기·도구, 위험과 사고, 사람(동료·손님·상대) 다루기, 실패에서 배운 것, 초보가 흔히 틀리는 것.
- 현장 사람만 아는 것(몸으로 익힌 감각, 사고 뒤에 생긴 관례, 초보의 착각)을 우선한다.
- 일반화가 서로 비슷한 경험칙 둘은 하나만 남긴다.
- 출처 이름·URL·통계를 지어내지 않는다. 출처 칸은 없다.
- 의료·안전 지침이 아니라 생각의 재료다. 위험한 절차를 따라 하게 만드는 자세한 방법은 쓰지 않는다.

## 문체
한국어 일상어. 전문용어는 처음 쓸 때 괄호로 풀어서. 칸마다 1~2문장.

## 모양 단어장 (shapes에 id를 쓴다)
{_shape_lines}
"""

GEN_SCHEMA = {
    "type": "object",
    "properties": {
        "field": {"type": "string"},
        "items": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "rule": {"type": "string"},
                "why": {"type": "string"},
                "breaks": {"type": "string"},
                "general": {"type": "string"},
                "shapes": {"type": "array", "items": {"type": "string", "enum": list(SHAPES)}},
                "confidence": {"type": "string", "enum": ["높음", "중간", "낮음"]},
            },
            "required": ["rule", "why", "breaks", "general", "shapes", "confidence"],
            "additionalProperties": False,
        }},
    },
    "required": ["field", "items"],
    "additionalProperties": False,
}

REVIEW_SYSTEM = f"""너는 다른 AI가 정리한 현장 경험칙을 따져 보는 검토자다. 칭찬하지 말고, 틀리거나 흐린 곳을 찾는다.

경험칙마다 다음을 판단한다.
- verdict: 그 분야 현장에서 실제로 통용되는 경험칙이라고 볼 수 있나.
  - 지지: 네가 아는 바로 그 분야에서 실제로 쓰는 경험칙이고, 이유(why)도 맞다.
  - 일부: 대체로 맞지만 숫자·조건·이유 가운데 틀리거나 지역·유파에 따라 다른 곳이 있다, 또는 네가 확인할 만큼 알지 못한다.
  - 반박: 틀렸거나, 현장에서 반대로 하거나, 지어낸 것으로 보인다.
- general_ok: 일반화 문장(general)에 분야·직업·도구·재료·동물 이름이 없고, 경험칙에서 정말 따라 나오며, 왜 통하는지가 남아 있나 (true/false).
- shapes: 아래 모양 단어장에서 이 경험칙이 기대는 상황 1~3개. 이미 붙어 있으면 맞는지 보고 고친 목록을 쓴다.
- general_fix: general_ok가 false이거나 일반화 문장이 비어 있으면, 고친 일반화 문장(분야·직업·도구·재료·동물 이름 없이, 조건과 결론과 이유가 보이게, 한두 문장). 문제없으면 빈 문자열.
- note: 판단 이유 한 문장. 일부·반박이면 무엇이 틀렸는지 구체적으로. general_ok가 false면 무엇이 문제인지.
번호(n)는 받은 그대로 쓴다. 한국어 일상어.

## 모양 단어장
{_shape_lines}
"""

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {"reviews": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "n": {"type": "integer"},
            "verdict": {"type": "string", "enum": ["지지", "일부", "반박"]},
            "general_ok": {"type": "boolean"},
            "shapes": {"type": "array", "items": {"type": "string", "enum": list(SHAPES)}},
            "general_fix": {"type": "string"},
            "note": {"type": "string"},
        },
        "required": ["n", "verdict", "general_ok", "shapes", "general_fix", "note"],
        "additionalProperties": False,
    }}},
    "required": ["reviews"],
    "additionalProperties": False,
}


def _system(text: str) -> list[dict]:
    # 공통 시스템 프롬프트에 캐시 표시: 같은 접두부를 쓰는 요청들이 캐시를 읽는다
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def gen_params(field: dict) -> dict:
    user = f"분야: {field['ko']}\n이 분야의 경험칙 {PER_FIELD}개를 써라. field 칸에는 분야 이름을 그대로."
    return {"model": MODEL, "max_tokens": 32000, "system": _system(GEN_SYSTEM),
            "output_config": {"effort": "high", "format": {"type": "json_schema", "schema": GEN_SCHEMA}},
            "messages": [{"role": "user", "content": user}]}


def review_params(field_ko: str, items: list[dict]) -> dict:
    lines = []
    for i, it in enumerate(items, 1):
        lines.append(f"[{i}] 경험칙: {it['rule']}\n    왜: {it['why']}\n    깨지는 조건: {it['breaks']}\n"
                     f"    일반화: {it['general'] or '(비어 있음)'}\n    붙은 모양: {', '.join(it.get('shapes') or []) or '(없음)'}")
    user = f"분야: {field_ko}\n\n" + "\n\n".join(lines)
    return {"model": MODEL, "max_tokens": 16000, "system": _system(REVIEW_SYSTEM),
            "output_config": {"effort": "high", "format": {"type": "json_schema", "schema": REVIEW_SCHEMA}},
            "messages": [{"role": "user", "content": user}]}


def fields() -> list[dict]:
    return json.loads(FIELDS.read_text(encoding="utf-8"))


def text_of(message: dict) -> str:
    return next(b["text"] for b in message["content"] if b["type"] == "text")


def _append(name: str, rec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{name}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def cmd_test(slugs: list[str]) -> None:
    by = {f["slug"]: f for f in fields()}
    for s in slugs:
        r = api.call("POST", "/v1/messages", gen_params(by[s]))
        _append("test_gen", {"custom_id": f"gen-{s}", "stop_reason": r["stop_reason"],
                             "usage": r["usage"], "data": json.loads(text_of(r)) if r["stop_reason"] == "end_turn" else None})
        print(s, r["stop_reason"], r["usage"]["output_tokens"], f"${api.cost(r['usage']):.3f}")


def cmd_submit_gen(limit: int | None) -> None:
    fs = fields()[:limit] if limit else fields()
    reqs = [{"custom_id": f"gen-{f['slug']}", "params": gen_params(f)} for f in fs]
    b = api.call("POST", "/v1/messages/batches", {"requests": reqs})
    print(b["id"], b["processing_status"], len(reqs))


def cmd_submit_review(names: list[str]) -> None:
    reqs = []
    lines = [ln for name in names for ln in (OUT / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()]
    for line in lines:
        rec = json.loads(line)
        if rec.get("data"):
            cid = rec["custom_id"].replace("gen-", "rev-", 1)
            reqs.append({"custom_id": cid, "params": review_params(rec["data"]["field"], rec["data"]["items"])})
    b = api.call("POST", "/v1/messages/batches", {"requests": reqs})
    print(b["id"], b["processing_status"], len(reqs))


def cmd_status(bid: str) -> None:
    b = api.call("GET", f"/v1/messages/batches/{bid}")
    print(b["processing_status"], b["request_counts"], b.get("ended_at"))


def cmd_fetch(bid: str, name: str) -> None:
    b = api.call("GET", f"/v1/messages/batches/{bid}")
    raw = api.call("GET", b["results_url"].replace(api.BASE, ""), raw=True).decode("utf-8")
    path = OUT / f"{name}.jsonl"
    OUT.mkdir(parents=True, exist_ok=True)
    n = bad = 0
    with path.open("w", encoding="utf-8") as f:
        for line in raw.splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            res = r["result"]
            rec = {"custom_id": r["custom_id"], "type": res["type"]}
            if res["type"] == "succeeded":
                m = res["message"]
                rec |= {"stop_reason": m["stop_reason"], "usage": m["usage"]}
                try:
                    rec["data"] = json.loads(text_of(m)) if m["stop_reason"] == "end_turn" else None
                except (StopIteration, json.JSONDecodeError):
                    rec["data"] = None
            else:
                rec["error"] = res.get("error")
            bad += rec.get("data") is None
            n += 1
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{n}건 저장, 데이터 없음 {bad}건 → {path}")


def cmd_cost(name: str, batch: bool) -> None:
    tot = {}
    for line in (OUT / f"{name}.jsonl").read_text(encoding="utf-8").splitlines():
        u = json.loads(line).get("usage") or {}
        for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
            tot[k] = tot.get(k, 0) + (u.get(k) or 0)
    print(tot, f"${api.cost(tot, batch=batch):.2f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "test":
        cmd_test(a[1:])
    elif a[0] == "submit-gen":
        cmd_submit_gen(int(a[2]) if len(a) > 2 and a[1] == "--limit" else None)
    elif a[0] == "submit-review":
        cmd_submit_review(a[1:])
    elif a[0] == "status":
        cmd_status(a[1])
    elif a[0] == "fetch":
        cmd_fetch(a[1], a[2])
    elif a[0] == "cost":
        cmd_cost(a[1], "--batch" in a)
    else:
        print(__doc__)
