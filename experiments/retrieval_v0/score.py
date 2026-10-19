"""채점: 점수 매기는 방법(scorer) 하나를 받아, 질문마다 후보를 줄 세우고 상위 k개를 '뽑힘'으로 본다.

- 2종 오류(놓침): 정답 '예'인데 상위 k에 없음.   재현율 = 1 − 놓친 비율 = P(뽑힘 | 진짜 예)
- 1종 오류(헛짚음): 정답 '아니오'인데 상위 k에 있음.  정밀도 = P(진짜 예 | 뽑힘)  (채점되는 것만 셈)
- 우연 기준: 후보를 무작위로 줄 세우면 재현율 기댓값 = k / 후보 수
- 기대 효용: 질문 하나에 U(k) = −(읽기 비용 × k) − (놓침 비용 × 놓친 수). 비용 비율(놓침 ÷ 읽기)마다 U가 가장 큰 k를 고른다.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .data import Dataset

Scorer = Callable[[str, dict[str, str]], dict[str, float]]  # (질문, 후보) → 후보 id별 점수
KS = (1, 3, 5, 10)
COST_RATIOS = (1, 5, 20)


@dataclass
class Result:
    k: int
    recall: float
    precision: float
    misses: float  # 질문당 평균 놓침
    false_alarms: float  # 질문당 평균 헛짚음
    chance_recall: float


def rank(scorer: Scorer, query: str, candidates: dict[str, str]) -> list[str]:
    scores = scorer(query, candidates)
    # 같은 점수는 id 순으로(결과가 매번 같도록)
    return sorted(candidates, key=lambda c: (-scores.get(c, 0.0), c))


def evaluate(ds: Dataset, scorer: Scorer, ks: tuple[int, ...] = KS) -> tuple[list[Result], dict]:
    ranked = {c.id: rank(scorer, c.query, ds.candidates) for c in ds.cases}
    n = len(ds.candidates)
    results = []
    for k in ks:
        tp = fn = fp = 0
        for c in ds.cases:
            top = set(ranked[c.id][:k])
            tp += len(c.yes & top)
            fn += len(c.yes - top)
            fp += len(c.no & top)
        q = len(ds.cases)
        results.append(Result(k, tp / (tp + fn) if tp + fn else 0.0, tp / (tp + fp) if tp + fp else 0.0,
                              fn / q, fp / q, min(1.0, k / n)))
    per_state = {}
    k_ref = 5
    for s in ds.candidates:
        pos = [c for c in ds.cases if s in c.yes]
        neg = [c for c in ds.cases if s in c.no]
        if not pos and not neg:
            continue
        hit = sum(s in ranked[c.id][:k_ref] for c in pos)
        alarm = sum(s in ranked[c.id][:k_ref] for c in neg)
        per_state[s] = {"base_rate": len(pos) / (len(pos) + len(neg)), "pos": len(pos), "neg": len(neg),
                        "recall": hit / len(pos) if pos else None,
                        "false_alarm_rate": alarm / len(neg) if neg else None,
                        "p_true_given_picked": hit / (hit + alarm) if hit + alarm else None}
    return results, per_state


def best_k(results: list[Result], ratio: float) -> tuple[int, float]:
    """놓침 비용 = ratio × 읽기 비용일 때 기대 효용(질문당)이 가장 큰 k."""
    utils = [(r.k, -(r.k + ratio * r.misses)) for r in results]
    return max(utils, key=lambda kv: kv[1])
