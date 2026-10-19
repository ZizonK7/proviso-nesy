# docs/ — 설계 문서

- `sela-paper-draft.md`: 사용자가 쓴 원안 논문(2026-10-14 받은 그대로). 수정 금지 — 철학과 출발점의 기준.
- `rule-drafts-v0.md`: 코드 전에 손으로 써 본 규칙 4개(분야 A, ai_company 기록 기반). 양식 검증용. 사용자 검토 결과를 여기에 반영.
- `knowledge-format-v0.md`: 정보 층위와 분야 A 조건 단어장, 개정된 규칙, 그리고 사용자가 논리를 쌓은 과정(3절). "선호" 층은 3-4절에서 폐지됐다. 현재 칸 정의는 [proviso/CLAUDE.md](../proviso/CLAUDE.md).
- `pieces-v0.md`: 논리 조각(P1~P6)과 상황별 대 보기. 조각 문장의 최신본.
- `nonfiction-games-v0.md`: 비문학(책·논문·기록) 기반 게임 사례 조사(2026-10-19). 확인 칸(✔ 원문 / △ 검색 요약)을 지킨다 — △를 ✔로 올리려면 원문을 직접 본다. 조각을 뽑기 전 단계의 사례 모음.
- `AGENT-LOG.md`: 하위 에이전트 배치별 모델·effort·품질과 가져온 교훈. 예측과 실측은 `domains/agent_usage/dispatches.toml`. 메인이 쓴다.
- `worklog/`: 하위 에이전트 작업 보고서(작업마다 하나). 양식은 그 폴더 CLAUDE.md.
- `experiments/`: 본체 실험 보고서. 스크립트가 생성하고, "사용자 판정" 칸은 사용자가 채운다.
- 설계 결정이 원안과 달라지면 원안을 고치지 말고 여기에 별도 문서(예: `design-decisions.md`)로 "무엇을, 왜 바꿨는지" 기록.
