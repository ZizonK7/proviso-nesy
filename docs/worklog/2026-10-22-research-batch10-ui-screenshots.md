# 2026-10-22 — 배치 10: 화면 패턴 스크린샷 회차 (ui_patterns v3·v4)

에이전트: 배치 9의 ui_patterns 클라우드 세션(Haiku 5.5, searching)에 메인이 `send_message`로 이어 보냄(v3 지시 08:37:49Z, v4 지시 08:42:50Z). 하위의 하위 에이전트: 없음.
커밋·push: 작업자는 안 함. 메인이 정리해서 커밋.

## 한 일
- 사용자 질문("디자인 쪽은 어떻게 된 거야? 스크린샷을 못 봤다고?")으로 드러난 빈틈을 메움. 원인은 v2 지시서가 '스크린샷 설명(alt 텍스트)'을 요구해 그림 파일 자체를 받아 보게 하지 않은 것. 이 세션(메인 환경)은 play.google.com이 프록시 403이라 searching 환경의 작업자가 받아 봄.
- 지시서(`out/research/2026-10-22-language-learning/briefs/batch10_ui_screenshots.md`): 스토어 HTML에서 `play-lh.googleusercontent.com/...=w1000` 주소를 뽑아 받고 Read로 열어 장별 기록. **전송 조건**: 앱 5개·30장을 실제로 본 뒤에만 보낼 것.
- v3(5.0분): 앱 6개 32장 + Duolingo 공식 블로그 3장. v4(2.2분): 나머지 35장(스픽 10 포함) + Duolingo 블로그 연속 기록·알림 글 그림 6장. 말해보카·Mondly 일부는 홍보 합성 목업으로 표시하고 '강' 계산에서 뺌. 보고서는 `out/.../ui_patterns.md`에 v3·v4 절로 이어 붙임.
- 논리집: F_ui_patterns를 실제 화면 근거로 다시 씀(강 5: 홈·카드·말하기 입력·역할극·듣기 / 중 7 / 약 1), R_ui_patterns_v1 방법을 고침(목록형 홈, 역할극 목표 칩, 완료 고비 축하, 복습 세 칸, 말하기 비교는 Speak식). 설계 문서 `docs/study-system-design-v1.md` 1·5·8절 갱신.
- agent_usage: p28 실측(7.2분·10.7M·0.94달러)과 돌아보기, 새 상태 S_send_gate, 관찰 O_b10_send_gate, H_cloud_session_rounds → v2(전송 조건 유무로 쪼갬). AGENT-LOG 배치 10.

## 확인한 것 (어떻게)
- `PYTHONIOENCODING=utf-8 python -m proviso validate language_learning` / `validate agent_usage` → 문제 없음. `audit agent_usage` → 오류 없음. `python -m domains.agent_usage.dispatches` → 기록 문제 없음(153건), p28 '높게 잡음'(잠깐).
- `python -m unittest discover -s tests -t .` → 통과(아래 커밋 전 실행).
- 실측: `get_session` usage의 앞 회차(p25) 대비 차이(캐시 읽기 1042.6만, 캐시 쓰기 22.2만, 출력 7.8만), 시간은 지시 전송 → v4 도착.

## 확인 못 한 것
- 작업자가 본 그림 70장을 메인이 다시 보지는 않았다. 장별 기록의 접근 표시(실제 캡처/목업)를 그대로 믿었다.
- 끊긴 뒤 복귀 화면, 오류·빈 상태, 알림 시각 설정, 녹음 점수 화면은 스토어 그림에 없어 근거가 여전히 없다.
- 턴 수는 세지 않았다(자기 보고 도구 호출 22+14).

## 알려진 문제
- 작업자 보고서 파일(세션 scratchpad)은 v3까지만이고 v4는 메시지로만 왔다. 메인 쪽 `ui_patterns.md`에 v4 절을 붙여 두었다.
- 작업자가 "메시지에 첨부된 그림 3장은 파일 경로가 없었다"고 했는데, 메인은 그림을 보낸 적이 없다. 무엇이었는지 확인 못 함(근거에 넣지 않았으니 영향 없음).

## 다음 작업자에게
- 클라우드 조사 지시서에는 전송 조건을 숫자로 적는다(S_send_gate). 그림을 봐야 하는 조사는 '설명 글'이 아니라 '그림 파일을 받아 Read로 열기'를 지시한다.
- 화면 구현 때 R_ui_patterns_v1의 출처 앱을 코드 주석에 남기고, 근거 '약'인 화면(복귀·오류·알림 시각)은 사용 뒤 고친다.
