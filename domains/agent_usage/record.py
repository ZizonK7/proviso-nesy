"""묶음 명령 — 보낼 때와 끝났을 때의 기록 절차를 한 번에 (2026-11-03 사용자 결정, CLAUDE.md '보낼까 판단').

사용법 (저장소 루트):
  python -m domains.agent_usage.record send <보낼 일 파일>
      기록을 덧붙인다: 상황 값·손 예측(파일) + 계산기 답(그 기록의 상황 값으로) + 보낼까 판단(decide) + 배치 머리(AGENT-LOG에 없으면).
      그리고 빗댄 기록 규칙(정해진 일이면)과 사용자에게 할 말을 보여 준다. 기록 id는 다음 빈 번호(파일에 id가 있으면 그것).
  python -m domains.agent_usage.record finish <기록 id> <작업자 대화 기록> [--after 시각] [--report 경로] [--repo 경로] [--feedback "F102,F103 | 없음: 이유"]
                                             [--missed "F014,F051 | 없음: 이유"]
      실측(분·줄·토큰·시작·끝)과 턴 길이 표, 로그 숫자([dispatch.log], 2026-11-05), git 숫자([dispatch.git], 2026-11-05)를 그 기록에 채운다.
      이어 보낸 회차는 --after(`agent_usage.py --rounds`로 본 그 회차 시작). 이미 있는 턴 표·로그 숫자는 다시 쓰지 않는다.
      git: 보낼 때 찍은 기준(send)과 지금을 견준다 — 아무것도 쓰기 전에. 저장소는 기준의 이름으로 찾고(이 저장소, 그 옆 폴더), 못 찾으면 --repo.
      --feedback: 이번 일에서 백서에 올린 피드백 번호(쉼표로) 또는 "없음: 이유" → review.feedback (2026-11-06부터 끝난 기록에 필수).
      --missed: 보낼 때 이미 백서에 있었는데 [feedback] hit에 없던, 알고 보니 이 일에 걸린 피드백 번호(쉼표로) 또는 "없음: 이유"
                → review.missed (2026-11-07부터 보낸 기록이 끝나면 필수, hit와 겹치면 막는다). 예: 새로 올린 항목을 막았을 기존 항목.
  python -m domains.agent_usage.record cloud <기록 id> <숫자.json> [--until 시각]
      클라우드 세션 일의 result 사건 숫자를 [dispatch.cloud]로(2026-11-05). JSON은 measure.CLOUD_* 칸(사건의 칸 이름 그대로, 합한 값)
      또는 MCP list_events(kinds=["result"]) 출력 그대로 — 그러면 여기서 합한다(--until: 그 시각까지 끝난 사건만). session 칸이 있으면 기록에도.
  python -m domains.agent_usage.record direct <직접 할 일 파일>
      직접 하기로 한 일을 direct.toml에 덧붙인다(보낼까 판단과 함께).
  python -m domains.agent_usage.record finish <m001> <메인 대화 기록> --after 시작 --until 끝
      직접 한 일의 실측(메인이 그 요청에 쓴 분·줄·토큰)과 같은 창의 로그 숫자([direct.log])를 채운다.
돌아보기(review.reason, 빗나가면 wrong·why)와 배치 줄의 표·교훈은 판단이 필요해 메인이 손으로 쓴다.

보낼 일 파일(TOML): project, batch, task, model, effort, agent, round, [files](write, edit — 쓰는 파일 수, 2026-11-04부터 필수),
(date, id, size), [situation], [predicted](minutes, turns, tokens_m, rules, analog, reason; told은 비우면 가운데 값의 구간),
(선택) [decide](why, left, main_ctx_k),
(선택) repo = "<경로>" — 작업자가 일할 git 저장소(기본: 기록 파일이 든 저장소 = 이 저장소). 보낼 때 기준([dispatch.git])을 찍는다,
session = "session_…" — 클라우드 세션으로 보낸 일(S_cloud_session = 예)의 세션 id. 2026-11-06부터 클라우드 일에 필수.
(선택) brief = "<저장소>:<상대 경로>.md" — 작업자에게 준 지시서 글이 있는 곳(예: "gemmin:docs/briefs/p246.md", 직접 할 일 파일도 같다).
  기록에 그대로 옮긴다. 이 저장소는 공개라 지시서 글은 여기 저장하지 않는다 — 비공개 저장소에 두고 경로만(feedback labels --brief-root가 붙여 읽는다).
[feedback] — 피드백 읽기(feedback/CLAUDE.md "강제", 직접 할 일 파일도 같다). 기록에는 [dispatch.feedback]으로 남는다.
  read = ["common", …] — 읽은 메인 피드백 파일 이름(feedback/main/). 2026-11-06부터 필수. 2026-11-07부터는 메인 파일 **전부**가
    들어 있지 않으면 보내지 않는다(그 전 날짜는 `python -m feedback topics "<task>"`가 고른 파일 — 지금은 참고로만 찍는다).
  searched = ["낱말", …] — 메인 모델이 고른 백서 색인 낱말(`python -m feedback find <낱말>...`을 돌린 것). 2026-11-07부터 필수, 한 개 이상.
    보낸 뒤 출력에 그 낱말로 찾은 백서 항목(번호 · 제목 · 자리)이 찍힌다.
  hit = ["F014", …] — 이번 일에 걸린다고 본 항목(메인·백서, 백서에 있는 번호). 2026-11-07부터 필수. 없으면 hit = [] 와 hit_none = "이유".
model·effort는 보낼 모델과 effort(dispatches.MODELS·EFFORTS). S_other_model은 이 둘에서 계산해 상황에 넣는다(적으면 같아야 한다).
files는 실제 지시서에서 센다(dispatches.py FILES_COUNTS 주석): 지시서가 수를 안 정하면 files = {}(모름).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
import tomllib
from pathlib import Path

import feedback as fb
from scripts import agent_usage as au

from . import analog as an
from . import decide as de
from . import dispatches as dp
from . import measure as ms
from . import predict as pr

HERE = Path(__file__).resolve().parent


def _v(x) -> str:
    """TOML 값 하나."""
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, (int, float)):
        return f"{x:g}" if isinstance(x, float) else str(x)
    if isinstance(x, (dt.date, dt.datetime)):
        return x.isoformat()
    if isinstance(x, list):
        return "[" + ", ".join(_v(i) for i in x) + "]"
    if isinstance(x, dict):
        return "{ " + ", ".join(f"{k} = {_v(v)}" for k, v in x.items()) + " }"
    return json.dumps(str(x), ensure_ascii=False)


def next_id(records: list[dict]) -> str:
    nums = [int(d["id"][1:]) for d in records if re.fullmatch(r"p\d+", d["id"])]
    n = max(nums, default=0) + 1
    return f"p{n:02d}" if n < 100 else f"p{n}"


def token_classes(rng: list[float]) -> list[str]:
    lo, hi = dp.TOKEN_CLASSES.index(dp.token_class(rng[0])), dp.TOKEN_CLASSES.index(dp.token_class(rng[-1]))
    return list(dp.TOKEN_CLASSES[lo:hi + 1])


def _size_and_main(job: dict, situation: dict, project: str, predicted: dict) -> tuple[tuple[float, float], float]:
    """일의 크기: 손 예측(보내기 전에 적은 것 — 빗댄 기록에서 출발해 계산기보다 잘 맞는다)의 가운데 값, 없으면 계산기."""
    t, k = predicted.get("turns", []), predicted.get("tokens_m", [])
    size = (math.sqrt(t[0] * t[1]), math.sqrt(k[0] * k[1])) if len(t) >= 2 and len(k) >= 2 else de.from_calculator(situation, project)
    if not size:
        raise SystemExit("손 예측에 turns·tokens_m 범위가 없고 계산기도 '모름' — 보낼까 판단을 못 한다")
    main_k = job.get("decide", {}).get("main_ctx_k")
    if main_k is None:
        log = de.latest_main_log()
        main_k = de.main_context_k(log) if log else None
    if main_k is None:
        raise SystemExit("메인 맥락을 못 읽음 — 파일의 [decide]에 main_ctx_k(천 토큰)를 적는다")
    return size, float(main_k)


FEEDBACK_KEYS = ("read", "searched", "hit", "hit_none")  # 보낼 일 파일의 [feedback] 칸 → 기록의 [dispatch.feedback]/[direct.feedback]


def _feedback_table(job: dict, rid: str, date, root: Path = dp.ROOT) -> dict | None:
    """보낼 일 파일의 [feedback] 표를 검사한다(2026-11-05·11-06 사용자 결정, feedback/CLAUDE.md "강제"). 기록에 옮길 칸만 돌려준다.
    FEEDBACK_REQUIRED_FROM부터 read가 없거나 빠진 파일이 있으면 막는다 — FEEDBACK_ALL_FROM부터는 메인 파일 전부와 searched·hit도
    (dispatches.feedback_send_errors). 칸이 있으면 날짜와 상관없이 모양을 본다."""
    fbt = job.get("feedback")
    read = fbt.get("read") if isinstance(fbt, dict) else None
    main_dir = root / "feedback" / "main"
    rec = {"id": rid, "date": str(date), "project": job.get("project"), "task": job.get("task", ""), "feedback": fbt}
    late = dp.on_or_after(rec, dp.FEEDBACK_REQUIRED_FROM)
    all_late = dp.on_or_after(rec, dp.FEEDBACK_ALL_FROM)
    if fbt is None and not late:
        return None
    need = fb.main_files(main_dir) if all_late else fb.topics(str(job.get("task", "")), main_dir)
    how = (f"메인 피드백은 전부 읽는다({dp.FEEDBACK_ALL_FROM}부터)" if all_late
           else "`python -m feedback topics \"<task>\"`")
    if isinstance(read, list):
        missing = [s for s in need if s not in read]
        if missing:
            raise SystemExit("메인 피드백을 다 읽지 않음 — 빠진 파일: " + ", ".join(f"feedback/main/{s}.md" for s in missing)
                             + f" — 읽고 보낼 일 파일의 [feedback] read에 적어라 ({how})")
    elif read is None:
        raise SystemExit("보낼 일 파일에 [feedback] read가 없음 — 이 일에 읽을 메인 피드백: "
                         + ", ".join(f"feedback/main/{s}.md" for s in need) + " — 읽고 [feedback] read = [...]에 적어라")
    bad = dp.feedback_send_errors(rec, root)
    if bad:
        raise SystemExit("\n".join(bad))
    return {k: fbt[k] for k in FEEDBACK_KEYS if k in fbt}


FEEDBACK_SHOW_MAX = 25  # 읽은 메인 피드백 줄이 이보다 많으면 번호와 제목만 찍는다


def feedback_lines(table: dict, root: Path = dp.ROOT, task: str | None = None) -> list[str]:
    """보낸 뒤 출력: 읽은 메인 피드백 파일들의 F 줄 그대로(메인이 지시서에 붙인다, 줄이 많으면 번호와 제목만),
    키워드가 고른 파일(참고), searched 낱말로 찾은 백서 항목(번호 · 제목 · 자리 — 메인 모델의 맥락을 한 번 지나가게), hit."""
    read = table.get("read", [])
    main_dir = root / "feedback" / "main"
    by = {m["stem"]: m for m in fb.mains(main_dir)}
    rows = [(s, i, line) for s in read if s in by for i, line in by[s]["ids"]]
    out = ["읽은 메인 피드백: " + ", ".join(f"feedback/main/{s}.md" for s in read) + " — 지시서에 이 경로를 적어 작업자도 읽게 한다"]
    if len(rows) > FEEDBACK_SHOW_MAX:
        titles = {e["id"]: e["title"] for e in fb.entries(root / "feedback" / "whitepaper.md")}
        out += [f"  [{s}] {i} · {titles.get(i, '')}" for s, i, _ in rows]
    else:
        out += [f"  [{s}] {line}" for s, _, line in rows]
    return out + search_lines(table, root, task)


def search_lines(table: dict, root: Path = dp.ROOT, task: str | None = None) -> list[str]:
    """searched 낱말로 찾은 백서 항목과 hit (2026-11-06 사용자 결정 — 피드백 정답 모으기)."""
    out = []
    paper = root / "feedback" / "whitepaper.md"
    if task is not None:
        out.append("키워드가 고른 메인 파일(참고): " + ", ".join(fb.topics(task, root / "feedback" / "main")))
    if table.get("searched"):
        hits = fb.find(table["searched"], paper)
        out.append(f"백서에서 찾은 항목 (낱말: {', '.join(table['searched'])}) {len(hits)}개 — 걸리는 것은 백서에서 다시 읽는다:")
        out += [f"  {e['id']} · {e['title']} — 자리 {e.get('자리', '?')}" for e in hits]
    if "hit" in table:
        titles = {e["id"]: e["title"] for e in fb.entries(paper)}
        out.append("이번 일에 걸린다고 본 항목(hit): " + (", ".join(f"{i} {titles.get(i, '')}" for i in table["hit"])
                                                     or f"없음 — {table.get('hit_none', '')}"))
    return out


def send(job_path: Path, path: Path = dp.HERE / "dispatches.toml", log_path: Path = dp.AGENT_LOG) -> str:
    job = tomllib.loads(job_path.read_text(encoding="utf-8"))
    records = dp.load(path)
    for k in ("project", "batch", "task", "model", "effort", "agent", "round", "situation", "predicted"):
        if k not in job:
            raise SystemExit(f"보낼 일 파일에 {k}가 없음")
    if job["model"] not in dp.MODELS or job["effort"] not in dp.EFFORTS:
        raise SystemExit(f"model은 {dp.MODELS}, effort는 {dp.EFFORTS} 중 하나 (새 모델이면 dispatches.py MODELS에 더한다)")
    rid = job.get("id") or next_id(records)
    if any(d["id"] == rid for d in records):
        raise SystemExit(f"기록 id {rid}가 이미 있음")
    date = job.get("date") or dt.datetime.now(dt.timezone.utc).date()
    if "files" not in job and str(date) >= dp.FILES_REQUIRED_FROM:
        raise SystemExit("보낼 일 파일에 [files]가 없음 — 지시서에서 쓰는 파일 수를 센다: write = 새로 만들거나 통째로 다시 쓰는 파일, "
                         "edit = 일부 고치는 파일 (읽는 파일·절·항목은 안 센다). 지시서가 수를 안 정하면 files = {}")
    ftab = _feedback_table(job, rid, date)
    situation, predicted, project = dict(job["situation"]), dict(job["predicted"]), job["project"]
    other = dp.other_model(job["model"], job["effort"])
    if situation.get("S_other_model", other) != other:
        raise SystemExit(f"상황의 S_other_model '{situation['S_other_model']}'이 {job['model']} {job['effort']}로 계산한 '{other}'와 다름 "
                         f"— 상황에서 빼면 계산해 넣는다")
    situation["S_other_model"] = other
    if "files" in job:
        bad = dp.files_errors({"id": rid, "date": str(date), "project": project, "files": job["files"], "situation": situation})
        if bad:
            raise SystemExit("\n".join(bad))
    kn = pr.load_kn()
    pred = pr.predict(situation, project, pr.live_pieces(kn), kn)
    calc_m = pred.minutes()
    size, main_k = _size_and_main(job, situation, project, predicted)
    c = de.costs(size[0], size[1], main_k, de.params(), job.get("decide", {}).get("left"))
    why = job.get("decide", {}).get("why")
    if not why:
        if c["cheaper"] != "보냄":
            raise SystemExit(f"비용으로는 직접이 싸다(직접 {c['direct_m']:.1f}M · 보냄 {c['send_m']:.1f}M) — 그래도 보내면 [decide] why에 "
                             f"다른 까닭({', '.join(dp.DECIDE_WHY[1:])})을 적고, 아니면 직접 한다(`record direct`)")
        why = ["비용"]
    told = predicted.get("told") or dp.say_zone(predicted.get("minutes", []))
    lines = ["", "[[dispatch]]", f'id = "{rid}"', f"project = {_v(project)}", f"batch = {job['batch']}", f"date = {_v(date)}",
             f"task = {_v(job['task'])}", f"model = {_v(job['model'])}", f"effort = {_v(job['effort'])}",
             f"agent = {_v(job['agent'])}", f"round = {job['round']}"]
    cloud = situation.get("S_cloud_session") == "예"
    if "session" in job:
        if not (isinstance(job["session"], str) and ms.SESSION_ID.match(job["session"])):
            raise SystemExit("session은 클라우드 세션 id(session_…)여야 함")
        lines.append(f"session = {_v(job['session'])}")
    elif cloud and str(date) >= dp.CLOUD_REQUIRED_FROM:
        raise SystemExit("클라우드 세션으로 보내는 일(S_cloud_session = 예)은 보낼 일 파일에 session = \"session_…\"(만든 세션 id)를 적는다 "
                         "— 끝나면 그 세션의 result 사건 숫자를 `record cloud`로 옮긴다")
    lines += _brief_line(job)
    if job.get("size"):
        lines.append(f"size = {_v(job['size'])}")
    if "files" in job:
        lines.append(f"files = {_v(job['files'])}")
    lines.append("[dispatch.situation]")
    lines += [f"{k} = {_v(v)}" for k, v in situation.items()]
    lines += ["[dispatch.predicted]", "written_before = true", f"told = {_v(told)}"]
    for k in ("minutes", "turns", "tokens_m"):
        if k in predicted:
            lines.append(f"{k} = {_v(predicted[k])}")
    if "tokens_m" in predicted:
        lines.append(f"tokens_class = {_v(predicted.get('tokens_class') or token_classes(predicted['tokens_m']))}")
    for k in ("rules", "analog", "reason"):
        if k in predicted:
            lines.append(f"{k} = {_v(predicted[k])}")
    lines.append("hypotheses = []")
    if calc_m:
        lines += ["[dispatch.calc]", f'told = "{pred.told()}"', f"minutes = [{round(calc_m[0][0], 2):g}, {round(calc_m[0][1], 2):g}]"]
    lines += de.decide_block(c, "dispatch", why, "보냄").rstrip("\n").split("\n")
    if ftab is not None:
        lines += ["[dispatch.feedback]"] + [f"{k} = {_v(v)}" for k, v in ftab.items()]
    lines += ["[dispatch.actual]", 'status = "unknown"  # 예측만 기록됨 (record finish가 채운다)']
    text = path.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    if job["batch"] not in dp.logged_batches(log_path) and project != "batman":
        log = log_path.read_text(encoding="utf-8").rstrip("\n")
        log += (f"\n\n## 배치 {job['batch']} · {date} · {job['task'][:40]}\n"
                f"- (보낸 뒤 결과가 나오면 표 한 줄 — 모델·effort·품질 1–5·메모 — 과 교훈을 적는다)\n")
        log_path.write_text(log, encoding="utf-8")
    if not cloud:  # 보낼 때 기준(2026-11-05): 기록 파일과 배치 머리를 쓴 뒤에 찍는다 — 메인의 보내기 전 기록도 기준에 들어간다
        _git_send(path, Path(job["repo"]) if job.get("repo") else None)
    out = [f"기록 {rid}를 덧붙였다 ({path.name}). 사용자에게: 말할 구간 '{told}'({dp.ZONE_SAY.get(told, '')}), "
           f"분 {predicted.get('minutes')}, 토큰 {predicted.get('tokens_m')}M — 이유: {predicted.get('reason', '')[:80]}",
           f"계산기: {pred.told() or '모름'}" + (f" {calc_m[0][0]:.1f}–{calc_m[0][1]:.1f}분" if calc_m else ""),
           de.explain(c)]
    if situation.get("S_specified") == "예":
        d = next(r for r in dp.load(path) if r["id"] == rid)
        out.append("빗댄 기록 규칙(시험 중, 참고): " + an.show(d, dp.load(path), an.load_rule()))
    if ftab is not None:
        out += feedback_lines(ftab, task=job["task"])
    return "\n".join(out)


GIT_TABLE = re.compile(r"^\[dispatch\.git\]\n(?:[^\[\n][^\n]*\n)*", flags=re.M)


def _git_table(block: dict) -> str:
    return "\n".join(["[dispatch.git]"] + ms.git_lines(block)) + "\n"


def _git_send(path: Path, repo: Path | None) -> None:
    """[dispatch.git] 기준 찍기를 파일 끝 기록(방금 덧붙인 것)의 [dispatch.actual] 앞에 넣는다.
    repo가 없으면 기록 파일이 든 저장소(= 이 저장소). 기록 파일 자신은 기준 표가 들어가기 전 내용으로 해시한다(finish가 표를 떼고 견준다)."""
    text = path.read_text(encoding="utf-8")
    top = ms.toplevel(repo or path)
    overrides = {}
    if top is not None:
        try:
            overrides[path.resolve().relative_to(top.resolve()).as_posix()] = text.encode("utf-8")
        except ValueError:
            pass
    snap = ms.snapshot(top, overrides) if top is not None else {"skip": "저장소 밖 일"}
    i = text.rindex("[dispatch.actual]\n")
    path.write_text(text[:i] + _git_table(snap) + text[i:], encoding="utf-8")


def _find_repo(name: str, path: Path) -> Path | None:
    """기준의 저장소 이름으로 폴더를 찾는다: 기록 파일이 든 저장소, 이 저장소, 그 옆 폴더(이 PC의 ../stock-rader 같은)."""
    for c in (path, dp.ROOT, dp.ROOT.parent / name):
        top = ms.toplevel(c) if Path(c).exists() else None
        if top is not None and top.name == name:
            return top
    return None


def _git_finish(d: dict, text: str, a: int, b: int, path: Path, log: Path, after, until, repo: Path | None) -> dict | None:
    """끝날 때 [dispatch.git] 숫자. 기록 파일에 아무것도 쓰기 전에 부른다. 클라우드 세션 일이면 None(git 대신 [dispatch.cloud])."""
    snap = d.get("git")
    if d.get("situation", {}).get("S_cloud_session") == "예":
        return None
    if snap is None:
        return {"skip": "보낼 때 기준을 안 찍음 (record send가 기준을 찍기 전 기록)"}
    if "skip" in snap or "git_write" in snap:
        return None  # 이미 끝난 표
    top = ms.toplevel(repo) if repo else _find_repo(snap["repo"], path)
    if top is None:
        return {**snap, "skip": "기준 저장소를 못 찾음 — record finish … --repo <경로>"}
    overrides = {}
    try:
        rel = path.resolve().relative_to(top.resolve()).as_posix()
        block = GIT_TABLE.sub("", text[a:b], count=1)
        overrides[rel] = (text[:a] + block + text[b:]).encode("utf-8")
    except ValueError:
        pass
    counts = ms.compare(top, snap, overrides)
    if "skip" in counts:
        return {**snap, **counts}
    return {**snap, **counts, **ms.named(top, snap["head"], au.brief_text(str(log), after, until))}


def _put_git(block: str, g: dict) -> str:
    m = GIT_TABLE.search(block)
    if m:
        return block[:m.start()] + _git_table(g) + block[m.end():]
    i = block.find("[dispatch.actual]\n")
    return block[:i] + _git_table(g) + block[i:] if i >= 0 else block.rstrip("\n") + "\n" + _git_table(g)


def _brief_line(job: dict) -> list[str]:
    """보낼(직접 할) 일 파일의 brief(지시서 경로)를 기록 줄로. 모양이 틀리면 아무것도 쓰기 전에 막는다."""
    if "brief" not in job:
        return []
    bad = fb.brief_error(job["brief"])
    if bad:
        raise SystemExit(bad)
    return [f"brief = {_v(job['brief'])}"]


def direct(job_path: Path, path: Path = dp.DIRECT_TOML) -> str:
    job = tomllib.loads(job_path.read_text(encoding="utf-8"))
    for k in ("project", "task"):
        if k not in job:
            raise SystemExit(f"직접 할 일 파일에 {k}가 없음")
    entries = dp.load_direct(path)
    nums = [int(e["id"][1:]) for e in entries if re.fullmatch(r"m\d+", e["id"])]
    rid = job.get("id") or f"m{max(nums, default=0) + 1:03d}"
    date = job.get("date") or dt.datetime.now(dt.timezone.utc).date()
    ftab = _feedback_table(job, rid, date)
    situation, predicted = job.get("situation", {}), job.get("predicted", {})
    ptab = {k: predicted[k] for k in dp.DIRECT_PREDICT_KEYS + ("ctx_start_k",) if k in predicted}
    if ptab:
        ptab = {"written_before": True, **ptab}
    bad = dp.direct_predicted_errors({"id": rid, "date": str(date), "predicted": ptab or None})
    if bad:
        raise SystemExit("\n".join(bad))
    size, main_k = _size_and_main(job, situation, job["project"], predicted)
    c = de.costs(size[0], size[1], main_k, de.params(), job.get("decide", {}).get("left"))
    why = job.get("decide", {}).get("why")
    if not why:
        if c["cheaper"] != "직접":
            raise SystemExit(f"비용으로는 보내는 게 싸다(직접 {c['direct_m']:.1f}M · 보냄 {c['send_m']:.1f}M) — 그래도 직접 하면 [decide] why에 "
                             f"다른 까닭(대화 맥락 등)을 적고, 아니면 보낸다(`record send`)")
        why = ["비용"]
    lines = ["", "[[direct]]", f'id = "{rid}"', f"project = {_v(job['project'])}", f"date = {_v(date)}", f"task = {_v(job['task'])}"]
    lines += _brief_line(job)
    if situation:
        lines.append("[direct.situation]")
        lines += [f"{k} = {_v(v)}" for k, v in situation.items()]
    lines += de.decide_block(c, "direct", why, "직접").rstrip("\n").split("\n")
    if ptab:  # 손 예측(2026-11-06 사용자 결정 — 직접 하는 작업도 예측해 둔다)
        lines += ["[direct.predicted]"] + [f"{k} = {_v(v)}" for k, v in ptab.items()]
    if ftab is not None:
        lines += ["[direct.feedback]"] + [f"{k} = {_v(v)}" for k, v in ftab.items()]
    lines += ["[direct.actual]", 'status = "unknown"  # record finish가 메인 대화 기록으로 채운다']
    base = path.read_text(encoding="utf-8").rstrip("\n") if path.is_file() else ""
    path.write_text(base + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join([f"직접 한 일 {rid}를 덧붙였다 ({path.name}).", de.explain(c)] + (feedback_lines(ftab, task=job["task"]) if ftab is not None else []))


def _block(text: str, header: str, rid: str) -> tuple[int, int]:
    """id가 rid인 [[header]] 묶음의 (시작, 끝) 글자 위치."""
    starts = [m.start() for m in re.finditer(rf"^\[\[{header}\]\]$", text, flags=re.M)] + [len(text)]
    for a, b in zip(starts, starts[1:]):
        if re.search(rf'^id = "{re.escape(rid)}"$', text[a:b], flags=re.M):
            return a, b
    raise SystemExit(f"{rid} 기록을 못 찾음")


def _replace_table(block: str, table: str, new_lines: list[str]) -> str:
    """묶음 안의 [table] 표를 새 줄로 바꾼다(없으면 끝에 붙인다)."""
    m = re.search(rf"^\[{re.escape(table)}\]$.*?(?=^\[|\Z)", block, flags=re.M | re.S)
    new = "\n".join([f"[{table}]"] + new_lines) + "\n"
    return block[:m.start()] + new + block[m.end():] if m else block.rstrip("\n") + "\n" + new


def feedback_value(text: str):
    """--feedback 값 → review.feedback: 'F102, F103'이면 번호 목록, 아니면 글 그대로('없음: 이유')."""
    parts = [x.strip() for x in text.split(",")]
    return parts if all(re.fullmatch(r"F\d+", x) for x in parts) else text.strip()


def _put_review(block: str, header: str, key: str, value) -> str:
    """묶음의 [header.review] 표에 key = value를 넣는다(있으면 바꾼다, 표가 없으면 끝에 만든다)."""
    rev = re.search(rf"^\[{header}\.review\]$.*?(?=^\[|\Z)", block, flags=re.M | re.S)
    line = f"{key} = {_v(value)}\n"
    if not rev:
        return block.rstrip("\n") + f"\n[{header}.review]\n" + line
    body = rev.group(0)
    if re.search(rf"^{key} = ", body, flags=re.M):
        body = re.sub(rf"^{key} = .*\n?", line, body, count=1, flags=re.M)
    else:
        body = body.replace(f"[{header}.review]\n", f"[{header}.review]\n" + line, 1)
    return block[:rev.start()] + body + block[rev.end():]


def _check_missed(rid: str, missed, path: Path, is_direct: bool) -> None:
    """--missed 값을 기록에 쓰기 전에 본다: 번호가 백서에 있고, 그 기록의 feedback.hit와 겹치지 않는다(2026-11-06 사용자 결정)."""
    d = next((r for r in (dp.load_direct(path) if is_direct else dp.load(path)) if r["id"] == rid), None)
    if d is None:
        raise SystemExit(f"{rid} 기록을 못 찾음")
    review = {**d.get("review", {}), "missed": missed}
    bad = [e for e in dp.feedback_review_errors({**d, "review": review}) if "review.missed" in e]
    if bad:
        raise SystemExit("\n".join(bad))


def finish(rid: str, log: Path, after: str | None = None, until: str | None = None, report: str | None = None,
           path: Path | None = None, repo: Path | None = None, feedback: str | None = None, missed: str | None = None) -> str:
    is_direct = bool(re.fullmatch(r"m\d+", rid))
    path = path or (dp.DIRECT_TOML if is_direct else dp.HERE / "dispatches.toml")
    header = "direct" if is_direct else "dispatch"
    if missed:  # 아무것도 쓰기 전에 (hit와 겹치면 막는다)
        _check_missed(rid, feedback_value(missed), path, is_direct)
    s = au.summarize(str(log), after, until)
    if not s["start_iso"]:
        raise SystemExit("대화 기록에서 줄을 못 찾음 (--after·--until을 확인)")
    act = ['status = "done"', f"minutes = {s['duration_min']}  # record finish ({'메인 대화 기록' if is_direct else '알림의 실행 시간이 있으면 그것으로 고친다'})",
           f"turns = {s['turns']}", f"tokens_m = {au.total(s) / 1e6:.2f}  # 캐시 생성 + 캐시 읽기 + 입력 + 출력(추정)",
           f'start = "{s["start_iso"]}"', f'end = "{s["end_iso"]}"']
    if is_direct:
        grew = de.context_growth_k(log, after, until)
        if grew is not None:
            act.append(f"added_k = {round(grew)}  # 메인 맥락이 실제로 늘어난 양(천 토큰) — 그 뒤 모든 응답에서 다시 읽힌다")
    text = path.read_text(encoding="utf-8")
    a, b = _block(text, header, rid)
    git = None
    if not is_direct:  # git 비교는 기록 파일에 아무것도 쓰기 전에 (2026-11-05)
        git = _git_finish(next(r for r in dp.load(path) if r["id"] == rid), text, a, b, path, log, after, until, repo)
    block = _replace_table(text[a:b], f"{header}.actual", act)
    if git is not None:
        block = _put_git(block, git)
    if report and not is_direct:
        rev = re.search(r"^\[dispatch\.review\]$.*?(?=^\[|\Z)", block, flags=re.M | re.S)
        if rev and not re.search(r"^report = ", rev.group(0), flags=re.M):
            block = block[:rev.start()] + rev.group(0).replace("[dispatch.review]\n", f"[dispatch.review]\nreport = {_v(report)}\n", 1) + block[rev.end():]
        elif not rev:
            block = block.rstrip("\n") + f"\n[dispatch.review]\nreport = {_v(report)}\n"
    if feedback:  # 이번 일에서 올린 피드백 (2026-11-05 사용자 결정, feedback/CLAUDE.md "강제")
        block = _put_review(block, header, "feedback", feedback_value(feedback))
    if missed:  # 놓친 피드백 — 보낼 때 이미 있었는데 hit에 없던, 알고 보니 걸린 항목 (2026-11-06 사용자 결정)
        block = _put_review(block, header, "missed", feedback_value(missed))
    if not is_direct and not re.search(r"^\[dispatch\.turns\]", block, flags=re.M):
        block = block.rstrip("\n") + "\n" + au.turn_toml(au.turn_rows(str(log), after)) + "\n"
    if not re.search(rf"^\[{header}\.log\]", block, flags=re.M):  # 로그 숫자(2026-11-05) — 실측과 같은 창, 턴 표 뒤
        body = block.rstrip("\n")
        block = body + "\n" + au.log_toml(au.log_numbers(str(log), after, until), header) + (block[len(body):] or "\n")
    path.write_text(text[:a] + block + text[b:], encoding="utf-8")
    d = next(r for r in (dp.load_direct(path) if is_direct else dp.load(path)) if r["id"] == rid)
    out = [f"{rid} 실측: {s['duration_min']}분 · {s['turns']}줄 · {au.total(s) / 1e6:.2f}M ({path.name}에 채움)"]
    if git is not None:
        out.append("  git: " + (f"건너뜀 — {git['skip']}" if "skip" in git else
                                 f"새 {git['git_write']} · 고침 {git['git_edit']} · 지움 {git['git_delete']} 파일, +{git['git_lines_added']}/−{git['git_lines_removed']}줄, "
                                 f"커밋 {git['git_commits']} · 지시서에 적힌 파일 {git['named_files']}개 {git['named_lines']}줄"))
    if is_direct and d.get("predicted"):  # 직접 한 일: 손 예측 범위와 실측 (2026-11-06)
        p, got = d["predicted"], {"minutes": s["duration_min"], "turns": s["turns"], "tokens_m": round(au.total(s) / 1e6, 2)}
        marks = []
        for k, name in (("minutes", "분"), ("turns", "줄"), ("tokens_m", "M")):
            lo, hi = p.get(k, [None, None])
            if lo is not None:
                where = "안" if lo <= got[k] <= hi else ("아래" if got[k] < lo else "위")
                marks.append(f"{name} {got[k]} (예측 {lo:g}–{hi:g}, {where})")
        out.append("  손 예측 vs 실측: " + " · ".join(marks))
    if not is_direct:
        told, zone = d.get("predicted", {}).get("told"), dp.zone(s["duration_min"])
        out.append(f"  말한 구간 '{told}' → 실제 '{zone}'" + ("" if told == zone else " — 빗나감: review.wrong·why를 적는다"))
    dec = d.get("decide", {})
    if dec:
        p = de.params()
        lines = dec["left"] * p["lines_per_response"]
        if is_direct:
            grew = de.context_growth_k(log, after, until) or dec.get("added_k", 0)
            mine = au.total(s) / 1e6 + grew * lines / 1000
        else:
            mine = au.total(s) / 1e6 + (p["send_overhead_lines"] * dec["main_ctx_k"] + p["report_k"] * lines) / 1000
        other = dec["direct_m"] if not is_direct else dec["send_m"]
        out.append(f"  보낼까 판단: 고른 쪽 실제 {mine:.1f}M({'늘어난 맥락 × 남은 줄' if is_direct else '메인 몫'}은 추정) vs 다른 쪽 추정 {other:.1f}M → "
                   f"{'고른 쪽이 쌌다' if mine <= other else '다른 쪽이 쌌을 수 있다'}")
    left = "review.reason(빗나가면 wrong·why), 배치 줄의 표 한 줄과 교훈, 검사·커밋"
    if "feedback" not in d.get("review", {}) and str(d.get("date", "")) >= dp.FEEDBACK_REQUIRED_FROM:
        left = ("review.feedback(이번 일에서 백서에 올린 피드백 번호 목록 또는 \"없음: 이유\" — `--feedback`으로 다시 주거나 손으로), "
                + left)
    if "missed" not in d.get("review", {}) and dp.on_or_after(d, dp.FEEDBACK_ALL_FROM):
        left = ("review.missed(보낼 때 이미 있었는데 hit에 없던, 알고 보니 걸린 피드백 번호 또는 \"없음: 이유\" — `--missed`로 다시 주거나 손으로), "
                + left)
    out.append("남은 일: " + left)
    return "\n".join(out)


def _load_numbers(src: Path, until: str | None) -> dict:
    """숫자 JSON, 또는 list_events 출력({"ccr": {"data": [...]}} — 앞뒤에 다른 글이 붙어 있어도 된다)이면 여기서 합한다."""
    text = src.read_text(encoding="utf-8")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        i = text.find('{"ccr"')
        if i < 0:
            raise SystemExit(f"{src}: JSON을 못 읽음")
        raw, _ = json.JSONDecoder().raw_decode(text[i:])
    if isinstance(raw, dict) and ("ccr" in raw or "data" in raw):
        return ms.cloud_from_events(raw, until)
    return raw


def cloud(rid: str, src: Path, path: Path | None = None, until: str | None = None) -> str:
    """클라우드 세션의 result 사건 숫자를 [dispatch.cloud]로 (2026-11-05). 결과 글은 받지도 적지도 않는다."""
    path = path or dp.HERE / "dispatches.toml"
    n = _load_numbers(src, until)
    errors = ms.cloud_errors(n) if isinstance(n, dict) else ["숫자 JSON은 표여야 함"]
    if errors:
        raise SystemExit("숫자 JSON 문제:\n  - " + "\n  - ".join(errors))
    d = next((r for r in dp.load(path) if r["id"] == rid), None)
    if d is None:
        raise SystemExit(f"{rid} 기록을 못 찾음")
    if d.get("situation", {}).get("S_cloud_session") != "예":
        raise SystemExit(f"{rid}는 클라우드 세션 일(S_cloud_session = 예)이 아님 — 로컬 일은 record finish가 [dispatch.git]·[dispatch.log]를 붙인다")
    if "cloud" in d:
        raise SystemExit(f"{rid}에 [dispatch.cloud]가 이미 있음 (숫자는 고치지 않는다)")
    if n.get("session") and d.get("session") and n["session"] != d["session"]:
        raise SystemExit(f"{rid}의 session {d['session']}과 JSON의 session이 다름")
    text = path.read_text(encoding="utf-8")
    a, b = _block(text, "dispatch", rid)
    block = text[a:b]
    if n.get("session") and not d.get("session"):
        i = re.search(r"^\[dispatch\.", block, flags=re.M).start()
        block = block[:i] + f"session = {_v(n['session'])}\n" + block[i:]
    body = block.rstrip("\n")
    table = "\n".join(["[dispatch.cloud]  # record cloud — 클라우드 세션 result 사건의 숫자 합 (숫자만, 실측)"] + ms.cloud_lines(n))
    block = body + "\n" + table + (block[len(body):] or "\n")
    path.write_text(text[:a] + block + text[b:], encoding="utf-8")
    m = sum(u["outputTokens"] for u in n["models"].values())
    return (f"{rid} 클라우드 숫자: 사건 {n['results']} · {n['duration_ms'] / 60000:.1f}분 · 턴 {n['num_turns']} · 출력 {m:,} 토큰 · "
            f"${n['total_cost_usd']:.2f} ({path.name}에 채움)")


def _arg(argv: list[str], name: str) -> str | None:
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "send":
        print(send(Path(argv[1])))
    elif cmd == "direct":
        print(direct(Path(argv[1])))
    elif cmd == "finish" and len(argv) >= 3:
        repo = _arg(argv, "--repo")
        print(finish(argv[1], Path(argv[2]), _arg(argv, "--after"), _arg(argv, "--until"), _arg(argv, "--report"),
                     repo=Path(repo) if repo else None, feedback=_arg(argv, "--feedback"), missed=_arg(argv, "--missed")))
    elif cmd == "cloud" and len(argv) >= 3:
        print(cloud(argv[1], Path(argv[2]), until=_arg(argv, "--until")))
    else:
        print(__doc__)
        return 2
    errors = dp.validate(dp.load(), pr.load_kn()) + dp.validate_direct(dp.load_direct())
    if errors:
        print("기록 검사 문제:\n  - " + "\n  - ".join(errors[:10]))
        return 1
    print("기록 검사: 문제 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
