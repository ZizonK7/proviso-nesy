"""하위 에이전트 작업 기록(dispatches.toml)을 읽고, 예측이 맞았는지 계산한다.

사용법 (저장소 루트):
  python -m domains.agent_usage.dispatches     기록 검사 + 예측·실측 비교표 (시간은 세 마디 구간)

기록은 보낸 순서대로 이어 쓴다. 가설 검사(checks.py)는 이 순서로 '가설을 세운 뒤의 기록'을 고른다.
"""
from __future__ import annotations

import math
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

import feedback as fb
from proviso import schema
from scripts.agent_usage import LOG_KEYS

from . import measure as ms

HERE = Path(__file__).resolve().parent

# 시간 구간 세 마디 (사용자 결정 2026-10-19): 사용자가 할 일로 말한다.
#   잠깐 ≤ 10분 "잠깐 기다려" · 다른 일 10–40분 "다른 거 하고 있어" · 신경 끄기 > 40분 "신경 쓰지 말고 있어"
ZONES = ("잠깐", "다른 일", "신경 끄기")
ZONE_EDGES = (10, 40)
ZONE_SAY = {"잠깐": "잠깐 기다려", "다른 일": "다른 거 하고 있어", "신경 끄기": "신경 쓰지 말고 있어"}
OLD_TIME_CLASSES = ("S", "M", "L", "XL")  # 2026-10-19 전의 시간 등급. 옛 기록의 time_class 칸에만 남는다
TOKEN_CLASSES = ("T1", "T2", "T3", "T4")
SITUATION_VALUES = ("예", "아니오", "일부", "모름")
STATUSES = ("done", "stopped", "unknown")
# 돌아보기의 '틀린 조각' 갈래: 조건 흐림 → 쪼갠다 / 이유 틀림 → 새 버전 / 바깥 상황 → 예외
# / 까닭 모름 → 고치지 않고 쌓아 두고 사용자에게 넘긴다 (2026-11-03 사용자 결정. 까닭: 칸이 셋뿐이면 흔들림에도 까닭을
#   지어 붙이게 된다 — p09는 '일찍 끝남' 칸이 없어 형식상 '조건 흐림'을 적었다). 까닭 모름이면 review.wrong은 비워도 된다
UNKNOWN_WHY = "까닭 모름"
WHY = ("조건 흐림", "이유 틀림", "바깥 상황", UNKNOWN_WHY)
# 이 기록 다음부터(파일 순서) 시간 구간이 빗나가면 review.wrong·review.why가 필수다 (2026-10-19 결정 뒤의 기록)
WRONG_REQUIRED_AFTER = "p03"
# 이 날짜부터 끝난 기록은 턴 길이 표([dispatch.turns])와 보고서 경로(review.report)가 필수다 (2026-11-02 사용자 결정).
# 까닭: 문서에만 적힌 단계는 빠졌다 — p65 이후 세션 안 하위 에이전트 53건 중 --turns 4건. 검사가 막는 단계(review.wrong)는 72/73.
# 번호가 아니라 날짜로 자른다: 브랜치를 합치며 번호를 다시 매겨도 지난 기록이 걸리지 않게.
FORM_REQUIRED_FROM = "2026-11-03"
# 이 날짜부터 끝난 기록은 실측의 시작·끝 시각(actual.start/end, UTC ISO)과 에이전트·회차(agent, round)가 필수다 (2026-11-03 사용자 결정).
# 까닭: 빗댄 기록 규칙이 '보낼 때 이미 끝나 있던 기록'과 '같은 에이전트의 앞 회차'를 정확히 가르려면 필요하다
# (2026-11-03 시험에서 규칙이 틀린 5건 중 3건이 시각이 없어 같은 배치의 앞 회차를 못 쓴 것).
TIMES_REQUIRED_FROM = "2026-11-04"
ISO_UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
# 일의 크기 (2026-11-03 사용자 결정, CLAUDE.md '일의 크기 모델'): 지시서에서 센 수. 기록의 size = { 이름 = 수 } (모르면 칸을 뺀다)
#   reads 읽을 것 · outputs 만들 것 · chunks 쓸 덩어리(절·단계) · edits 고칠 곳 · checks 확인 횟수 · find_cap 찾는 일의 상한(글, 예 "25 원문")
SIZE_COUNTS = ("reads", "outputs", "chunks", "edits", "checks")
SIZE_TEXT = ("find_cap",)
# 쓰는 파일 수 (2026-11-04 사용자 결정, CLAUDE.md '파일 수 비율 조각'): 기록의 files = { write = 새로 만들거나 통째로 다시 쓰는 파일 수,
#   edit = 일부만 고치는 파일 수 }. 단위는 파일 하나뿐 — 절·항목·줄은 세지 않는다(size의 chunks·edits에 섞여 실패한 까닭).
#   읽는 파일은 세지 않는다. 지시서에 이름이나 개수로 적힌 것만; 스크립트 한 번이 여러 파일을 뱉으면 쓰기가 아니라 확인(size.checks) 1;
#   "필요한 만큼"이면 칸을 뺀다(모름, 0이 아님). 메인이 실제 지시서에서 센다. FILES_REQUIRED_FROM부터 보낸 기록에 필수(batman·메인 자신 제외).
#   계산기의 비율 조각(C_turns_files_scale)이 빗댄 기록의 같은 칸과 비를 낸다.
#   after = true: 결과(실측)를 본 뒤에 채운 수 — 비율 조각의 시험에서 뺀다(holdout._scale_scores). 보내기 전·결과 전에 적은 것만 시험이다
FILES_COUNTS = ("write", "edit")
FILES_FLAGS = ("after",)
FILES_REQUIRED_FROM = "2026-11-04"
# 로그 숫자 (2026-11-05 사용자 결정: 작업자 로그에서 싸게 얻는 숫자는 다 자동으로 뽑아 쌓는다). [dispatch.log] — 칸은 scripts/agent_usage.py
#   LOG_KEYS(뜻은 log_numbers 설명과 dispatches.toml 머리 주석). 실측(결과)이지 예측 입력이 아니다 — 계산기·맞추기는 읽지 않는다.
#   `record finish`가 채운다. 이 날짜부터 끝난 기록에 필수(턴 길이 표와 같은 방식: 못 재면 skip = "이유", 이어 보낸 회차는 skip 못 함)
LOG_REQUIRED_FROM = "2026-11-06"
# git 숫자와 클라우드 숫자 (2026-11-05 사용자 결정: 싸게 얻는 숫자는 다 자동으로, measure.py). 이 날짜부터 끝난 기록에 필수 —
#   로컬 일은 [dispatch.git](record send가 기준을 찍고 record finish가 견준다; 저장소 밖 일이면 skip = "저장소 밖 일"),
#   클라우드 세션 일(S_cloud_session = 예)은 [dispatch.cloud](record cloud, 못 재면 skip). 클라우드 일은 보낼 때 session(세션 id)도 필수
GIT_REQUIRED_FROM = "2026-11-06"
CLOUD_REQUIRED_FROM = "2026-11-06"
# 피드백 읽기·쓰기 (2026-11-05 사용자 결정: 이 저장소의 목적이 "이전 실수들을 통해 발전한다"로 바뀜, feedback/CLAUDE.md "강제").
#   보낸 기록에 [dispatch.feedback] read = [읽은 메인 피드백 파일 이름] — common과 `python -m feedback topics <task>`가 고른 파일이 다 들어 있어야 한다.
#   끝난 기록에 review.feedback = 이번 일에서 올린 피드백 번호 목록(["F102"], 백서에 있어야 함) 또는 "없음: 이유".
#   까닭: 문서에만 적힌 단계는 빠졌다(F051, 4/53 vs 72/73). 이 날짜부터 필수(batman 기록 제외), 직접 한 일(direct.toml)도 같은 두 칸
FEEDBACK_REQUIRED_FROM = "2026-11-06"
FEEDBACK_NONE = "없음: "
FEEDBACK_NONE_MIN = 5  # '없음: ' 뒤 이유의 최소 글자 수
ROOT = HERE.parent.parent
# 다른 저장소의 보고서는 "저장소:경로"로 적는다 (예: "movie_game:docs/worklog/2026-11-03-x.md")
OTHER_REPO = re.compile(r"^[\w.-]+:(?!/)")


def zone(minutes: float) -> str:
    """실제 분의 구간. 잠깐 ≤ 10 · 다른 일 10–40 · 신경 끄기 > 40"""
    for name, upper in zip(ZONES, ZONE_EDGES):
        if minutes <= upper:
            return name
    return ZONES[-1]


def say_zone(bounds: list[float]) -> str | None:
    """사용자에게 말할 구간 (R_say_numbers_v3, 2026-11-03 사용자 결정): 예측 분 범위의 가운데 값(√(하한×상한))이 든 구간.
    6–15분 → 가운데 9.5분 → 잠깐. 하나만 있는 열린 범위('이상')는 가운데가 없어 예전처럼 덮는 구간 중 긴 쪽.
    2026-11-03 전에는 걸치면 긴 쪽이었다(R_say_numbers_v2) — 지난 기록의 predicted.told는 그때 말한 그대로 둔다."""
    zs = zones_of(bounds)
    if not zs:
        return None
    if len(bounds) < 2:
        return zs[-1]
    return zone(math.sqrt(max(bounds[0], 0) * bounds[1]))


def zones_of(bounds: list[float]) -> list[str]:
    """예측 분 범위가 덮는 구간들. 아래 끝이 경계값과 같으면 위 구간에서 시작한다([10, 20] → 다른 일만).
    하나만 있으면 '이상'이라 맨 위 구간까지 덮는다."""
    if not bounds:
        return []
    lo = bounds[0]
    hi = bounds[1] if len(bounds) > 1 else float("inf")
    first = ZONES.index(zone(hi)) if lo == hi else next(i for i, e in enumerate(ZONE_EDGES + (float("inf"),)) if lo < e)
    return list(ZONES[first: ZONES.index(zone(hi)) + 1])


def token_class(tokens_m: float) -> str:
    """T1 < 20M · T2 20–60M · T3 60–120M · T4 > 120M"""
    for name, upper in zip(TOKEN_CLASSES, (20, 60, 120)):
        if tokens_m < upper:
            return name
    return "T4"


def judge(predicted: list[str], actual: str | None, order: tuple[str, ...]) -> str:
    """예측 등급·구간(범위면 여러 개)과 실제를 비교한다."""
    if actual is None or not predicted:
        return "모름"
    if actual in predicted:
        return "맞음"
    highest = max(order.index(p) for p in predicted)
    return "낮게 잡음" if order.index(actual) > highest else "높게 잡음"


def in_range(value: float | None, bounds: list[float]) -> bool | None:
    """실측이 [하한, 상한] 안인가. 하나만 있으면 '이상'. 모르면 None."""
    if value is None or not bounds:
        return None
    return bounds[0] <= value <= (bounds[1] if len(bounds) > 1 else float("inf"))


def load(path: Path = HERE / "dispatches.toml") -> list[dict]:
    return tomllib.loads(path.read_text(encoding="utf-8")).get("dispatch", [])


def done(d: dict) -> bool:
    """끝까지 한 작업만 판정에 쓴다."""
    return d.get("actual", {}).get("status", "done") == "done"


def situation(d: dict, state_id: str) -> str:
    return d.get("situation", {}).get(state_id, "모름")


def midpoint(bounds: list[float]) -> float | None:
    """[하한, 상한]의 가운데. 하한만 있으면("이상") 하한."""
    if not bounds:
        return None
    return bounds[0] if len(bounds) == 1 else (bounds[0] + bounds[1]) / 2


def measures(d: dict) -> dict:
    """실측 숫자와 거기서 계산한 값. 없으면 None."""
    a = d.get("actual", {})
    minutes, turns, tokens = a.get("minutes"), a.get("turns"), a.get("tokens_m")
    return {
        "minutes": minutes,
        "turns": turns,
        "tokens_m": tokens,
        "tokens_per_min": tokens / minutes if tokens and minutes else None,
        "ctx_per_turn_k": tokens * 1000 / turns if tokens and turns else None,
        "turns_per_min": turns / minutes if turns and minutes else None,
    }


def zone_verdict(d: dict) -> str | None:
    """예측 분 범위의 구간과 실제 구간 비교: 맞음 / 낮게 잡음 / 높게 잡음. 분 범위가 없으면 None."""
    want = zones_of(d["predicted"].get("minutes", []))
    if not want or measures(d)["minutes"] is None:
        return None
    return judge(want, zone(measures(d)["minutes"]), ZONES)


def wrong_required(records: list[dict], d: dict) -> bool:
    """2026-10-19 결정 뒤의 끝난 기록이 시간 구간을 빗나갔나 (그러면 review.wrong·why 필수).
    사용자에게 말한 구간(told)과 실제 구간이 다르면 예측 범위 안이라도 빗나간 것으로 본다(사용자가 받는 것은 told)."""
    order = [r.get("id") for r in records]
    if WRONG_REQUIRED_AFTER not in order or d.get("id") not in order:
        return False
    after = order.index(d["id"]) > order.index(WRONG_REQUIRED_AFTER)
    if not (after and done(d)):
        return False
    told, minutes = d.get("predicted", {}).get("told"), d.get("actual", {}).get("minutes")
    if told and minutes is not None and zone(minutes) != told:
        return True
    return zone_verdict(d) not in (None, "맞음")


# 보낼까 판단 (2026-11-03 사용자 결정, decide.py): 이 날짜부터 보낸 기록에 [dispatch.decide]가 필수(batman 기록 제외).
# 직접 한 일은 direct.toml에 같은 모양의 decide 칸과 함께 적는다(기록이 없으면 검사할 대상도 없어 막지 못한다 — 문턱은 CLAUDE.md)
DECIDE_REQUIRED_FROM = "2026-11-04"
DECIDE_WHY = ("비용", "새 눈", "대화 계속", "대화 맥락", "결과를 가림")
DIRECT_TOML = HERE / "direct.toml"
AGENT_LOG = ROOT / "docs" / "AGENT-LOG.md"
BATCH_HEAD = re.compile(r"^## 배치 (\d+)(?:\s*[–-]\s*(\d+))?", re.M)


def logged_batches(path: Path = AGENT_LOG) -> set[int]:
    """docs/AGENT-LOG.md의 배치 머리('## 배치 N' 또는 '## 배치 N–M')에 적힌 배치 번호."""
    if not path.is_file():
        return set()
    out = set()
    for m in BATCH_HEAD.finditer(path.read_text(encoding="utf-8")):
        lo = int(m.group(1))
        out.update(range(lo, int(m.group(2) or lo) + 1))
    return out


def decide_errors(did: str, dec, chose: str) -> list[str]:
    """보낼까 판단 칸(decide)의 모양. 비용만 까닭으로 들었는데 비용으로는 다른 쪽이 싸면 오류 — 다른 까닭을 적거나 다른 쪽을 고른다."""
    if not isinstance(dec, dict):
        return [f"{did}: decide는 표여야 함 (decide.py 출력)"]
    errors = []
    for k in ("main_ctx_k", "left", "direct_m", "send_m") + (("added_k",) if "added_k" in dec else ()):
        if isinstance(dec.get(k), bool) or not isinstance(dec.get(k), (int, float)) or dec[k] < 0:
            errors.append(f"{did}: decide.{k}는 0 이상의 수여야 함 (`python -m domains.agent_usage.decide`)")
    if dec.get("chose") != chose:
        errors.append(f"{did}: decide.chose는 여기서 \"{chose}\"여야 함")
    why = dec.get("why")
    if not (isinstance(why, list) and why and all(w in DECIDE_WHY for w in why)):
        errors.append(f"{did}: decide.why는 {DECIDE_WHY} 중 하나 이상의 목록")
    elif why == ["비용"] and not errors:
        mine, other = (dec["send_m"], dec["direct_m"]) if chose == "보냄" else (dec["direct_m"], dec["send_m"])
        if mine > other:
            errors.append(f"{did}: 비용만 까닭으로 들었는데 비용으로는 다른 쪽이 싸다({mine} > {other}) — 다른 까닭을 적거나 다른 쪽을 고른다")
    return errors


def load_direct(path: Path = DIRECT_TOML) -> list[dict]:
    """메인이 직접 한 일(보낼까 판단에서 '직접'을 고른 일)."""
    return tomllib.loads(path.read_text(encoding="utf-8")).get("direct", []) if path.is_file() else []


def validate_direct(entries: list[dict]) -> list[str]:
    errors, seen = [], set()
    for d in entries:
        did = d.get("id", "?")
        if not re.fullmatch(r"m\d{3,}", str(did)):
            errors.append(f"{did}: 직접 한 일의 id는 m001 꼴")
        if did in seen:
            errors.append(f"{did}: id가 겹침")
        seen.add(did)
        for k in ("project", "date", "task"):
            if k not in d:
                errors.append(f"{did}: {k}가 없음")
        errors.extend(decide_errors(did, d.get("decide"), "직접"))
        act = d.get("actual", {})
        if act.get("status", "unknown") not in STATUSES:
            errors.append(f"{did}: actual.status는 {STATUSES} 중 하나")
        if act.get("status") == "done":
            for k in ("minutes", "turns", "tokens_m"):
                if not isinstance(act.get(k), (int, float)) or isinstance(act.get(k), bool):
                    errors.append(f"{did}: 끝난 일인데 actual.{k}가 없음 (메인 대화 기록 `--rounds`로 그 요청의 시각을 보고 `--actual --after --until`)")
            for k in ("start", "end"):
                if not (isinstance(act.get(k), str) and ISO_UTC.match(act[k])):
                    errors.append(f"{did}: 끝난 일인데 actual.{k}(UTC ISO)가 없음")
        errors.extend(log_errors(d, required=False))
        errors.extend(feedback_errors(d, prefix="direct"))
    return errors


# 모델·effort (2026-11-03 사용자 결정): 기록에 보낸 모델과 effort를 칸으로 적고, '기본 설정이 아닌가'(S_other_model)는 이 두 칸에서
# 계산한다(기본 설정 = Opus 5.5 high, knowledge.toml F_setup). 전에는 S_other_model 하나라 Sonnet max·Haiku·Fable xhigh·Opus xhigh가
# 한 덩어리였다. 지난 기록은 작업 설명에 적힌 것과 S_other_model = 아니오로만 채웠다(dispatches.toml 머리 주석). 이 날짜부터 필수.
MODELS = ("Opus 5.5", "Sonnet 5.5", "Haiku 5.5", "Fable 5.1", "GPT-6.1 Sol")  # 새 모델을 쓰면 여기에 더한다
EFFORTS = ("low", "medium", "high", "xhigh", "max")
DEFAULT_SETUP = ("Opus 5.5", "high")
MODEL_REQUIRED_FROM = "2026-11-04"


def other_model(model: str | None, effort: str | None) -> str | None:
    """두 칸에서 계산한 S_other_model 값('예' = 기본 설정 Opus 5.5 high가 아님). 모르면 None."""
    if model is None:
        return None
    if model != DEFAULT_SETUP[0]:
        return "예"
    if effort is None:
        return None
    return "아니오" if effort == DEFAULT_SETUP[1] else "예"


def setup(d: dict) -> tuple[str | None, str | None]:
    """기록의 (모델, effort). 칸이 없는 옛 기록은 S_other_model이 아니오면(적지 않으면 기본값 아니오) 기본 설정, 아니면 (None, None)."""
    if d.get("model"):
        return d["model"], d.get("effort")
    if d.get("situation", {}).get("S_other_model", "아니오") == "아니오":
        return DEFAULT_SETUP
    return None, None


def model_errors(d: dict) -> list[str]:
    """model·effort 칸 검사: 값, 필수(MODEL_REQUIRED_FROM부터), S_other_model과 맞는가(적지 않으면 기본값 아니오로 본다)."""
    did, errors = d.get("id", "?"), []
    model, effort = d.get("model"), d.get("effort")
    if model is not None and model not in MODELS:
        errors.append(f"{did}: model은 {MODELS} 중 하나여야 함 (새 모델이면 dispatches.py MODELS에 더한다)")
    if effort is not None and effort not in EFFORTS:
        errors.append(f"{did}: effort는 {EFFORTS} 중 하나여야 함")
    if effort is not None and model is None:
        errors.append(f"{did}: effort만 있고 model이 없음")
    if str(d.get("date", "")) >= MODEL_REQUIRED_FROM:
        main_self = d.get("situation", {}).get("S_main_self") == "예"  # 메인 자신의 일: 세션이 자기 effort를 모를 수 있다
        if model is None or (effort is None and not main_self):
            errors.append(f"{did}: model·effort(보낸 모델과 effort)가 없음 — 보낼 일 파일에 적으면 `record send`가 옮기고 "
                          f"S_other_model도 계산해 넣는다")
    want, have = other_model(model, effort), d.get("situation", {}).get("S_other_model", "아니오")
    if want is not None and have != want:
        errors.append(f"{did}: S_other_model = '{have}'인데 model·effort({model} {effort})로는 '{want}' — 이 상태는 두 칸에서 계산한다")
    return errors


def files_errors(d: dict) -> list[str]:
    """쓰는 파일 수(files) 검사: 모양, 필수(FILES_REQUIRED_FROM부터), '정해진 입력'(출력 하나) 상태와 어긋나면 막는다."""
    did, errors = d.get("id", "?"), []
    files = d.get("files")
    sit = d.get("situation", {})
    if files is None:
        if (str(d.get("date", "")) >= FILES_REQUIRED_FROM and d.get("project") != "batman"
                and sit.get("S_main_self") != "예"):
            errors.append(f"{did}: files(쓰는 파일 수: write 새로·통째로 쓰는 파일, edit 일부 고치는 파일)가 없음 — 지시서에서 세어 "
                          f"보낼 일 파일에 적으면 `record send`가 옮긴다. 지시서가 수를 안 정하면 files = {{}}")
        return errors
    if not isinstance(files, dict):
        return [f"{did}: files는 {{ write = 수, edit = 수 }} 표여야 함"]
    total = 0
    for k, v in files.items():
        if k in FILES_FLAGS:
            if v is not True:
                errors.append(f"{did}: files.{k}는 true만 (결과를 본 뒤 채웠을 때만 적고, 아니면 칸을 뺀다)")
        elif k not in FILES_COUNTS:
            errors.append(f"{did}: files의 칸 '{k}'는 {FILES_COUNTS} 중 하나여야 함 (단위는 파일 — 절·항목·줄은 size에)")
        elif isinstance(v, bool) or not isinstance(v, int) or v < 0:
            errors.append(f"{did}: files.{k}는 0 이상의 정수(파일 수)여야 함 (모르면 칸을 뺀다)")
        else:
            total += v
    if sit.get("S_fixed_input") == "예" and total >= 2:
        errors.append(f"{did}: S_fixed_input = 예(출력 하나인 순수 추론)인데 쓰는 파일이 {total}개 — 파일이 여럿이면 아니오 "
                      f"(p183–p186이 이렇게 대 보기를 틀려 계산기가 10배 작게 봤다)")
    return errors


def form_required(d: dict) -> bool:
    """FORM_REQUIRED_FROM 뒤의 끝난(실측이 있는) 기록인가 — 그러면 turns 칸과 review.report가 필수."""
    return done(d) and "minutes" in d.get("actual", {}) and str(d.get("date", "")) >= FORM_REQUIRED_FROM


def log_required(d: dict) -> bool:
    """LOG_REQUIRED_FROM 뒤의 끝난(실측이 있는) 기록인가 — 그러면 [dispatch.log]가 필수 (form_required와 같은 모양)."""
    return done(d) and "minutes" in d.get("actual", {}) and str(d.get("date", "")) >= LOG_REQUIRED_FROM


def log_errors(d: dict, required: bool | None = None) -> list[str]:
    """로그 숫자([dispatch.log]) 검사. 칸이 있으면 날짜와 상관없이 모양을 본다(LOG_KEYS가 다 있고 0 이상의 수, 또는 skip 한 줄).
    required를 안 주면 log_required(d) — 직접 한 일(direct.toml)은 모양만 본다(required=False)."""
    did, log = d.get("id", "?"), d.get("log")
    need = log_required(d) if required is None else required
    if log is None:
        return [f"{did}: 로그 숫자([dispatch.log])가 없음 — `python -m domains.agent_usage.record finish <id> <로그>`가 붙인다"
                f"(또는 `scripts/agent_usage.py <로그> --log --toml`). 잴 수 없으면 [dispatch.log] 아래 skip = \"이유\""] if need else []
    if not isinstance(log, dict):
        return [f"{did}: log는 표여야 함 (agent_usage.py --log --toml 출력)"]
    if "skip" in log:
        errors = []
        if not (isinstance(log["skip"], str) and log["skip"].strip()) or len(log) > 1:
            errors.append(f"{did}: log.skip은 못 잰 이유 문장 하나만 (숫자와 함께 쓰지 않는다)")
        rnd = d.get("round")
        if need and isinstance(rnd, int) and rnd >= 2 and d.get("situation", {}).get("S_cloud_session") != "예":
            errors.append(f"{did}: 이어 보낸 회차의 로그 숫자는 skip하지 않는다 — `agent_usage.py <로그> --rounds`로 이 회차 시작 시각을 보고 "
                          f"`--log --toml --after <그 시각>`")
        return errors
    errors = []
    missing = [k for k in LOG_KEYS if k not in log]
    if missing:
        errors.append(f"{did}: log에 칸이 빠짐: {', '.join(missing)} (agent_usage.py --log --toml 출력을 그대로)")
    unknown = [k for k in log if k not in LOG_KEYS]
    if unknown:
        errors.append(f"{did}: log의 칸 {', '.join(unknown)}는 LOG_KEYS(scripts/agent_usage.py)에 없음")
    bad = [k for k in LOG_KEYS if k in log and (isinstance(log[k], bool) or not isinstance(log[k], (int, float)) or log[k] < 0)]
    if bad:
        errors.append(f"{did}: log.{', '.join(bad)}는 0 이상의 수여야 함")
    return errors


def _is_cloud(d: dict) -> bool:
    return d.get("situation", {}).get("S_cloud_session") == "예"


def git_required(d: dict) -> bool:
    """GIT_REQUIRED_FROM 뒤의 끝난 로컬 기록인가 — 그러면 [dispatch.git] 숫자(또는 skip)가 필수."""
    return done(d) and "minutes" in d.get("actual", {}) and str(d.get("date", "")) >= GIT_REQUIRED_FROM and not _is_cloud(d)


def cloud_required(d: dict) -> bool:
    """CLOUD_REQUIRED_FROM 뒤의 끝난 클라우드 세션 기록인가 — 그러면 [dispatch.cloud](또는 skip)가 필수."""
    return done(d) and "minutes" in d.get("actual", {}) and str(d.get("date", "")) >= CLOUD_REQUIRED_FROM and _is_cloud(d)


def _nonneg_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def git_errors(d: dict) -> list[str]:
    """[dispatch.git] 검사. 칸이 있으면 날짜와 상관없이 모양을 본다: 보낼 때 기준(repo·head·dirty·dirty_hashes)은 넷이 같이,
    끝날 때 숫자(measure.GIT_KEYS)는 모두 같이(기준도 있어야), skip은 이유 문장(기준과는 같이 둘 수 있고 숫자와는 안 된다)."""
    did, g = d.get("id", "?"), d.get("git")
    if g is None:
        if git_required(d):
            return [f"{did}: git 숫자([dispatch.git])가 없음 — `record send`가 기준을 찍고 `record finish`가 채운다. "
                    f"저장소 밖 일이면 [dispatch.git] 아래 skip = \"저장소 밖 일\""]
        return []
    if not isinstance(g, dict):
        return [f"{did}: git은 표여야 함"]
    errors = []
    unknown = [k for k in g if k not in ("skip",) + ms.GIT_SEND_KEYS + ms.GIT_KEYS]
    if unknown:
        errors.append(f"{did}: git의 칸 {', '.join(unknown)}는 measure.GIT_SEND_KEYS·GIT_KEYS에 없음")
    if "skip" in g and not (isinstance(g["skip"], str) and g["skip"].strip()):
        errors.append(f"{did}: git.skip은 못 잰 이유 문장이어야 함")
    sent = [k for k in ms.GIT_SEND_KEYS if k in g]
    if sent and len(sent) < len(ms.GIT_SEND_KEYS):
        errors.append(f"{did}: git 기준 칸은 {', '.join(ms.GIT_SEND_KEYS)} 넷이 같이 있어야 함")
    if "repo" in g and not (isinstance(g["repo"], str) and re.fullmatch(r"[\w.-]+", g["repo"])):
        errors.append(f"{did}: git.repo는 저장소 폴더 이름만(경로 없이)")
    if "head" in g and not (isinstance(g["head"], str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", g["head"])):
        errors.append(f"{did}: git.head는 커밋 해시여야 함")
    if "dirty" in g and not _nonneg_int(g["dirty"]):
        errors.append(f"{did}: git.dirty는 0 이상의 정수여야 함")
    hashes = g.get("dirty_hashes")
    if hashes is not None and not (isinstance(hashes, list) and all(isinstance(h, str) and ms.HASH_ITEM.match(h) for h in hashes)
                                   and (not _nonneg_int(g.get("dirty")) or len(hashes) == g["dirty"])):
        errors.append(f"{did}: git.dirty_hashes는 \"경로 해시 8자:내용 해시 12자\" 목록이고 길이가 dirty와 같아야 함")
    counted = [k for k in ms.GIT_KEYS if k in g]
    if counted:
        if "skip" in g:
            errors.append(f"{did}: git.skip은 숫자와 같이 쓰지 않는다")
        missing = [k for k in ms.GIT_KEYS if k not in g]
        if missing:
            errors.append(f"{did}: git에 칸이 빠짐: {', '.join(missing)} (record finish 출력을 그대로)")
        if len(sent) < len(ms.GIT_SEND_KEYS):
            errors.append(f"{did}: git 숫자는 보낼 때 기준(repo·head·dirty·dirty_hashes)과 같이 있어야 함")
        bad = [k for k in counted if not _nonneg_int(g[k])]
        if bad:
            errors.append(f"{did}: git.{', '.join(bad)}는 0 이상의 정수여야 함")
    elif git_required(d) and "skip" not in g:
        errors.append(f"{did}: git에 끝날 때 숫자가 없음 — `record finish <id> <로그>`가 채운다(기준 저장소를 못 찾으면 --repo)")
    return errors


def cloud_record_errors(d: dict) -> list[str]:
    """클라우드 세션 기록 검사: session 칸(보낼 때, CLOUD_REQUIRED_FROM부터 필수)과 [dispatch.cloud](끝난 기록에 필수, 못 재면 skip)."""
    did, errors = d.get("id", "?"), []
    sess = d.get("session")
    if sess is not None and not (isinstance(sess, str) and ms.SESSION_ID.match(sess)):
        errors.append(f"{did}: session은 클라우드 세션 id(session_…)여야 함")
    if sess is None and _is_cloud(d) and str(d.get("date", "")) >= CLOUD_REQUIRED_FROM:
        errors.append(f"{did}: 클라우드 세션 일인데 session(세션 id)이 없음 — 보낼 일 파일에 session = \"session_…\"")
    c = d.get("cloud")
    if c is None:
        if cloud_required(d):
            errors.append(f"{did}: 클라우드 숫자([dispatch.cloud])가 없음 — 그 세션의 result 사건(list_events, kinds=[\"result\"])을 "
                          f"`python -m domains.agent_usage.record cloud <id> <숫자.json>`으로. 못 재면 [dispatch.cloud] 아래 skip = \"이유\"")
        return errors
    if not isinstance(c, dict):
        return errors + [f"{did}: cloud는 표여야 함"]
    if "skip" in c:
        if not (isinstance(c["skip"], str) and c["skip"].strip()) or len(c) > 1:
            errors.append(f"{did}: cloud.skip은 못 잰 이유 문장 하나만 (숫자와 함께 쓰지 않는다)")
        return errors
    models = c.get("models")
    back = {**{k: c.get(k) for k in ms.CLOUD_NUM_KEYS + ms.CLOUD_TEXT_KEYS if k in c},
            "models": {name: {src: u.get(dst) for src, dst in ms.CLOUD_MODEL_KEYS.items() if dst in u}
                       for name, u in models.items() if isinstance(u, dict)} if isinstance(models, dict) else models}
    if "models" not in c:
        back.pop("models")
    extra = [k for k in c if k not in ms.CLOUD_NUM_KEYS + ms.CLOUD_TEXT_KEYS + ("models",)]
    extra += [f"models.{n}.{k}" for n, u in (models or {}).items() if isinstance(u, dict) for k in u
              if k not in ms.CLOUD_MODEL_KEYS.values()]
    if extra:
        errors.append(f"{did}: cloud의 모르는 칸: {', '.join(extra)}")
    errors += [f"{did}: cloud — {e}" for e in ms.cloud_errors(back)]
    return errors


def files_vs_git(records: list[dict]) -> dict[str, Counter]:
    """지시서에서 센 files(write·edit)와 git으로 잰 git_write·git_edit를 둘 다 가진 기록끼리 견준다 (2026-11-05)."""
    out = {k: Counter() for k in FILES_COUNTS}
    for d in records:
        files, g = d.get("files"), d.get("git")
        if not (isinstance(files, dict) and isinstance(g, dict)) or "skip" in g:
            continue
        for k in FILES_COUNTS:
            if isinstance(files.get(k), int) and isinstance(g.get(f"git_{k}"), int):
                n = g[f"git_{k}"]
                out[k]["같음" if files[k] == n else ("git이 많음" if n > files[k] else "git이 적음")] += 1
    return out


def files_vs_log(records: list[dict]) -> dict[str, Counter]:
    """지시서에서 센 files(write·edit)와 로그에서 잰 log.write·log.edit를 둘 다 가진 기록끼리 견준다 (2026-11-05).
    칸마다 같음 / 로그가 많음 / 로그가 적음 수. files에 그 칸이 없으면(모름) 그 칸은 안 센다."""
    out = {k: Counter() for k in FILES_COUNTS}
    for d in records:
        files, log = d.get("files"), d.get("log")
        if not (isinstance(files, dict) and isinstance(log, dict)) or "skip" in log:
            continue
        for k in FILES_COUNTS:
            if isinstance(files.get(k), int) and isinstance(log.get(k), int):
                out[k]["같음" if files[k] == log[k] else ("로그가 많음" if log[k] > files[k] else "로그가 적음")] += 1
    return out


def feedback_errors(d: dict, root: Path = ROOT, prefix: str = "dispatch") -> list[str]:
    """피드백 읽기(feedback.read)와 쓰기(review.feedback) 검사. 칸이 있으면 날짜와 상관없이 모양을 본다.
    (가) 읽기: 문자열 목록, 각각 실제 메인 파일, common 포함, `feedback.topics(task)`가 고른 파일이 다 들어 있다 —
         없으면 FEEDBACK_REQUIRED_FROM부터 오류(batman 기록 제외).
    (나) 쓰기: 끝난 기록(실측 분이 있음)이면 FEEDBACK_REQUIRED_FROM부터 review.feedback이 F 번호 목록(백서에 있는 번호)이거나
         '없음: 이유'(이유 FEEDBACK_NONE_MIN자 이상)."""
    did, errors = d.get("id", "?"), []
    main_dir, paper = root / "feedback" / "main", root / "feedback" / "whitepaper.md"
    late = str(d.get("date", "")) >= FEEDBACK_REQUIRED_FROM and d.get("project") != "batman"
    fbt = d.get("feedback")
    read = fbt.get("read") if isinstance(fbt, dict) else None
    if fbt is not None and not isinstance(fbt, dict):
        errors.append(f"{did}: feedback은 [{prefix}.feedback] 표여야 함 (read = [...])")
    elif read is None:
        if late:
            errors.append(f"{did}: 피드백 읽기가 없음 — 보낼 일 파일에 [feedback] read = [...] — `python -m feedback topics` 가 고른 파일을 "
                          f"읽고 적는다 (기록에는 [{prefix}.feedback])")
    elif not (isinstance(read, list) and read and all(isinstance(s, str) for s in read)):
        errors.append(f"{did}: feedback.read는 읽은 메인 피드백 파일 이름(문자열) 목록이어야 함 (예: [\"common\", \"brief\"])")
    else:
        stems = set(fb.main_files(main_dir))
        for s in read:
            if s not in stems:
                errors.append(f"{did}: feedback.read의 '{s}'는 feedback/main/에 없는 파일")
        if fb.COMMON not in read:
            errors.append(f"{did}: feedback.read에 '{fb.COMMON}'이 없음 (모든 일에 읽는다)")
        missing = [s for s in fb.topics(str(d.get("task", "")), main_dir) if s not in read]
        if missing:
            errors.append(f"{did}: feedback.read에 {', '.join(missing)}가 빠짐 — task에 키워드가 걸린 메인 피드백 "
                          f"(`python -m feedback topics`)을 읽고 적는다")
    rev = d.get("review", {}).get("feedback") if isinstance(d.get("review"), dict) else None
    finished = done(d) and "minutes" in d.get("actual", {})
    if rev is None:
        if finished and late:
            errors.append(f"{did}: review.feedback이 없음 — 이번 일에서 올린 피드백 번호 또는 '없음: 이유' "
                          f"(`record finish … --feedback \"F102\"` 또는 `--feedback \"없음: 이유\"`)")
    elif isinstance(rev, str):
        if not (rev.startswith(FEEDBACK_NONE) and len(rev[len(FEEDBACK_NONE):].strip()) >= FEEDBACK_NONE_MIN):
            errors.append(f"{did}: review.feedback 글은 '{FEEDBACK_NONE}이유'(이유 {FEEDBACK_NONE_MIN}자 이상) 꼴이어야 함")
    elif isinstance(rev, list) and rev and all(isinstance(i, str) for i in rev):
        known = {e["id"] for e in fb.entries(paper)} if paper.is_file() else set()
        for i in rev:
            if not re.fullmatch(r"F\d+", i):
                errors.append(f"{did}: review.feedback의 '{i}'는 F 번호(F102 꼴)가 아님")
            elif i not in known:
                errors.append(f"{did}: review.feedback의 {i}가 백서(feedback/whitepaper.md)에 없음 — 항목을 적고 `python -m feedback index --write`")
    else:
        errors.append(f"{did}: review.feedback은 F 번호 목록([\"F102\"]) 또는 '{FEEDBACK_NONE}이유' 글이어야 함")
    return errors


def form_errors(d: dict, root: Path = ROOT) -> list[str]:
    """턴 길이 표와 보고서 경로 검사. 칸이 있으면 날짜와 상관없이 모양을 본다."""
    did, errors = d.get("id", "?"), []
    turns = d.get("turns")
    if turns is None:
        if form_required(d):
            errors.append(f"{did}: 턴 길이 표가 없음 — `python scripts/agent_usage.py <로그> --turns --toml` 출력을 기록 끝에 붙이거나, "
                          f"잴 수 없으면(클라우드 세션 등) [dispatch.turns] 아래 skip = \"이유\"")
    elif "skip" in turns:
        if not (isinstance(turns["skip"], str) and turns["skip"].strip()) or len(turns) > 1:
            errors.append(f"{did}: turns.skip은 못 잰 이유 문장 하나만 (표와 함께 쓰지 않는다)")
    elif not turns or not all(isinstance(v, dict) and isinstance(v.get("n"), int) and v["n"] > 0 for v in turns.values()):
        errors.append(f"{did}: turns는 동작마다 {{ n = 턴 수, ... }} 모양이어야 함 (agent_usage.py --turns --toml 출력)")
    act = d.get("actual", {})
    need = done(d) and "minutes" in act and str(d.get("date", "")) >= TIMES_REQUIRED_FROM
    if "time_skip" in act:
        if not (isinstance(act["time_skip"], str) and act["time_skip"].strip()):
            errors.append(f"{did}: actual.time_skip은 시각을 못 적은 이유 문장이어야 함")
    else:
        for k in ("start", "end"):
            if k in act and not (isinstance(act[k], str) and ISO_UTC.match(act[k])):
                errors.append(f"{did}: actual.{k}는 UTC ISO 시각이어야 함 (예: \"2026-11-04T05:24:13Z\", agent_usage.py --actual)")
            elif k not in act and need:
                errors.append(f"{did}: actual.{k}(시작·끝 시각)가 없음 — `python scripts/agent_usage.py <로그> --actual` 출력을 쓰거나, "
                              f"못 재면 actual.time_skip = \"이유\"")
        if isinstance(act.get("start"), str) and isinstance(act.get("end"), str) and act["start"] > act["end"]:
            errors.append(f"{did}: actual.start가 end보다 늦음")
    agent, rnd = d.get("agent"), d.get("round")
    if agent is not None and not (isinstance(agent, str) and agent.strip()):
        errors.append(f"{did}: agent는 같은 에이전트를 가리키는 이름이어야 함 (회차마다 같은 이름)")
    if rnd is not None and (isinstance(rnd, bool) or not isinstance(rnd, int) or rnd < 1):
        errors.append(f"{did}: round는 1 이상의 정수여야 함 (처음 보낸 회차 = 1)")
    if need and (agent is None or rnd is None):
        errors.append(f"{did}: agent(같은 에이전트 이름)와 round(몇 번째 회차, 처음 = 1)가 없음")
    if isinstance(rnd, int) and d.get("situation", {}).get("S_resumed") == "예" and rnd < 2:
        errors.append(f"{did}: 이어 보낸 회차(S_resumed = 예)인데 round가 2보다 작음")
    if need and d.get("project") != "batman" and isinstance(d.get("batch"), int) and d["batch"] not in logged_batches(root / "docs" / "AGENT-LOG.md"):
        errors.append(f"{did}: 배치 {d['batch']} 줄이 docs/AGENT-LOG.md에 없음 — '## 배치 {d['batch']} · 날짜 · 주제' 머리와 표 한 줄"
                      f"(모델·effort·품질 1–5·메모)과 교훈 (batman 기록은 batman 쪽 AGENT-LOG)")
    if (need and isinstance(turns, dict) and "skip" in turns and isinstance(rnd, int) and rnd >= 2
            and d.get("situation", {}).get("S_cloud_session") != "예"):
        errors.append(f"{did}: 이어 보낸 회차의 턴 길이 표는 skip하지 않는다 — `agent_usage.py <로그> --rounds`로 이 회차 시작 시각을 보고 "
                      f"`--turns --toml --after <그 시각>`")
    if "decide" in d:
        errors.extend(decide_errors(did, d["decide"], "보냄"))
    elif str(d.get("date", "")) >= DECIDE_REQUIRED_FROM and d.get("project") != "batman":
        errors.append(f"{did}: 보낼까 판단(decide)이 없음 — `python -m domains.agent_usage.decide <상황 파일>` 출력의 [dispatch.decide] "
                      f"(묶음 명령 `record send`가 붙여 준다)")
    rep = d.get("review", {}).get("report")
    if rep is None:
        if form_required(d):
            errors.append(f"{did}: review.report(작업 보고서 경로)가 없음 — 이 저장소면 docs/worklog/..., 다른 저장소면 \"저장소:경로\"")
    elif not (isinstance(rep, str) and rep.strip()):
        errors.append(f"{did}: review.report는 경로 문장이어야 함")
    elif not OTHER_REPO.match(rep) and not (root / rep).is_file():
        errors.append(f"{did}: review.report '{rep}' 파일이 없음 (다른 저장소면 \"저장소:경로\")")
    return errors


def validate(records: list[dict], kn: schema.Knowledge) -> list[str]:
    """기록의 문제 목록. 규칙·상태·가설 id는 지식 파일에 있어야 한다."""
    errors, seen = [], set()

    def expect(did: str, ref: str, kinds: tuple[str, ...]) -> None:
        node = kn.nodes.get(ref)
        if node is None or node.kind not in kinds:
            names = "·".join(schema.KIND_LABEL[k] for k in kinds)
            errors.append(f"{did}: '{ref}'는 지식 파일에 있는 {names}이 아님")

    for d in records:
        did = d.get("id", "?")
        if did in seen:
            errors.append(f"id 중복: {did}")
        seen.add(did)
        for key in ("project", "batch", "date", "task", "predicted", "actual"):
            if key not in d:
                errors.append(f"{did}: '{key}' 칸이 비어 있음")
        p = d.get("predicted", {})
        for cls in p.get("time_class", []):
            if cls not in OLD_TIME_CLASSES:
                errors.append(f"{did}: 옛 시간 등급 '{cls}'는 {OLD_TIME_CLASSES} 중 하나여야 함")
        if "told" in p and p["told"] not in ZONES:
            errors.append(f"{did}: predicted.told는 {ZONES} 중 하나여야 함")
        calc = d.get("calc", {})
        if calc and calc.get("told") not in ZONES:
            errors.append(f"{did}: calc.told(계산기가 낸 말할 구간)는 {ZONES} 중 하나여야 함")
        for cls in p.get("tokens_class", []):
            if cls not in TOKEN_CLASSES:
                errors.append(f"{did}: 토큰 등급 '{cls}'는 {TOKEN_CLASSES} 중 하나여야 함")
        for rid in p.get("rules", []):
            expect(did, rid, ("rule",))
        for sid, value in d.get("situation", {}).items():
            expect(did, sid, ("state",))
            if value not in SITUATION_VALUES:
                errors.append(f"{did}.{sid}: 값은 {SITUATION_VALUES} 중 하나여야 함")
        review = d.get("review", {})
        for hid in review.get("hypotheses", []):
            expect(did, hid, ("hypothesis",))
        for wid in review.get("wrong", []):
            expect(did, wid, ("rule", "hypothesis", "state"))
        if "why" in review and review["why"] not in WHY:
            errors.append(f"{did}: review.why는 {WHY} 중 하나여야 함")
        if wrong_required(records, d) and not (review.get("why") and (review.get("wrong") or review["why"] == UNKNOWN_WHY)):
            errors.append(f"{did}: 시간 구간이 빗나갔는데 review.wrong(틀린 조각 id)과 review.why({'/'.join(WHY)})가 없음"
                          f" (까닭을 못 찾았으면 why = \"{UNKNOWN_WHY}\", 이때 wrong은 비워도 된다)")
        size = d.get("size")
        if size is not None:
            if not isinstance(size, dict):
                errors.append(f"{did}: size는 {{ 이름 = 수 }} 표여야 함")
            else:
                for k, v in size.items():
                    if k in SIZE_COUNTS:
                        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                            errors.append(f"{did}: size.{k}는 0 이상의 수여야 함 (모르면 칸을 뺀다)")
                    elif k in SIZE_TEXT:
                        if not isinstance(v, str):
                            errors.append(f"{did}: size.{k}는 글이어야 함 (예: \"25 원문\")")
                    else:
                        errors.append(f"{did}: size의 칸 '{k}'는 {SIZE_COUNTS + SIZE_TEXT} 중 하나여야 함")
        status = d.get("actual", {}).get("status", "done")
        if status not in STATUSES:
            errors.append(f"{did}: actual.status는 {STATUSES} 중 하나여야 함")
        if done(d) and "minutes" not in d.get("actual", {}):
            errors.append(f"{did}: 끝난 작업인데 실측 시간이 없음")
        errors.extend(model_errors(d))
        errors.extend(form_errors(d))
        errors.extend(log_errors(d))
        errors.extend(git_errors(d))
        errors.extend(cloud_record_errors(d))
        errors.extend(files_errors(d))
        errors.extend(feedback_errors(d))
    return errors


def _num(value: float | None, fmt: str, unit: str = "") -> str:
    return "–" if value is None else format(value, fmt) + unit


def _bounds(b: list[float]) -> str:
    return "–" if not b else (f"{b[0]:g}–{b[1]:g}" if len(b) > 1 else f"{b[0]:g}+")


def miss_split(d: dict) -> tuple[str, str] | None:
    """분이 범위를 빗나간 기록을 기계적으로 가른다: (방향, 갈래). 빗나가지 않았으면 None.
    턴이 범위 안이었으면 '속도'(분당 턴 조각 탓), 밖이었으면 '양'(턴 수 조각 탓), 턴 예측이 없으면 '턴 예측 없음'."""
    p, m = d["predicted"], measures(d)
    hit = in_range(m["minutes"], p.get("minutes", []))
    if hit is None or hit:
        return None
    direction = "아래" if m["minutes"] < p["minutes"][0] else "위"
    turns_hit = in_range(m["turns"], p.get("turns", []))
    branch = "턴 예측 없음" if turns_hit is None else ("속도" if turns_hit else "양")
    return direction, branch


def rescore(records: list[dict]) -> dict:
    """끝난 기록을 새 시간 구간으로 다시 채점한 집계. 기록 파일은 건드리지 않는다."""
    out = {"판정": Counter(), "보내기 전": Counter(), "구간별": {z: Counter() for z in ZONES},
           "걸침": Counter(), "걸침 기록": [], "분 범위 없음": [], "말한 구간": Counter(),
           "분 빗나감": Counter(), "분 범위": Counter(), "양 반대 방향": []}
    for d in records:
        if not done(d):
            continue
        p, m = d["predicted"], measures(d)
        want = zones_of(p.get("minutes", []))
        if not want:
            out["분 범위 없음"].append(d["id"])
            continue
        got = zone(m["minutes"])
        verdict = judge(want, got, ZONES)
        out["판정"][verdict] += 1
        if p.get("written_before", True):
            out["보내기 전"][verdict] += 1
        if len(want) == 1:
            out["구간별"][want[0]][verdict] += 1
        else:
            fell = ("긴 쪽" if got == want[-1] else "짧은 쪽" if got == want[0] else
                    "가운데" if got in want else "밖")
            out["걸침"][fell] += 1
            out["걸침 기록"].append(f"{d['id']} {'/'.join(want)} → {got}")
        if "told" in p:
            out["말한 구간"]["맞음" if p["told"] == got else "빗나감"] += 1
        out["분 범위"]["맞음" if in_range(m["minutes"], p["minutes"]) else "빗나감"] += 1
        split = miss_split(d)
        if split:
            out["분 빗나감"][split] += 1
            if split[1] == "양" and (m["turns"] < p["turns"][0]) != (split[0] == "아래"):
                out["양 반대 방향"].append(d["id"])
    return out


def _tally(c: Counter) -> str:
    return ", ".join(f"{k} {c[k]}" for k in ("맞음", "낮게 잡음", "높게 잡음", "모름") if c[k]) or "없음"


def hand_vs_calc(records: list[dict]) -> dict:
    """보내기 전에 손 예측(predicted.told)과 계산기(calc.told)를 둘 다 적은 끝난 기록에서 누가 맞았나."""
    out = Counter()
    for d in records:
        told, calc, minutes = d.get("predicted", {}).get("told"), d.get("calc", {}).get("told"), d.get("actual", {}).get("minutes")
        if not (done(d) and told and calc and minutes is not None):
            continue
        got = zone(minutes)
        out[{(True, True): "둘 다 맞음", (True, False): "손만 맞음",
             (False, True): "계산기만 맞음", (False, False): "둘 다 틀림"}[(told == got, calc == got)]] += 1
    return out


def for_user(records: list[dict]) -> list[str]:
    """돌아보기에서 까닭을 못 찾은(why = 까닭 모름) 기록 중 사용자의 답(review.user)이 아직 없는 것.
    사용자에게 넘긴다(2026-11-03 사용자 결정: 이 분야는 사용자가 판정하지 않지만, 까닭 모름만은 넘긴다)."""
    return [d["id"] for d in records
            if d.get("review", {}).get("why") == UNKNOWN_WHY and not d["review"].get("user")]


def report(records: list[dict]) -> str:
    """예측·실측 비교표와 맞음/빗나감 집계. 시간은 세 마디 구간으로 (분 숫자로 다시 채점)."""
    head = ("| id | 배치 | 예측 분 | 예측 구간 | 말한 구간 | 실제 | 판정 | 예측 토큰 | 실제 | 판정 | 턴 | 분당 토큰 | 턴당 맥락 |\n"
            "|---|--:|---|---|---|---|---|---|---|---|--:|--:|--:|")
    lines = [head]
    tokens, tokens_before = Counter(), Counter()
    for d in records:
        p = d["predicted"]
        want_m, want_z = _bounds(p.get("minutes", [])), "/".join(zones_of(p.get("minutes", []))) or "–"
        told, want_k = p.get("told", "–"), "–".join(p.get("tokens_class", []))
        if not done(d):
            lines.append(f"| {d['id']} | {d['batch']} | {want_m} | {want_z} | {told} | 판정에서 뺌 "
                         f"({d['actual'].get('status')}) | | {want_k} | | | | | |")
            continue
        m = measures(d)
        got_k = token_class(m["tokens_m"]) if m["tokens_m"] is not None else None
        judged_k = judge(p.get("tokens_class", []), got_k, TOKEN_CLASSES)
        tokens[judged_k] += 1
        if p.get("written_before", True):
            tokens_before[judged_k] += 1
        lines.append(
            f"| {d['id']} | {d['batch']} | {want_m} | {want_z} | {told} | {m['minutes']}분 ({zone(m['minutes'])}) "
            f"| {zone_verdict(d) or '판정에서 뺌 (분 범위 없음)'} "
            f"| {want_k} | {_num(m['tokens_m'], '.1f', 'M')} ({got_k or '–'}) | {judged_k} "
            f"| {m['turns'] or '–'} | {_num(m['tokens_per_min'], '.2f', 'M')} | {_num(m['ctx_per_turn_k'], '.0f', 'k')} |"
        )
    r = rescore(records)
    n = sum(r["판정"].values())
    lines += ["", f"시간 구간 (잠깐 ≤10분 · 다른 일 10–40분 · 신경 끄기 >40분), 분 숫자로 다시 채점한 {n}건",
              f"  전체: {_tally(r['판정'])} · 보내기 전에 적은 것만: {_tally(r['보내기 전'])}"]
    for z in ZONES:
        c = r["구간별"][z]
        lines.append(f"  예측이 '{z}' 하나: {sum(c.values())}건 — {_tally(c)}")
    span = r["걸침"]
    lines.append(f"  걸침(두 구간 이상): {sum(span.values())}건 — 실제 낙하: "
                 + (", ".join(f"{k} {span[k]}" for k in ("짧은 쪽", "가운데", "긴 쪽", "밖") if span[k]) or "없음")
                 + " (2026-11-03 전에는 걸치면 긴 쪽으로 말했다 — 그때 맞은 것은 '긴 쪽'. 지금은 가운데 값의 구간, R_say_numbers_v3)")
    lines.append(f"  분 범위가 없어 뺀 기록 {len(r['분 범위 없음'])}건: {', '.join(r['분 범위 없음']) or '없음'}")
    lines.append(f"  말한 구간(predicted.told)이 있는 끝난 기록: {sum(r['말한 구간'].values())}건"
                 + (f" — 맞음 {r['말한 구간']['맞음']}, 빗나감 {r['말한 구간']['빗나감']}" if r["말한 구간"] else ""))
    hv = hand_vs_calc(records)
    lines.append(f"손 예측 vs 계산기 (보내기 전에 둘 다 적은 끝난 기록 {sum(hv.values())}건, 말한 구간 기준): "
                 + (", ".join(f"{k} {hv[k]}" for k in ("둘 다 맞음", "손만 맞음", "계산기만 맞음", "둘 다 틀림") if hv[k]) or "아직 없음")
                 + " · 지난 기록 홀드아웃(뒤 절반 61건): 손 62 %, 계산기 51 % (holdout)")
    asks = for_user(records)
    lines.append(f"사용자에게 넘길 것 (까닭 모름, 답 아직 없음): {', '.join(asks) if asks else '없음'}")
    lines.append(f"분 범위 적중(숫자 그대로): 맞음 {r['분 범위']['맞음']}, 빗나감 {r['분 범위']['빗나감']}")
    miss = r["분 빗나감"]
    lines.append("분 빗나감의 갈래 (턴 범위가 맞았으면 속도 조각 탓, 틀렸으면 양 조각 탓):")
    lines.append("| 분 | 속도 | 양 | 턴 예측 없음 | 계 |\n|---|--:|--:|--:|--:|")
    for direction in ("아래", "위"):
        row = [miss[(direction, b)] for b in ("속도", "양", "턴 예측 없음")]
        lines.append(f"| 실제가 범위 {direction} | {' | '.join(map(str, row))} | {sum(row)} |")
    lines.append(f"  '양' 중 턴이 분과 반대로 빗나간 기록(속도도 틀림): {', '.join(r['양 반대 방향']) or '없음'}")
    lines.append(f"토큰 등급 — 전체: {_tally(tokens)} · 보내기 전에 적은 것만: {_tally(tokens_before)}")
    fl = files_vs_log(records)
    lines.append("쓰는 파일 수 — 지시서에서 센 files vs 로그에서 잰 log (둘 다 있는 기록): "
                 + " · ".join(f"{k} {sum(c.values())}건(" + (", ".join(f"{n} {c[n]}" for n in ("같음", "로그가 많음", "로그가 적음") if c[n]) or "없음") + ")"
                              for k, c in fl.items()))
    fg = files_vs_git(records)
    lines.append("쓰는 파일 수 — 지시서에서 센 files vs git으로 잰 [dispatch.git] (둘 다 있는 기록): "
                 + " · ".join(f"{k} {sum(c.values())}건(" + (", ".join(f"{n} {c[n]}" for n in ("같음", "git이 많음", "git이 적음") if c[n]) or "없음") + ")"
                              for k, c in fg.items()))
    return "\n".join(lines)


def main() -> int:
    records = load()
    kn = schema.load(HERE / "knowledge.toml")
    errors = validate(records, kn) + validate_direct(load_direct())
    if errors:
        print("기록에 문제 있음:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"기록 문제 없음 ({len(records)}건)\n")
    print(report(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
