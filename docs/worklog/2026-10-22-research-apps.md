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

## 이어서: 원문 확인 (2026-10-22, 네트워크 허용 뒤)

- 지시: 메인이 "네트워크가 열렸다. 원문을 열어 확인하고 제자리에서 고쳐라"고 보냄. apps.md를 전체 다시 써서 같은 경로에 덮어썼다 (315줄 → 317줄).
- 원문 확인 수: 약 50건. 공식 문서·블로그 약 25쪽 (WaniKani 지식베이스 5, Anki 매뉴얼·FAQ 3, Tofugu 6, Duolingo 블로그 4 + 연구 페이지, Bunpro·LingoDeer·Renshuu·Memrise·Pimsleur·Busuu·Dr. Moku 공식 홈), 포럼 스레드 9개 (WaniKani 4, Bunpro 5), 앱 스토어 4쪽, 학술 PDF 1편 (CALL-EJ 2022), 네이버 블로그 후기 8편.
- 방법: WebFetch는 이 호스트들의 이름을 못 찾아(ENOTFOUND, 프록시를 안 탐) curl로 받았다. `curl -sS -L -A <브라우저 UA> -o <파일> -w "%{http_code}"`로 받고, 스크래치패드의 bs4 스크립트(`python3 -I`)로 본문만 뽑아 grep했다. Discourse 포럼은 `/t/<id>.json`, 네이버는 `m.blog.naver.com/<id>/<글번호>`로 받았다. PDF는 pypdf로 앞 3쪽.
- 바뀐 수치·판정:
  - WaniKani: Apprentice 3 간격 "약 23시간(커뮤니티)" → 1일 (공식). 전체 표 4h/8h/1d/2d/1w/2w/1mo/4mo, 레벨 1·2 가속 2h/4h/8h/1d, 오답 공식, 정시 내림, 레벨 1~3 무료, 가나는 전제 아님. 확신도 중간 → 높음(장치).
  - Anki: 학습 단계 "(일반론)" → 매뉴얼 예시 1m 10m, 재학습 최소 간격 1일, 희망 기억률 기본 90%, FSRS 첫 간격 3~5일 정상, 학습 단계 1일 미만 권장, "같은 날 반복은 장기 기억 기여 적음". 새 카드 기본값 수치는 매뉴얼에 없음 → "[원문에 없음]". 확신도 중간 → 높음(장치)/중간(효과).
  - Duolingo: 간격 방식 "모름" → HLR(반감기 회귀). 스트릭 수치 8개 추가 (2.4배, +3.3% D14, +10.5%/+19%, +14% D7, +4%/−5%, +0.38%, 3.6배). 가나: 히라가나→가타카나(섹션 1 초반)→한자(섹션 1 후반), 문자 탭 3개. CALL-EJ 리뷰로 선택 편향 비판 확인. 기준 (5) "확인 못 함" → "일부" (한국어 후기 1편). 우리 상황 적용 "일부" → "예".
  - Bunpro: 간격 "확인 못 함" → 4h/8h/24h/2d/4d/8d/2w/1mo/2mo/4mo/6mo (약 1년 2개월), 고스트 4h/12h/24h/48h. 하루 새 문법 1~10개, 스트릭·목표, 가나 연습 있음. 기준 (3) "아니오" → "일부". 우리 상황 적용 "아니오" → "일부".
  - LingoDeer: 세션 2~3개 묶음, 일일 목표 5/10/20 스타, "5분 레슨", 문제 유형 9가지. 확신도 낮음 → 중간.
  - Dr. Moku: 무료 "25% (2019)" → 히라가나 11자·가타카나 8자. 퀴즈 유형 확정.
  - Tofugu: 열 5자 구조, 워크시트 5분·10분 대기, 쓰기 생략 근거, 비슷한 글자 쌍 목록 확정.
  - Pimsleur: 30분 레슨, Daily Challenges, Reading Lessons 공식 확인. 간격 수치는 공식에 없음.
  - Memrise·Busuu·Renshuu: 공식 홈 확인. 간격 수치 없음. Busuu 가나 코스 있음 (기준 (3) "확인 못 함" → "예"). Renshuu 가나 경로 있음.
  - 각도 요약의 "가장 강한 근거 3개"를 Duolingo A/B → Anki 문서 → WaniKani·Bunpro 밀림 보고 순으로 바꿨고, "부딪히는 근거"에 하락 규칙·객관식 항목을 더했다.
- 새 후보 수: 2 (후보 12 시원스쿨 일본어, 후보 13 야나두 일본어). 1차 탈락에서 복귀. 출처는 네이버 블로그 글 제목만, 계정·실명 없음. 홍보성 글은 제외.
- 못 연 곳: reddit.com 검색·JSON 엔드포인트 (403 세 번: www+브라우저 UA, old.reddit, www+기본 UA. 서브레딧 목록 자체는 200). 사이트 거부로 적고 우회하지 않음. duolingo.com/efficacy (200이지만 스크립트 렌더링, 본문 72자). investors.duolingo.com (연결 실패), globenewswire.com (403), github.com fsrs4anki 위키 (403), knowledge.wanikani.com 레슨 묶음 페이지 (404, 경로 추정), en.wikipedia.org Pimsleur_method·WaniKani (404).
- 확인 못 한 것: Anki 새 카드/복습 기본값 숫자 (매뉴얼 본문에 없음). WaniKani 레슨 묶음 기본 크기. Duolingo 효과 연구의 원 보고서 PDF (CALL-EJ 리뷰로 대신). 한국어 UI 지원 여부 (어느 앱도 확인 안 함). CALL-EJ PDF는 앞 3쪽만 읽음.
- 알려진 문제: 포럼·후기 인용은 여전히 개인 보고다. Tofugu 리뷰는 WaniKani와 같은 회사(Tofugu LLC)의 글이라 Bunpro·LingoDeer·Dr. Moku 평가에 이해관계가 있을 수 있다. Duolingo 수치는 모두 회사 보고.
- 다음 작업자에게: 보고서 안 "[원문 확인]"은 2차에서 원문으로 본 항목, "[원문에 없음]"은 원문에 뒷받침이 없는 1차 주장이다. 스크래치패드의 받은 파일은 세션이 끝나면 사라지므로 수치는 보고서가 기준이다.
