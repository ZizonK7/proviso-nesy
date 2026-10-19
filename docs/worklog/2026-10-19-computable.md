# 2026-10-19 — agent_usage를 계산되는 논리로 (효과 칸, 계산기, 시간 순서 홀드아웃, 빈틈 쪼개기)

에이전트: 계산 논리 하위 에이전트 (Opus 5.5, effort high). 하위 에이전트 호출: 없음.
커밋·push: 안 함 (메인이 한다).

## 한 줄 요약
가설에 기계가 읽는 효과 칸을 붙이고, 상황 값만으로 숫자와 말할 구간을 내는 계산기를 만들었다. 끝난 기록을 시간 순서로 반으로 나눠 앞 절반으로 세우고 뒤 절반으로 시험하니, **말할 구간 적중은 쪼개기 전 계산기 38 % → 쪼갠 뒤 51 %, 당시 손 예측 62 %** — 계산기는 아직 손 예측보다 못하다. 방향(논리)이 틀린 조각 하나를 찾아 물렸다.

## 효과 칸 구조 (코어 `proviso/schema.py`가 검사)
가설·규칙 아래 `[[hypothesis.effect]]`(또는 `[[rule.effect]]`)를 여럿 둘 수 있다.

| 칸 | 뜻 | 검사 |
|---|---|---|
| `on` | 무엇에 작용하나. 이름은 분야가 `[domain] quantities`로 밝힌다. agent_usage: `turns`(턴, 양) · `turns_per_min`(분당 턴, 속도) · `add_minutes`(더하는 분) · `ctx_k`(턴당 맥락, 천 토큰) · `minutes`(턴이 분을 정하지 않는 일의 분) | 목록 안 |
| `op` | `base` 기준값 / `mul` 곱하기 / `add` 더하기 | 셋 중 하나 |
| `range` | [하한, 상한] | 0 < 하한 ≤ 상한, **상한/하한 ≤ `[domain] max_ratio`(2)** (G) |
| `when` | 언제: 상태 id = 값 또는 값 목록, 앞에 `!`는 '아님' | **상태가 `known_before = true`** (C), 노드 `conditions`에 있음, 값은 `situation_values` 안 |
| `dir` | 곱하기·더하기의 방향 주장 `up`/`down` | **조건 조각이면 필수, 범위와 맞아야 함** — 1을 넘나드는 곱하기는 방향이 없다(오류) (A) |
| `reason` | 왜 이 조건이 이 차이를 만드나 | **비면 오류**, 노드의 `reason`도 필수 (B) |
| `analog` | 비유: 빗댄 기록의 실측 × 범위 (기준값만) | base만 |

분야 칸(코어는 모른다): 조각 노드에 `seen_until`(맞출 때 본 마지막 기록), `fit`(fit.py가 적는 근거: 맞춘 기간과 설명한 기록), 쪼갠 조각에 `split_from`·`why_condition`. 상태에 `known_before`(+ 까닭 `known_before_note`), `default`, `from_project`.
- 일의 성질이 아닌 상태는 `known_before = false`로 표시했다: S_short(150턴 안쪽 = 계산할 값 그 자체, 순환), S_impl_hour(순환), S_turns(메타 칸), S_unsaved_doc(결과 쪽), S_mid_notes(실행 중에 생김), S_zone_span(예측에서 계산). 이 상태들은 계산 조건으로 못 쓴다.

## 계산 (`domains/agent_usage/predict.py`)
- 턴 = 기준값 × 곱하기들, 분당 턴도 같다. 분 = 턴 ÷ 분당 턴 + 더하기. 분 기준값 조각이 맞으면 그것이 분을 정한다. 토큰 = 턴 × 턴당 맥락.
- 기준값이 여럿 맞으면 조건이 가장 많은 것. 하나도 없으면 **'모름'**(지어내지 않는다).
- 범위 합치기: 조각마다의 범위를 독립인 불확실성으로 보고 로그 반폭을 제곱합 제곱근으로 합친다(전 구간 곱보다 좁다). 합친 범위가 2배를 넘으면 기하 중심 둘레 2배로 자른다(G).
- 말할 구간 = 분 범위의 구간, 걸치면 긴 쪽(R_say_numbers_v2).
- 설명: 근거(맞춘 기간·설명한 기록) → 조각(왜) → 조합 → 숫자. 빼도 말할 구간과 토큰 등급이 안 바뀌는 효과는 설명에서 빼고 '쓴 조각' 목록에만 둔다.
- 비유: 보내기 전에 적은 `predicted.analog`가 끝난 기록이면 비유 계산을 따로 보여 준다. 비유 기준값에는 곱하기를 얹지 않는다(빗댄 기록이 모양을 담고 있다). 성적은 따로(지금 p04 하나, 맞춰 본 것).
- 상황 값: 적힌 값 → `from_project`(S_small_codebase: proviso 예, batman 아니오) → `default`(S_other_model 아니오 = F_setup, S_many_turn_model 아니오) → 모름.
- 숫자는 `fit.py`가 기록에서 기계적으로 맞춘다: 2배 폭 창으로 값을 가장 많이 담는 창(같으면 가운데 값에 가까운 창)을 담긴 값의 최소–최대로. 기준값은 곱하기가 안 걸린 기록으로, 곱하기는 '실측 ÷ (기준값 × 다른 곱하기)'로 세 번 돌려 맞춘다. 사람은 모양만 적는다.

## 홀드아웃 경계와 뒤 절반 성적
- **경계: d38b (배치 17 끝, 2026-10-16).** 끝난 기록 125건 중 앞 절반 64건(d01–d38b), 뒤 절반 61건(d39–p04). 가운데(63번째)에 가장 가까운 배치 경계(배치 안에서 자르면 같은 지시서 묶음이 갈린다).
- 앞 절반만 보고 세우고 쪼갰다: `holdout.toml`의 두 세트 숫자는 `fit_until = d38b`로 맞췄고, 테스트가 '앞 절반으로 다시 맞춘 값과 같다'를 확인한다(`test_holdout_numbers_come_only_from_the_front_half`). 탐색 스크립트도 앞 절반만 출력하게 해서 썼다.
- 당시 손 예측의 말한 구간: `predicted.told`가 있는 것은 p04 하나뿐이라, 나머지는 분 범위의 긴 쪽(R_say_numbers_v2를 지난 기록에 댐)으로 셌다. 예측 없이 보낸 d88은 '모름'.

`python -m domains.agent_usage.holdout`, 뒤 절반 61건:

| | 쪼개기 전 계산기 | 쪼갠 뒤 계산기 | 당시 손 예측 |
|---|--:|--:|--:|
| **말할 구간 맞음** | 23/61 (38%) | 31/61 (51%) | 38/61 (62%) |
| 말할 구간 모름(계산 못 함) | 6 | 6 | 1 |
| 분 범위 맞음 | 11/61 (18%) | 18/61 (30%) | 28/61 (46%) |
| 턴 범위 맞음 (턴을 낸 것 중) | 13/47 (28%) | 17/47 (36%) | 35/60 (58%) |
| 분 빗나감: 실제가 아래·양 | 23 | 13 | 10 |
| 분 빗나감: 실제가 아래·속도 | 5 | 5 | 12 |
| 분 빗나감: 실제가 아래·턴 예측 없음 | 5 | 5 | 0 |
| 분 빗나감: 실제가 위·양 | 9 | 12 | 6 |
| 분 빗나감: 실제가 위·속도 | 2 | 2 | 4 |

- 읽기: 쪼개기는 뒤 절반에서도 좋아졌다(+8건, 양 탓 아래 23 → 13). 그래도 손 예측이 낫다. 손 예측은 빗댄 기록과 할 일의 수를 보는데, 계산기에는 **일의 크기를 말해 주는 보내기 전 상태가 없다**(S_short는 순환이라 막았다). 계산기 '모름' 6건은 기본이 아닌 모델의 문서·도구 일(조각 없음).
- 참고: 분 범위는 맞았는데 긴 쪽으로 말해 구간이 틀린 기록 — 쪼갠 뒤 3, 손 예측 8. 가운데 값의 구간으로 말했다면 손 예측은 46/61, 쪼갠 뒤 계산기는 31/61.
- **최종본**(같은 모양 + 아래 쪼개기 넷을 전체 기록 p04까지로 다시 맞춤): 맞춰 본 것 83/125(손 예측 84/125), 분 범위 65/125(손 49), 턴 67/101(손 56/108). 맞춰 본 숫자라 시험이 아니다. `seen_until = p05`: p05 다음 기록부터 시험된다(`piece_direction`·`piece_size`가 지금 모두 '시험 전').

## 쪼갠 것 목록
| 단계 | 쪼갠 것 | 더한 조건 | 설명한 기록 (맞춘 기록 중) | 왜 이 조건이 차이를 만드나 |
|---|---|---|---|---|
| 앞 절반 | C_turns_research → C_turns_research_v2 | S_fixed_input ≠ 예 | 앞 절반 8/8 | 정해진 입력의 풀이는 찾는 턴조차 없어 조사보다 훨씬 적다. 같은 일을 두 조각이 줄이면 숫자가 흐려진다 |
| 앞 절반 | C_turns_base에서 C_turns_no_check를 떼어 냄 | S_external_check = 아니오, S_research ≠ 예, S_fixed_input ≠ 예, S_resumed ≠ 예 | 앞 절반 7/9 | 기준 턴은 확인 고리가 있는 구현에서 왔고, 돌려 보고 고치는 고리가 턴의 큰 몫이다 |
| 전체 | C_turns_resumed → C_turns_resumed_v2 | S_integration ≠ 예 | 전체 9/19 (앞 절반에 통합 2건: d12b·d26b) | 이어 보내서 줄어드는 몫은 다시 찾지 않는 탐색인데, 여러 갈래를 합치는 일은 찾을 것이 앞 회차에 없던 것이다 |
| 전체 | C_turns_base에서 C_fix_existing (턴↓·맥락↓·분당 턴↑) | S_fix_existing = 예 (분당 턴은 + S_long_lap ≠ 예) | 전체 8/9 · 9/9 · 8/8 (앞 절반 0건) | 고칠 곳이 지시서에 적혀 있으면 짓는 양과 읽는 양이 둘 다 작고, 편집과 확인이 짧게 이어진다 |
| 전체 | C_turns_base에서 C_small_codebase (턴↓) | S_small_codebase = 예 | 전체 3/4: p01·p02·p04 (앞 절반 0건) | 읽을 코드가 적으면 찾는 턴이 짧고, 검사가 몇 초면 확인이 즉시 끝나 큰 편집 몇 번으로 끝난다 |
| 전체 | C_min_other_fixed에서 C_min_light_model (분↓) | S_many_turn_model = 아니오 | 전체 6/8 (앞 절반에 같은 방향 짝 넷: d20·d25·d38·d38b) | 턴을 잘게 나눠 쓰는 모델은 정해진 입력도 여러 번 다시 읽고 고쳐 쓰고, 그렇지 않은 모델은 한 번 읽고 한 번 쓴다 |

- 하지 않은 쪼개기(장치 E): (1) 첫 C_turns_no_check(이어 보내기를 빼지 않은 것)는 앞 절반에서 6건(d29b·d29c·d30b·d30c·d32b·d15b)을 잃었다 → S_resumed ≠ 예를 더해 다시 쪼갬. (2) 외부 확인 없는 일을 '긴 글 쓰기 / 읽고 짧게 쓰기'로 더 나누는 것은 턴은 나아졌지만 d31·d32·d30e를 잃어 하지 않았다.
- 남긴 회귀 하나(이유와 함께 `holdout.REGRESSION_OK`): d15b — 쪼개기 전에는 상쇄로 맞았다(턴을 2.3배 크게, 분당 턴도 크게). 남은 빗나감은 설계부터 하는 새로 쓰기의 느린 분당 턴(2.8)인데 그런 기록이 앞 절반에 하나뿐이라 쪼개지 않았다(D).
- 넣다가 뺀 효과: C_fix_existing의 분당 턴을 조건 없이 걸면 범위가 0.93–1.8로 1을 넘나들었다(방향 없음) → 한 바퀴가 긴 확인(S_long_lap = 예, 기다림)을 빼는 조건을 더하니 1.21–1.8. C_small_codebase의 분당 턴은 0.87–1.32로 방향이 없어 넣지 않았다.
- 새 상태 셋(모두 known_before = true): S_small_codebase(project로 정해짐), S_integration(d12b·d26b·d39b·d68·d94를 사후에 채움), S_many_turn_model(S_other_model = 예 21건을 사후에 채움: Sonnet 예, Fable 아니오; d89는 실수로 다른 모델을 보내 보낼 때 몰랐으므로 비움). dispatches.toml 머리 주석에 적었다. 기존 예측·실측 숫자, review.reason, p05는 건드리지 않았다(`git diff`로 확인: 주석 네 줄과 상황 값 26줄만 더함).

## 방향 성적에서 틀린 조각
- **C_turns_spec_fixed '설계 문서가 동작·데이터·검사까지 정해 두면 턴이 준다'**: 앞 절반으로 맞추면 ×0.46–0.71(줄인다), 뒤 절반의 방향 성적은 쪼개기 전 세트에서 **반박**(조건 있음/없음 ×1.09, 같은 기준값끼리의 거친 비교), 쪼갠 뒤 세트에서는 지지(×0.91, 겨우). 전체 기록으로 맞추면 범위가 ×0.57–1.12로 1을 넘나든다(방향 없음). → 최종본에서 물렸다(`status = retired`, why = 이유 틀림). 해석: 설계가 정해져 있어도 그만큼 많이 쓰게 되어 턴은 줄지 않았고, 줄어드는 것은 분(빠른 편집)이었다 — 그 몫은 고치는 일에서만 C_fix_existing의 분당 턴이 잡는다.
- 그 밖의 조건 조각은 뒤 절반에서 방향 지지 또는 시험 전(웹 조사는 뒤 절반에 조건 있음·없음이 둘씩 안 돼 시험 전). 크기 성적은 대부분 낮다(예: 쪼갠 뒤 세트 C_turns_resumed 3/11, C_turns_spec_fixed 5/16, C_turns_fixed_input 1/4) — 크기만 틀린 것은 조건이 흐린 것(쪼개기 후보)으로 읽는다.

## 설명 못 한 채 남은 기록 (최종본, 맞춰 본 것 기준 42/125)
- **분 범위는 맞았는데 긴 쪽으로 말해 틀린 12건**: dR2, dR5C, d38, d38b, d44, d45, d46, d67, d72, d73, d83, d92. 조건의 빈틈이 아니라 말하기 규칙의 몫이다(범위가 22–45분처럼 걸치면 '신경 끄기'로 말한다). 가운데 값의 구간으로 말했다면 최종본은 91/125.
- **'모름' 6건**: d42(턴을 잘게 쓰는 모델의 도구 일), d49·d75(같은 모델의 문서), d50·d76(다른 모델의 문서), d89(실수로 다른 모델을 이어 보냄). 기본이 아닌 모델의 정해진 입력이 아닌 일에 기준값 조각이 없다. 근거가 모양마다 1–2건이라 세우지 않았다.
- **진짜 빈틈 24건**:
  - 일의 크기를 말해 주는 보내기 전 상태가 없다: 첫 회차 구현이 30–38분에 끝난 것(d14, d16, d27, d30, d40, d43, d60, d61 — 계산은 48–96분), CI 캐시가 따뜻한 짧은 일 d08, 이어 보낸 큰 일(d15c, d30d, d69c)과 아주 작은 후속(d33b, d64). S_short가 이 몫을 하던 상태인데 계산할 값 그 자체라 막았다.
  - 설계부터 하는 문서 새로 쓰기가 느리다: d15b, d77(분당 턴 2.8·3.5). 앞 절반에 한 건이라 쪼개지 않았다.
  - 경계에 붙은 것: 웹 조사 dR1·dR4(8분, 계산 8.7–17.4), d33(9.2분), 고치는 일 d70·d71(19–22분, 계산 22–45), 작은 코드베이스 p01·p02, 이어 보낸 정해진 입력 d66.

## 상한 값과 근거
- **범위 폭 ≤ 2배** (조각 범위와 계산한 분·턴·토큰 범위 모두; `[domain] max_ratio`): 사용자에게는 결국 한 구간을 말해야 한다. 2배면 범위가 구간 둘까지만 걸친다(10–40분 구간 자체가 4배라 셋에 걸칠 수 없다). 넓혀서 맞추는 길을 막는다.
- **효과 수 ≤ 설명한 기록 수 ÷ 4** (`checks.EFFECT_PER_RECORDS`, 살아 있는 조각에 audit 오류): 효과 하나가 숫자 둘(하한·상한)을 기록에서 맞추므로, 숫자 하나에 설명한 기록이 둘 이상이어야 외워서 맞춘 것이 아니라고 본다(장치 D의 '두 건 이상'과 같은 잣대). 지금 효과 18개 × 4 = 72 ≤ 설명한 기록 83.
  - 참고: 앞 절반 세트는 이 상한을 넘는다(쪼개기 전 효과 12 × 4 = 48 > 설명 39, 쪼갠 뒤 13 × 4 = 52 > 47). 경계 시점의 규칙은 데이터에 비해 조각이 많았다는 뜻이다. 상한은 지식 파일의 살아 있는 조각에만 강제한다.
- **한 효과는 맞출 기록 중 2건 이상을 설명** (D, audit 오류와 fit.window).

## 지킬 장치가 어떻게 강제되나 (테스트 `tests/test_computable.py`)
| 장치 | 강제하는 곳 | 테스트 |
|---|---|---|
| A 방향·크기 따로 | schema(방향 필수·범위와 맞음), holdout.piece_scores(방향 = 조건 있음/없음 비교, 크기 = 범위 안 몫), checks.piece_direction/piece_size, audit 오류(시험 기록에서 방향 반박) | test_A_* 넷 |
| B 이유 없는 숫자 금지 | schema(노드·효과 reason), audit(쪼갠 조각의 why_condition) | test_B_*, test_split_pieces_say_why_the_condition_matters |
| C 보내기 전 조건만 | schema(when 상태 known_before = true) | test_C_* 셋 |
| D 한 건짜리 금지 | fit.window(2건 미만 None), audit(설명 < 2 오류) | test_D_one_record_cannot_make_a_piece |
| E 회귀 금지 | holdout.regressions + REGRESSION_OK(이유) | test_E_no_unexplained_regression_from_splitting |
| F 조각 수 상한 | audit(효과 × 4 > 설명한 기록이면 오류) | test_F_effect_count_cap |
| G 숫자만 넓히기 금지 | schema(폭 ≤ 2배), predict.clamp, audit(맞춘 값과 다른 범위 = 손으로 넣은 숫자), 기존 '쪼개지 않은 개정' 경고 | test_G_* 넷 |
| H 맨 위 줄은 말할 구간 | holdout.score_table 첫 줄, predict 설명 첫 줄 | test_H_top_line_is_the_told_zone |
| SEEN_UNTIL | 조각의 seen_until(p05), NODE_CUT 검사 | test_seen_until_principle_final_pieces_are_untested_now |
| 이름에 분야·앱 없음 | — | test_pieces_name_no_project_or_app |

## 다른 분야에서 다시 쓸 수 있을 것 같은 조각
조각 이름·문장·이유에는 프로젝트·앱·모델 이름을 쓰지 않았다(테스트가 막는다). 일을 맡기고 시간을 재는 곳이면 그대로 읽힌다:
- C_turns_no_check — 확인할 바깥 시스템이 없으면 돌려 보고 고치는 몫이 없어 일이 작다.
- C_fix_existing — 고칠 곳이 정해진 고침은 짓는 일보다 양이 적고, 읽는 범위가 좁고, 손이 빨리 돈다(바퀴가 긴 확인을 기다리면 빠르기 몫은 사라진다).
- C_small_codebase — 확인이 즉시 끝나는 작은 작업장에서는 찾는 몫이 짧다.
- C_turns_resumed_v2 — 같은 사람에게 이어 맡기면 다시 찾는 몫이 빠진다, 단 여러 갈래를 합치는 일은 예외.
- C_turns_fixed_input / C_ctx_fixed_input — 입력이 정해진 순수 추론은 양도 읽을 것도 작다.
- C_rate_web / C_ctx_web — 작은 조각을 자주 찾는 일은 손이 빠르고 머리에 쌓이는 양이 작다.
- C_min_other_fixed / C_min_light_model — 생각이 긴 일은 손의 수가 아니라 생각 시간이 시간을 정하고, 잘게 나눠 다시 보는 작업자는 더 오래 걸린다.
- C_turns_analog — 같은 종류의 직전 사례에 빗대면 그 사례의 양에서 출발한다(모양을 이미 담고 있어 보정을 얹지 않는다).

## 한 일
- 코어: `proviso/schema.py` 효과 칸 검사(`OPS`·`DIRS`·`MAX_RATIO`, `effects()`, `when_items()`, `_effect_errors`), 상태 `known_before` 모양 검사. `proviso/audit.py` `report(kn, extra)`(분야 점검). `proviso/__main__.py` `domain_audit()` — 분야 오류도 audit 실패. `proviso/mcp_server.py` audit에 분야 점검. 분야 단어는 넣지 않았다.
- 새 파일: `domains/agent_usage/predict.py`(계산기·설명·CLI), `fit.py`(숫자 맞추기, `--write`), `holdout.py`(다시 돌리기·비교표·방향/크기 성적·빈틈·회귀), `holdout.toml`(front_v0·front_split), `tests/test_computable.py`(32개).
- `domains/agent_usage/checks.py`: `piece_direction`·`piece_size`(노드 seen_until로 자름, `NODE_CUT`), `audit_pieces` = `AUDIT`, `EFFECT_PER_RECORDS = 4`.
- `domains/agent_usage/knowledge.toml`: `[domain]` quantities·situation_values·max_ratio, 상태 25개에 known_before(+ 까닭), S_other_model default, 새 상태 셋, **계산 조각 구역**(살아 있는 16 + 이전 버전 3: C_turns_research, C_turns_resumed, C_turns_spec_fixed). 기존 규칙·가설은 그대로.
- `domains/agent_usage/dispatches.toml`: 머리 주석 + S_integration 5줄 + S_many_turn_model 21줄(사후 채움). 기존 숫자·reason·p05 그대로.
- `tests/test_agent_usage_domain.py`: 검사 이름 테스트가 NODE_CUT(seen_until)을 받게.
- 문서: 루트 `CLAUDE.md`(명령, agent_usage 줄, 지금 상태, 다음 할 일 5), `proviso/CLAUDE.md`(효과 칸 설계 결정, 칸 표, audit 분야 점검), `domains/CLAUDE.md`(AUDIT), `domains/agent_usage/CLAUDE.md`(파일, 고리 1단계 '계산기 먼저', 규칙 요약 0, p05 절).

## 확인한 것 (어떻게)
- `for d in flowlog music_player agent_usage; do PYTHONIOENCODING=utf-8 python -m proviso validate $d; PYTHONIOENCODING=utf-8 python -m proviso audit $d; done` → validate 셋 "문제 없음", audit 셋 "오류 없음"(exit 0; 경고 1·2·14, 분야 점검 0).
- `PYTHONIOENCODING=utf-8 python -m proviso check agent_usage` → exit 0, 계산 조각 16개 모두 '시험 전'(맞춰 본 것은 detail에).
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.dispatches` → "기록 문제 없음 (130건)", exit 0.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.predict p04` → 말할 구간 '다른 일' 9.85–19.7분, 근거 → 조각 → 조합 → 숫자, 실측 17.0분 구간 맞음(맞춰 본 것으로 표시), 비유 계산(p01) 따로, 당시 손 예측 40–65분.
- `PYTHONIOENCODING=utf-8 python -m domains.agent_usage.holdout` → 위 비교표.
- `python -m domains.agent_usage.fit final --write`, `… holdout --write`를 한 번 더 돌려 두 파일이 바뀌지 않음(diff 없음) — 숫자가 기록에서 그대로 다시 나온다.
- `python -m unittest discover -s tests -t .` → 99개 통과.
- `python -m proviso graph agent_usage` → out/에 html 생성(브라우저로 보지 않음).

## 확인 못 한 것
- 그래프 html을 브라우저로 열어 보지 않았다(계산 조각 19개 노드가 늘었다).
- MCP stdio로 audit을 직접 부르지 않았다(`handle()` 테스트만, 분야 점검이 붙은 뒤에도 통과).
- 계산기를 보내기 전 예측에 실제로 써 본 적이 없다(p05는 내가 손으로 한 예측; 계산기는 p05를 '신경 끄기' 21–42분, 손은 '다른 일' 18–35분으로 본다 — p05 실측이 첫 비교가 된다. 단 p05는 seen_until 안쪽이라 조각 성적에는 들지 않는다).

## 알려진 문제
- **오염**: 앞 절반 세트의 모양을 정하기 전에 나는 전체 기록 표를 이미 봤다. 막은 것: 숫자는 앞 절반에서 기계로만 맞췄고(테스트), 앞 절반 세트의 조건은 경계 시점에 있던 상태·규칙만 썼고(S_render·S_fix_existing·S_integration 등 그 뒤 상태는 안 씀), 쪼갤 곳을 찾는 출력은 앞 절반만 보여 주게 했다. 모양 선택에 섞인 영향은 없앨 수 없었다.
- 사후에 채운 상태 둘(S_integration, S_many_turn_model)은 지시서 글과 모델 이름에서 채웠지만 내 판단이다. 비유 조각은 맞출 때 사후에 읽은 빗댄 기록(PAST_ANALOG 다섯)도 썼다(예측할 때는 보내기 전에 적은 것만 쓴다).
- 방향 성적은 거친 비교다: 같은 기준값을 고른 기록끼리 '실측 ÷ (그 조각을 뺀 계산)'의 가운데 값을 비교한다. 다른 조각이 흐리면 방향도 흔들린다(C_turns_spec_fixed는 세트에 따라 반박 ×1.09 / 지지 ×0.91).
- 조각끼리 조건이 겹치면 두 번 줄어든다 — 그래서 `!예` 조건으로 서로 빼 두었다(조사 ↔ 정해진 입력, 외부 확인 없음 ↔ 조사·정해진 입력·이어 보내기). 새 조각을 더할 때 겹침을 확인해야 한다(fit이 서로 맞추지만 겹침 자체는 막지 않는다).
- `add_minutes`(바퀴 몫) 칸은 계산기·fit에 있지만 쓰는 조각이 없다: 바퀴 수(찾을 것의 수)가 보내기 전에 적히지 않는다.
- 토큰 계산은 턴 × 맥락이라 턴이 틀리면 같이 틀린다(p04 토큰 밖).

## 메인 판단 필요
1. **계산기를 어디에 둘지**: 뒤 절반에서 손 예측보다 낮다(51 % vs 62 %). 나는 '계산기 먼저 돌리고 손 예측과 나란히, 다르면 둘 다 적기'로 agent_usage CLAUDE.md 고리 1단계를 고쳤다. 사용자에게 말하는 구간은 지금처럼 손 예측으로 할지 확인해 달라.
2. **긴 쪽으로 말하기의 값**: 범위가 맞았는데 긴 쪽으로 말해 틀린 것이 최종본 12건, 뒤 절반 손 예측 8건(가운데 값의 구간이면 손 예측 46/61). 사용자 결정(R_say_numbers_v2, 판정 '지지')이라 바꾸지 않았다. 이 숫자를 사용자에게 보여 줄지.
3. **일의 크기 상태**: 남은 빈틈의 가장 큰 몫이 일의 크기다. S_short는 순환이라 known_before = false로 막았다. 대안: 지시서에서 셀 수 있는 크기(예: '할 일 항목 수', '새로 짓는 화면·파일 수')를 보낼 때 상태로 적게 하기. 지난 기록은 사후에 채워야 해서 내 판단이 섞인다 — 할지.
4. **다른 모델의 문서·도구 일은 '모름'**: 조각을 세울 근거가 모양마다 1–2건. 지금처럼 R_models_*로 손으로 잡는 것으로 둘지.
5. **상한 값**: 효과 수 ≤ 설명한 기록 ÷ 4, 범위 폭 ≤ 2배. 앞 절반 세트는 효과 상한을 넘었다(경계 시점 규칙이 데이터에 비해 많았다). 값이 맞는지.
6. **R_turns_analogy_v2 등 기존 손 규칙**은 건드리지 않았다(계산 조각은 병행). 계산 조각이 p05 다음 기록에서 성적을 쌓으면 어느 손 규칙을 물릴지 다음 정리에서 정한다.
7. p05(이 작업)의 실측을 메인이 넣을 때: 손 예측은 '다른 일', 계산기는 '신경 끄기'였다.

## 다음 작업자에게
- 보낼 때: 상황 파일(`project`, `[situation]`, `analog`)로 `python -m domains.agent_usage.predict 파일`. 기록에는 새 상태 S_integration·S_many_turn_model도 적는다(S_small_codebase는 project로 정해짐).
- 조각을 고칠 때: 모양(on·op·when·dir·reason, why_condition)만 손으로 고치고 `python -m domains.agent_usage.fit final --write`로 숫자를 다시 맞춘다. 범위를 손으로 바꾸면 audit 오류. 쪼갤 때는 이전 버전을 retired + replaced_by로 남기고 새 버전 conditions에 더한 상태를 적는다. `seen_until`을 맞춘 마지막 기록으로 옮기면 그 전 기록은 '맞춰 본 것'이 된다.
- 쪼갤 곳 찾기: `python -m domains.agent_usage.holdout --gaps`(앞 절반), 최종본의 빈틈은 `holdout.gaps(pr.live_pieces(kn), 끝난 기록, kn, 기록)`.
- 함정: 조건이 겹치는 조각을 더하면 두 번 줄어든다. 범위가 1을 넘나드는 효과는 방향이 없다는 뜻이니 조건을 찾거나 넣지 않는다.
