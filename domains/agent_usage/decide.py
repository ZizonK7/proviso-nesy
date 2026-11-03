"""보낼까 판단 — 하위 에이전트에 맡길지 메인이 직접 할지를 계산으로 (2026-11-03 사용자 결정, CLAUDE.md '보낼까 판단').

사용법 (저장소 루트):
  python -m domains.agent_usage.decide <상황 파일 | 기록 id> [--main <메인 대화 기록>] [--main-ctx 천토큰] [--left 응답수]
                                       [--turns 줄수 --tokens 백만]   (계산기가 '모름'일 때 손 예측 숫자)

AI는 혼자 판단하면 안 보내는 쪽으로 기운다 — 보내는 비용(지시서·기록)은 바로 보이고, 직접 했을 때의 비용(메인 맥락이 커져
그 뒤 모든 응답에서 다시 읽힘)은 나중에 조금씩 나가 안 보인다. 그래서 둘을 같은 단위(토큰, 기록 단위)로 놓는다.
  직접 = T × (M + A/2) + A × L          보냄 = S + K × M + R × L
  T 일의 줄 수(계산기), S 작업자 토큰(계산기), M 지금 메인 맥락, A 직접 하면 메인 맥락이 늘어날 양 = 2 × (S/T − base),
  L 남은 대화 줄 수(= 남은 응답 × 2), K 보내고 기록하는 메인 줄 수, R 보내면 메인에 남는 보고 크기 (숫자는 decide.toml)
토큰 말고 고를 까닭(새 눈이 필요한 검토·점검, 대화를 이어 가야 함, 대화에서 쌓인 판단이 많이 필요함)은 decide 칸의 why에 적는다.
"""
from __future__ import annotations

import json
import math
import sys
import tomllib
from pathlib import Path

from . import dispatches as dp
from . import predict as pr

HERE = Path(__file__).resolve().parent
DECIDE_TOML = HERE / "decide.toml"


def params(path: Path = DECIDE_TOML) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def latest_main_log(root: Path | None = None) -> Path | None:
    """가장 최근에 쓰인 메인 대화 기록(하위 에이전트 기록이 아닌 세션 파일). 지금 세션이 쓰고 있는 파일이 가장 새것이다."""
    root = root or Path.home() / ".claude" / "projects"
    logs = [p for p in root.glob("*/*.jsonl") if p.is_file()]
    return max(logs, key=lambda p: p.stat().st_mtime) if logs else None


def main_context_k(log: Path) -> float | None:
    """메인 대화 기록의 마지막 응답이 읽은 맥락(천 토큰) = 캐시 읽기 + 캐시 생성 + 입력."""
    last = None
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if isinstance(d, dict) and d.get("type") == "assistant" and isinstance(d.get("message"), dict):
                u = d["message"].get("usage") or {}
                total = sum((u.get(k) or 0) for k in ("cache_read_input_tokens", "cache_creation_input_tokens", "input_tokens"))
                if total:
                    last = total
    return last / 1000 if last else None


def context_growth_k(log: Path, after: str | None, until: str | None) -> float | None:
    """메인이 직접 한 일에서 메인 맥락이 실제로 늘어난 양(천 토큰) = 그 구간 마지막 응답의 맥락 − 첫 응답의 맥락."""
    from scripts import agent_usage as au
    ctx, cut = [], None
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = au.parse_ts(d.get("timestamp", "")) if isinstance(d, dict) and d.get("timestamp") else None
            if not ts:
                continue
            if cut is None:
                cut = (au._after_ts(after, ts) if after else None, au._after_ts(until, ts) if until else None)
            if (cut[0] and ts < cut[0]) or (cut[1] and ts > cut[1]):
                continue
            if d.get("type") == "assistant" and isinstance(d.get("message"), dict):
                u = d["message"].get("usage") or {}
                total = sum((u.get(k) or 0) for k in ("cache_read_input_tokens", "cache_creation_input_tokens", "input_tokens"))
                if total:
                    ctx.append(total)
    return (ctx[-1] - ctx[0]) / 1000 if len(ctx) > 1 else None


def costs(turns: float, tokens_m: float, main_k: float, p: dict, left: float | None = None) -> dict:
    """두 비용(백만 토큰, 기록 단위)과 그 바탕 숫자."""
    left = p["left_responses"] if left is None else left
    lines = left * p["lines_per_response"]
    avg_k = tokens_m * 1000 / turns if turns else 0
    added_k = max(0.0, 2 * (avg_k - p["base_k"]))
    direct = (turns * (main_k + added_k / 2) + added_k * lines) / 1000
    send = tokens_m + (p["send_overhead_lines"] * main_k + p["report_k"] * lines) / 1000
    return {"turns": turns, "tokens_m": tokens_m, "main_ctx_k": main_k, "left": left, "added_k": added_k,
            "direct_m": direct, "send_m": send, "cheaper": "보냄" if send < direct else "직접"}


def from_calculator(situation: dict, project: str) -> tuple[float, float] | None:
    """계산기의 (줄 수, 토큰 백만) 가운데 값. 계산기가 '모름'이면 None."""
    kn = pr.load_kn()
    pred = pr.predict(situation, project, pr.live_pieces(kn), kn)
    t, k = pred.turns(), pred.tokens()
    if not (t and k):
        return None
    return math.sqrt(t[0] * t[1]), math.sqrt(k[0] * k[1])


def decide_block(c: dict, table: str, why: list[str] | None = None, chose: str | None = None) -> str:
    """기록에 붙일 [<table>.decide] 줄."""
    chose = chose or c["cheaper"]
    why = why or (["비용"] if chose == c["cheaper"] else [])
    return (f"[{table}.decide]\n"
            f"main_ctx_k = {round(c['main_ctx_k'])}\nleft = {round(c['left'])}\n"
            f"direct_m = {round(c['direct_m'], 1)}\nsend_m = {round(c['send_m'], 1)}\n"
            f"added_k = {round(c['added_k'])}\n"
            f'chose = "{chose}"\nwhy = [{", ".join(json.dumps(w, ensure_ascii=False) for w in why)}]\n')


def explain(c: dict) -> str:
    return (f"보낼까 판단 (토큰은 기록 단위, 백만):\n"
            f"  일의 크기: {c['turns']:.0f}줄, 작업자 토큰 {c['tokens_m']:.1f}M → 직접 하면 메인 맥락이 {c['added_k']:.0f}천 늘어남\n"
            f"  지금 메인 맥락 {c['main_ctx_k']:.0f}천, 남은 응답 어림 {c['left']:.0f}\n"
            f"  직접 = {c['direct_m']:.1f}M · 보냄 = {c['send_m']:.1f}M → 토큰으로는 '{c['cheaper']}'\n"
            f"  토큰 말고: 새 눈이 필요한 검토·점검이면 보냄, 대화를 이어 가야 하면 보냄(뒤에서 돌게), 대화에서 쌓인 판단이 많이 필요하면 직접.")


def _arg(argv: list[str], name: str) -> str | None:
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    target, p = argv[0], params()
    if Path(target).is_file():
        raw = tomllib.loads(Path(target).read_text(encoding="utf-8"))
        situation, project = raw.get("situation", {}), raw.get("project", "")
    else:
        found = [d for d in dp.load() if d["id"] == target]
        if not found:
            print(f"기록 id도 상황 파일도 아님: {target}")
            return 2
        situation, project = found[0].get("situation", {}), found[0].get("project", "")
    size = (float(_arg(argv, "--turns")), float(_arg(argv, "--tokens"))) if _arg(argv, "--turns") and _arg(argv, "--tokens") \
        else from_calculator(situation, project)
    if not size:
        print("계산기가 '모름' — 손 예측 숫자를 --turns <줄 수> --tokens <백만>으로 준다")
        return 2
    main_k = float(_arg(argv, "--main-ctx")) if _arg(argv, "--main-ctx") else None
    if main_k is None:
        log = Path(_arg(argv, "--main")) if _arg(argv, "--main") else latest_main_log()
        main_k = main_context_k(log) if log and log.is_file() else None
    if main_k is None:
        print("메인 맥락을 못 읽음 — --main <메인 대화 기록> 또는 --main-ctx <천 토큰>")
        return 2
    left = float(_arg(argv, "--left")) if _arg(argv, "--left") else None
    c = costs(size[0], size[1], main_k, p, left)
    print(explain(c))
    print()
    print(decide_block(c, "dispatch" if c["cheaper"] == "보냄" else "direct"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
