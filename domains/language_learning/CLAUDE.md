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

## 현재 상태 (2026-10-22, 원문 확인 반영 뒤)
- 목표 5, 상태 4, 사실 35(앱 동작 15 + 연구·사례 근거 20), 관찰 2(조사 범위), 가설 25(이전 버전 1), 규칙 10(제안), 판정 기록 2.
- 조사 배치 7(검색 요약)과 배치 8(같은 작업자가 원문 약 200건 확인) 끝. 원문 확인으로 바뀐 것: 섞어 배우기 판정 뒤집힘(단어는 몰아서 → H_similar_interleave를 v2로 쪼갬), 확장 vs 고정 간격 차이 없음, 여행 장면·스트릭 보호·가나 연상의 근거 상승, 1차 오류(AI 생성 글·다른 앱 혼동·기사 오독·원문과 다른 요약) 제거. 아직 못 연 곳: Wiley·OUP 등 일부 출판사, Reddit, 네이버 카페 본문.
- **audit 오류 3(의도한 것, 사용자 결정 대기)**: H_false_known_lost(알았음 재시험 없음 → R_known_retest 제안), H_recognition_only_gap(복습 한 방향 → R_two_directions 제안), H_backlog_risk(R_known_retest의 부작용 → R_backlog_cap과 함께 받아들일지). 받아들이거나 고치면 accepted_for를 적거나 사실을 갱신한다.
- 경고: 시험 수단 없음 32 — 모두 test_plan만 있다. 실사용 기록 재생 검사(이벤트 로그 내보내기)가 붙으면 줄어든다.
- 제안 규칙 10개는 모두 가설이고 사용자 판정 전이다. 사용자용 정리는 language_learning 저장소 `docs/study-system-proposal-v0.md`(v0.1), 여행 앱 설계(기능 목록만)는 같은 곳 `docs/travel-app-design-v0.md`(v0.1).
- 코드에서 본 결함(규칙이 아니라 고칠 일): 완료 기준 세 곳 불일치(F_archive_threshold_mismatch), 복습 기준 시각 고정(F_review_now_frozen), 가짜 최고 기록(F_streak_from_log). 사용자가 앱 변경을 결정하면 같이 고친다.
- 사용자 조건 미확인: 여행 시기·기간·동행 수, 하루 공부 가능 시간, 한자 지식 수준(H_korean_kanji_meaning). 목표 G_use_in_japan 문장도 확인 대기(준비 뒤 여행 사례의 결과와는 맞는다, H_reading_first_gain).

## 다음 할 일
1. 사용자 판정: audit 오류 3건과 제안 규칙 10개 중 무엇을 받아들일지. 받아들인 규칙은 앱 변경으로 옮기고(language_learning 저장소), 변경 뒤 관련 사실을 새 커밋 해시로 갱신한다.
2. 원문 확인: 환경의 Allowed domains가 넓어지면 같은 작업자들에게 원문 확인을 이어 보낸다(우선 F_r_retrieval·F_r_spacing·F_r_implementation_intention·F_travel_scenes). 확인되면 note의 '검색 요약만'을 고친다.
3. 실사용 기록 재생 검사: 앱의 이벤트 로그를 내보내 `checks.py`에 재생 검사를 붙인다(H_known_overconfident·H_spacing_total_span·H_streak_small_min부터).
4. 데이터 작업: R_scene_units(장면 재배치), R_patterns_reading(패턴 읽기), R_kana_plan(연상·비슷한 쌍·탁음), R_data_review(검토) — 받아들이면 한 에이전트에 몰아서.
