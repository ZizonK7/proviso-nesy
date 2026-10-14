"""하위 에이전트 대화 기록(JSONL)을 사용량 숫자로 요약한다 → docs/AGENT-LOG.md에 옮겨 적는다.

batman 저장소의 scripts/agent_usage.py를 가져와 고쳤다 (2026-10-14):
- 파일을 UTF-8로 읽는다 (Windows 기본 인코딩 문제 방지).
- 옆에 `<이름>.meta.json`이 있으면 그 안의 작업 설명(description)을 이름으로 쓴다.

사용법 (저장소 루트):
  python scripts/agent_usage.py "C:/Users/<사용자>/.claude/projects/<프로젝트>/<세션>/subagents/agent-*.jsonl" --md
  [--label ID=이름 ...]   ID는 파일 이름의 앞부분

대화 내용은 절대 출력하지 않고 집계 숫자만 낸다:
시작·끝 시각(UTC), 걸린 시간, 응답 수(turns), 도구 호출 수, 입력 / 캐시 생성 / 캐시 읽기 / 출력 토큰,
그리고 글자 수로 추정한 출력 토큰 (기록에 남는 output_tokens는 스트리밍 중 값이라 실제보다 작다).
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os


def parse_ts(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def meta_description(path):
    meta = os.path.splitext(path)[0] + ".meta.json"
    try:
        with open(meta, encoding="utf-8") as f:
            return (json.load(f).get("description") or "").strip() or None
    except Exception:
        return None


def summarize(path):
    usage = collections.Counter()
    tools = collections.Counter()
    turns = 0
    out_chars = 0
    tool_result_chars = 0
    first = last = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            ts = parse_ts(d.get("timestamp", "")) if d.get("timestamp") else None
            if ts:
                first = first or ts
                last = ts
            msg = d.get("message") if isinstance(d.get("message"), dict) else None
            if d.get("type") == "assistant" and msg:
                turns += 1
                for k, v in (msg.get("usage") or {}).items():
                    if isinstance(v, (int, float)):
                        usage[k] += v
                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        out_chars += len(block.get("text") or "")
                    elif block.get("type") == "tool_use":
                        tools[block.get("name") or "?"] += 1
                        out_chars += len(json.dumps(block.get("input") or {}, ensure_ascii=False))
                    elif block.get("type") == "thinking":
                        out_chars += len(block.get("thinking") or "")
            elif d.get("type") == "user" and msg:
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        c = block.get("content")
                        if isinstance(c, str):
                            tool_result_chars += len(c)
                        elif isinstance(c, list):
                            for cc in c:
                                if isinstance(cc, dict) and cc.get("type") == "text":
                                    tool_result_chars += len(cc.get("text") or "")
    dur = (last - first) if (first and last) else None
    return {
        "file": os.path.basename(path),
        "description": meta_description(path),
        "start": first.strftime("%H:%M:%S") if first else "-",
        "end": last.strftime("%H:%M:%S") if last else "-",
        "duration_min": round(dur.total_seconds() / 60, 1) if dur else None,
        "turns": turns,
        "tool_calls": sum(tools.values()),
        "tools": dict(tools.most_common()),
        "input_tokens": usage.get("input_tokens", 0),
        "cache_creation": usage.get("cache_creation_input_tokens", 0),
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "output_reported": usage.get("output_tokens", 0),
        "output_est": round(out_chars / 3.6),
        "tool_result_est": round(tool_result_chars / 3.6),
    }


def total(s):
    return s["input_tokens"] + s["cache_creation"] + s["cache_read"] + s["output_est"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--label", action="append", default=[], help="ID=이름 (ID는 파일 이름의 앞부분)")
    ap.add_argument("--md", action="store_true", help="마크다운 표로 출력")
    a = ap.parse_args(argv)
    labels = dict(l.split("=", 1) for l in a.label)
    files = []
    for p in a.paths:
        files.extend(glob.glob(p) or ([p] if os.path.isfile(p) else []))
    rows = []
    for p in sorted(set(files)):
        s = summarize(p)
        s["name"] = next((v for k, v in labels.items() if s["file"].startswith(k)), None) \
            or s["description"] or s["file"][:15]
        rows.append(s)
    if a.md:
        print("| 에이전트 | 시작 | 끝 | 실제 분 | 응답 수 | 도구 호출 | 캐시 생성 | 캐시 읽기 | 입력 | 출력(추정) | 합계 |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for s in rows:
            print(f"| {s['name']} | {s['start']} | {s['end']} | {s['duration_min']} | {s['turns']} | {s['tool_calls']} | "
                  f"{s['cache_creation']:,} | {s['cache_read']:,} | {s['input_tokens']:,} | ~{s['output_est']:,} | ~{total(s):,} |")
    else:
        for s in rows:
            print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
