# docs/ — 설계 문서

- `purpose-2026-11-05.md`: 목적 변경 기록(피드백으로) — 원안 대비 무엇을 왜 바꿨고 무엇이 그대로인지. 본체는 [../feedback/CLAUDE.md](../feedback/CLAUDE.md).
- `agent-usage-research-ideas.md`: 자원 예측·사례·정돈된 피드백의 효과를 비교할 논문 아이디어(아직 미검증). 현재 EDA 목적은 계산기에 쓸 이론적 분류 확인이며, 논문 비교는 추후 검토한다.
- `sela-paper-draft.md`: 사용자가 쓴 원안 논문(2026-10-14 받은 그대로). 수정 금지 — 철학과 출발점의 기준.
- `rule-drafts-v0.md`: 코드 전에 손으로 써 본 규칙 4개(분야 A, ai_company 기록 기반). 양식 검증용. 사용자 검토 결과를 여기에 반영.
- `knowledge-format-v0.md`: 정보 층위와 분야 A 조건 단어장, 개정된 규칙, 그리고 사용자가 논리를 쌓은 과정(3절). "선호" 층은 3-4절에서 폐지됐다. 5절: 규칙·가설 통합(검증됨 폐지, 성적표, 틀리면 쪼갠다, 2026-10-19). 현재 칸 정의는 [proviso/CLAUDE.md](../proviso/CLAUDE.md).
- `pieces-v0.md`: 논리 조각(P1~P6)과 상황별 대 보기. 조각 문장의 최신본.
- `dispatch.md`: 하위 에이전트 보내기의 자세한 절차(역할, 모델, 조사, 지시서, 끝난 뒤 기록). 순서는 루트 CLAUDE.md의 체크리스트. 2026-11-02 루트에서 옮김.
- `history.md`: 루트 CLAUDE.md에서 옮긴 지난 경위(옮기기 전 글 그대로). CLAUDE.md는 지금 기준만 둔다(2026-11-02 사용자 결정). 분야 경위는 그 폴더 `history.md`.
- `AGENT-LOG.md`: 하위 에이전트 배치별 모델·effort·품질과 가져온 교훈. 예측과 실측은 `domains/agent_usage/dispatches.toml`. 메인이 쓴다.
- `worklog/`: 하위 에이전트 작업 보고서(작업마다 하나). 양식은 그 폴더 CLAUDE.md.
- `worklog/2026-11-06-spec-fixed-regression.md`: 설계 사전 고정(`S_spec_fixed`)과 턴 수의 탐색 회귀. 표본·보정·민감도·한계·주 분석 재현 코드. 무작위 개입 실험 결과와 구분한다.
- `worklog/2026-11-06-resumed-regression.md`: 이어 보내기(`C_turns_resumed_v2`)와 턴 수의 탐색 회귀. 분석 계획을 결과 전에 고정, 주 분석 ×0.456(0.33–0.64) — 방향 지지, 크기는 계산기 범위와 겨우 겹침. 주 분석 재현 코드.
- `agent-usage-calculator-explainer.html` · `.pdf`: agent_usage 계산기 해설서(구조·기록 데이터·시험 장치·개입 지점, 논문 문체, A4 17쪽) — 2026-11-05 스냅숏이라 숫자는 그날 것(p237). HTML이 원본, PDF는 Chromium 렌더.
- `experiments/`: 본체 실험 보고서. 스크립트가 생성하고, "사용자 판정" 칸은 사용자가 채운다.
- 설계 결정이 원안과 달라지면 원안을 고치지 말고 여기에 별도 문서(예: `design-decisions.md`)로 "무엇을, 왜 바꿨는지" 기록.
