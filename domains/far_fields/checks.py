"""먼 분야 조각 검사.

자동 검사(CHECKS)는 없다: 조각의 참거짓을 기계가 가를 재료가 없다. 성적은 AI 검토 판정([[judgment]] source="ai")뿐이다.
AUDIT은 양식만 본다 — 일반화 문장(text)에 분야 이름 낱말이 새어 들어갔으면 경고(조각에는 분야 이름을 쓰지 않는다, 루트 CLAUDE.md).
"""
from __future__ import annotations

import re

CHECKS: dict = {}

# 분야 이름에 흔히 붙지만 일반 낱말이기도 한 것 (새어 들어갔다고 보지 않는다)
_GENERIC = {"관리", "운영", "운전", "만들기", "작업", "정비", "재배", "수확", "설치", "시공", "조절", "판단", "제작",
            "손질", "다루기", "기르기", "쌓기", "현장", "시기", "보수", "점검", "통제", "진행", "조종", "처리", "연주",
            "채취", "사육", "훈련", "가공", "수리", "경주", "연기", "고르기", "구조", "지휘", "조리", "서비스", "이송",
            "포획", "운반", "생산", "탐지", "추적", "기술", "공정", "전통", "의례", "의식", "노래", "그리기", "칠하기",
            "세우기", "짓기", "뽑기", "잡이", "날리기", "물길", "투어", "가이드", "안내", "대량", "장거리", "수동"}


def _tokens(field: str) -> list[str]:
    words = re.split(r"[\s()·,/]+", field)
    out = []
    for w in words:
        w = re.sub(r"(와|과|의|을|를)$", "", w)
        if len(w) >= 2 and w not in _GENERIC:
            out.append(w)
    return out


def AUDIT(kn):
    warnings = []
    for n in kn.of("hypothesis"):
        field = n.data.get("field", "")
        leaked = [t for t in _tokens(field) if t in n.data.get("text", "")]
        if leaked:
            warnings.append(f"{n.id}: 일반화 문장에 분야 낱말이 있음 ({', '.join(leaked)} ← {field})")
    return [], warnings
