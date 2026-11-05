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
(domains/agent_usage/CLAUDE.md "전제 1"). 동작 종류는 도구 이름이고 Bash는 실제 동작 낱말(bash_verb: 앞의 `cd <폴더> &&`·`cd <폴더>;`,
환경 변수 대입, time·env 같은 감싸는 명령을 떼고 첫 낱말의 파일 이름). 2026-11-05(p238)부터 잰 표가 이 이름이고, 그 전 표는 첫 낱말
그대로다(`Bash:cd`·`Bash:PYTHONPATH=.` 등 — 다시 재지 않는다). 명령 본문·글은 출력하지 않는다.
  --turns --toml   같은 숫자를 dispatches.toml 기록 끝에 그대로 붙일 [dispatch.turns] 블록으로 (2026-11-02: 2026-11-03부터 끝난 기록은 필수)
  --after 시각     이 시각 뒤의 턴만 (이어 보낸 회차를 앞 회차와 가른다). ISO 시각 또는 HH:MM:SS(UTC, 기록 첫날)
--rounds (2026-11-03): 회차 경계(지시가 들어온 시각마다)와 회차마다 시작·끝·응답 줄 수. 이어 보낸 회차는 여기 나온 그 회차의
  시작 시각을 --after에 주고 --actual·--turns --toml을 돌린다(앞 회차 기록에 끝 시각이 없어도 된다).
--actual (2026-11-03): 실측을 dispatches.toml의 [dispatch.actual] 줄로(분·턴·토큰 + 시작·끝 시각 start/end, UTC ISO).
  이어 보낸 회차는 --after <앞 회차 끝 시각>을 같이 주면 그 회차만 센다(시작 시각도 그 회차의 첫 줄).
  시작·끝 시각은 빗댄 기록 규칙이 '보낼 때 이미 끝나 있던 기록'을 가르는 데 쓴다(2026-11-04부터 끝난 기록에 필수).
--log (2026-11-05): 로그에서 싸게 얻는 숫자를 모두(LOG_KEYS — 응답·블록 수, 쓴·고친·임시 파일 수와 글자, 읽기·명령·검색 호출,
  도구 오류, 같은 명령 되풀이, 맥락 처음·최대·끝, 생각 블록·시간, 지시 길이; 뜻은 log_numbers 설명). --actual과 같은 창(--after·--until).
  --toml이면 기록에 붙일 [dispatch.log] 블록(`record finish`가 붙인다, 2026-11-06부터 끝난 기록에 필수). 결과(실측)이지 예측 입력이 아니다 —
  다만 지시 길이(brief_chars·brief_lines)는 보내기 전에 알 수 있는 값을 로그에서 읽은 것이다. 글·명령·경로는 출력하지 않는다.
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re


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


def _window(path, after=None, until=None):
    """기록의 줄을 (시각, 줄) 로 — --actual과 같은 창. after(시각)가 있으면 그 시각 전 줄(시각 없는 줄 포함)은 빼고,
    until(시각)이 있으면 그 시각 뒤에서 멈춘다. 두 시각은 기록 첫 시각을 보고 푼다(HH:MM:SS면 그날)."""
    cut = end_cut = None
    if after or until:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d0 = json.loads(line)
                except Exception:
                    continue
                ts0 = parse_ts(d0.get("timestamp", "")) if isinstance(d0, dict) and d0.get("timestamp") else None
                if ts0:
                    cut = _after_ts(after, ts0) if after else None
                    end_cut = _after_ts(until, ts0) if until else None
                    break
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
            if end_cut and ts and ts > end_cut:
                break
            yield ts, d


def _result_size(c):
    """도구 결과 하나의 (글자 수, 그림 수). 글은 문자열이거나 text 항목, 그림은 image 항목(글자로 안 센다)."""
    if isinstance(c, str):
        return len(c), 0
    chars = images = 0
    for x in c if isinstance(c, list) else []:
        if isinstance(x, dict):
            if x.get("type") == "text":
                chars += len(x.get("text") or "")
            elif x.get("type") == "image":
                images += 1
    return chars, images


def summarize(path, after=None, until=None):
    """after(시각)가 있으면 그 뒤의 줄만 센다 — 이어 보낸 회차를 앞 회차와 가른다(시작 시각도 그 회차의 첫 줄).
    until(시각)이 있으면 그 시각까지만 — 메인이 직접 한 일처럼 기록이 그 뒤로 이어질 때 그 요청만 잰다."""
    usage = collections.Counter()
    tools = collections.Counter()
    turns = 0
    out_chars = 0
    tool_result_chars = 0
    first = last = None
    for ts, d in _window(path, after, until):
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
                    tool_result_chars += _result_size(block.get("content"))[0]
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


_WORD = r"""(?:"[^"]*"|'[^']*'|[^\s;&|]+)"""
# 명령 앞에 붙어 실제 동작을 가리는 것들 (2026-11-05): 차례로 떼어 낸다
_LEADS = [
    re.compile(r"[({]\s*"),                                              # ( 묶음 / { 묶음
    re.compile(rf"cd\s+{_WORD}\s*(?:&&|;)\s*"),                          # cd <폴더> && / cd <폴더>;
    re.compile(r"[A-Za-z_]\w*=\$\(\s*"),                                  # X=$(명령 …) → 안의 명령
    re.compile(rf"(?:export\s+)?[A-Za-z_]\w*={_WORD}?\s*(?:&&|;)\s*"),   # X=값; / X=값 && (따로 선 대입)
    re.compile(rf"[A-Za-z_]\w*={_WORD}?\s+"),                             # X=값 명령 (환경 변수 앞붙이)
    re.compile(r"(?:time|nohup|env|sudo|exec)\s+"),                        # 감싸는 명령
    re.compile(r"timeout\s+\S+\s+"),
]


def bash_verb(cmd):
    """Bash 명령의 실제 동작 낱말 (2026-11-05): 앞의 `cd <폴더> &&`·`cd <폴더>;`, 환경 변수 대입(`X=값 명령`, `X=값;`),
    감싸는 명령(time·nohup·env·sudo·exec·timeout N)을 떼고 첫 낱말의 파일 이름만. 그 전에는 첫 낱말 그대로라
    `cd /repo && python …`이 'cd'로 찍혔다(턴 표 줄의 28 %). 명령 본문은 돌려주지 않는다."""
    s = str(cmd or "").strip()
    moved = True
    while moved:
        moved = False
        for pat in _LEADS:
            m = pat.match(s)
            if m and m.end() < len(s):
                s, moved = s[m.end():].lstrip(), True
                break
    word = s.split()[0].strip("\"'();") if s.split() else ""
    return os.path.basename(word.rstrip("/")) or "?"


def _action(blocks):
    """턴의 동작 종류: 도구 이름(여럿이면 '+'로 잇고, Bash는 실제 동작 낱말 — bash_verb). 도구가 없으면 '글'."""
    names = []
    for b in blocks:
        if not isinstance(b, dict) or b.get("type") != "tool_use":
            continue
        name = b.get("name") or "?"
        if name == "Bash":
            name = f"Bash:{bash_verb((b.get('input') or {}).get('command'))[:12]}"
        names.append(name)
    return "+".join(dict.fromkeys(names)) if names else "글"


# [dispatch.log] 칸 (2026-11-05 사용자 결정: 로그에서 싸게 얻는 숫자는 다 자동으로 뽑아 쌓는다). 모두 결과(실측)이지 예측 입력이 아니다 —
# 예측 입력(상황·files)과 섞지 않으려고 따로 둔 블록이다. 칸 뜻은 dispatches.toml 머리 주석과 log_numbers 설명.
LOG_KEYS = ("responses", "blocks", "write", "edit", "scratch_files", "write_chars", "edit_chars", "write_lines",
            "read_calls", "read_files", "read_chars", "images", "bash_calls", "bash_out_chars", "grep_calls", "glob_calls",
            "web_search", "web_fetch", "agent_calls", "other_tool_calls", "tool_errors", "repeat_cmds",
            "ctx_start_k", "ctx_max_k", "ctx_end_k", "thinking_blocks", "thinking_s", "brief_chars", "brief_lines")
_KNOWN_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Read", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "Agent", "Task"}
_SCRATCH = re.compile(r"^(?:/tmp/|/var/tmp/|(?:/root|/home/[^/]+|[A-Za-z]:/Users/[^/]+)/\.claude/|.*/AppData/Local/Temp/)", re.I)


def is_scratch(path):
    """임시 파일인가: /tmp·/var/tmp, 홈의 .claude(대화 기록·작업 메모 폴더), Windows Temp 아래."""
    p = str(path or "").replace("\\", "/")
    home = os.path.expanduser("~").replace("\\", "/").rstrip("/")
    return bool(_SCRATCH.match(p)) or p.startswith(home + "/.claude/")


def _instruction_text(d):
    """지시(도구 결과가 아닌 user 줄, 안내 줄 isMeta 제외)면 그 글, 아니면 None. 글은 길이를 재는 데만 쓴다."""
    if d.get("type") != "user" or d.get("isMeta"):
        return None
    c = d["message"].get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list) and not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
        texts = [b.get("text") or "" for b in c if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(texts) if texts else None
    return None


def log_numbers(path, after=None, until=None):
    """작업자 대화 기록 하나에서 숫자만 (2026-11-05). 창은 --actual과 같다(after·until). 글·명령·경로는 돌려주지 않는다.
    responses 서로 다른 응답(message id) 수 · blocks 응답 줄(블록) 수 = --actual의 turns
    write 새로 쓴(Write) 파일 수(Write와 Edit를 둘 다 받은 파일도 write) · edit Edit·NotebookEdit만 받은 파일 수 — 둘 다 임시 파일 뺌
    scratch_files 쓰거나 고친 임시 파일 수(is_scratch) · write_chars Write 글자 합 · edit_chars Edit 새 글(new_string) 글자 합 ·
    write_lines Write 줄 합 (셋 다 임시 파일 뺌)
    read_calls Read 호출 · read_files Read한 서로 다른 파일 · read_chars Read 결과의 글자(그림 뺌) · images 도구 결과의 그림 수
    bash_calls · bash_out_chars Bash 결과 글자 · grep_calls · glob_calls · web_search · web_fetch · agent_calls(Agent·Task) ·
    other_tool_calls 그 밖의 도구 호출 · tool_errors 오류로 끝난 도구 결과 · repeat_cmds 같은 Bash 명령을 다시 돌린 횟수(명령마다 횟수 − 1의 합)
    ctx_start_k·ctx_max_k·ctx_end_k 응답마다 맥락(입력 + 캐시 생성 + 캐시 읽기, 천 토큰)의 처음·최대·끝
    thinking_blocks 생각 블록 수 · thinking_s 기록이 남긴 생각 시간(thinkingDurationMs) 합(초 — 생각 글은 0글자로 남아 글자로 못 잰다)
    brief_chars·brief_lines 이 회차를 시작한 지시(창 안의 첫 지시)의 글자·줄 수 — 보내기 전에 알 수 있는 값이다."""
    ids, uses, ctx = set(), {}, []
    n = dict.fromkeys(LOG_KEYS, 0)
    writes, edits, scratch, reads, cmds = set(), set(), set(), set(), collections.Counter()
    thinking_ms, brief = 0, None
    for ts, d in _window(path, after, until):
        msg = d.get("message") if isinstance(d.get("message"), dict) else None
        if not msg:
            continue
        if d.get("type") == "assistant":
            n["blocks"] += 1
            mid = msg.get("id") or d.get("uuid") or f"줄{n['blocks']}"
            if mid not in ids:
                ids.add(mid)
                u = msg.get("usage") or {}
                ctx.append(sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
                               if isinstance(u.get(k) or 0, (int, float))) / 1000)
            if isinstance(d.get("thinkingDurationMs"), (int, float)):
                thinking_ms += d["thinkingDurationMs"]
            for b in msg.get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "thinking":
                    n["thinking_blocks"] += 1
                if b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name") or "?", b.get("input") if isinstance(b.get("input"), dict) else {}
                uses[b.get("id")] = name
                fp = str(inp.get("file_path") or inp.get("notebook_path") or "")
                if name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                    if is_scratch(fp):
                        scratch.add(fp)
                    elif name == "Write":
                        writes.add(fp)
                        text = str(inp.get("content") or "")
                        n["write_chars"] += len(text)
                        n["write_lines"] += len(text.splitlines())
                    else:
                        edits.add(fp)
                        news = [e.get("new_string") or "" for e in inp.get("edits") or [] if isinstance(e, dict)] \
                            if name == "MultiEdit" else [inp.get("new_string") or inp.get("new_source") or ""]
                        n["edit_chars"] += sum(len(str(x)) for x in news)
                elif name == "Read":
                    n["read_calls"] += 1
                    reads.add(fp)
                elif name == "Bash":
                    n["bash_calls"] += 1
                    cmds[str(inp.get("command") or "").strip()] += 1
                elif name == "Grep":
                    n["grep_calls"] += 1
                elif name == "Glob":
                    n["glob_calls"] += 1
                elif name == "WebSearch":
                    n["web_search"] += 1
                elif name == "WebFetch":
                    n["web_fetch"] += 1
                elif name in ("Agent", "Task"):
                    n["agent_calls"] += 1
                if name not in _KNOWN_TOOLS:
                    n["other_tool_calls"] += 1
        elif d.get("type") == "user":
            text = _instruction_text(d)
            if brief is None and text is not None:
                brief = text
            content = msg.get("content")
            for b in content if isinstance(content, list) else []:
                if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                    continue
                chars, images = _result_size(b.get("content"))
                n["images"] += images
                n["tool_errors"] += bool(b.get("is_error"))
                tool = uses.get(b.get("tool_use_id"))
                if tool == "Read":
                    n["read_chars"] += chars
                elif tool == "Bash":
                    n["bash_out_chars"] += chars
    n.update(responses=len(ids), write=len(writes), edit=len(edits - writes), scratch_files=len(scratch),
             read_files=len(reads), repeat_cmds=sum(v - 1 for v in cmds.values()),
             ctx_start_k=round(ctx[0]) if ctx else 0, ctx_max_k=round(max(ctx)) if ctx else 0, ctx_end_k=round(ctx[-1]) if ctx else 0,
             thinking_s=round(thinking_ms / 1000, 1), brief_chars=len(brief or ""), brief_lines=len((brief or "").splitlines()))
    return n


def log_toml(n, header="dispatch"):
    """log_numbers를 기록 끝에 붙일 [dispatch.log] 블록으로 (직접 한 일은 header = "direct")."""
    return "\n".join([f"[{header}.log]  # scripts/agent_usage.py --log --toml (숫자만, 실측 — 예측 입력 아님)"]
                     + [f"{k} = {_toml_num(n[k])}" for k in LOG_KEYS])


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
    ap.add_argument("--until", help="이 시각까지의 줄만 (--actual과 함께, 메인이 직접 한 일을 잴 때). ISO 시각 또는 HH:MM:SS(UTC)")
    ap.add_argument("--rounds", action="store_true",
                    help="회차 경계(지시가 들어온 시각마다)를 보여 준다 — 이어 보낸 회차의 --after에 그 회차 시작 시각을 준다")
    ap.add_argument("--actual", action="store_true",
                    help="dispatches.toml에 붙일 [dispatch.actual] 줄로 (시작·끝 시각 칸 포함, 2026-11-04부터 필수)")
    ap.add_argument("--log", action="store_true",
                    help="로그에서 싸게 얻는 숫자(파일·읽기·명령·맥락·지시 길이 등)를 [dispatch.log] 칸으로 (--toml이면 붙일 블록, 2026-11-06부터 필수)")
    a = ap.parse_args(argv)
    labels = dict(l.split("=", 1) for l in a.label)
    files = []
    for p in a.paths:
        files.extend(glob.glob(p) or ([p] if os.path.isfile(p) else []))
    rows = []
    for p in sorted(set(files)):
        s = summarize(p, a.after, a.until)
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
    if a.log:
        for p in sorted(set(files)):
            n = log_numbers(p, a.after, a.until)
            name = meta_description(p) or os.path.basename(p)[:15]
            print(f"# {name}\n{log_toml(n)}\n" if a.toml else json.dumps({"name": name, **n}, ensure_ascii=False))
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
