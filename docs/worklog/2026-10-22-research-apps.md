# 2026-10-22 — 조사: 앱 사례 — 일본어·언어 학습 앱에서 잘 된 장치와 안 된 것

에이전트: 조사 작업자 (Haiku 5.5, high). 하위 에이전트 호출: 없음.
커밋·push: 안 함.

## 한 일

- 조사 보고서 작성: `out/research/2026-10-22-language-learning/apps.md` (315줄). 후보 11개 (Anki+FSRS, WaniKani, Duolingo, Memrise, Pimsleur, Busuu, Bunpro, Renshuu, LingoDeer, Dr. Moku, Tofugu 가나 가이드), 탈락 후보 4건, 각도 요약, 조사 범위 돌아보기 절.
- 이 작업 보고서 작성.
- 저장소의 다른 파일은 수정하지 않음.

## 확인한 것 (어떻게)

- 웹 검색 16회 (검색어 목록은 apps.md 0절).
- WebFetch로 en.wikipedia.org 문서 5개를 읽음: Spaced_repetition, Duolingo, Anki_(software), Memrise, Busuu. Duolingo 문서는 약 17만 자 중 10만 자까지만 읽혔다 (요약 도구의 안내). Pimsleur_method, WaniKani 문서는 404.
- WebFetch로 blog.duolingo.com, docs.ankiweb.net, faqs.ankiweb.net, knowledge.wanikani.com, www.tofugu.com 시도: 호스트 해석 실패 (ENOTFOUND).
- 직접 curl 확인 (`curl -sS -m 15 -o /dev/null -w "%{http_code}" <URL>`):
  - en.wikipedia.org/wiki/Spaced_repetition → 200.
  - duolingo.com/efficacy, reddit.com/r/LearnJapanese, docs.ankiweb.net, blog.duolingo.com, knowledge.wanikani.com, github.com/open-spaced-repetition/fsrs4anki → "CONNECT tunnel failed, response 403" (정책 차단으로 보임). duolingo.com/efficacy, reddit, docs.ankiweb.net은 재시도 1회 했고 같은 결과였다.
  - memrise.com, pimsleur.com, busuu.com, bunpro.jp, renshuu.org, tofugu.com, community.wanikani.com → 응답 코드 000 (연결 실패).
- `curl -sS "$HTTPS_PROXY/__agentproxy/status"`: 최근 거부 기록에 blog.duolingo.com, knowledge.wanikani.com 403이 있었다. 이 작업이 요청하지 않은 damoang.net 403 기록도 함께 있었다 (다른 활동으로 보임).
- 우회 시도는 하지 않았다. 403은 재시도하지 않았다.
- 보고서 파일: Write로 생성한 뒤 Bash heredoc으로 이어 썼다. 완성 후 `grep '^## '`로 절 구조를 확인했고 `wc -l`은 315였다.

## 확인 못 한 것

- 공식 문서 원문 대부분 (Anki FAQ, WaniKani 지식베이스, Duolingo 효과 페이지, Tofugu 가나 가이드, Bunpro, LingoDeer, Renshuu). 검색 요약만 사용했고 보고서에 "검색 요약만"으로 표시했다.
- Anki 기본 학습 단계 값 (1분·10분·1일·4일). 출처를 찾지 못해 "(일반론)"으로 표시했다.
- 대부분 앱의 세션 길이, 스트릭·알림 세부, 한국어 UI 지원 여부.
- 시원스쿨 일본어·야나두 일본어의 실제 후기 (검색 결과가 무관한 기사뿐이었다).
- Wikipedia 요약에 인용된 원연구의 원문과 저자 확인. 인용 정리만 기록했다.

## 알려진 문제

- 검색 요약과 Wikipedia 요약은 2차 자료다. 메인이 근거 강도를 판단할 때 원문 미확인을 고려해야 한다.
- 핵심 원문 (Duolingo 효과 페이지, WaniKani 공식 표, Anki FAQ)이 접근 차단으로 빠졌다. 이 상태에서 "효과 연구" 판단은 불완전하다.
- 보고서를 쓰는 도중 apps.md가 외부에서 바뀌었다는 표시가 있었다. 변경 내용은 읽지 않았다. 제목·절 구조와 줄 수(315)는 확인했다. 다음 작업자는 diff를 확인하는 것이 좋다.
- Wikipedia의 Pimsleur_method와 WaniKani 문서가 404다. 문서 제목이 다를 수 있다.

## 다음 작업자에게

- 원문 확인 우선순위:
  1. Anki FAQ의 FSRS 첫 간격과 기본 학습 단계 값.
  2. WaniKani 공식 SRS 표 (첫 대기 4시간 확인).
  3. Duolingo 효과 페이지 (독립 연구 목록).
  4. Tofugu 가나 가이드 원문 (열 구성, 세션 크기).
  5. LingoDeer·Renshuu의 가나 드릴 여부.
- 막힌 호스트 (403 또는 연결 실패)를 접근 허용 목록에 넣을지는 메인이 판단해야 한다. 우회하지 말 것.
- 가나 입문 설계에 직접 쓸 만한 후보: 후보 11 (열 단위 학습과 헷갈리는 쌍 차트), 후보 9 (객관식만으로는 떠올리기 훈련이 약함).
- 첫 복습 1일 간격의 근거는 약하다. 앱마다 첫 간격이 수 초에서 1일까지 다르다. 간격 실험 설계가 필요하다.
- 블로거와 포럼 사용자의 실명·계정은 적지 않았다.
