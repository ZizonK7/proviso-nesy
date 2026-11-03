"""묶음 명령 — 보낼 때와 끝났을 때의 기록 절차를 한 번에 (2026-11-03 사용자 결정, CLAUDE.md '보낼까 판단').

사용법 (저장소 루트):
  python -m domains.agent_usage.record send <보낼 일 파일>
      기록을 덧붙인다: 상황 값·손 예측(파일) + 계산기 답(그 기록의 상황 값으로) + 보낼까 판단(decide) + 배치 머리(AGENT-LOG에 없으면).
      그리고 빗댄 기록 규칙(정해진 일이면)과 사용자에게 할 말을 보여 준다. 기록 id는 다음 빈 번호(파일에 id가 있으면 그것).
  python -m domains.agent_usage.record finish <기록 id> <작업자 대화 기록> [--after 시각] [--report 경로]
      실측(분·줄·토큰·시작·끝)과 턴 길이 표를 그 기록에 채운다. 이어 보낸 회차는 --after(`agent_usage.py --rounds`로 본 그 회차 시작).
  python -m domains.agent_usage.record direct <직접 할 일 파일>
      직접 하기로 한 일을 direct.toml에 덧붙인다(보낼까 판단과 함께).
  python -m domains.agent_usage.record finish <m001> <메인 대화 기록> --after 시작 --until 끝
      직접 한 일의 실측(메인이 그 요청에 쓴 분·줄·토큰)을 채운다.
돌아보기(review.reason, 빗나가면 wrong·why)와 배치 줄의 표·교훈은 판단이 필요해 메인이 손으로 쓴다.

보낼 일 파일(TOML): project, batch, task, agent, round, (date, id, size), [situation], [predicted](minutes, turns, tokens_m,
rules, analog, reason; told은 비우면 가운데 값의 구간), (선택) [decide](why, left, main_ctx_k).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
import tomllib
from pathlib import Path

from scripts import agent_usage as au

from . import analog as an
from . import decide as de
from . import dispatches as dp
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


def send(job_path: Path, path: Path = dp.HERE / "dispatches.toml", log_path: Path = dp.AGENT_LOG) -> str:
    job = tomllib.loads(job_path.read_text(encoding="utf-8"))
    records = dp.load(path)
    for k in ("project", "batch", "task", "agent", "round", "situation", "predicted"):
        if k not in job:
            raise SystemExit(f"보낼 일 파일에 {k}가 없음")
    rid = job.get("id") or next_id(records)
    if any(d["id"] == rid for d in records):
        raise SystemExit(f"기록 id {rid}가 이미 있음")
    date = job.get("date") or dt.datetime.now(dt.timezone.utc).date()
    situation, predicted, project = job["situation"], dict(job["predicted"]), job["project"]
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
             f"task = {_v(job['task'])}", f"agent = {_v(job['agent'])}", f"round = {job['round']}"]
    if job.get("size"):
        lines.append(f"size = {_v(job['size'])}")
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
    lines += ["[dispatch.actual]", 'status = "unknown"  # 예측만 기록됨 (record finish가 채운다)']
    text = path.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    if job["batch"] not in dp.logged_batches(log_path) and project != "batman":
        log = log_path.read_text(encoding="utf-8").rstrip("\n")
        log += (f"\n\n## 배치 {job['batch']} · {date} · {job['task'][:40]}\n"
                f"- (보낸 뒤 결과가 나오면 표 한 줄 — 모델·effort·품질 1–5·메모 — 과 교훈을 적는다)\n")
        log_path.write_text(log, encoding="utf-8")
    out = [f"기록 {rid}를 덧붙였다 ({path.name}). 사용자에게: 말할 구간 '{told}'({dp.ZONE_SAY.get(told, '')}), "
           f"분 {predicted.get('minutes')}, 토큰 {predicted.get('tokens_m')}M — 이유: {predicted.get('reason', '')[:80]}",
           f"계산기: {pred.told() or '모름'}" + (f" {calc_m[0][0]:.1f}–{calc_m[0][1]:.1f}분" if calc_m else ""),
           de.explain(c)]
    if situation.get("S_specified") == "예":
        d = next(r for r in dp.load(path) if r["id"] == rid)
        out.append("빗댄 기록 규칙(시험 중, 참고): " + an.show(d, dp.load(path), an.load_rule()))
    return "\n".join(out)


def direct(job_path: Path, path: Path = dp.DIRECT_TOML) -> str:
    job = tomllib.loads(job_path.read_text(encoding="utf-8"))
    for k in ("project", "task"):
        if k not in job:
            raise SystemExit(f"직접 할 일 파일에 {k}가 없음")
    entries = dp.load_direct(path)
    nums = [int(e["id"][1:]) for e in entries if re.fullmatch(r"m\d+", e["id"])]
    rid = job.get("id") or f"m{max(nums, default=0) + 1:03d}"
    date = job.get("date") or dt.datetime.now(dt.timezone.utc).date()
    situation, predicted = job.get("situation", {}), job.get("predicted", {})
    size, main_k = _size_and_main(job, situation, job["project"], predicted)
    c = de.costs(size[0], size[1], main_k, de.params(), job.get("decide", {}).get("left"))
    why = job.get("decide", {}).get("why")
    if not why:
        if c["cheaper"] != "직접":
            raise SystemExit(f"비용으로는 보내는 게 싸다(직접 {c['direct_m']:.1f}M · 보냄 {c['send_m']:.1f}M) — 그래도 직접 하면 [decide] why에 "
                             f"다른 까닭(대화 맥락 등)을 적고, 아니면 보낸다(`record send`)")
        why = ["비용"]
    lines = ["", "[[direct]]", f'id = "{rid}"', f"project = {_v(job['project'])}", f"date = {_v(date)}", f"task = {_v(job['task'])}"]
    if situation:
        lines.append("[direct.situation]")
        lines += [f"{k} = {_v(v)}" for k, v in situation.items()]
    lines += de.decide_block(c, "direct", why, "직접").rstrip("\n").split("\n")
    lines += ["[direct.actual]", 'status = "unknown"  # record finish가 메인 대화 기록으로 채운다']
    base = path.read_text(encoding="utf-8").rstrip("\n") if path.is_file() else ""
    path.write_text(base + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return f"직접 한 일 {rid}를 덧붙였다 ({path.name}).\n" + de.explain(c)


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


def finish(rid: str, log: Path, after: str | None = None, until: str | None = None, report: str | None = None,
           path: Path | None = None) -> str:
    is_direct = bool(re.fullmatch(r"m\d+", rid))
    path = path or (dp.DIRECT_TOML if is_direct else dp.HERE / "dispatches.toml")
    header = "direct" if is_direct else "dispatch"
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
    block = _replace_table(text[a:b], f"{header}.actual", act)
    if report and not is_direct:
        rev = re.search(r"^\[dispatch\.review\]$.*?(?=^\[|\Z)", block, flags=re.M | re.S)
        if rev and not re.search(r"^report = ", rev.group(0), flags=re.M):
            block = block[:rev.start()] + rev.group(0).replace("[dispatch.review]\n", f"[dispatch.review]\nreport = {_v(report)}\n", 1) + block[rev.end():]
        elif not rev:
            block = block.rstrip("\n") + f"\n[dispatch.review]\nreport = {_v(report)}\n"
    if not is_direct and not re.search(r"^\[dispatch\.turns\]", block, flags=re.M):
        block = block.rstrip("\n") + "\n" + au.turn_toml(au.turn_rows(str(log), after)) + "\n"
    path.write_text(text[:a] + block + text[b:], encoding="utf-8")
    d = next(r for r in (dp.load_direct(path) if is_direct else dp.load(path)) if r["id"] == rid)
    out = [f"{rid} 실측: {s['duration_min']}분 · {s['turns']}줄 · {au.total(s) / 1e6:.2f}M ({path.name}에 채움)"]
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
    out.append("남은 일: review.reason(빗나가면 wrong·why), 배치 줄의 표 한 줄과 교훈, 검사·커밋")
    return "\n".join(out)


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
        print(finish(argv[1], Path(argv[2]), _arg(argv, "--after"), _arg(argv, "--until"), _arg(argv, "--report")))
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
