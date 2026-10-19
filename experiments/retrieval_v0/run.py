"""후보 뽑기 실험 v0: 점수 방법별로 1종·2종 오류, 조건부확률, 기대 효용을 잰다.

사용법 (저장소 루트):
  python -m experiments.retrieval_v0.run                       표준 라이브러리 방법만(overlap, bigram)
  python -m experiments.retrieval_v0.run --embed <모델 이름>    임베딩도(외부 패키지 필요, requirements.txt)
  --e5   e5 계열 모델이면 'query: ' / 'passage: ' 접두어를 붙인다
  --out <파일>   보고서를 파일로(기본: 화면)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import scorers
from .data import all_datasets
from .score import COST_RATIOS, best_k, evaluate


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x * 100:.0f}%"


def report(methods: dict) -> str:
    lines = ["# 후보 뽑기 실험 v0 결과", ""]
    for ds in all_datasets():
        pos = sum(len(c.yes) for c in ds.cases)
        neg = sum(len(c.no) for c in ds.cases)
        lines += [f"## {ds.name}",
                  f"질문 {len(ds.cases)}개, 후보 {len(ds.candidates)}개. 채점되는 판정: 예 {pos} · 아니오 {neg} "
                  f"(기본 비율 {_pct(pos / (pos + neg))}).", ""]
        for name, scorer in methods.items():
            results, per_state = evaluate(ds, scorer)
            lines += [f"### {name}", "",
                      "| k | 재현율 P(뽑힘∣예) | 우연 | 정밀도 P(예∣뽑힘) | 질문당 놓침(2종) | 질문당 헛짚음(1종) |",
                      "|--:|--:|--:|--:|--:|--:|"]
            for r in results:
                lines.append(f"| {r.k} | {_pct(r.recall)} | {_pct(r.chance_recall)} | {_pct(r.precision)} "
                             f"| {r.misses:.2f} | {r.false_alarms:.2f} |")
            picks = ", ".join(f"놓침이 읽기의 {c}배 → k={best_k(results, c)[0]}" for c in COST_RATIOS)
            lines += ["", f"기대 효용이 가장 큰 k: {picks}", "",
                      "상태별 (k=5): 기본 비율 · 재현율 · 헛짚음 비율 · P(진짜 예∣뽑힘)", "",
                      "| 상태 | 예/아니오 | 기본 비율 | 재현율 | 헛짚음 비율 | P(예∣뽑힘) |", "|---|--:|--:|--:|--:|--:|"]
            for s, v in sorted(per_state.items(), key=lambda kv: -kv[1]["pos"]):
                lines.append(f"| {s} | {v['pos']}/{v['neg']} | {_pct(v['base_rate'])} | {_pct(v['recall'])} "
                             f"| {_pct(v['false_alarm_rate'])} | {_pct(v['p_true_given_picked'])} |")
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--embed", action="append", default=[])
    p.add_argument("--e5", action="store_true")
    p.add_argument("--out")
    a = p.parse_args(argv)
    methods = {"overlap (지금 엔진의 낱말 겹침)": scorers.overlap, "bigram (글자 두 개 겹침)": scorers.bigram}
    for m in a.embed:
        qp, pp = ("query: ", "passage: ") if a.e5 else ("", "")
        methods[f"embed {m}"] = scorers.make_embed(m, qp, pp)
    text = report(methods)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
        print(f"썼음: {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
