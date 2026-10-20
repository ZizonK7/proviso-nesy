# 2026-10-20 — Flowlog 유사 앱·시장 조사

에이전트: 유사 앱·시장 조사 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

## 한 일
- 조사 결과 파일: `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/reports/03-similar-projects-market.md` (약 500줄, 저장소 밖 임시 폴더).
  - 맨 위 한눈 표(15개) → 0. 출처 확인 방식 → 1. Flowlog 요약 → A. 후보별 엄격 양식 15개 → B. 시장(규모·수익 모델·1인 앱 위치·Flowlog 시장 가치) → C. 공통 교훈(호평 5, 비판 5, 그만두는 이유 5).
- 후보 15개: 오픈소스 6(Simple Time Tracker, ActivityWatch, Super Productivity, Loop Habit Tracker, Kimai, TimeTagger), 상용 9(Toggl Track, Clockify, RescueTime, ATracker, aTimeLogger, Structured, Forest, 열품타 YPT, 투두메이트). 한국 앱 2개.
- 1인 앱 성공·정체 사례로 Watson, Timecop, Rize, Timing을 B3에 추가(후보 양식은 아님).
- 저장소 파일은 이 보고서 하나만 만들었다.

## 확인한 것 (어떻게)
- `/home/user/Flowlog/README.md`를 읽어 Flowlog 기능을 정리(앱 동작은 README 기준, 코드는 안 봄).
- WebFetch로 **실제로 열어 읽은 페이지 43개**(모두 2026-10-20):
  - github.com 38개 — 6개 오픈소스 후보의 저장소 첫 화면·커밋 목록·반응 순 이슈 목록, 개별 이슈(Simple Time Tracker #167 #173 #237 #499, ActivityWatch #35 #144 #259, Kimai #963, Loop #702, TimeTagger #55 #159), Super Productivity Android 이슈 검색, toggl-open-source 조직, timecop·traggo·Watson 저장소와 커밋.
  - en.wikipedia.org 5개 — Toggl, Toggl_Track, Forest_(app), Time-tracking_software, Quantified_self.
- GitHub 별 수·최근 커밋 날짜는 위 페이지에서 직접 읽었다. 예: Super Productivity 별 23.0k·2026-10-19 커밋, ActivityWatch 19.3k, Loop 10.3k, Kimai 5.1k, TimeTagger 1.8k, Simple Time Tracker 1.2k, Watson 2.5k·마지막 커밋 2022-07-15.
- WebSearch 약 24회. 그 결과 요약에만 있는 내용은 보고서에 모두 **[검색 요약 · 열지 못함]**으로 따로 표시했다(본문에 '열어 봄' 64곳, '열지 못함' 80곳).

## 확인 못 한 것
- **네트워크 제한**: 이 세션에서 WebFetch가 열리는 곳은 github.com·en.wikipedia.org뿐이었다. 막힌 곳(ENOTFOUND 또는 가져오기 불가): play.google.com, apps.apple.com, f-droid.org, reddit.com, news.ycombinator.com, hn.algolia.com, alternativeto.net, capterra.com, trustpilot.com, producthunt.com, indiehackers.com, toggl.com, community.toggl.com, structured.app, forestapp.cc, namu.wiki, ko.wikipedia.org, statista.com, grandviewresearch.com, fortunebusinessinsights.com, businessofapps.com, globenewswire.com, techcrunch.com, medium.com, dev.to, stackoverflow.com, jibble.io, appgoblin.info, chrome-stats.com, pmc.ncbi.nlm.nih.gov, arxiv.org. `gh api`도 이 세션에서 저장소 접근이 막혔고(403), curl로 github.com도 403.
  - 그래서 **스토어 별점·다운로드 수, 상용 앱 리뷰, 시장 규모 숫자, 그만두는 이유 연구는 전부 원문을 열지 못했다.** 검색 엔진 요약에 나온 값이다.
- 한국 앱: 검색이 미국 위주라 한국어 검색이 거의 안 됐다. 열품타 비판은 싱가포르 학생 신문 한 편, 투두메이트 비판은 App Store 리뷰 한두 개와 업데이트 노트가 근거라 약하다. 투두메이트 규모 기사(가입 27만+)의 발행 연도를 모른다.
- 후보 예시 중 Goodtime(adrihanu/goodtime)은 GitHub 주소가 404여서 뺐다. Timely, Sectograph, Opal, Timery, Rize는 후보 양식으로 조사하지 않았다(Rize는 B3 사례로만).
- 1인 앱 매출: Rize(2022 자기 보고 월 1.1만 달러)만 숫자가 있고 원문을 못 열었다. TimeTagger·Timing·Super Productivity 매출은 공개 숫자를 못 찾았다.
- "시간 기록 앱"만 다룬 중단 이유 연구는 찾지 못했다. C3은 자기 기록·활동량계·생활 앱 연구 + 후보 불만을 합친 것이다.

## 알려진 문제
- GitHub 커밋 날짜가 여러 저장소에서 2026-10-18~19로 몰려 나왔다. 페이지에 그렇게 나왔지만, 상대 날짜("어제")를 변환하는 과정의 영향일 수 있다. 정확한 날짜가 판단에 중요하면 다시 확인할 것.
- GitHub 이슈 목록의 숫자는 페이지에 이름표가 없어서 '반응 수'인지 '댓글 수'인지 확실하지 않은 경우가 있다(보고서에는 대개 반응으로 적음).
- 시장 규모 보고서들은 회사용(B2B) 근태 소프트웨어 중심이고 서로 2배 넘게 다르다. Flowlog 같은 개인용 앱 시장 크기로 쓰면 안 된다.
- 경쟁사가 쓴 리뷰(Jibble → ATracker, Timely·BuddyPunch → Clockify)가 섞여 있다. 보고서에 표시했다.
- "학생 계획표 + 실제 시간 + Todo 연결 조합을 가진 앱 0개"는 이번 15개 범위에서의 결과다. 한국·일본 앱을 충분히 못 봐서 놓쳤을 수 있다.

## 다음 작업자에게
- 이 보고서를 판단에 쓸 때 **[열어 봄]만 확정 근거로, [검색 요약 · 열지 못함]은 방향 참고로** 볼 것.
- 스토어 숫자·한국 앱 리뷰가 꼭 필요하면 이 환경의 네트워크 허용 목록을 넓히거나(Play·App Store·나무위키 등), 사용자 PC에서 직접 확인해야 한다.
- 여러 후보에서 겹친 교훈(메인이 Flowlog 방향을 정할 때 볼 것): (1) 동기화가 오픈소스 경쟁자의 최대 약점이고 Flowlog에는 이미 있다. 다만 1인에게는 가장 비싼 기능. (2) "켜는 걸 잊음 / 끼어든 일 / 지난 기록 고치기"가 공통 불만 → 빈 시간 채우기, 너무 오래 도는 타이머 알림, 시간표에서 끌어 고치기. (3) 돌아보기에서 얻는 것(주간 요약, 계획 vs 실제, 강도 점수)이 그만두기를 막는 쪽으로 다음 숙제.
- 출시 판단 재료: 이번 조사의 성공 사례는 모두 최소 F-Droid나 Play에 있다. Flowlog는 직접 빌드 + 자기 Firebase가 필요해서 지금은 일반 사용자가 설치할 수 없다.
