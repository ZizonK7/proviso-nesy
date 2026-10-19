# 2026-10-19 — 규칙·가설을 "성적 붙은 가설" 하나로 + 시간 구간 세 마디

에이전트: 구조 개편 하위 에이전트 (Opus 5.5, effort high). 하위 에이전트 호출: 없음.
커밋·push: 안 함 (메인이 한다).

## 구조 선택과 이유
- **표 이름 `rule`/`hypothesis`를 남기고 뜻만 맞췄다.** 둘 다 "성적 붙은 가설"(`schema.CLAIMS`)이고, 규칙은 방법(method)이 붙은 가설이다. 상태·개정·성적·점검은 두 표가 똑같이 받는다.
  - 상태는 `hypothesis` / `retired` 둘. `verified`는 validate 오류. 가설 표에도 `status`·`replaced_by`를 열었고, 옛 `superseded_by`(8건)는 `status = "retired"` + `replaced_by`로 옮겼다(남아 있으면 validate 오류).
  - 합치지 않은 까닭(덜 깨지는 쪽): `dispatches.toml`의 `predicted.rules`(규칙 id만, 테스트가 막음)·`review.hypotheses`, 그래프 모양(규칙 상자/가설 깃발), 쿼리 설명(`[규칙 R v2 …]`), 세 분야 지식 파일 179개 노드가 모두 표 이름에 기대고 있다. 합치면 바뀌는 것은 많고 뜻은 같다. 성적표·audit은 `kn.claims()`로 두 표를 한 번에 본다.
- **성적표 = 새 코어 모듈 `proviso/score.py`.** (i) 자동 검사: 노드의 `check`(이름 하나나 목록), 분야 `checks.py`의 `SOURCE`가 출처(agent_usage "measured", flowlog "simulation"). 검사 함수는 인자 없이 또는 노드 id를 받는다(여러 규칙에 같이 거는 검사용). (ii) 판정 기록: 새 최상위 표 `[[judgment]]`(of, source, verdict 지지/반박/일부, date, note, evidence). 출처 무게는 `schema.SOURCES` 순서: 사용자 실사용 > 실제 기록 재생 > 실측 > 자동 확인 > 시뮬레이션 > AI 판단. 출력은 출처별 줄, 사용자 판정에 ★, '종합'은 판정이 난 가장 무거운 출처의 것(다른 출처와 갈리면 표시), 맨 끝 한눈 표.
  - 판정 기록을 노드가 아니라 따로 둔 까닭: 판정은 그래프의 주장이 아니라 주장에 붙는 시험 기록이고, 앞으로 학습 고리(Episode 로그)가 계속 덧붙일 곳이라서.
- **agent_usage 규칙의 자동 검사 두 종류.** 주장 검사 = 가설 검사 함수를 그대로 건다(예: R_time_turns_v2 ← `turn_rate_non_web`). 쓴 예측 검사 = `used_minutes`·`used_turns`·`used_tokens`(노드 id를 받음): 그 규칙을 `predicted.rules`에 적은, 보내기 전에 적은 끝난 예측이 범위에 맞았나. 예측 자체가 세운 뒤의 시험이라 SEEN_UNTIL이 필요 없다(`checks.NO_CUT`). 보내기 전에 적지 않은 기록(d01–d06, d15b, d32b, d88)은 뺀다 — 그래서 R_time_turns_v2의 쓴 예측 분은 메인이 센 30/62가 아니라 30/61(d32b 빠짐).

## 한 일
- `proviso/schema.py`: `STATUS`(가설/이전 버전, `RULE_STATUS`는 옛 이름으로 남김), `CLAIMS`, `SOURCES`, `VERDICTS`, `alive()`, `check_names()`, `Knowledge.claims()`·`judgments_of()`·`judgments`. validate에 더한 것: 상태 검사(두 표 모두, verified면 안내), retired인데 `replaced_by` 없음, `superseded_by` 남음, `check` 모양, **새 버전이 더한 조건은 상태·사실 노드여야 함**(5번 할 일: 기존 validate는 참조가 있고 종류가 상태·사실·관찰인지만 봤다 → 더한 조건이 관찰이면 오류로 막음), 판정 기록 칸 검사. REFS: 가설 표에 `conditions`·`replaced_by`, 규칙의 `replaced_by`가 가설도 가리킬 수 있게.
- `proviso/score.py` (새): 위 성적표.
- `proviso/audit.py`: 오류(목표 해침, 그대로)와 경고 분리. 경고 = `unsplit_revisions`(새 버전이 더한 조건 없음; "숫자만 바뀜"·"합침"·"조건을 뺌" 표시) + `untested`(시험 수단 없음, `test_plan`이 있으면 같이 보임). 조건 칸이 양쪽 다 없는 가설 표 개정은 비교할 수 없어 "참고" 한 줄로만 센다. CLI는 오류가 있을 때만 1.
- `proviso/__main__.py`: `check` = 성적표(검사 이름이 checks.py에 없으면 1), `validate`가 판정 기록 수도 보여 줌, graph의 상태 이름.
- `proviso/query.py`: `explain`이 시험 수단(자동 검사 이름, 판정 기록 ★)을 보여 줌, 이전 버전 가설 표시. `proviso/graph.py`: 상태 이름만.
- `proviso/mcp_server.py`: 도구 `scorecard` 추가(분야 checks를 불러 성적표), `audit` 설명에 경고.
- `domains/agent_usage/dispatches.py`: 시간 구간 `ZONES`(잠깐 ≤10 · 다른 일 10–40 · 신경 끄기 >40), `zone()`, `zones_of()`(예측 범위 → 구간; 아래 끝이 경계값이면 위 구간부터, 한 값이면 '이상'), `in_range()`, `zone_verdict()`, `miss_split()`(분이 빗나간 기록 → 방향 × 속도/양/턴 예측 없음), `rescore()`, 새 비교표·집계. validate: `predicted.told`, `review.wrong`(규칙·가설·상태 id), `review.why`(조건 흐림/이유 틀림/바깥 상황), **p03 다음 기록부터 시간 구간이 빗나가면 wrong·why 필수**. 옛 `time_class`는 옛 등급으로만 검사(판정에 안 씀). `TIME_CLASSES`·`time_class()`는 없앰.
- `domains/agent_usage/dispatches.toml`: 맨 위 칸 설명(told, wrong, why, 옛 time_class)과 p04에 `told = "신경 끄기"` 한 줄만. 기존 예측·실측 숫자와 review.reason은 건드리지 않음(`git diff`로 확인: 주석과 그 한 줄뿐).
- `domains/agent_usage/checks.py`: `SOURCE = "measured"`, `used_minutes/turns/tokens`, `told_zone`, `NO_CUT`.
- `domains/agent_usage/knowledge.toml`: 가설 8건 `superseded_by` → `status/replaced_by`; verified 셋(R_time_turns_v2, R_tok_rate_check, R_models_doc) → hypothesis + note에 한 줄; 살아 있는 규칙 19개에 `check`; R_preflight·R_long_doc_save에 `test_plan`(못 붙이는 까닭); **R_say_numbers → R_say_numbers_v2**(구간으로 말하기, 걸치면 긴 쪽, `told` 적기; 조건 `S_zone_span`을 더해 나눔 → 쪼개지 않은 개정 경고 없음; 검사 `told_zone`); 새 상태 `S_zone_span`(적지 않고 dispatches.py가 계산); 머리 주석.
- `domains/flowlog/knowledge.toml`: R_P1a verified → hypothesis, 근거를 판정 둘로(사용자 '좋다' — v1의 빈도 순서 부분, 재생 98%). R_P1b에 재생 판정 '일부'(1등 튀기 13% 없앰 vs 새 제목 적중 2%p 낮음)와 `test_plan`. `checks.py`에 `SOURCE = "simulation"`.
- `domains/music_player/knowledge.toml`: R_M1b에 시뮬레이션 판정 '일부'(F_dup_window의 대기열 시뮬레이션: 같은 곡 재등장 없음 = 이유 부분; 흐름은 실사용 전)와 `test_plan`, R_S1에 `test_plan`.
- 테스트: `tests/test_score.py`(새, 상태·판정·성적표·audit 경고 15개), `tests/test_agent_usage_domain.py`(구간·다시 채점·wrong/why 검증·쓴 예측 검사·verified 없음·예측 규칙마다 검사나 test_plan), `tests/test_query.py`(MCP 도구 여섯이 세 분야에서 돔, scorecard·explain 내용).
- 문서: 루트 `CLAUDE.md`(설계 결정 한 줄 + 규칙 칸·audit·지금 상태·다음 할 일·하위 에이전트 운영의 말하기), `proviso/CLAUDE.md`(설계 결정 절, 칸 표, judgment), `domains/CLAUDE.md`, `domains/agent_usage/CLAUDE.md`(고리 절차: told·wrong·why·쪼갤 때 조건, 방식 4, **규칙 요약에 성적**, 개편 요약), `domains/flowlog/CLAUDE.md`, `domains/music_player/CLAUDE.md`, `docs/knowledge-format-v0.md` 5절(바뀐 칸, 원안 대비), `docs/AGENT-LOG.md` 정의(시간 구간, 옛 등급), `docs/CLAUDE.md`(5절 안내 한 마디 — 지시서 범위 밖이지만 문서 목록 설명이라 고침).

## 새 시간 구간으로 다시 채점 (분 숫자로, 기록 파일은 그대로)
분 범위가 있는 끝난 기록 118건. 분 범위가 없는 6건(dR1, dR2, dR3, dR4, d14, d16)은 판정에서 뺐다. 끝나지 않은 5건(d15 멈춤, 끝났는지 모르는 d78·d79·d80·p04)은 원래대로 빠진다. 129 = 118 + 6 + 5.

| | 건수 | 맞음 | 낮게 잡음 | 높게 잡음 |
|---|--:|--:|--:|--:|
| 전체 | 118 | 102 | 4 | 12 |
| 보내기 전에 적은 것만 | 109 | 95 | 2 | 12 |
| 예측이 '잠깐' 하나 | 12 | 11 | 1 | 0 |
| 예측이 '다른 일' 하나 | 34 | 27 | 3 | 4 |
| 예측이 '신경 끄기' 하나 | 38 | 31 | 0 | 7 |
| 걸침(두 구간 이상) | 34 | 33 | 0 | 1 |

- 걸침 34건의 실제 낙하: **짧은 쪽 18, 긴 쪽 15, 밖 1**(d08: 다른 일/신경 끄기 → 잠깐). 긴 쪽으로 말하는 규칙(R_say_numbers_v2)을 지난 기록에 대면 15/34만 말한 구간이 맞는다.
- 걸침은 '잠깐/다른 일' 12건, '다른 일/신경 끄기' 22건. 세 구간에 걸친 예측은 없다.
- 비교(참고): 옛 등급(S/M/L/XL)으로는 124건 중 맞음 92·낮게 8·높게 24였다. 구간이 넓어 맞음이 많아진 것이지 예측이 좋아진 것은 아니다 — 분 범위 그대로의 적중은 **49/118**.
- `predicted.told`가 있는 끝난 기록은 아직 0건(p04가 첫 기록, 끝났는지 모름).

## 분 빗나감의 양/속도 갈래 (기계적으로 계산)
분이 예측 범위를 벗어난 69건. 턴이 범위 안이었으면 속도(분당 턴) 조각 탓, 밖이었으면 양(턴 수) 조각 탓.

| 분 | 속도 | 양 | 턴 예측 없음 | 계 |
|---|--:|--:|--:|--:|
| 실제가 범위 아래 | 19 | 30 | 1 | 50 |
| 실제가 범위 위 | 4 | 8 | 7 | 19 |

- 양 38건 중 35건은 턴도 분과 같은 방향으로 빗나갔다. 반대 방향 3건(d19, d69c, d91)은 속도도 틀린 것.
- 읽기: 빗나감의 주인은 **턴 수 잡기**(대개 R_turns_analogy_v2: 쓴 예측 턴 34/54)이고 방향은 크게 잡는 쪽이다. 분당 턴 띠(R_time_turns_v2 주장 46/56)는 상대적으로 덜 틀린다. 다음 정리에서 먼저 쪼갤 곳은 턴 수 잡기다. 턴 예측이 없는 8건은 대부분 배치 1–4(d01–d12b).

## 성적표 요약 (agent_usage 살아 있는 규칙, `python -m proviso check agent_usage`)
| 규칙 | 주장 검사 | 쓴 예측 |
|---|---|---|
| R_time_turns_v2 | 분당 턴 띠 46/56 | 분 30/61 |
| R_turns_analogy_v2 | – | 턴 34/54, 분 26/54 |
| R_tok_rate_check | 분당 토큰 25/29 | 0건 |
| R_models_doc | 분당 턴 3/3 | 0건 |
| R_tok_short_v5 | – | 토큰 19/22 |
| R_resume_ctx_v2 | – | 토큰 15/19 |
| R_research | 시험 전 | 턴 8/15 |
| R_verify_once | – | 분 6/9 |
| R_third_pass | – | 턴 3/6, 분 4/6 |
| R_variants | – | 턴 1/2, 분 2/2 |
| 시험 전 (쓴 예측 0건, 주장 검사도 시험 전) | | R_tok_long_v5, R_verify_ci, R_verify_laps, R_doc_work_v2, R_fixed_input_v2, R_models_reasoning, R_models_tool, R_integration, R_build_tools, R_say_numbers_v2 |
| 시험 수단 없음 | | R_preflight, R_long_doc_save (못 붙이는 까닭을 `test_plan`에) |

자동 검사를 못 붙인 규칙과 까닭: R_preflight — 점검 넷을 했는지와 막은 손실을 적는 칸이 기록에 없다. R_long_doc_save — 이어 쓰기를 지시했는지 적는 칸이 없고, d03 뒤 반례(S_unsaved_doc=예)도 없다.

## 경고 목록 (audit, 실패 아님)
쪼개지 않은 개정 13건 — 고치지 않았다(다음 정리에서 처리):
- agent_usage 12: R_tok_v2 → R_tok_v3 (숫자만 바뀜), R_tok_short → R_tok_short_v5, R_resume_ctx → R_resume_ctx_v2, R_turns_analogy → R_turns_analogy_v2 (합침), R_time_turns → R_time_turns_v2, R_verify_v1 → R_verify_other, R_verify_other → R_verify_once, R_spec_fixed → R_turns_analogy_v2 (합침, 조건 S_spec_fixed를 뺌), R_fixed_input → R_fixed_input_v2, R_other_models → R_other_models_v2, R_other_models_v2 → R_other_models_v3, R_other_models_v3 → R_models_doc.
  - "숫자만 바뀜"은 방법 문장에서 숫자·범위 기호를 지운 뼈대가 같을 때만 붙는다(R_tok_v2→v3 하나). R_time_turns_v2·R_fixed_input_v2·R_other_models_v2/v3처럼 **방법 문장 안에서 작업 모양으로 갈랐지만 그 모양을 조건(상태)으로 올리지 않은** 개정이 대부분이다 — 사용자가 말한 "흐리게 잡은 논리"가 이 모양이다.
- music_player 1: R_M1 → R_M1b (메인 판단 필요 1).
- 참고(경고 아님): 가설 표의 개정 9건은 조건 칸이 양쪽 다 없어(조건이 문장과 검사 코드에만 있음) 쪼갰는지 엔진이 못 본다.

시험 수단 없음 4건: flowlog H_slot_count, music_player R_S1(계획: 폰 실사용 판정), agent_usage R_preflight, R_long_doc_save.

## 확인한 것 (어떻게)
- `for d in flowlog music_player agent_usage; do PYTHONIOENCODING=utf-8 python -m proviso validate $d; PYTHONIOENCODING=utf-8 python -m proviso audit $d; PYTHONIOENCODING=utf-8 python -m proviso check $d; done` → validate 셋 "문제 없음"(exit 0), audit 셋 "오류 없음"(exit 0; 경고 1·2·14), check 셋 exit 0.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.dispatches` → "기록 문제 없음 (129건)", 위 다시 채점 표 출력, exit 0.
- `python -m unittest discover -s tests -t .` → 67개 통과(전 44개).
- MCP: 테스트 `test_every_tool_runs_on_every_domain`이 도구 여섯(list_domains, goal_tree, search, explain, audit, scorecard)을 세 분야에서 `handle()`로 부른다. stdio로도: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"scorecard","arguments":{"domain":"music_player"}}}' | python -m proviso.mcp_server` → 성적표 텍스트가 든 JSON-RPC 답.
- `python -m proviso graph <분야>` 셋 → out/에 html 생성(그림 자체는 브라우저로 보지 않았다).
- `git diff domains/agent_usage/dispatches.toml` → 주석 줄과 p04의 `told` 한 줄뿐.

## 확인 못 한 것
- 그래프 html을 브라우저로 열어 보지 않았다(가설 표에 조건 선이 생길 수 있게 됐지만 지금 그런 노드는 없다).
- 실제 Claude Code에 MCP 서버를 등록해 `scorecard`를 불러 보지 않았다(stdio 한 줄과 `handle()` 테스트만).
- `experiments/run_body_v0.py`는 돌리지 않았다(외부 `claude -p` 호출). 쓰는 도구 넷의 이름과 입력은 그대로라 영향은 없을 것으로 본다 — 확인 못 함.

## 알려진 문제
- `used_*` 검사는 예측 하나에 규칙 여럿이 섞여 있어서, 빗나감을 그 규칙 탓으로 볼 수 없다. 탓을 가르는 것은 앞으로의 `review.wrong`이다(지금은 0건).
- `zones_of`는 아래 끝이 경계값(10, 40)과 같으면 위 구간부터 센다([10, 20] → 다른 일만). 이 해석 때문에 p04 [40, 65]는 걸침이 아니라 '신경 끄기' 하나다.
- review.wrong 필수 조건은 **예측 구간 밖**일 때다. 걸친 예측이 짧은 쪽에 떨어지면(말한 긴 쪽은 틀렸지만) 필수가 아니다.
- `_skeleton`(숫자만 바뀜 판정)은 숫자·범위 기호와 '만/배/분/턴'을 지워 비교하는 거친 방법이다. 경고 자체는 조건 집합으로 내고, 이건 표시만 한다.
- README.md(범위 밖)의 명령 설명 두 줄("check = 가설 확인", "audit = 목표를 해치는데 받아들인 기록이 없는 것")은 옛 설명 그대로다.
- `AGENT-LOG.md` 배치 1 표의 "(S)"는 옛 등급 그대로 두었다(정의에 옛 등급이라고 적음).

## 메인 판단 필요
1. **R_M1 → R_M1b 경고**: 조건은 그대로고 방법을 바꿨다(부작용 S_dup_possible을 없앤 개정). "이유 틀림 → 새 버전"은 조건을 안 더해도 정당한데, 엔진은 지금 그걸 가르지 못한다. 제안: 새 버전에 `why`(review.why와 같은 세 값)를 달게 하고, "이유 틀림"이면서 이유 문장이 바뀌었으면 경고를 끈다. 사용자에게 물을지, 이 경고를 그대로 둘지.
2. **걸칠 때 긴 쪽**: 지난 걸친 예측 34건은 짧은 쪽 18·긴 쪽 15. 긴 쪽으로 말하면 절반 넘게 한 구간 길게 말하게 된다. 규칙은 사용자 결정대로 넣었고, 이유 칸의 "짧게 말했다가 늦으면 기다리던 시간이 버려진다"는 AI 해석(사용자 확인 전)이라고 적었다. 이 숫자를 사용자에게 보여 줄지.
3. **wrong·why 필수 조건**: 지금은 '예측 구간 밖'. '말한 구간(told)과 다름'까지 넓힐지(걸친 예측이 짧은 쪽에 떨어진 경우도 돌아보게 됨).
4. **내가 판정 기록으로 옮긴 읽기 둘**: flowlog R_P1a의 사용자 판정 '지지'(note의 "빈도 순서 부분은 v1 실사용에서 '좋다'" — v2 자체 평가는 아님), music_player R_M1b의 시뮬레이션 판정 '일부'(F_dup_window에 적힌 시뮬레이션을 이유 부분의 시험으로 읽음). 둘 다 기존 글에서 옮겼지만 판정 칸에 놓은 것은 내 해석이다.
5. **가설 표에 조건 칸 채우기**: 이제 스키마가 받는다. 채우면 가설 표 개정 9건도 "쪼갰나"를 엔진이 본다. 다음 정리 범위인지.
6. **README.md**(범위 밖) 명령 설명 두 줄 갱신.

## 다음 작업자에게
- 예측을 보낼 때: `predicted.minutes`(범위)와 `predicted.told`(걸치면 긴 쪽)를 적고 `time_class`는 더 적지 않는다. 끝나서 구간이 빗나가면 `review.wrong`·`review.why`를 적어야 `dispatches` 검증이 통과한다(p04부터).
- 규칙을 고칠 때: 새 버전의 `conditions`에 더한 상태가 없으면 audit 경고. 가장 먼저 쪼갤 곳은 턴 수 잡기(양 탓 38/69).
- 성적은 `python -m proviso check <분야>` 맨 끝 한눈 표, MCP는 `scorecard`. 같은 검사 기록 목록이 두 번 나오면 두 번째는 "(기록 목록은 위 …에)"로 줄인다.
