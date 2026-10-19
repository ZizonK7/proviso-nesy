"""Flowlog 가설 검사 함수. knowledge.toml의 hypothesis.check 이름으로 찾는다.

각 함수는 (판정, 설명)을 돌려준다. 판정: "지지됨" / "반박됨" / "불명".
시뮬레이션 결과일 뿐이므로 판정 뒤에 출처를 붙인다.
"""
from __future__ import annotations

from . import simulate as sim

SOURCE = "simulation"  # 이 분야의 자동 검사는 가상 사용 패턴 시뮬레이션이다 (실제 기록 재생 결과는 판정 기록으로)


def alternate_two_new() -> tuple[str, str]:
    """H_alternate: 새 활동 둘을 번갈아 하면 v2에서도 계속 직접 입력하게 되는가."""
    lines, supported = [], True
    for name, routine in (("평소 활동 4개", sim.ROUTINE_4), ("평소 활동 6개", sim.ROUTINE_6)):
        one = sim.run(sim.recommend_v2, routine, sim.SCENARIOS["새 활동 하나를 매일"])
        two = sim.run(sim.recommend_v2, routine, sim.SCENARIOS["새 활동 둘을 번갈아"])
        one_rate = one.typed["A"] / one.used["A"]
        two_rate = sum(two.typed.values()) / sum(two.used.values())
        lines.append(f"  {name}: 하나를 매일 → 직접 입력 {one_rate:.0%}, 둘을 번갈아 → {two_rate:.0%}")
        supported &= two_rate >= 0.8 and two_rate > one_rate * 3
    verdict = "지지됨 (시뮬레이션)" if supported else "불명 (시뮬레이션)"
    return verdict, "\n".join(lines)


def routine_pushed_out() -> tuple[str, str]:
    """H_routine_pushed: 평소 활동이 많으면 v2가 v1보다 평소 활동 직접 입력을 늘리는가."""
    lines, supported = [], True
    for name, routine, expect_more in (("평소 활동 4개", sim.ROUTINE_4, False),
                                       ("평소 활동 6개", sim.ROUTINE_6, True)):
        sched = sim.SCENARIOS["새 활동 하나를 매일"]
        v1 = sim.run(sim.recommend_v1, routine, sched).routine_typed
        v2 = sim.run(sim.recommend_v2, routine, sched).routine_typed
        lines.append(f"  {name}, 새 활동 하나를 매일: 평소 활동 직접 입력 v1 {v1}번 → v2 {v2}번")
        if expect_more:
            supported &= v2 > v1
    verdict = "지지됨 (시뮬레이션)" if supported else "불명 (시뮬레이션)"
    return verdict, "\n".join(lines)


CHECKS = {"alternate_two_new": alternate_two_new, "routine_pushed_out": routine_pushed_out}
