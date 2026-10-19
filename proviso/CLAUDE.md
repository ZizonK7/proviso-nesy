# proviso/ — 코어 (분야를 모른다)

지식 파일을 읽고(`schema.py`), 검사하고, 그래프로 그린다(`graph.py`). 명령은 `__main__.py`.
- `query.py`: LLM용 조회 (분야 목록, 목표 나무, 낱말 검색, 노드와 연결 설명). 원안의 `query_logic_graph`. `explain`은 가설의 시험 수단(자동 검사 이름, 판정 기록)도 보여 준다.
- `mcp_server.py`: MCP 도구 6개(list_domains, goal_tree, search, explain, audit, scorecard)를 내놓는 stdio 서버. 표준 라이브러리로 JSON-RPC 직접 구현. 읽기 전용 — 규칙 기록(원안의 `commit_logic_and_alignment`)은 다음 단계. `scorecard`는 분야의 `checks.py`를 불러 성적표를 만든다(CLI `check`와 같은 출력).
- `score.py`: **성적표**. 살아 있는 가설(규칙 포함)마다 (i) 자동 검사(분야 `checks.py`, 출처는 분야의 `SOURCE`)와 (ii) 판정 기록(`[[judgment]]`)을 출처별로 모으고, 판정이 난 가장 무거운 출처로 '종합'을 낸다. CLI `check`, MCP `scorecard`.
- `audit.py`: 엔진 점검(LLM 없이 그래프만으로 판단). **오류**(실패): 목표를 해치는데 대가로 받아들인 기록이 없는 것 — 사실의 해침은 항상 문제, 상태·가설의 해침은 그걸 낳는 규칙이 전부 이전 버전이면 지난 일로 본다. **경고**(실패 아님): 쪼개지 않은 개정(새 버전이 더한 조건이 없음; 숫자만 바뀜·합침·조건을 뺌을 표시), 시험 수단 없음(자동 검사도 판정도 없는 살아 있는 가설). CLI `audit`은 오류가 있을 때만 1로 끝난다.
- `search`는 단순 낱말 겹침이라 한국어 조사·활용형에 약하다. 질문 번역(원안의 로컬 통역기)이 붙으면 개선.

## 설계 결정: 규칙·가설은 "성적 붙은 가설" 하나 (2026-10-19)
- 이유: 사용자 목표는 Lean처럼 모든 주장에 증명(시험) 기록이 붙고, 틀리면 어느 단계가 틀렸는지 드러나는 것. 논리 자체는 잘 안 틀리고, 틀리는 건 조건을 흐리게 잡아서다 → 틀리면 쪼갠다.
- 상태는 둘: `hypothesis`(지금 것) / `retired`(이전 버전, 지우지 않고 `replaced_by`로 새 것을 가리킴). **`verified`는 없다.** 믿을 만한지는 성적표가 보여 준다.
- **표 이름 `rule`/`hypothesis`는 남겼다.** 규칙 = 방법(method)이 붙은 가설, 가설 = 문장(text)만 있는 가설. 두 표는 칸 모양만 다르고 상태·성적·개정·점검은 같다(`schema.CLAIMS`). 하나로 합치지 않은 까닭: 세 분야 지식 파일, `dispatches.toml`의 `predicted.rules`(규칙 id만 받음)·`review.hypotheses`, 그래프 모양, 쿼리 설명이 모두 표 이름에 기대고 있어서, 합치면 바뀌는 것은 많고 뜻은 같다.
- 목표·상태·사실·관찰은 가설이 아니다. 성적을 받지 않는다.
- 판정 출처와 무게(`schema.SOURCES` 순서, 앞이 무겁다): 사용자 실사용 > 실제 기록 재생 > 실측 > 자동 확인 > 시뮬레이션 > AI 판단. 성적표는 사용자 판정에 ★를 붙이고 맨 앞에 둔다.

## 규칙
- 여기에는 특정 분야(Flowlog 등)의 단어나 로직을 넣지 않는다. 분야 것은 `domains/<id>/`로. 성적표에 필요한 검사 함수와 출처는 부르는 쪽(CLI·MCP)이 분야에서 불러 넘긴다.
- 외부 패키지 없이 표준 라이브러리만 (TOML은 `tomllib`, 테스트는 `unittest`). 의존성을 늘리려면 사용자와 먼저 상의.
- 지식 파일 칸을 바꾸면 `REQUIRED`/`REFS`, `graph.EDGE`, 아래 표, 테스트를 같이 고친다.

## 지식 파일 칸 (domains/<id>/knowledge.toml)
| 종류 | 필수 | 선택 (→ 가리키는 종류) |
|---|---|---|
| goal 목표 | text | parent → goal |
| state 상태 | text | serves → goal, harms → goal, accepted_for → goal |
| fact 사실 | text, checked(날짜), source | harms → goal, accepted_for → goal, note |
| observation 관찰 | text, source("user" 등) | date |
| hypothesis 가설 | text, source | status(hypothesis/retired, 없으면 hypothesis), replaced_by → rule/hypothesis, conditions → state/fact/observation, evidence → observation/fact, against → observation/fact, harms → goal, accepted_for → goal, check(검사 이름 하나나 목록), test_plan, note |
| rule 규칙 (= 방법이 붙은 가설) | method, reason, status(hypothesis/retired), version | serves → goal, conditions → state/fact/observation, results → state, evidence → observation/fact, against → observation/fact, side_effects → hypothesis/state, exceptions → state, replaced_by → rule/hypothesis, check, test_plan, note |
| judgment 판정 기록 (노드 아님) | of → rule/hypothesis, source(user/replay/measured/auto/simulation/ai), verdict(지지/반박/일부), date, note | evidence → observation/fact |

- `against`(반대 근거): 그 규칙·가설과 어긋난 관찰. 지우지 않고 남겨서, 예외로 둘지 고칠지(새 버전) 쪼갤지의 근거로 쓴다 (2026-10-16, agent_usage 분야에서 추가).
- `check`: 분야 `checks.py`의 `CHECKS` 이름. 함수는 인자 없이, 또는 노드 id 하나를 받아 `(판정 문장, 자세히)`를 돌려준다(판정 문장은 '지지됨'/'반박됨'/'시험 전'/'불명'으로 시작). 노드 id를 받는 검사는 여러 규칙에 같이 건다(예: agent_usage의 '이 규칙을 쓴 예측이 맞았나').
- `test_plan`: 자동 검사를 못 붙이는 까닭이나 앞으로 시험할 방법. 있어도 '시험 수단 없음' 경고는 그대로 나고, 계획이 같이 보인다.
- `[[judgment]]`: 사람·기록 재생 등이 내린 판정. 지우지 않고 쌓는다. 예전의 `verified`는 이 판정으로 옮겼다(flowlog R_P1a).
- 규칙·가설을 고칠 때: 이전 것은 지우지 않고 `status="retired"` + `replaced_by`로 새 것을 가리킨다. 틀린 까닭이 조건이 흐려서면 **조건을 더해 쪼갠다**(새 버전이 더한 조건이 없으면 audit 경고). 더한 조건은 상태·사실 노드여야 한다(validate 오류). 이유가 틀렸으면 새 버전, 드문 바깥 상황이면 `exceptions`.
- 옛 칸 `superseded_by`(가설 표)는 없앴다 → `status="retired"` + `replaced_by`. 남아 있으면 validate 오류.
- 그래프 방향: 아래(조건·근거) → 규칙 → 위(목표). 조건·근거·예외는 그 노드에서 규칙으로 들어가는 선.
- 배경: [docs/knowledge-format-v0.md](../docs/knowledge-format-v0.md)
