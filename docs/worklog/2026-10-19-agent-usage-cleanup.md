# 2026-10-19 — agent_usage 논리집 전체 정리

에이전트: agent_usage 정리 (Opus 5.5, effort high). 하위 에이전트 호출: 없음.
커밋·push: 안 함 (메인이 검토 후).

## 한 일
- `python -m proviso check agent_usage`·`python -m domains.agent_usage.dispatches`로 가설 17개 전수 판정, 기록 d01–d94의 `review.reason`을 훑어 반복된 교훈을 찾고, 규칙 30개의 겹침·안 씀·물린 것을 봤다. 일회용 분석 스크립트는 스크래치패드에만 두었다.
- `domains/agent_usage/knowledge.toml`: 가설 결정(아래 표1), 규칙 결정(표2). 새 상태 셋(S_fix_existing·S_open_seams·S_build_tools), 새 관찰 13개, 새 가설 7개, 새 규칙 11개(개정판 포함). F_setup 문장을 지금 기록에 맞게 고침. 가설 24·규칙 41(살아 있는 것 22, verified 3).
- `domains/agent_usage/checks.py`: 새 검사 7개(SEEN_UNTIL = d94), 검사 고침 2개(render_turn_rate에 S_long_lap=아니오, research_cap에 S_web=예), 빗댄 기록을 읽는 `_analog`(`predicted.analog` → 없으면 사후에 읽은 `PAST_ANALOG`, SEEN_UNTIL 앞이라 보여 주기만), 뒤엉켜 있던 SEEN_UNTIL 주석 정리.
- `domains/agent_usage/dispatches.toml`: **예측·실측 숫자는 건드리지 않았다.** 새 상태 셋을 과거 17곳에 사후로 채우고(모두 SEEN_UNTIL 앞이라 판정에 들지 않음) 맨 위 주석에 그 사실, `predicted.analog` 칸 설명, 돌아보기 글에 섞인 batman 쪽 기록 이름(d88 'd51b'=d58, d89 'd52b'=d64, d94 'd64'=d68)을 적었다. p01·p02·p03은 건드리지 않았다.
- `domains/agent_usage/CLAUDE.md`: "지금 쓰는 규칙 요약"(살아 있는 규칙만, 모양별 조건 → 숫자 → 근거 건수) 새로 넣음. 현재 상태를 이번 정리로 새로 쓰고, 이전 상태 일곱 단락을 "지난 고리" 한 줄씩(아홉 줄)으로 줄임. 이전 상태에 흩어져 있던 절차 교훈(규칙은 knowledge.toml에서 읽기, predicted.rules에 가설 id 금지, 재시작 실행은 기록 안 함, superseded_by)은 "고리"로 옮김.
- 루트 `CLAUDE.md`: "지금 상태"의 agent_usage 줄, "다음 할 일" 5번.
- `tests/test_agent_usage_domain.py`: 테스트 6개 추가(새 검사의 SEEN_UNTIL, 새 검사가 세울 때 본 기록과 맞는지, 렌더 검사가 짧은 바퀴만 보는지, research_cap이 웹 조사만 보는지, analog 찾기, 살아 있는 규칙에 '기록 없음' 이유가 없고 물린 규칙은 replaced_by가 있는지).

### 표1. 가설 결정
| id | 정리 전 판정 | 결정 | 이유 한 줄 |
|---|---|---|---|
| H_turns_over | 지지 1/1 | 그대로 | 시험 1건, 검사가 물린 v1만 봐서 더 시험되지 않음. 올릴 규칙은 v2가 이미 대신 |
| H_cancel | 시험 전 | 보류 | 조건(예상 800턴+)이 v2 뒤 사라짐(최대 d94 500–750). 참고: 300턴+ 16건 중 상쇄는 d15b뿐 |
| H_mid_notes | 반박 1/5 | 개정 → H_mid_notes2 | 이유가 틀림: 도중 지시는 몇~20분만 더함(기록 여섯 모두 상한의 1.05배 안). [dispatch.mid_notes]는 끝내 안 적혔다 |
| H_tok_rate_long | 지지 25/29 | 올림 → R_tok_rate_check ✔ | 시험 29건, 이어진 규칙이 없어 새로 만듦 |
| H_turn_rate_shape | 지지 44/53(정리 중 p02로 44/54) | 그대로 | 지시서는 '반박'이라 했지만 d94까지 83 %로 넘어섬. R_time_turns_v2 ✔ 유지 |
| H_research_cap | 시험 전 | 검사 고침 + 보류 | 배치 15 뒤 웹 조사를 안 보냄. 검사가 문장의 '웹 조사'를 빠뜨려 p02(웹 아님)를 잴 뻔함 → S_web=예 |
| H_sonnet_max_rate | 시험 전 | 보류 | d43 뒤 Sonnet 여섯 번 모두 문서·고정 입력(쓰임새가 조건을 막음, 방식 6) |
| H_render_rate | 반박 0/3 | 검사 고침 | 문장의 '렌더 한 회 1–2분' = S_long_lap=아니오를 검사가 빠뜨림(d69 일부, d69c 예). 남은 d69b 0/1 — 한 건이라 개정 보류 |
| H_check_loop3 | 반박 1/6 | 개정 → H_turn_rate_shape로 대체 | 이유가 틀림: 큰 구현의 긴 바퀴는 분당 4.4–5.9(일반 띠). 바퀴는 분에 더함(R_verify_laps) |
| H_given_design_rate2 | 시험 전 | 보류 | d73 뒤 조건에 맞는 기록 0/21. 작은 적힌 고침은 베타 배치에서만 나옴 — 드물지만 다시 올 조건 |
| H_model_mult_shape | 지지 3/3 | 올림 → R_models_doc ✔ | 약속대로 문서 칸을 verified. 시험한 것은 분당 턴 |
| 대체됨 6개(H_check_loop, H_tok_per_min, H_tok_per_min_long, H_turn_rate, H_check_loop2, H_given_design_rate) | 대체됨 | 그대로 | 이미 다음 가설로 넘어감 |
| H_mid_notes2 (새) | – | 새 가설 | 도중 지시를 받아도 예측 상한 ×1.25 안 (맞춰 본 6/7, d01만 ✗) |
| H_sonnet_floor (새) | – | 새 가설 | 'Sonnet 최소 분' 두 번(d37b ×6.3, d91 ×12.8). 첫 회차 고정 입력 13–28분 (맞춰 본 7/7) |
| H_fixed_input_opus (새) | – | 새 가설 | R_fixed_input 숫자가 여섯 건 연속 아래. 1–7분·5–20턴 (맞춰 본 8/8) |
| H_ctx_fix (새) | – | 새 가설 | R_tok_long 밖 7건 중 6건이 고치는 작업. 턴당 13–25만 (맞춰 본 8/8) |
| H_settled_integration (새) | – | 새 가설 | 다 판정한 통합 ×0.65·×0.71(d39b·d94), 열린 면 남은 통합 ×2.6(d68) |
| H_build_tools (새) | – | 새 가설 | 도구를 직접 만든 월드 에이전트 둘이 d61의 분 ×1.5(d62·d87) |
| H_doc_spec_minutes (새) | – | 새 가설 | R_doc_work를 쓴 세 번이 모두 아래. 설계가 정해진 문서 18–45분 (맞춰 본 4/4) |

요약: 올림 2, 개정 2, 검사 고침 2, 보류 4(H_research_cap은 검사 고침과 겹쳐 셈), 그대로 8(대체됨 6 포함), 새 가설 7(H_mid_notes의 개정판 1, 개정한 규칙의 시험 4, 새 규칙의 시험 2). 예외로 처리한 것은 없다.

### 표2. 규칙 상태가 바뀐 것
| id | 정리 전 | 결정 | 이유 한 줄 |
|---|---|---|---|
| R_tok_long | 가설 | 개정 → R_tok_long_v5 | 밖 7/28 중 6건이 고치는 작업(13.3–23.8만): '길수록 쌓인다'가 틀리고 읽는 방식이 정함 |
| R_fixed_input | 가설 | 개정 → R_fixed_input_v2 | d36 뒤 Opus 여섯 건 모두 아래. 여섯 사건짜리 값을 바닥으로 씀 |
| R_doc_work | 가설 | 개정 → R_doc_work_v2 | 쓴 세 번 모두 아래. 근거가 설계부터 한 글 한 건뿐(쓰던 범위) |
| R_verify_loop | 가설 | 개정 → R_verify_laps | 돌아보기 여섯이 '배수 말고 바퀴를 세라'(d68·d69·d69c·d70·d71·d73) |
| R_other_models_v3 | 가설 | 나눔 → R_models_doc ✔ / R_models_reasoning / R_models_tool | 모양별로 근거 수가 달라 셋으로(방식 3). 순수 추론 칸은 배수 대신 실측 범위로 개정 |
| R_spec_fixed | 가설 | 모음 → R_turns_analogy_v2 | 틀려서가 아니라 v2 첫 갈래와 같은 말(겹침) |
| R_full_brief | 가설 | 모음 → R_turns_analogy_v2 | d26 뒤 90건 모두 S_full_brief=예라 조건이 아무것도 안 가름 |
| R_impl_hour | 가설 | 모음 → R_turns_analogy_v2 | 조건이 예측 자체라 순환, 반대 근거 있음, d11 뒤 안 씀 |
| R_tok_rate_check | – | 새로, verified | H_tok_rate_long 25/29 |
| R_integration | – | 새로, 가설 | 찾을 것의 수가 통합의 분을 정함(근거 3) |
| R_build_tools | – | 새로, 가설 | 도구 만들기 ×1.3–1.7(근거 2) |
| R_preflight | – | 새로, 가설 | 보내기 전에 막을 수 있던 손실 다섯(d73·d89·d90·d92) |
| R_other_models_v2 | 물림 | 그대로(replaced_by를 목록으로만 고침) | 형식 맞춤 |
| R_turns_analogy_v2, R_time_turns_v2, R_research, R_variants, R_verify_once, R_verify_ci | – | 그대로, 메모만 | 새 근거·쓰임 횟수·적중률을 note에 |

가장 많이 쓴 R_turns_analogy_v2는 시험할 가설이 없어 그대로 가설이다(d29 뒤 이 규칙을 쓴 Opus 예측 40건의 분 범위 적중 21건). 시험하려면 `predicted.analog`가 쌓여야 한다.

### 정리하며 본 것 (작업 중 메모)
- 정리 전 `check`: 지지 4(H_turns_over 1/1, H_tok_rate_long 25/29, H_turn_rate_shape 44/53, H_model_mult_shape 3/3), 반박 3(H_mid_notes 1/5, H_render_rate 0/3, H_check_loop3 1/6), 시험 전 4(H_cancel, H_research_cap, H_sonnet_max_rate, H_given_design_rate2), 대체됨 6.
- H_turn_rate_shape는 지시서가 '반박'이라 했지만 지금은 지지(44/53 = 83 %). 배치 29 때 33/42(79 %)였다가 그 뒤 11건 중 11건이 맞아 넘어섰다. 빗나간 9건 중 7건이 설계·글이 다 적힌 편집(분당 6.6–8.1턴).
- 분 범위 쏠림: d29–d76 67건은 범위 안 32·아래 28·위 7(실측/가운데 중앙값 0.80), d77–d94 14건은 안 8·아래 3·위 3(0.90). 예전의 '높게 잡는' 버릇은 최근 배치에서 거의 사라졌다 → 보정 규칙은 만들지 않고 관찰로만.
- R_turns_analogy_v2를 쓴 Opus 예측(d29 이후 40건)의 분 범위 적중은 21/40(±10 % 허용 26/40). 이 규칙을 시험할 가설이 없다 → 앞으로 `predicted.analog`(빗댄 기록 id)를 적게 해 배수 가설을 시험할 수 있게 한다.
- R_tok_long(턴당 24–46만): d16 뒤 150턴 넘는 Opus 첫 회차 28건 중 21건 안. 빗나간 7건 중 6건(d44–d47·d72·d73)은 기존 코드를 나눠 읽으며 고치는 작업(13.3–23.8만), 1건(d30 시안 넷, 22.7만)은 바로 아래 → 개정 대상.
- R_fixed_input(15–30턴, 5–10분): d36 뒤 Opus 고정 입력 6건이 모두 범위 아래(5–11턴, 1.5–3.8분). 숫자가 여섯 사건짜리(d18) 값이었다 → 개정 대상.
- R_doc_work(새로 쓰기 50–70분): 쓴 세 번(d31·d32·d51)이 모두 아래(19.9–38.3분) → 개정 대상.
- S_full_brief는 d26 뒤 90건 모두 '예'(상태가 아무것도 가르지 않음), S_impl_hour·S_ci_*·S_unsaved_doc는 d26 뒤 한 번도 안 씀.
- d94의 review가 말하는 'd64'는 이 파일 id로는 d68(통합)이다(분 90.6/128 = 0.71). d88의 'd51b'는 d58, d89의 'd52b'는 d64. 배치 쪽 이름이 섞였다.
- 정리 중에 메인이 p02(실측)·p03(예측)을 덧붙였다. p02는 d94 뒤라 H_turn_rate_shape의 시험에 들어가 44/54(81 %, 여전히 지지). p03 예측은 이번에 물린 R_fixed_input을 쓴다 — 다음 예측부터 R_fixed_input_v2.
- H_research_cap 검사가 문장의 '웹 조사' 조건을 빠뜨려 p02(웹 아님)를 반례로 잴 뻔했다 → 검사 고침(S_web=예). 맞춰 본 일곱은 그대로.
- H_render_rate 검사 고침 뒤 남은 시험 d69b는 S_long_lap=아니오로 적혀 있었다(내 첫 덤프가 '아니오'를 숨겨 처음에 '모름'으로 읽었다) → 0/1 반박으로 남김, 한 건이라 개정 보류.

## 확인한 것 (어떻게)
- `PYTHONIOENCODING=utf-8 python -m proviso validate agent_usage` → `목표 3, 상태 24, 사실 2, 관찰 51, 가설 24, 규칙 41` / `문제 없음`.
- `PYTHONIOENCODING=utf-8 python -m proviso audit agent_usage` → `점검 통과: 목표를 해치는 것은 모두 대가로 받아들인 기록이 있음`.
- `PYTHONIOENCODING=utf-8 python -m proviso check agent_usage` → 지지 4(H_turns_over 1/1, H_tok_rate_long 25/29, H_turn_rate_shape 44/54, H_model_mult_shape 3/3), 반박 1(H_render_rate 0/1), 시험 전 11, 대체됨 8.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.dispatches` → `기록 문제 없음 (128건)`, 시간 등급 맞음 91·낮게 8·높게 23, 토큰 등급 맞음 97·낮게 9·높게 14·모름 2. p01·p03은 unknown이라 빠짐(정상).
- `python -m unittest discover -s tests -t .` → `Ran 44 tests` `OK`(정리 전 38).
- 새 검사 일곱이 세울 때 본 기록과 맞는지(✗가 없는지)는 테스트로 고정했다(mid_notes_bounded는 보내기 전에 적지 않은 d01만 ✗).
- dispatches.toml의 바뀐 줄이 상태 17줄과 맨 위 주석뿐인지 `git diff`로 확인했다(그 밖의 차이는 메인이 덧붙인 p02·p03).

## 확인 못 한 것
- 새 가설 일곱은 모두 시험 전이다(d95부터). 지금 숫자는 맞춰 본 것이지 예측으로 확인된 것이 아니다.
- 사후로 채운 상태 17곳은 돌아보기 글과 작업 설명으로 판단했다. 그 지시서 원문(batman)은 이 환경에 없어 대조하지 못했다.
- PAST_ANALOG의 d68·d87은 돌아보기 글이 비유를 밝히지 않아 내가 골랐다(보여 주기만, 판정에 안 듦).
- batman 쪽 AGENT-LOG·STATUS와의 대조는 하지 않았다(이 환경에 없음).

## 알려진 문제
- H_render_rate는 검사를 고친 뒤에도 0/1로 반박이다(d69b: 시안 열두 장을 한 번 실행, 반복이 없었음). 한 건이라 개정을 미뤘다. 다음 짧은 바퀴 렌더도 빗나가면 물린다.
- 배수 가설 둘(H_settled_integration, H_build_tools)은 `predicted.analog`가 없으면 시험되지 않는다. `analog`는 dispatches.py의 검사 대상 칸이 아니라(범위 밖이라 안 고침) 없는 id를 적어도 오류가 나지 않는다 — `_analog`가 None을 돌려 그 기록이 빠질 뿐이다. 제안: dispatches.py의 `validate`에 `predicted.analog`가 있는 기록 id인지 검사를 더한다.
- 메인이 정리 중에 적은 p03 예측은 이번에 물린 R_fixed_input을 쓴다(검증상 문제는 없음). 다음 예측부터 R_fixed_input_v2.
- H_turn_rate_shape의 시험에 이 저장소 기록(p02)도 들어간다. batman 작업과 모양이 다른 조사·정리 작업이 섞이면 띠가 흔들릴 수 있다 — 지금은 81 %로 지지.
- 코어(proviso/)는 고치지 않았다. 고칠 필요가 있던 것: 없음.

## 다음 작업자에게
- 예측할 때는 `domains/agent_usage/CLAUDE.md`의 "지금 쓰는 규칙 요약" 한 장만 보면 된다. 새 상태 셋(S_fix_existing, S_open_seams, S_build_tools)과 `predicted.analog`를 꼭 적는다 — 새 가설 셋이 이것 없이는 시험되지 않는다.
- 도중 지시를 보내면 S_mid_notes=예를 적는다(d63·d69는 안 적혀서 근거로 못 썼다).
- 다음 batman 배치(37~)에서 볼 것: H_render_rate(짧은 바퀴 렌더), H_ctx_fix(고치는 작업), H_fixed_input_opus·H_sonnet_floor(비교 라운드가 오면), H_doc_spec_minutes(문서 라운드).
- 판정 메모의 숫자는 아래 일회용 분석으로 냈다: 범위 적중·쏠림은 `predicted.minutes`와 `actual.minutes` 비교, 턴당 맥락은 `tokens_m × 1000 / turns`. 다시 내려면 `dispatches.measures()`로 같은 계산을 하면 된다.
