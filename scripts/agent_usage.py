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
  --turns --toml   같은 숫자를 dispatches.toml 기록 끝에 그대로 붙일 [dispatch.turns] 블록으로 (2026-11-02: 2026-11-03부터 끝난 기록은 필수)
  --after 시각     이 시각 뒤의 턴만 (이어 보낸 회차를 앞 회차와 가른다). ISO 시각 또는 HH:MM:SS(UTC, 기록 첫날)
--rounds (2026-11-03): 회차 경계(지시가 들어온 시각마다)와 회차마다 시작·끝·응답 줄 수. 이어 보낸 회차는 여기 나온 그 회차의
  시작 시각을 --after에 주고 --actual·--turns --toml을 돌린다(앞 회차 기록에 끝 시각이 없어도 된다).
--actual (2026-11-03): 실측을 dispatches.toml의 [dispatch.actual] 줄로(분·턴·토큰 + 시작·끝 시각 start/end, UTC ISO).
  이어 보낸 회차는 --after <앞 회차 끝 시각>을 같이 주면 그 회차만 센다(시작 시각도 그 회차의 첫 줄).
  시작·끝 시각은 빗댄 기록 규칙이 '보낼 때 이미 끝나 있던 기록'을 가르는 데 쓴다(2026-11-04부터 끝난 기록에 필수).
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


def summarize(path, after=None):
    """after(시각)가 있으면 그 뒤의 줄만 센다 — 이어 보낸 회차를 앞 회차와 가른다(시작 시각도 그 회차의 첫 줄)."""
    cut = None
    if after:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d0 = json.loads(line)
                except Exception:
                    continue
                ts0 = parse_ts(d0.get("timestamp", "")) if isinstance(d0, dict) and d0.get("timestamp") else None
                if ts0:
                    cut = _after_ts(after, ts0)
                    break
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
            if cut and (ts is None or ts < cut):
                continue
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
        "start_iso": first.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if first else None,
        "end_iso": last.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if last else None,
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


def _after_ts(after, first):
    """--after 값을 시각으로. ISO 시각이면 그대로, HH:MM:SS면 기록 첫 시각의 날짜(UTC)에 붙인다."""
    ts = parse_ts(after)
    if ts and ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt.timezone.utc)
    if ts is None and first is not None:
        ts = dt.datetime.combine(first.date(), dt.time.fromisoformat(after), tzinfo=dt.timezone.utc)
    return ts


def turn_rows(path, after=None):
    """턴마다 한 줄: 동작, 턴 길이(초, 이 응답 시각 → 다음 응답 시각), 도구 시간(초, 이 응답 → 도구 결과),
    출력 글자, 맥락(천 토큰 = 캐시 읽기 + 캐시 생성 + 입력). 마지막 턴의 길이는 기록의 마지막 시각까지.
    after(시각)가 있으면 그 뒤에 시작한 턴만 (이어 보낸 회차)."""
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
    cut = _after_ts(after, entries[0][0] if entries else None) if after else None
    for i, (ts, d) in enumerate(entries):
        if d.get("type") != "assistant" or (cut and ts < cut):
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


def rounds(path):
    """회차 경계: 사람(또는 메인)이 보낸 지시(도구 결과가 아닌 user 줄)마다 새 회차. [(시작, 끝, 응답 줄 수)] (UTC)."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict) or not isinstance(d.get("message"), dict):
                continue
            ts = parse_ts(d.get("timestamp", "")) if d.get("timestamp") else None
            if not ts:
                continue
            content = d["message"].get("content")
            is_instruction = d.get("type") == "user" and (
                isinstance(content, str) or (isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "text" for b in content)
                    and not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)))
            if not out or (is_instruction and out[-1][2] > 0):  # 답한 뒤에 들어온 지시만 새 회차(첫 지시에 붙는 안내 줄은 같은 회차)
                out.append([ts, ts, 0])
            out[-1][1] = ts
            out[-1][2] += d.get("type") == "assistant"
    return [(s, e, n) for s, e, n in out]


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


def _toml_num(x):
    return str(round(x, 1)) if isinstance(x, float) else str(x)


def turn_toml(rows):
    """동작 종류별 숫자를 dispatches.toml 기록에 붙일 [dispatch.turns] 블록으로.
    n 턴 수 · sum_s 합한 턴 길이(초) · 중앙값: turn_s 턴 길이, tool_s 도구 시간, out_chars 출력 글자, ctx_k 맥락(천 토큰)."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r["action"]].append(r)
    lines = ["[dispatch.turns]  # scripts/agent_usage.py --turns --toml"]
    for action, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        vals = {"n": len(rs), "sum_s": round(sum(r["turn_s"] or 0 for r in rs), 1),
                "turn_s": _median([r["turn_s"] for r in rs]), "tool_s": _median([r["tool_s"] for r in rs]),
                "out_chars": _median([r["out_chars"] for r in rs]), "ctx_k": _median([r["ctx_k"] for r in rs])}
        body = ", ".join(f"{k} = {_toml_num(v)}" for k, v in vals.items() if v is not None)
        lines.append(f"{json.dumps(action, ensure_ascii=False)} = {{ {body} }}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--label", action="append", default=[], help="ID=이름 (ID는 파일 이름의 앞부분)")
    ap.add_argument("--md", action="store_true", help="마크다운 표로 출력")
    ap.add_argument("--turns", action="store_true", help="턴마다 동작·길이·맥락을 뽑아 동작 종류별 중앙값 표로 (전제 1 시험)")
    ap.add_argument("--toml", action="store_true", help="--turns 결과를 dispatches.toml에 붙일 [dispatch.turns] 블록으로")
    ap.add_argument("--after", help="이 시각 뒤의 턴만 (이어 보낸 회차). ISO 시각 또는 HH:MM:SS(UTC)")
    ap.add_argument("--rounds", action="store_true",
                    help="회차 경계(지시가 들어온 시각마다)를 보여 준다 — 이어 보낸 회차의 --after에 그 회차 시작 시각을 준다")
    ap.add_argument("--actual", action="store_true",
                    help="dispatches.toml에 붙일 [dispatch.actual] 줄로 (시작·끝 시각 칸 포함, 2026-11-04부터 필수)")
    a = ap.parse_args(argv)
    labels = dict(l.split("=", 1) for l in a.label)
    files = []
    for p in a.paths:
        files.extend(glob.glob(p) or ([p] if os.path.isfile(p) else []))
    rows = []
    for p in sorted(set(files)):
        s = summarize(p, a.after)
        s["name"] = next((v for k, v in labels.items() if s["file"].startswith(k)), None) \
            or s["description"] or s["file"][:15]
        rows.append(s)
    if a.rounds:
        iso = lambda x: x.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for p in sorted(set(files)):
            print(f"# {meta_description(p) or os.path.basename(p)[:15]}")
            for i, (s, e, n) in enumerate(rounds(p), 1):
                print(f"회차 {i}: {iso(s)} → {iso(e)} · {round((e - s).total_seconds() / 60, 1)}분 · 응답 줄 {n}"
                      + (f"   (이 회차만: --after {iso(s)})" if i > 1 else ""))
        return
    if a.turns:
        for p in sorted(set(files)):
            rows = turn_rows(p, a.after)
            name = meta_description(p) or os.path.basename(p)[:15]
            if a.toml:
                print(f"# {name} — 턴 {len(rows)}\n{turn_toml(rows)}\n")
            else:
                print(f"### {name} — 턴 {len(rows)}")
                print(turn_table(rows))
        return
    if a.actual:
        for s in rows:
            print(f"# {s['name']}\n[dispatch.actual]\nstatus = \"done\"\n"
                  f"minutes = {s['duration_min']}  # 기록의 첫 시각 → 끝 시각. 이어 보낸 회차는 알림의 실행 시간으로 고친다\n"
                  f"turns = {s['turns']}\ntokens_m = {total(s) / 1e6:.2f}  # 캐시 생성 + 캐시 읽기 + 입력 + 출력(추정)\n"
                  f"start = \"{s['start_iso']}\"\nend = \"{s['end_iso']}\"\n")
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
