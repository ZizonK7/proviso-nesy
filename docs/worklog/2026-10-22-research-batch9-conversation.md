# 2026-10-22 — 배치 9: 대화 중심 조사 여섯 건 (클라우드 'searching' 세션)

에이전트: 조사 작업자 여섯 (Haiku 5.5, 클라우드 환경 searching, `create_session`으로 생성, permission_mode 상속 'auto'). 메인이 이어서 지시(v2, 둘은 v3)를 `send_message`로 보냄. 하위의 하위 에이전트: 없음.
커밋·push: 작업자는 안 함(저장소 없음). 메인이 정리해서 커밋.

## 한 일
- 각도 여섯: speaking_listening(p22) · conversation_apps(p23) · reuse_structure(p24) · ui_patterns(p25) · travel_dialogues(p26) · experiments_courses(p27). 공통 지시서와 각도 지시서는 `out/research/2026-10-22-language-learning/briefs/batch9_*.md`(git 제외), 세션 id는 같은 폴더 `batch9_sessions.txt`.
- 1차 보고(생성 3~4분 뒤)는 원문 0~4건이라 완료 조건에 못 미쳐, 원문 최소 수·구체 주소(J-STAGE `_pdf/-char/ja`, Crossref/PubMed/ERIC API, play.google.com 패키지 주소, NHK 레슨 목록 등)를 적은 이어서 지시를 보냈다. 최종 보고서는 `out/research/2026-10-22-language-learning/<각도>.md`(v3는 같은 파일 뒤에 "v3 추가분"으로 이어 붙임), 1차 요약은 `batch9_v1/summaries_v1.md`.
- 메인이 보고서를 대조해 논리집에 넣었다: 상태 3(S_conversation_first·S_simple_review·S_solo_app), 사실 15, 관찰 1(O_scope_batch9), 가설 11, 규칙 12(새 8 + v2 개정 4: R_scene_units·R_two_directions·R_spacing_wider·R_kana_plan), 판정 기록 6(source=ai). 설계 결정은 language_learning 저장소 `docs/study-system-design-v1.md`.
- agent_usage: p22–p27 실측·돌아보기, 새 상태 S_cloud_session, 관찰 O_b9_cloud_haiku, 가설 H_cloud_session_rounds(SEEN_UNTIL p27). `docs/AGENT-LOG.md` 배치 9.

## 확인한 것 (어떻게)
- `PYTHONIOENCODING=utf-8 python -m proviso validate language_learning` → 문제 없음 (목표 7, 상태 7, 사실 52, 관찰 6, 가설 36, 규칙 22, 판정 기록 8).
- `python -m proviso audit language_learning` → 오류 2건(H_false_known_lost·H_recognition_only_gap — 의도: 앱이 바뀔 때까지 해치는 중), 경고 '시험 수단 없음' 45(재생 검사 미부착).
- `python -m proviso validate agent_usage` → 문제 없음. `python -m domains.agent_usage.dispatches` → 기록 문제 없음(152건), p22–p27 실측 표.
- `python -m unittest discover -s tests -t .` → 104개 통과.
- 실측은 `get_session`의 created_at→updated_at(분)과 usage 네 항목 합(토큰). 작업자 보고서의 원문 수는 보고서의 "이번 회차에 연 원문 수" 줄을 그대로 썼고, 메인이 원문을 다시 열어 보지는 않았다(메인이 직접 확인한 것은 열리는 도메인뿐).

## 확인 못 한 것
- 작업자가 적은 수치(g, p, wpm, 문장 원문)를 메인이 원문으로 재확인하지는 않았다. 보고서의 접근 표시('열어서 읽음'/'초록만'/'검색 요약만')를 그대로 믿고 강도를 매겼다.
- 턴 수: 세션 이벤트가 스트림 조각 위주라 세지 않았다(작업자 자기 보고 도구 호출 수 회차당 8~30).
- 앱 코드는 바꾸지 않았다. 설계 문서의 데이터 구조는 초안이다.

## 알려진 문제
- 화면 패턴은 스크린샷을 한 장도 못 봤다(스토어 alt 텍스트가 일반 문구). '강' 근거가 없다.
- 식당 입장 인원 말, 시착의 손님 말, 면세 점원 말은 원문 미확보 — 데이터에 '원문 미확인' 표시로 둔다.
- Albelihi 2022는 원문 수치 불일치. Semantic Scholar는 429가 잦다. Google Scholar는 세션에 따라 403.
- 1차 보고서(v1) 본문은 메인 세션 대화 기록에만 있다(요약만 파일로).

## 다음 작업자에게
- 클라우드 세션 조사를 또 보내면: 지시서에 "원문 n건을 열기 전에는 보고서를 보내지 말 것"과 열리는 주소 목록(이 보고서의 O_scope_batch9)을 처음부터 적는다. 그래도 1차가 얕으면 이어서 지시 1회를 계획에 넣는다(H_cloud_session_rounds).
- 설계 v1을 구현할 때는 `docs/study-system-design-v1.md` 7절 순서(데이터·복습 → 홈·꾸준함 → 재사용·측정 → 가나·ASR)로 한 에이전트에 몰아서. 줄 데이터는 R_data_own_scripts대로 출처 칸을 비우지 않는다.
- 논리집 audit 오류 2건은 앱이 바뀌어 F_known_not_retested·F_review_one_direction을 새 커밋 해시로 갱신하면 사라진다.
