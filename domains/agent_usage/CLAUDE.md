# domains/agent_usage/ — 하위 에이전트 시간·사용량 예측 (AI가 스스로 쌓는 논리집)

하위 에이전트를 보낼 때 걸릴 시간과 쓸 토큰을 예측해, 이유와 함께 사용자에게 말하기 위한 논리집. 2026-10-16에 만들었다.

## 역할 (사용자 결정 2026-10-16)
- **사용자는 이 분야를 판단하지 않는다**("잘 모르겠다"). 분야 A(AI 코딩 과정)를 보류한 것과 같은 이유다.
- 대신 **AI가 사용자가 자기 논리집을 쌓는 방식을 그대로 따라 해서 스스로 쌓고, 스스로 쓴다.** 판정은 실측(`scripts/agent_usage.py`)이 한다.
- 사용자에게는 예측(분·토큰 숫자)과 그렇게 본 이유만 말한다(R_say_numbers).

## 파일
- `knowledge.toml`: 목표 3, 지휘 모델이 쓴 예측 규칙(버전별), 관찰, 가설. 관찰 출처: `measured`(실측) / `director`(지휘 모델 메모) / `conversation`.
- `dispatches.toml`: 작업마다 **예측 → 실측 → 돌아보기** 한 묶음. 보낸 순서대로 이어 쓴다. 상황 값(대 보기)은 상태 id = 예/아니오/일부/모름.
- `dispatches.py`: 기록 검사 + 예측·실측 비교표. `python -m domains.agent_usage.dispatches`
- `checks.py`: 가설을 실측 기록으로 판정. **가설은 세운 뒤에 나온 기록으로만 시험한다**(`SEEN_UNTIL`). 세울 때 본 기록은 "맞춰 본 것"으로 따로 보여 준다(사후 설명 방지).

## 고리 (한 작업마다)
1. **보내기 전**
   - 논리집에서 맞는 규칙을 찾는다(MCP `search`·`explain` 또는 이 파일들).
   - `dispatches.toml`에 기록을 하나 덧붙인다: 상황 값, 예측(분 범위·등급·턴·토큰), 쓴 규칙 id, 이유, `written_before = true`(기본).
   - 사용자에게 숫자와 이유를 말한다.
2. **끝나면** `scripts/agent_usage.py`로 실측을 넣는다. 멈춘 작업은 `status = "stopped"`, 끝났는지 모르면 `"unknown"`(판정에서 빠진다).
3. **돌아보기**: `python -m domains.agent_usage.dispatches`, `python -m proviso check agent_usage`.
   - 맞았든 틀렸든 이유를 `review.reason`에 적는다. 맞았을 때도 적는다(H_cancel처럼 맞았는데 이유가 틀린 경우를 잡으려고).
   - 이유가 새 주장이면 가설로 세우고 `checks.py`에 검사와 `SEEN_UNTIL`(지금 마지막 기록 id)을 넣는다.
4. **고치기**: 아래 "따라 할 방식"대로 고친다.
   - 규칙을 고칠 때는 이전 버전을 지우지 않고 `status = "retired"` + `replaced_by`로 남긴다.
   - 어긋난 관찰은 `against`(반대 근거)로 남긴다.
5. `python -m proviso validate agent_usage`, `python -m proviso audit agent_usage`, 테스트.

## 따라 할 방식 — 사용자가 자기 논리집을 쌓은 방식 (출처: docs/knowledge-format-v0.md 3절, docs/pieces-v0.md, 2026-10-14 대화)
1. **빠진 고리를 묻는다.** "반복한다고 왜 점수를 매기나, 최근은 갑자기 어디서 나왔나" → 목표와 이유가 없는 규칙은 채운다. 이유가 "기록 없음"인 규칙(R_tok_v1, R_turns_analogy)이 우선.
2. **실패하면 예외인지 개정인지 가른다.** "예외가 아니라 논리를 수정해야 하는 거 아닐까?"
   - 자주 일어나고 이유 안의 가정이 틀렸으면 → 새 버전.
   - 이유는 맞는데 드문 바깥 상황이면 → 예외.
3. **예외는 원래 전제에 있어야 했던 조건으로 본다.** "애초 전제에 '시험 기간이다'가 있어야 했던 거 아니야?" → 자주 걸리면 조건으로 올리거나 규칙을 둘로 나눈다. 예: R_tok_v3 → 작업 길이로 나눔.
4. **확인 안 된 건 가설로 둔다.** "확인되지 않은 가설이니까" → 새 규칙은 `status = "hypothesis"`, 시험을 통과하면 `verified`.
5. **부작용을 보면 숨은 목표를 찾고, 대가로 받아들일지 정한다.** 받아들인 기록이 없으면 `audit`이 잡는다(지금 H_turns_over).
6. **사용 습관과 능력을 구분한다.** "Flash는 거의 병렬 작업용으로만 썼다" → 규칙의 근거가 쓰던 범위에서만 나왔는지 본다. 예: R_tok_v3의 근거는 큰 작업 세 건뿐이었다.
7. **판정한 이유를 원리로 만든다.** 질문 1의 "개수의 차이" → H_slot_count처럼, 돌아보기의 이유를 가설로 올린다.
8. **의심 가는 근거는 실제 기록으로 확인한다.** "6~8번째 품질" → 기록 재생으로 약 1%. 지휘 모델 메모도 실측과 대조한다.
9. **근거를 고치거나 범위를 넓힌다.** P5 "재입력 수고" → "재사용 기대". 규칙 문장이 실제 이유와 다르면 문장을 고친다.

## 지킬 것
- 공개 저장소다. 작업 설명은 종류만 적는다(게임 내용, 캐릭터, 이야기, 비공개 저장소 코드는 적지 않는다).
- 숫자 범위는 Opus 5.5, effort high에서만 확인된 것이다(F_setup). 모델이나 effort가 바뀌면 사실부터 다시 확인한다.
- 대화 기록에서는 숫자만 뽑는다(`scripts/agent_usage.py`). 대화 내용은 옮기지 않는다.

## 현재 상태 (2026-10-18 밤, batman 배치 32–33까지)
- 기록 117건(d78–d83: 배치 32 검토 라운드 — 꾸러미 작성, 비평 둘, 블라인드 풀이 셋 — 모두 실측; d84–d87: 배치 33 구현 1차 넷, 예측만).
- **여덟 번째 고리 (배치 32)**: 고정 입력의 Opus는 세 번째로 한 번 읽고 한 번 썼다(R_fixed_input 지지, d81 3.8분·11턴). 순수 추론 배수:
  Sonnet max 분 ×4.7(R_other_models_v3의 ×4–5 안), **Fable xhigh 분 ×1.8**(가설 ×2–3의 아래 끝 밖: 장마다 한 번 읽고 인용을 다시 확인하지 않았다).
  반복 라운드의 비평은 d53/d54의 ×0.95–1.07로 돌아 "앞 라운드 기록의 ×1.1–1.5"의 아래 끝이 맞았다. 꾸러미 작성은 분·턴은 안, 토큰은 ×2.0(두 장의
  글 양이 1,900줄로 늘어 읽기가 늘었다) → 꾸러미 토큰은 장의 글 양을 따른다는 관찰을 다음 라운드에서 시험. 배치 33의 넷은 d59–d62의 비유.

## 이전 상태 (2026-10-18 밤, batman 배치 30–31까지)
- 기록 107건(d74–d76: 배치 30, 같은 설계 피치를 세 모델이 쓴 라운드; d77: 배치 31 수석 작가, 예측만).
- **일곱 번째 고리 (배치 30)**: H_model_mult_shape **지지(2/2)**: 문서 작업에서 Sonnet max 분당 3.3턴, Fable xhigh 5.2턴(둘 다 Opus 범위 안).
  그러나 R_other_models_v2의 문서 작업 배수가 낮았다(Sonnet 분 ×3.1 vs 예측 ×2; 토큰 ×4.4 vs ×3–4) → **개정** R_other_models_v3(Sonnet 문서: 분 ×2–3,
  턴 ×2–2.5, 토큰 ×3.5–4.5; Fable 문서: 턴 ×0.8–1.2). 관찰 O_models_doc_b30. 읽고 쓰는 작업에서 입력이 1/3 늘어도 Opus의 분은 늘지 않았다
  (d74: 턴당 맥락이 늘 뿐) → R_turns_analogy_v2를 쓸 때 '읽을 것이 더 많다'는 분 배수가 아니라 토큰 배수다.

## 이전 상태 (2026-10-18 저녁, batman 배치 29까지)
- 기록 104건(d72·d73 추가: 배치 29, 원인과 설계가 지시서에 적힌 고침 둘 — 코드 하나, 글 하나 — 클라우드). 둘 다 분·턴·토큰이 범위 안.
- **여섯 번째 고리 (배치 29)**: H_given_design_rate의 첫 시험 — d72(코드, 글까지 전부 적힘) 분당 5.9 맞음, d73(글, 말은 에이전트가 씀,
  S_spec_fixed=일부) 분당 5.5 빗남 → 반박됨(2건 중 1건). 가른 결과는 **개정**: 조건에 '일부'를 넣은 가정이 틀렸다(말을 쓰는 턴이 붙고, 검사의
  글 규칙(자막 ≤80자)이 지시서에 없어 전체 스모크가 두 바퀴). H_given_design_rate → superseded, **H_given_design_rate2**(S_spec_fixed=예만;
  검사 `given_design_rate2`, SEEN_UNTIL d73). d73의 이유는 맞게 적혀 있었던 두 가지 바깥 요인도 보였다: 컨테이너에 없는 도구(sox) 설치가
  한 번 도는 바깥 단계로 더 들고, 글을 쓰는 작업은 검사의 글 규칙을 지시서에 적지 않으면 전체 바퀴가 둘(O_text_two_laps_b29). 예측 때 적용:
  `which sox ffmpeg`로 도구를 확인해 없는 것마다 2분, 글을 쓰는 작업은 전체 바퀴 둘로 센다.
- H_turn_rate_shape는 d72·d73 모두 범위 안(반박된 채로 33/42).

## 이전 상태 (2026-10-18, batman 배치 28까지)
- 기록 102건(d70·d71 추가: 배치 28, 원인과 설계가 지시서에 적힌 작은 고침 둘, 클라우드). 둘 다 분 범위 아래, 턴은 안, 토큰은 아래/바로 아래.
- **다섯 번째 고리 (배치 28)**: 틀린 이유 둘. (1) 한 번 도는 바깥 단계(R_verify_once)의 분을 PC 경험(5–10분)으로 잡았는데 클라우드 컨테이너에서는
  2.5분 → 환경마다 재서 더한다(규칙 문장은 그대로, 관찰 O_given_design_b28에 적음). (2) 에이전트가 새 검사 절을 따로 돌릴 수 있게 만들면 전체
  바퀴를 한 번만 돈다 → 예측은 전체 바퀴 하나 + 짧은 바퀴들로 센다. 새 가설 H_given_design_rate(원인·설계가 적힌 작은 고침은 분당 5.5–8.5턴;
  검사 `given_design_rate`, SEEN_UNTIL d71). 맞으면 R_turns_analogy_v2에 '적힌 고침은 분 ×0.6–0.8' 칸을 더한다.
- H_turn_rate_shape는 d70(7.7)로 반례가 하나 더 쌓였다(이미 반박됨: 30/38). 작은 고침은 빠른 쪽에 모이는 모양이라, H_given_design_rate가 그 갈래다.

## 이전 상태 (2026-10-17 저녁, batman 배치 23까지)
- 기록 50건 + 진행 중 1건(d51, `actual.status = "unknown"`로 두어 판정에서 뺌; 끝나면 실측을 넣는다).
- **네 번째 고리 (배치 23)**: 같은 설계 문서 쓰기를 세 모델이 했다(d48 Opus, d49 Sonnet max, d50 Fable xhigh). R_other_models의
  분 배수가 둘 다 빗나갔다(Sonnet ×2.05, Fable ×1.0; 턴·토큰 배수는 맞음). 이유 안의 가정("모델이 속도를 정한다")이 틀렸고 근거가
  고정 입력 한 종류였으므로 **개정**: R_other_models → retired, R_other_models_v2(작업 모양 셋 — 순수 추론·도구 고리·문서 — 별 배수).
  새 관찰 O_models_doc_b23, 새 가설 H_model_mult_shape(문서 작업에서는 다른 모델도 Opus와 같은 분당 2.5–5.5턴; 검사 `model_mult_shape`,
  SEEN_UNTIL d50). H_sonnet_max_rate는 도구 작업(S_external_check=예)에만 걸리므로 d49는 그 시험에 들어가지 않는다(가설 그대로).
- 배치 23 돌아보기에서 더 배운 것: 컨테이너 재시작으로 날아간 디스패치(d51 첫 실행, 14분 읽기만)는 예측이 볼 수 없는 바깥 상황이라
  기록하지 않고 batman AGENT-LOG에만 적었다. 재시작이 반복되면 상태 S_restart를 둔다.

## 이전 상태 (2026-10-17, batman 배치 22까지)
- 기록 46건(batman 배치 1–22). 배치 19–22는 소유자가 베타를 하는 동안 바로 고친 작업 6건(d42–d47).
- **세 번째 고리 (배치 19–22)**: d42(Sonnet max)가 예측의 3배 턴 → 새 가설 H_sonnet_max_rate(도구 작업만, 순수 추론 풀이는 뺌).
  H_turn_rate_shape가 27건 중 20건으로 반박됐는데 틀린 것은 잣대였다: 렌더 반복 작업까지 일반 작업 범위로 쟀다 →
  상황 S_render를 새로 두고 검사에서 빼서 다시 지지(23건 중 19건), 렌더 작업은 새 가설 H_render_rate(분당 5.5–8.5턴)로 시험.
  validate·audit 통과.
- 같은 돌아보기에서: 반박된 가설을 쪼개 다시 세우면 옛 가설에 `superseded_by`를 단다(지우지 않음, `check`는 '대체됨'으로 보여 준다). 오래 미뤄 둔 H_check_loop2를 한 바퀴 길이(S_long_lap)와 렌더(S_render)로 갈라 H_check_loop3·H_render_rate로 넘겼다. H_mid_notes는 측정이 없어 보류: 도중 지시를 보낼 때 처리 분을 보고하게 하고 `[dispatch.mid_notes]`에 count·minutes를 적는다.
- 배운 것: `python -m proviso check`는 가설만 보여 준다. 보내기 전에는 `knowledge.toml`의 규칙(`[[rule]]`, retired 아닌 것)도 읽는다. 배치 19에서 R_other_models를 놓쳐 d42 예측이 크게 빗나갔다. `predicted.rules`에는 규칙 id만 적는다(가설 id를 적으면 테스트가 실패한다).

## 이전 상태 (2026-10-16, batman 배치 13까지)
- 기록 40건(batman 배치 1–13). 판정 39건, 판정에서 뺀 것 1건(d15 멈춤). d16은 batman 기록으로 끝난 것이 확인됐다.
- **두 번째 고리 (배치 11–13 시험)**:
  - 지지: H_turns_over(1건). → R_turns_analogy v2(덜 정해진 과거 작업에 빗대면 0.4–0.7배)로 고쳐서 `audit`이 통과한다.
  - 반박: H_turn_rate(길이가 아니라 작업 모양이 분당 턴을 정함 → H_turn_rate_shape, R_time_turns v2), H_tok_per_min_long(긴 쪽 6건은 다 맞고 짧은 쪽이 틀림 → 긴 쪽만 H_tok_rate_long), H_check_loop(검사 잣대가 이미 반복을 넣은 예측과 비교해서 틀림 → 분당 턴 잣대의 H_check_loop2. 반대 근거가 쌓여 R_verify_other를 R_verify_loop / R_verify_once로 나눔), H_mid_notes(1건, 잣대가 거침 → 다음부터 지시 횟수와 처리 분을 적는다).
  - 새 규칙(모두 가설): R_tok_short_v5(읽는 방식으로 나눔), R_resume_ctx(이어서 보내는 에이전트), R_spec_fixed(동작·데이터·검사까지 정한 설계 문서 → 0.4–0.6배), R_doc_work(문서만 다루는 작업), R_fixed_input(고정 입력 순수 추론), R_other_models(Sonnet 5.5 max, Fable 5.1 xhigh 배수).
  - 작업 모양 상태 5개(S_web, S_fixed_input, S_other_model, S_resumed, S_spec_fixed)를 더했다. 숫자 범위 검사는 S_other_model=예를 뺀다(F_setup).
- 새 가설 셋(H_tok_rate_long, H_turn_rate_shape, H_check_loop2)은 `SEEN_UNTIL = d26b`, batman 배치 14부터 시험된다. H_cancel은 예상 800턴 이상 작업이 나와야 시험된다.
- batman 지휘 모델이 이 논리집으로 예측한다(batman CLAUDE.md §7). batman AGENT-LOG의 에이전트별 예측 줄을 여기 기록으로 옮기고, 클라우드 세션이 push하지 못하면 batman STATUS에 "proviso sync pending: batch N"이 남는다(PC 세션이 옮긴다). 보낼 때 새 상태 5개도 대 본다.
