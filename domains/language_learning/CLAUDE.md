# domains/language_learning/ — 일본어 왕초보 학습 시스템

사용자의 Android 앱 language_learning(github.com/ZizonK7/language_learning, 공개)과 그 둘레의 공부 방법에 대한 지식. 2026-10-22에 만들었다.

## 역할
- 사용자(한국어 화자, 일본어를 전혀 모름)가 일본 여행에서 쓸 일본어를 꾸준히 공부할 시스템을 설계하기 위한 논리집. 앱일 수도, 수업이나 다른 방법일 수도 있다(사용자 2026-10-22).
- 결정 방식(사용자): 결정 전에 논리집을 보거나 잘 된 케이스를 조사해 근거를 대입한다(R_decide_by_cases).
- 스페인어 데이터는 앱에 있지만 이 분야의 범위 밖이다(S_japanese_main).

## 출처
- 목표·조건: 2026-10-22 사용자 대화. 큰 목표 G_use_in_japan은 내장 데이터 metadata의 goal_ko에서 가져왔고 사용자 확인 대기.
- 사실: language_learning 저장소 코드(커밋 해시를 적는다). 앱 동작은 사용자에게 묻지 않고 코드에서 확인한다. 이 세션의 컨테이너에는 Android SDK가 없어 빌드·실기기 확인은 못 한다.
- 조사: `out/research/2026-10-22-language-learning/`(git 제외)의 보고서 6개 — 연구 근거(research_evidence), 앱 사례(apps), 한국인 학습자 사례(korean_learners), 여행 생존 범위(travel_survival), 꾸준함 장치(habit), 여행 앱(travel_app). 지시서는 같은 폴더 `briefs/`. 작업 보고서는 `docs/worklog/2026-10-22-research-*.md`. 조사에서 뽑은 조각은 가설로 넣고 출처(URL·종류·강도)를 note에 적는다. 넣을 때 지킬 것(루트 CLAUDE.md "다음 할 일 3"): 출처 실재 확인, 필요한 것만, 충돌 시 개인 경험 > 일반 원리.
- 판정: 사용자 실사용이 가장 무겁다. 사용자가 일본어를 모르므로 '방법이 맞나'는 처음엔 조사 근거(source="ai" 판정 기록)로, '꾸준히 되나'와 '여행에서 됐나'는 사용자 판정으로.

## 현재 상태 (2026-10-22, 배치 9 뒤 — 설계 결정 v1)
- 목표 7, 상태 7, 사실 52(앱 동작 15 + 조사 근거 37), 관찰 6, 가설 36(이전 버전 1), 규칙 22(이전 버전 5: R_similar_interleave 계열 1 + v2로 개정한 4), 판정 기록 8(모두 source=ai).
- 사용자 방향(2026-10-22): 배운 것을 계속 다시 써먹는 구조, 글자보다 대화, 복습은 1일·7일 정도면 됨, 화면은 다른 시스템에서, **설계 결정은 AI에게 위임**(O_user_delegates_design). 상태로 옮긴 것: S_conversation_first·S_simple_review·S_solo_app.
- 조사 배치 9(p22–p27, 클라우드 searching 세션 Haiku 5.5): 말하기·듣기 연구, 대화 앱 장치, 다시 써먹는 구조, 화면 패턴, 여행 대화 대본, 실험·단기 코스. 원문 약 130건. 새로 확정: 대화 앱 13곳의 첫 주 골격 공통(F_apps_speaking_loop), ASR 혼자 연습 불확실(F_r_asr_meta), 초급 쉐도잉 23주 원문(F_r_shadowing_beginner), 레슨 안 재등장 vs 별도 복습 비교 연구 없음(F_r_no_inlesson_vs_separate), 'Webb 10번'은 검사 방식(F_r_webb_generation), NHK 대본은 개인 용도 한정(F_nhk_easy_japanese), 장면별 접객 원문(F_travel_scripts), 화면 12역할 표(F_ui_patterns). 조사 범위 돌아보기는 O_scope_batch9.
- **설계 결정 v1**(AI, 사용자 위임): 장면 대화 단위(R_scene_units_v2), 줄 종류별 방향(R_two_directions_v2), 틀+슬롯(R_frame_slot), 별도 복습 + 소량 재등장 + 역할극(R_reuse_structure), 당일→1→7→여행 전 점검(R_spacing_wider_v2), 하루 세션(R_daily_session), 가나 보조 트랙(R_kana_plan_v2), 데이터 자체 작성(R_data_own_scripts), 화면 패턴 12(R_ui_patterns_v1), ASR 나중(R_asr_later), 측정 고리(R_measure_cycle). 기존 R_known_retest·R_backlog_cap·R_daily_habit·R_patterns_reading·R_data_review 채택. 사용자용 문서는 language_learning 저장소 `docs/study-system-design-v1.md`(제안 v0.1을 대신함). 앱 코드는 아직 안 바꿈.
- **audit 오류 2(의도)**: H_false_known_lost·H_recognition_only_gap — 결정은 '고친다'(R_known_retest·R_two_directions_v2). 앱이 바뀌어 F_known_not_retested·F_review_one_direction이 새 커밋 해시로 갱신될 때까지 남는다. H_backlog_risk는 G_request·G_recognize의 대가로 받아들임(accepted_for, 상한 30 조건).
- 경고: 시험 수단 없음 45 — 모두 test_plan만. 이벤트 로그 재생 검사가 붙으면 줄어든다.
- 코드에서 본 결함(규칙이 아니라 고칠 일): 완료 기준 세 곳 불일치(F_archive_threshold_mismatch), 복습 기준 시각 고정(F_review_now_frozen), 가짜 최고 기록(F_streak_from_log). 구현 1단계에서 같이 고친다.
- 사용자 조건 미확인: 여행 시기·기간·동행 수, 하루 공부 시간(설계는 기본값 8주·15분), 한자 지식(H_korean_kanji_meaning).

## 다음 할 일
1. 구현(사용자가 설계 v1을 보고 바꿀 것이 없으면): `docs/study-system-design-v1.md` 7절 순서로 한 에이전트에 몰아서 — 1단계 데이터·복습(장면/줄/틀 테이블, 간격표, 알았음 1일 재시험, 상한 30, 줄 종류별 카드) → 2단계 홈·온보딩·꾸준함 → 3단계 재사용·측정 → 4단계 가나·ASR. 변경 뒤 관련 사실을 새 커밋 해시로 갱신하고 audit 오류 2건을 닫는다.
2. 데이터: 장면 7개의 줄 약 80개를 F_travel_scripts의 원문 문장으로 쓰고 줄마다 출처 칸(R_data_own_scripts). 미확보 장면은 '원문 미확인'.
3. 실사용 기록 재생 검사: 이벤트 로그 내보내기 → `checks.py`에 H_known_overconfident·H_review_1_7_trip·H_separate_review_primary·H_frame_slot_reuse부터.
4. 사용자 판정: 2주 확인 세트와 여행 뒤 장면별 '들렸다/말했다'를 `[[judgment]] source="user"`로.
