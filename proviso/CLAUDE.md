# proviso/ — 코어 (분야를 모른다)

지식 파일을 읽고(`schema.py`), 검사하고, 그래프로 그린다(`graph.py`). 명령은 `__main__.py`.
- `query.py`: LLM용 조회 (분야 목록, 목표 나무, 낱말 검색, 노드와 연결 설명). 원안의 `query_logic_graph`.
- `mcp_server.py`: `query.py`를 MCP 도구 4개(list_domains, goal_tree, search, explain)로 내놓는 stdio 서버. 표준 라이브러리로 JSON-RPC 직접 구현. 읽기 전용 — 규칙 기록(원안의 `commit_logic_and_alignment`)은 다음 단계.
- `audit.py`: 엔진 점검(LLM 없이 그래프만으로 판단). 지금은 "목표를 해치는데 대가로 받아들인 기록이 없는 것". 사실의 해침은 항상 문제, 상태·가설의 해침은 그걸 낳는 규칙이 전부 이전 버전이면 지난 일로 본다. CLI `audit`, MCP 도구 `audit`.
- `search`는 단순 낱말 겹침이라 한국어 조사·활용형에 약하다. 질문 번역(원안의 로컬 통역기)이 붙으면 개선.

## 규칙
- 여기에는 특정 분야(Flowlog 등)의 단어나 로직을 넣지 않는다. 분야 것은 `domains/<id>/`로.
- 외부 패키지 없이 표준 라이브러리만 (TOML은 `tomllib`, 테스트는 `unittest`). 의존성을 늘리려면 사용자와 먼저 상의.
- 지식 파일 칸을 바꾸면 `REQUIRED`/`REFS`, `graph.EDGE`, 아래 표, 테스트를 같이 고친다.

## 지식 파일 칸 (domains/<id>/knowledge.toml)
| 종류 | 필수 | 선택 (→ 가리키는 종류) |
|---|---|---|
| goal 목표 | text | parent → goal |
| state 상태 | text | serves → goal, harms → goal, accepted_for → goal |
| fact 사실 | text, checked(날짜), source | harms → goal, accepted_for → goal, note |
| observation 관찰 | text, source("user" 등) | date |
| hypothesis 가설 | text, source | harms → goal, accepted_for → goal, check(분야 검사 함수 이름) |
| rule 규칙 | method, reason, status(hypothesis/verified/retired), version | serves → goal, conditions → state/fact/observation, results → state, evidence → observation/fact, side_effects → hypothesis/state, exceptions → state, replaced_by → rule, note |

- 규칙을 고칠 때: 이전 규칙은 지우지 않고 `status="retired"` + `replaced_by`로 새 규칙을 가리킨다.
- 그래프 방향: 아래(조건·근거) → 규칙 → 위(목표). 조건·근거·예외는 그 노드에서 규칙으로 들어가는 선.
- 배경: [docs/knowledge-format-v0.md](../docs/knowledge-format-v0.md)
