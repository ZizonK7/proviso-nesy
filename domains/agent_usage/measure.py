"""작업자가 바꾼 파일을 git으로, 클라우드 세션의 숫자를 result 사건에서 (2026-11-05 사용자 결정: 싸게 얻는 숫자는 다 자동으로).

[dispatch.git] — `record send`가 보낼 때 기준을 찍고(snapshot), `record finish`가 끝날 때 견준다(compare).
  로그의 write·edit는 Write·Edit 도구만 세서 Bash(파이썬 고침 스크립트·sed·heredoc)로 바꾼 파일을 놓친다(p238: 11개를 고쳤는데 로그 1).
  기준: 저장소 이름(폴더 이름만 — 전체 경로에는 사람 이름이 들 수 있다), HEAD, 그때 더러운(고쳐졌거나 추적 안 된) 파일 수와
  알아볼 표 `dirty_hashes = ["경로 해시 8자:내용 해시 12자", …]`(경로도 해시로 — 비공개 저장소의 파일 이름을 이 공개 저장소에 남기지 않는다).
  .gitignore는 따른다(git status). 내용은 `git hash-object -w`로 그 저장소 객체에 넣어 두어 끝날 때 줄 수를 견줄 수 있게 한다.
  작업자가 바꾼 파일 = 지금 더럽고, 보낼 때는 깨끗했거나 내용이 달라진 것. 새 파일 write, 있던 파일 고침 edit, 지움 delete,
  줄은 numstat(새 파일은 그 줄 수). git_commits = 보낼 때 HEAD 뒤 커밋 수 — 메인의 커밋(보내기 전 기록 커밋 등)도 들어간다.
  그래서 커밋된 파일은 작업자 파일로 세지 않는다. 알려진 오염: 작업자가 도는 동안 메인이 같은 저장소를 커밋 없이 고치거나,
  `record finish` 전에 작업자의 변경을 커밋하면 수가 틀린다. 보낼 때 더러웠다가 작업자가 되돌려 깨끗해진 파일도 안 센다.
  지시서에 이름이 적힌 파일(named_*)은 보낼 때 HEAD에서 잰 크기 — 계산은 끝날 때 하지만 보내기 전에 알 수 있는 양이다.
[dispatch.cloud] — 클라우드 세션은 작업자 로그가 이 세션에 없다. 대신 그 세션의 result 사건(MCP list_events, kinds=["result"])에
  숫자가 있다. `record cloud <id> <숫자.json>`이 칸을 검사해 적는다. 사건을 그대로 넘기면(`{"ccr": {"data": [...]}}`) 여기서 합한다.
숫자만 다룬다 — 글(지시서·결과)·명령·경로는 저장하지 않는다.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

GIT_SEND_KEYS = ("repo", "head", "dirty", "dirty_hashes")
GIT_KEYS = ("git_write", "git_edit", "git_delete", "git_lines_added", "git_lines_removed", "git_commits",
            "named_files", "named_lines", "named_bytes", "named_dirs")
GONE = "deleted"  # 보낼 때 지워져 있던 파일의 내용 해시 자리
HASH_ITEM = re.compile(r"^[0-9a-f]{8}:([0-9a-f]{12}|deleted)$")
# 클라우드 result 사건 숫자 (2026-11-05). JSON 칸 이름 = 사건의 칸 이름(메인이 보이는 그대로 옮기게), 기록 칸 이름은 오른쪽
CLOUD_NUM_KEYS = ("results", "duration_ms", "duration_api_ms", "num_turns", "total_cost_usd",
                  "web_search_requests", "web_fetch_requests", "subagents_spawned")
CLOUD_TEXT_KEYS = ("stop_reason", "subtype")
CLOUD_MODEL_KEYS = {"inputTokens": "input_tokens", "outputTokens": "output_tokens", "cacheReadInputTokens": "cache_read_tokens",
                    "cacheCreationInputTokens": "cache_creation_tokens", "thinkingTokens": "thinking_tokens",
                    "webSearchRequests": "web_search", "costUSD": "cost_usd"}
SESSION_ID = re.compile(r"^session_[A-Za-z0-9]+$")


def _git(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, check=True).stdout


def toplevel(path: Path) -> Path | None:
    """path가 든 git 저장소의 맨 위 폴더(없으면 None)."""
    p = Path(path)
    p = p if p.is_dir() else p.parent
    try:
        return Path(_git(p, "rev-parse", "--show-toplevel").decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        return None


def status(top: Path) -> dict[str, str]:
    """지금 더러운 파일 {저장소 기준 경로: 두 글자 상태}. 추적 안 된 파일은 하나씩, .gitignore는 따른다, 이름 바꿈은 지움 + 새 파일."""
    out = _git(top, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames").decode("utf-8", "replace")
    return {e[3:]: e[:2] for e in out.split("\0") if len(e) > 3}


def path_key(rel: str) -> str:
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]


def _blob(top: Path, rel: str, overrides: dict[str, bytes]) -> str:
    """파일 내용의 해시 12자(객체에 써 둔다). 없는 파일은 GONE. overrides는 그 경로를 이 내용으로 본다."""
    if rel in overrides:
        return _git(top, "hash-object", "-w", "--stdin", data=overrides[rel]).decode().strip()[:12]
    f = top / rel
    if not f.is_file():
        return GONE
    return _git(top, "hash-object", "-w", "--", rel).decode().strip()[:12]


def snapshot(repo: Path, overrides: dict[str, bytes] | None = None) -> dict:
    """보낼 때 기준. overrides: 저장소 기준 경로 → 그 경로를 이 내용으로 본다(기록 파일 자신 — 기준 표가 들어가기 전 내용)."""
    top = toplevel(repo)
    if top is None:
        return {"skip": "저장소 밖 일"}
    head = _git(top, "rev-parse", "HEAD").decode().strip()
    dirty = status(top)
    return {"repo": top.name, "head": head, "dirty": len(dirty),
            "dirty_hashes": sorted(f"{path_key(p)}:{_blob(top, p, overrides or {})}" for p in dirty)}


def count_lines(data: bytes) -> int:
    """numstat처럼: 바이너리(NUL 포함)는 0, 아니면 줄 수(끝 줄바꿈이 없어도 한 줄)."""
    if b"\0" in data:
        return 0
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def _numstat(top: Path, *args: str) -> tuple[int, int]:
    added = removed = 0
    for line in _git(top, "diff", "--numstat", *args).decode("utf-8", "replace").splitlines():
        a, r = line.split("\t")[:2]
        added += int(a) if a.isdigit() else 0
        removed += int(r) if r.isdigit() else 0
    return added, removed


def compare(repo: Path, snap: dict, overrides: dict[str, bytes] | None = None) -> dict:
    """끝날 때: 작업자가 바꾼 파일 수·줄 수와 HEAD 뒤 커밋 수. snap = 보낼 때 기준([dispatch.git]). 못 견주면 {"skip": 이유}."""
    top, overrides = toplevel(repo), overrides or {}
    if top is None:
        return {"skip": "저장소 밖 일"}
    if top.name != snap.get("repo"):
        return {"skip": f"기준 저장소와 다른 저장소 — record finish --repo <경로>"}
    try:
        _git(top, "cat-file", "-e", f"{snap['head']}^{{commit}}")
    except subprocess.CalledProcessError:
        return {"skip": "보낼 때 HEAD 커밋이 이 저장소에 없음"}
    before = dict(h.split(":") for h in snap.get("dirty_hashes", []))
    out = dict.fromkeys(GIT_KEYS[:6], 0)
    clean_tracked = []
    for rel, code in sorted(status(top).items()):
        now = _blob(top, rel, overrides)
        was = before.get(path_key(rel))
        if was is not None and was == now:
            continue  # 보낼 때와 같다 — 작업자 몫이 아니다
        if now == GONE:
            out["git_delete"] += 1
        elif was is None:
            out["git_write" if code in ("??", "A ", "AM", "AD") else "git_edit"] += 1
        else:
            out["git_edit" if was != GONE else "git_write"] += 1
        if was is None and code != "??":
            clean_tracked.append(rel)  # 보낼 때 깨끗했던 추적 파일: 지금 HEAD와 견준다
        elif was is None:
            out["git_lines_added"] += count_lines((top / rel).read_bytes())  # 추적 안 된 새 파일
        else:  # 보낼 때 더러웠다: 그때 내용과 견준다
            old = b"" if was == GONE else _git(top, "cat-file", "-p", was)
            new = b"" if now == GONE else _git(top, "cat-file", "-p", now)
            if was == GONE or now == GONE:
                out["git_lines_added" if was == GONE else "git_lines_removed"] += count_lines(new if was == GONE else old)
            else:
                a, r = _numstat(top, was, now)
                out["git_lines_added"] += a
                out["git_lines_removed"] += r
    if clean_tracked:
        a, r = _numstat(top, "HEAD", "--", *clean_tracked)
        out["git_lines_added"] += a
        out["git_lines_removed"] += r
    out["git_commits"] = int(_git(top, "rev-list", "--count", f"{snap['head']}..HEAD").decode().strip() or 0)
    return out


PATH_TOKEN = re.compile(r"[A-Za-z0-9_.~/-]+")


def named(repo: Path, head: str, text: str) -> dict:
    """지시서 글에서 경로처럼 생긴 낱말 중 보낼 때 HEAD에 있는 것: 파일 수·줄 수·바이트, 폴더 수. 숫자만 돌려준다.
    경로 = '/'가 들었거나 '.확장자'로 끝나는 낱말. 저장소 절대 경로는 앞을 떼고, 폴더 이름 없이 파일 이름만 적힌 것은
    HEAD에서 그 이름이 하나뿐일 때만 센다(CLAUDE.md처럼 여럿이면 뺀다)."""
    top = toplevel(repo)
    out = dict.fromkeys(GIT_KEYS[6:], 0)
    if top is None or not text:
        return out
    tree = _git(top, "ls-tree", "-r", "--name-only", head).decode("utf-8", "replace").splitlines()
    by_name: dict[str, list[str]] = {}
    for p in tree:
        by_name.setdefault(p.rsplit("/", 1)[-1], []).append(p)
    dirs = {p.rsplit("/", 1)[0] for p in tree if "/" in p}
    dirs |= {d.rsplit("/", i)[0] for d in list(dirs) for i in range(1, d.count("/") + 1)}
    files, folders, prefix = set(), set(), str(top).rstrip("/") + "/"
    for tok in PATH_TOKEN.findall(text):
        tok = tok.rstrip(".-")
        if tok.startswith(prefix):
            tok = tok[len(prefix):]
        slash = "/" in tok
        tok = tok.removeprefix("./").strip("/")
        if not tok or (not slash and not re.search(r"\.[A-Za-z][A-Za-z0-9]{0,5}$", tok)):
            continue
        if tok in dirs:
            folders.add(tok)
        elif tok in by_name.get(tok.rsplit("/", 1)[-1], []):
            files.add(tok)
        elif "/" not in tok and len(by_name.get(tok, [])) == 1:
            files.add(by_name[tok][0])
    for p in files:
        out["named_bytes"] += int(_git(top, "cat-file", "-s", f"{head}:{p}").decode().strip())
        out["named_lines"] += count_lines(_git(top, "cat-file", "-p", f"{head}:{p}"))
    out["named_files"], out["named_dirs"] = len(files), len(folders)
    return out


def git_lines(block: dict) -> list[str]:
    """[dispatch.git] 표의 줄 (머리 줄 빼고)."""
    keys = [k for k in ("skip",) + GIT_SEND_KEYS + GIT_KEYS if k in block]
    out = []
    for k in keys:
        v = block[k]
        if isinstance(v, list):
            out.append(f"{k} = [" + ", ".join(f'"{x}"' for x in v) + "]")
        elif isinstance(v, str):
            out.append(f'{k} = "{v}"')
        else:
            out.append(f"{k} = {v}")
    return out


# --- 클라우드 세션 ---------------------------------------------------------------------------

def cloud_from_events(raw, until: str | None = None) -> dict:
    """result 사건들을 합한다. 사건마다 새로 쌓이는 값(model_usage_since_last_result·duration_ms·num_turns·usage.server_tool_use)은 더하고,
    프로세스 안에서 누적되는 값(duration_api_ms·subagent_stats.spawned)은 줄어들면 새 프로세스로 보고 이어 붙인다.
    modelUsage·total_cost_usd도 누적이라 더하지 않는다 — 비용은 사건마다의 costUSD를 더한다(2026-11-05 확인: p211 사건 둘).
    until(ISO)이 있으면 그 시각까지 끝난 사건만(사건의 created_at은 raw에 있다)."""
    data = raw.get("ccr", raw).get("data", []) if isinstance(raw, dict) else raw
    events = [e for e in data or [] if isinstance(e, dict) and isinstance(e.get("result"), dict)
              and (until is None or str(e.get("created_at", ""))[:19] <= until.rstrip("Z")[:19])]
    out = dict.fromkeys(CLOUD_NUM_KEYS, 0)
    models: dict[str, dict] = {}
    prev = {"duration_api_ms": 0, "subagents_spawned": 0}
    for e in events:
        r = e["result"].get("internal_anthropic_catchall", e["result"])
        out["results"] += 1
        out["duration_ms"] += r.get("duration_ms") or 0
        out["num_turns"] += r.get("num_turns") or 0
        stu = (r.get("usage") or {}).get("server_tool_use") or {}
        out["web_search_requests"] += stu.get("web_search_requests") or 0
        out["web_fetch_requests"] += stu.get("web_fetch_requests") or 0
        cum = {"duration_api_ms": r.get("duration_api_ms") or 0, "subagents_spawned": (r.get("subagent_stats") or {}).get("spawned") or 0}
        for k, v in cum.items():
            out[k] += v - prev[k] if v >= prev[k] else v
            prev[k] = v
        for name, u in (r.get("model_usage_since_last_result") or r.get("modelUsage") or {}).items():
            m = models.setdefault(name, dict.fromkeys(CLOUD_MODEL_KEYS, 0))
            for k in CLOUD_MODEL_KEYS:
                m[k] += u.get(k) or 0
        for k in CLOUD_TEXT_KEYS:
            out[k] = r.get(k) or ""
    out["total_cost_usd"] = round(sum(m["costUSD"] for m in models.values()), 6)
    for m in models.values():
        m["costUSD"] = round(m["costUSD"], 6)
    out["models"] = models
    return out


def cloud_errors(n: dict) -> list[str]:
    """record cloud의 숫자 JSON 검사: 칸이 다 있고 모르는 칸이 없고 0 이상의 수."""
    errors = []
    allowed = set(CLOUD_NUM_KEYS) | set(CLOUD_TEXT_KEYS) | {"models", "session"}
    unknown = [k for k in n if k not in allowed]
    if unknown:
        errors.append(f"모르는 칸: {', '.join(unknown)} (숫자만 — 결과 글은 넣지 않는다)")
    missing = [k for k in CLOUD_NUM_KEYS + CLOUD_TEXT_KEYS + ("models",) if k not in n]
    if missing:
        errors.append(f"빠진 칸: {', '.join(missing)}")
    bad = [k for k in CLOUD_NUM_KEYS if k in n and (isinstance(n[k], bool) or not isinstance(n[k], (int, float)) or n[k] < 0)]
    if bad:
        errors.append(f"{', '.join(bad)}는 0 이상의 수여야 함")
    for k in CLOUD_TEXT_KEYS:
        if k in n and not (isinstance(n[k], str) and re.fullmatch(r"[a-z_]{0,40}", n[k])):
            errors.append(f"{k}는 짧은 영문 낱말이어야 함(예: end_turn, success)")
    models = n.get("models")
    if models is not None:
        if not (isinstance(models, dict) and models):
            errors.append("models는 { 모델 이름: { inputTokens, … } } 표여야 함")
        else:
            for name, u in models.items():
                if not (re.fullmatch(r"[a-z0-9.-]{1,60}", str(name)) and isinstance(u, dict)):
                    errors.append(f"models의 '{name}'는 모델 이름(예: claude-haiku-5-5)과 표여야 함")
                    continue
                miss = [k for k in CLOUD_MODEL_KEYS if k not in u]
                extra = [k for k in u if k not in CLOUD_MODEL_KEYS]
                neg = [k for k in CLOUD_MODEL_KEYS if k in u and (isinstance(u[k], bool) or not isinstance(u[k], (int, float)) or u[k] < 0)]
                if miss or extra or neg:
                    errors.append(f"models.{name}: 빠진 칸 {miss or '없음'} · 모르는 칸 {extra or '없음'} · 수가 아닌 칸 {neg or '없음'}"
                                  f" (칸: {', '.join(CLOUD_MODEL_KEYS)})")
    if "session" in n and not (isinstance(n["session"], str) and SESSION_ID.match(n["session"])):
        errors.append("session은 session_… 모양이어야 함")
    return errors


def _num(v) -> str:
    return repr(round(v, 6)) if isinstance(v, float) else str(v)


def cloud_lines(n: dict) -> list[str]:
    """[dispatch.cloud] 표의 줄 (머리 줄 빼고). 모델 칸 이름은 snake로."""
    out = [f"{k} = {_num(n[k])}" for k in CLOUD_NUM_KEYS]
    out += [f'{k} = "{n[k]}"' for k in CLOUD_TEXT_KEYS]
    for name, u in n["models"].items():
        cells = ", ".join(f"{CLOUD_MODEL_KEYS[k]} = {_num(u[k])}" for k in CLOUD_MODEL_KEYS)
        out.append(f'models."{name}" = {{ {cells} }}')
    return out
