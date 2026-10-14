"""실제 Flowlog 백업으로 추천 방식을 되감아 본다 (재생 시뮬레이션).

기록을 시간 순서대로 한 건씩 넘기며, 그 시점까지의 같은 카테고리 기록만 보고
v1/v2가 추천 5칸을 만들었다면 지금 쓴 제목이 그 안에 있었을지 센다.
그 당시 앱에 추천 기능이 있었는지와 상관없이 계산할 수 있다.

사용법 (저장소 루트):
  python -m domains.flowlog.replay <백업 json 경로> [사용자 uid]
uid를 안 주면 백업을 요청한 계정(requestedBy)만 쓴다. 다른 사용자 기록은 읽지 않는다.
백업 파일과 결과는 개인정보이므로 저장소에 넣지 않는다.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from . import simulate as sim

DAY_MS = 86_400_000
TYPED_SOURCES = {"MANUAL", None}  # 루틴·자동 버튼으로 생긴 기록은 제목을 고르지 않았으므로 평가에서 뺀다


def load_sessions(path: Path, uid: str | None = None) -> tuple[str, list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    uid = uid or data["requestedBy"]
    target = f"users/{uid}/flowlog/data/activitySessions"
    sessions = [doc["data"] for doc in data["documents"] if doc["collectionPath"] == target]
    return uid, sorted(sessions, key=lambda s: s["startTime"])


class Tally:
    def __init__(self):
        self.n = defaultdict(int)
        self.hit = defaultdict(int)

    def add(self, key: str, hit: bool) -> None:
        self.n[key] += 1
        self.hit[key] += hit

    def rate(self, key: str) -> str:
        return f"{self.hit[key] / self.n[key]:.0%} ({self.hit[key]}/{self.n[key]})" if self.n[key] else "-"


def replay(sessions: list[dict]) -> dict[str, Tally]:
    """버전별로 '추천 5칸 안에 있었나'를 센다.

    구분: 익숙한 제목(이전 5회 이상) = 목표 a, 새 제목(이전 1~3회) = 목표 b, 월별 전체.
    처음 쓰는 제목은 어떤 방식으로도 추천될 수 없으므로 따로 센다.
    """
    histories: dict[str, sim.History] = defaultdict(sim.History)
    out = {"v1": Tally(), "v2": Tally()}
    first_rank1 = Tally()
    pending_first: dict[str, set[str]] = defaultdict(set)  # 카테고리별, 방금 처음 쓴 제목들

    for s in sessions:
        cat, title = s["category"], s["title"].strip()
        now = s["startTime"] / DAY_MS
        h = histories[cat]
        prior = len(h.uses.get(title, []))
        evaluate = s.get("sourceType") in TYPED_SOURCES and title

        if evaluate and h.uses:
            month = datetime.fromtimestamp(s["startTime"] / 1000).strftime("%Y-%m")
            v1_shown = sim.recommend_v1(h, now)
            # v1에서 처음 쓴 제목이 다음 기회에 1등으로 오르는가 (사용자 관찰 O_first_jumps)
            for fresh in pending_first[cat]:
                first_rank1.add("first", bool(v1_shown) and v1_shown[0] == fresh)
            pending_first[cat].clear()
            for ver, fn in (("v1", sim.recommend_v1), ("v2", sim.recommend_v2)):
                shown = v1_shown if ver == "v1" else fn(h, now)
                hit = title in shown
                if prior == 0:
                    out[ver].add("처음 쓰는 제목", hit)
                    continue
                out[ver].add(f"월 {month}", hit)
                out[ver].add("전체 (두 번째 이상)", hit)
                if prior >= 5:
                    out[ver].add("익숙한 제목 (이전 5회 이상) · 목표 a", hit)
                elif prior <= 3:
                    out[ver].add("새 제목 (이전 1~3회) · 목표 b", hit)
        if title:
            if prior == 0:
                pending_first[cat].add(title)
            h.log(title, now)
    out["first_rank1"] = first_rank1
    return out


def report(sessions: list[dict]) -> str:
    result = replay(sessions)
    keys = [k for k in result["v1"].n if not k.startswith("월")]
    keys += sorted(k for k in result["v1"].n if k.startswith("월"))
    lines = [f"{'구분':<32} {'v1 (현재 앱)':>18} {'v2 (새 설계)':>18}"]
    for k in keys:
        lines.append(f"{k:<32} {result['v1'].rate(k):>18} {result['v2'].rate(k):>18}")
    lines.append(f"\nv1에서 처음 쓴 제목이 바로 다음 기회에 1등: {result['first_rank1'].rate('first')}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    uid, sessions = load_sessions(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
    first = datetime.fromtimestamp(sessions[0]["startTime"] / 1000).date()
    last = datetime.fromtimestamp(sessions[-1]["startTime"] / 1000).date()
    print(f"사용자 {uid[:6]}… 기록 {len(sessions)}건 ({first} ~ {last}), 카테고리별로 추천 5칸을 계산\n")
    print(report(sessions))
