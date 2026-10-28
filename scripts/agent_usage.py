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

--turns (2026-10-26, 전제 1 시험): 턴마다 (동작 종류, 턴 길이, 도구가 돈 시간, 출력 글자, 그때 맥락 크기)를 숫자로 뽑아
동작 종류별 중앙값 표를 낸다. "턴은 서로 비슷한 크기다"라는 전제를 가설로 두지 않고 재기 위한 것이다
(domains/agent_usage/CLAUDE.md "전제 1"). 동작 종류는 도구 이름이고 Bash는 명령의 첫 낱말만 본다. 명령 본문·글은 출력하지 않는다.
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


def _action(blocks):
    """턴의 동작 종류: 도구 이름(여럿이면 '+'로 잇고, Bash는 명령의 첫 낱말만). 도구가 없으면 '글'."""
    names = []
    for b in blocks:
        if not isinstance(b, dict) or b.get("type") != "tool_use":
            continue
        name = b.get("name") or "?"
        if name == "Bash":
            cmd = str((b.get("input") or {}).get("command") or "").strip()
            verb = os.path.basename(cmd.split()[0]) if cmd else "?"
            name = f"Bash:{verb[:12]}"
        names.append(name)
    return "+".join(dict.fromkeys(names)) if names else "글"


def turn_rows(path):
    """턴마다 한 줄: 동작, 턴 길이(초, 이 응답 시각 → 다음 응답 시각), 도구 시간(초, 이 응답 → 도구 결과),
    출력 글자, 맥락(천 토큰 = 캐시 읽기 + 캐시 생성 + 입력). 마지막 턴의 길이는 기록의 마지막 시각까지."""
    entries = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if isinstance(d, dict) and d.get("timestamp") and isinstance(d.get("message"), dict):
                ts = parse_ts(d["timestamp"])
                if ts:
                    entries.append((ts, d))
    rows = []
    last_ts = entries[-1][0] if entries else None
    for i, (ts, d) in enumerate(entries):
        if d.get("type") != "assistant":
            continue
        msg = d["message"]
        blocks = [b for b in (msg.get("content") or []) if isinstance(b, dict)]
        out_chars = sum(len(b.get("text") or "") for b in blocks if b.get("type") == "text") \
            + sum(len(b.get("thinking") or "") for b in blocks if b.get("type") == "thinking") \
            + sum(len(json.dumps(b.get("input") or {}, ensure_ascii=False)) for b in blocks if b.get("type") == "tool_use")
        nxt = next((t for t, e in entries[i + 1:] if e.get("type") == "assistant"), last_ts)
        result = next((t for t, e in entries[i + 1:] if e.get("type") == "user"), None)
        u = msg.get("usage") or {}
        ctx_k = (u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("input_tokens", 0)) / 1000
        rows.append({
            "action": _action(blocks),
            "turn_s": round((nxt - ts).total_seconds(), 1) if nxt else None,
            "tool_s": round((result - ts).total_seconds(), 1) if result and nxt and result <= nxt else None,
            "out_chars": out_chars,
            "ctx_k": round(ctx_k),
        })
    return rows


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    return None if not xs else (xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2)


def turn_table(rows):
    """동작 종류별 중앙값 표 (마크다운). 맨 끝에 맥락 크기별 '글' 턴 길이도 낸다(생각 시간이 맥락을 타는지 보려고)."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r["action"]].append(r)
    lines = ["| 동작 | 턴 수 | 턴 길이 중앙값(초) | 도구 시간 중앙값(초) | 출력 글자 중앙값 | 맥락 중앙값(천) |",
             "|---|--:|--:|--:|--:|--:|"]
    for action, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"| {action} | {len(rs)} | {_median([r['turn_s'] for r in rs])} | {_median([r['tool_s'] for r in rs])} | "
                     f"{_median([r['out_chars'] for r in rs])} | {_median([r['ctx_k'] for r in rs])} |")
    bands = [("≤100", lambda c: c <= 100), ("100–300", lambda c: 100 < c <= 300), (">300", lambda c: c > 300)]
    parts = []
    for label, test in bands:
        rs = [r for r in rows if test(r["ctx_k"])]
        if rs:
            parts.append(f"{label}천: {len(rs)}턴, 턴 길이 중앙값 {_median([r['turn_s'] for r in rs])}초")
    lines.append("맥락 크기별 (모든 턴) — " + (" · ".join(parts) or "없음"))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--label", action="append", default=[], help="ID=이름 (ID는 파일 이름의 앞부분)")
    ap.add_argument("--md", action="store_true", help="마크다운 표로 출력")
    ap.add_argument("--turns", action="store_true", help="턴마다 동작·길이·맥락을 뽑아 동작 종류별 중앙값 표로 (전제 1 시험)")
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
    if a.turns:
        for p in sorted(set(files)):
            rows = turn_rows(p)
            print(f"### {meta_description(p) or os.path.basename(p)[:15]} — 턴 {len(rows)}")
            print(turn_table(rows))
        return
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
