# 2026-10-27 — 첫 장면 브라우저 플레이판 v0 (배치 27, p76)

에이전트: 구현 Opus 5.5 high(세션 안). 메인(클라우드 세션)이 감독·검토·발행. 하위 에이전트 호출: 없음.
커밋·push: 메인이 함(movie_game `proto/scene01-play/`, proviso-nesy main). 작업자는 커밋하지 않음.

## 한 일
- 설계 데이터 `content/case01/scene01.json`을 글자 그대로 내장한 한 장짜리 페이지. 시작 → 의뢰(221B) → 거리 → 현장(뒷방) → 보드 → 결론 → 끝 화면(플레이 로그 10칸 + events + 설문 6개 + JSON 복사 + 다시 하기).
- 규칙 구현: 1단계 핫스팟은 표시·윤곽 없음(커서만), 2단계는 켜진 질문 + [관찰](3초 잠금, 횟수 집계)일 때만, 보드는 세 칸이 다 찰 때만 판정·틀린 칸만 비움·칸 종류별 반응(두 번째부터 "Not there.")·왓슨의 잘못된 제안 한 번, 결론은 큰 글자 2초 + 안쪽 문.
- 비공개 아티팩트로 발행: https://claude.ai/artifact/2MZv9MPnnoad3MnFZobHeu. 소스(템플릿·빌드·시험)는 movie_game `proto/scene01-play/`.

## 확인한 것 (어떻게)
- 작업자: Playwright 자동 플레이 61/61 통과, 콘솔 오류 0. Q 없이 관찰 → 속말만 / 두 칸만 찼을 때 무반응 / 1단계 핫스팟 윤곽 없음(계산된 스타일) / 1280·400px 가로 스크롤 없음 / 형식(doctype 없음, 외부 주소 fonts.googleapis.com뿐).
- 메인: 스크린샷 두 장(의뢰 장면, 보드 반응)을 직접 보고 발행. 실측 `scripts/agent_usage.py`: 14.1분·40턴·5.44M.

## 확인 못 한 것
- 아티팩트(https) 안에서 클립보드 복사가 되는지(file://에서는 실패 경로만 확인). 실제 휴대폰 터치(끌기는 마우스용). 다크 모드 화면. 사람이 1단계 부위를 실제로 찾아내는지 — 사용자 판정 몫.

## 알려진 문제
- JSON에 없어 페이지에 보탠 것: 합친 카드 이름(MERGED), "Nothing to ask yet." 자막, 대사 순서(FLOW), 설문 문구. 핫스팟 위치·2단계 부위 그림·합친 카드·보드 장소는 템플릿에 손으로 맞춤.
- Q2가 켜진 뒤 221B·거리에서 관찰하면 3초를 치르고도 아무것도 안 열린다("헛관찰", 규칙대로).
- 관찰 뒤 톱밥은 잘 보이고 굽 진흙은 아주 희미함(조정값 `.reveal` data-on). 결론 글자는 4.2초 뒤 자동으로 사라짐. 핫스팟은 키보드로 못 고름.
- 작업자가 보고서 파일을 쓰지 못함(도구가 scratchpad 쓰기를 막음) → 메시지로 보고, 메인이 이 파일로 옮김.

## 다음 작업자에게
- 빌드 `python3 proto/scene01-play/src/build.py`, 시험 `node proto/scene01-play/src/playtest.js`. JSON을 바꾸면 내용은 다시 빌드만, 핫스팟 위치·대사 순서(FLOW)·합친 카드(MERGED)·보드 장소(BOARD_AT)는 템플릿 손질.
- 관찰 대가 `OBSERVE_LOCK_MS`(3000), 판정 지연 `JUDGE_DELAY_MS`(350), 결론 표시 `CONCLUSION_HOLD_MS`(4200). 반응 규칙은 `pickReaction()` 하나.
- 사용자가 플레이 뒤 끝 화면 JSON을 주면 논리집 `[[judgment]]`(가설 6개)로 올린다. 그 뒤 UE 판(docs/briefs/case01-ue-brief.md)에 반영.
