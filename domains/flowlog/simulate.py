"""Flowlog 제목 추천 시뮬레이션.

v1: Flowlog README의 점수식으로 상위 5개 (현재 앱 동작).
v2: R_P1a(1~4칸 = 2회 이상 쓴 제목, 점수순) + R_P1b(5번째 칸 = 1~4칸에 없는 가장 최근 제목).

시간 단위는 '일'. 추천에 없는 제목을 쓰면 "직접 입력"으로 센다.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def score(times: list[float], now: float) -> float:
    """Flowlog ActivityTitleSuggestionRanker의 점수식 (README 기준)."""
    weighted = sum(2 ** (-(now - t) / 14) for t in times)
    idle = now - max(times)
    return (40 + 60 * weighted / (weighted + 3)) * 2 ** (-idle / 7)


@dataclass
class History:
    uses: dict[str, list[float]] = field(default_factory=dict)

    def log(self, title: str, t: float) -> None:
        self.uses.setdefault(title, []).append(t)


def recommend_v1(h: History, now: float) -> list[str]:
    return sorted(h.uses, key=lambda x: score(h.uses[x], now), reverse=True)[:5]


def recommend_v2(h: History, now: float) -> list[str]:
    multi = [x for x in h.uses if len(h.uses[x]) >= 2]
    shown = sorted(multi, key=lambda x: score(h.uses[x], now), reverse=True)[:4]
    rest = [x for x in h.uses if x not in shown]
    if rest:
        shown.append(max(rest, key=lambda x: max(h.uses[x])))
    return shown


# 평소 활동: (제목, 며칠마다, 하루 중 시각)
ROUTINE_4 = [("공부", 1, 0.30), ("식사", 1, 0.50), ("운동", 2, 0.60), ("휴식", 3, 0.70)]
ROUTINE_6 = ROUTINE_4 + [("독서", 4, 0.75), ("산책", 5, 0.80)]


@dataclass
class Result:
    typed: dict[str, int]      # 새 활동별 직접 입력 횟수
    used: dict[str, int]       # 새 활동별 사용 횟수
    routine_typed: int         # 평소 활동을 직접 입력한 횟수 (목표 a 확인용)


def run(recommend, routine, new_schedule, days: int = 14, warmup: int = 21) -> Result:
    """warmup일 동안 평소 활동만 하고, 이후 days일 동안 new_schedule(day)의 새 활동을 저녁에 한다."""
    h = History()
    for d in range(-warmup, 0):
        for title, every, at in routine:
            if d % every == 0:
                h.log(title, d + at)
    typed: dict[str, int] = {}
    used: dict[str, int] = {}
    routine_typed = 0
    for d in range(days):
        events = [(at, title, False) for title, every, at in routine if d % every == 0]
        events += [(0.90, title, True) for title in new_schedule(d)]
        for at, title, is_new in sorted(events):
            t = d + at
            hit = title in recommend(h, t)
            if is_new:
                used[title] = used.get(title, 0) + 1
                typed[title] = typed.get(title, 0) + (not hit)
            elif not hit:
                routine_typed += 1
            h.log(title, t)
    return Result(typed, used, routine_typed)


def first_use_rank(recommend, routine) -> int | None:
    """새 제목을 한 번 쓴 직후, 추천 몇 번째 칸에 오는가 (없으면 None)."""
    h = History()
    for d in range(-21, 0):
        for title, every, at in routine:
            if d % every == 0:
                h.log(title, d + at)
    h.log("새활동", 0.9)
    shown = recommend(h, 1.0)
    return shown.index("새활동") + 1 if "새활동" in shown else None


SCENARIOS = {
    "새 활동 하나를 매일": lambda d: ["A"],
    "새 활동 둘을 번갈아": lambda d: ["A"] if d % 2 == 0 else ["B"],
}


def report() -> str:
    lines = []
    for rname, routine in (("평소 활동 4개", ROUTINE_4), ("평소 활동 6개", ROUTINE_6)):
        lines.append(f"[{rname}]")
        for label, fn in (("v1", recommend_v1), ("v2", recommend_v2)):
            lines.append(f"  {label} 처음 쓴 직후 순위: {first_use_rank(fn, routine) or '추천에 없음'}")
        for sname, sched in SCENARIOS.items():
            for label, fn in (("v1", recommend_v1), ("v2", recommend_v2)):
                r = run(fn, routine, sched)
                per = ", ".join(f"{k} {r.typed[k]}/{r.used[k]}" for k in sorted(r.typed))
                lines.append(f"  {sname:<12} {label}: 직접 입력 {per} · 평소 활동 직접 입력 {r.routine_typed}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
