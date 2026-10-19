"""정답지 만들기: 논리집의 대 보기 기록 → (질문 글, 후보 상태들, 정답 예/아니오).

두 묶음:
- agent_usage: 질문 = 작업 설명(dispatches.toml의 task), 후보 = 상태 21개, 정답 = 그 기록의 상황 값
- nonfiction_games: 질문 = 게임의 사실 글(games.toml의 facts → knowledge.toml), 후보 = 상태 15개, 정답 = 상황 값

'예'는 양성, '아니오'는 음성. '일부'·'모름'·적지 않은 상태는 채점에서 뺀다(정답이 불분명).
표준 라이브러리만 쓴다.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Case:
    id: str
    query: str
    yes: set[str] = field(default_factory=set)
    no: set[str] = field(default_factory=set)


@dataclass
class Dataset:
    name: str
    candidates: dict[str, str]  # 상태 id → 글
    cases: list[Case]


def _toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _states(knowledge: dict) -> dict[str, str]:
    return {s["id"]: s["text"] for s in knowledge.get("state", [])}


def _labels(situation: dict) -> tuple[set[str], set[str]]:
    return ({k for k, v in situation.items() if v == "예"}, {k for k, v in situation.items() if v == "아니오"})


def agent_usage() -> Dataset:
    base = ROOT / "domains" / "agent_usage"
    cands = _states(_toml(base / "knowledge.toml"))
    cases = []
    for d in _toml(base / "dispatches.toml")["dispatch"]:
        yes, no = _labels(d.get("situation", {}))
        if yes or no:
            cases.append(Case(d["id"], d["task"], yes, no))
    return Dataset("agent_usage", cands, cases)


def nonfiction_games() -> Dataset:
    base = ROOT / "domains" / "nonfiction_games"
    kn = _toml(base / "knowledge.toml")
    facts = {f["id"]: f["text"] for f in kn.get("fact", [])}
    cands = _states(kn)
    cases = []
    for g in _toml(base / "games.toml")["game"]:
        yes, no = _labels(g.get("situation", {}))
        text = " ".join(facts[f] for f in g["facts"])
        cases.append(Case(g["id"], text, yes, no))
    return Dataset("nonfiction_games", cands, cases)


def all_datasets() -> list[Dataset]:
    return [agent_usage(), nonfiction_games()]
