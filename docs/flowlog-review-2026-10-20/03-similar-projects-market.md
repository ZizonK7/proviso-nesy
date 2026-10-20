# Flowlog 유사 앱·시장 조사 (2026-10-20)

조사자: 하위 에이전트 (Opus 5.5, effort high). 조사일: 2026-10-20.

## 한눈 표 (15개: 오픈소스 6, 상용 9 — 한국 앱 2)

규모 표시: ★ = GitHub 별(열어 봄), ⓢ = 검색 요약(열지 못함).

| 이름 | 종류 | 규모 | 호평 한 줄 | 비판 한 줄 | 배울 점 한 줄 |
|---|---|---|---|---|---|
| Simple Time Tracker | 오픈소스·1인·Android | ★1.2k, 2026-10-18 커밋 | 한 번 눌러 시작, 오프라인·무료 | 서버 동기화·일시정지 없음 | 파일 내보내기·자동 백업, F-Droid 배포 |
| ActivityWatch | 오픈소스·소규모·PC+Android | ★19.3k | 자동 기록, 데이터는 내 기기에 | 동기화 9년째 미완, "켜는 걸 잊는다" | 빈 시간 한 번에 채우기, 첫 화면은 오늘 숫자 |
| Super Productivity | 오픈소스·1인 중심·전 플랫폼 | ★23.0k | 할 일+시간+집중 무료, 계정 불필요 | 동기화 직접 설정, Android 알림·위젯 빈틈 | 할 일별 예상 vs 실제 시간 |
| Loop Habit Tracker | 오픈소스·1인·Android | ★10.3k | 가볍고 광고 없음, '습관 강도' 점수 | 동기화 5년 끌다 '계획 없음' | 연속 기록 대신 강도 점수, 알림에서 바로 체크 |
| Kimai | 오픈소스+클라우드·소규모·웹 | ★5.1k | 직접 설치, 청구·API까지 무료 | 일시정지 2019년부터 미해결, 투박한 화면 | 끼어든 일 뒤 이어 하기 |
| TimeTagger | 오픈소스+월 €3·1인·웹 | ★1.8k | 타임라인·태그로 간단 | 도는 기록이 잘 안 보임, 너무 오래 도는 타이머 알림 없음 | 평소보다 긴 활동 알림 |
| Toggl Track | 상용·회사·전 플랫폼 | ⓢ Play 100만+, 4.61 | 한 번 클릭 시작, 무료로 충분 | 모바일 사후 수정 투박, 무료 기능 축소 | 시간표에서 끌어 고치기 |
| Clockify | 상용·회사·전 플랫폼 | ⓢ 사용자 "수백만" | 무제한 무료, 단순 | 모바일 버그·동기화, 매번 프로젝트 선택 | 제목 추천이 입력 마찰을 푼다는 점을 내세우기 |
| RescueTime | 상용·회사·PC 중심 | ⓢ G2 4.2(93) | 손 안 대는 자동 기록 | 사생활, PC 밖 활동 못 잡음 | 주간 요약 알림 |
| ATracker | 상용·소규모·모바일 | ⓢ Android 10만+, 4.49 | 탭 한 번, 일회 구매 | 보기 방식 적음, 동기화 버그 | 일회 구매 모델 |
| aTimeLogger | 상용·소규모·모바일 | ⓢ Android 약 11만, 4.72 | 일시정지·동시 타이머, 그래프 | 개인정보 고지 불일치 의심 | 저장 위치를 한 화면으로 설명 |
| Structured | 상용·작은 회사·iOS 중심 | ⓢ 설치 약 15만(추정) | 색 블록 하루 타임라인 | 반복 일정 유료, 동기화, Android 차별 | 계획 블록 위에 실제 기록 겹치기 |
| Forest | 상용·회사·모바일 | ⓢ 약 85만 리뷰 4.4 / 위키 확인 | 나무 보상, 실제 나무 심기 | 2025-12 구독 전환 반발 | 기록이 쌓이는 그림(도시 은유) |
| 열품타 YPT (한국) | 상용·회사·모바일 | ⓢ Play 500만+, 4.6 | 친구와 공부 시간 공유·경쟁 | 비교·순위 압박, 광고 | 비교 없는 공부+생활 기록이라는 빈자리 |
| 투두메이트 (한국) | 상용·회사·전 플랫폼 | ⓢ 4.8, 가입 27만+(연도 미상) | 10~20대 인기, 친구 피드 | (근거 약함) Mac 한/영 전환, 광고 | 가벼운 공유(오늘 기록 이미지) |

## 0. 먼저 읽을 것 — 출처를 어떻게 확인했나

이 세션의 네트워크는 **github.com 과 en.wikipedia.org 만 열렸다.** Google Play, App Store, F-Droid, Reddit, Hacker News, Capterra, G2, 시장조사 회사 사이트, 각 앱 공식 사이트, 한국 사이트(나무위키 등)는 모두 "주소를 찾을 수 없음(ENOTFOUND)" 또는 "가져올 수 없음"으로 막혔다.

그래서 출처 표시를 세 가지로 나눈다.

- **[열어 봄]** — WebFetch로 실제로 열어 내용을 읽은 페이지. 날짜는 모두 2026-10-20.
- **[검색 요약 · 열지 못함]** — 검색 엔진(WebSearch)이 돌려준 결과 요약에만 나온 내용. 원문 페이지는 열지 못했다. 숫자는 검색 결과가 인용한 값이고, 원문과 다를 수 있다. **메인이 판단에 쓸 때는 한 단계 낮춰 볼 것.**
- **[추정]** — 위 둘을 바탕으로 한 조사자의 판단.

GitHub 별(스타) 수와 최근 커밋 날짜는 모두 [열어 봄]이다. 스토어 별점·다운로드 수는 전부 [검색 요약 · 열지 못함]이다(스토어 자체가 막혔다).

## 1. Flowlog 요약 (비교 기준)

`/home/user/Flowlog/README.md`(2026-10-20 읽음) 기준.
- Android 전용, 스토어 미출시(직접 빌드 + 자기 Firebase 설정 필요). 개발자 1인.
- 기록: 카테고리 빠른 타이머, 카테고리별 제목 추천(최근·자주 쓴 제목 가중, 안 쓰면 감쇠), 꾸준히 쓰는 카테고리를 빠른 버튼으로 승격, 운동 세트·반복 기록.
- 할 일(Todo)에 활동 시간을 연결해 실제 작업 시간 누적, 루틴 블록, 기상 후·식사 후·취침 전 부드러운 알림, 집중 모드(방해 금지 켜기), 홈 위젯.
- 돌아보기: 오늘 목록·시간표·카테고리 합계, 어제 비교, 최근 7일 평균, 빈 시간 수면으로 채우기.
- Google 로그인 → Firestore 동기화, 오프라인 우선(Room). 웹 대시보드: 통계, 운동 추세, **강의 계획표 붙여 넣으면 강의별 일정 생성**, 루틴 추적, 하루 한 번 체크인(동기·에너지·졸림).
- 추천은 전부 로컬 규칙(외부 AI 호출 없음).

## A. 유사 프로젝트 (후보별 엄격 양식)

---

### A1. Simple Time Tracker (Razeeman)
- **종류**: 오픈소스(GPL-3.0, Wear OS 앱은 MPL-2.0) / **플랫폼**: Android, Wear OS(Play판만) / **가격**: 무료, 광고 없음 / **개발 주체**: 1인(취미 프로젝트라고 본인이 밝힘)
- **규모 지표**
  - GitHub 별 1.2k, 포크 139, dev 브랜치 커밋 2,513 — [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker
  - 최근 커밋 2026-10-18(알림 색 그라데이션 등) — [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/commits/dev
  - 이슈 416건(반응 순 첫 페이지) — [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/issues?q=is%3Aissue+sort%3Areactions-%2B1-desc
  - F-Droid 최신 1.60(2026-09-21 추가), Android 5.0 이상 — [검색 요약 · 열지 못함] https://f-droid.org/packages/com.razeeman.util.simpletimetracker/
- **핵심 기능**: 한 번 눌러 활동 시작(여러 활동 동시 기록 — 검색 요약 근거), 태그·메모, 원형·막대·캘린더 통계, 위젯·알림, CSV 내보내기·자동 백업, 계정·인터넷 불필요.
- **호평**
  1. "매일 쓰는 최고의 FOSS(자유 오픈소스) Android 앱 중 하나" — 사용자가 후원하고 싶다고 연 이슈(2024-03-07). [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/issues/167
  2. 반복 작업·여러 일 동시 진행에 알맞다(미리 만든 '카드'로 시작) — HowToGeek. [검색 요약 · 열지 못함] https://www.howtogeek.com/6-best-time-tracking-apps-on-android/
  3. 오프라인·계정 없이 동작, 백업·위젯·다크 모드가 무료 — [검색 요약 · 열지 못함] https://apt.izzysoft.de/fdroid/index/apk/com.razeeman.util.simpletimetracker
- **비판**
  1. 서버 동기화가 없다 — "서버로 동기화" 요청이 2024-10부터 열려 있고 개발자 답 없음. [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/issues/237
  2. 일시정지가 없어 쉬는 시간마다 기록이 잘게 쪼개진다 — 개발자가 "과한 복잡화"라며 거절, 대신 '최근 시작한 활동 목록'은 검토. [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/issues/173
  3. 1.60 업데이트 뒤 자동 백업·표 내보내기가 멈췄다는 보고(원인 미확인, 폴더 다시 고르니 됨). [열어 봄] https://github.com/Razeeman/Android-SimpleTimeTracker/issues/499
  - 참고: 반응이 많은 요청 — Google 캘린더 연동(#31), 달력처럼 미리 일정 잡기(#161), PC 웹 화면(#427). [열어 봄] 위 이슈 목록 페이지.
- **Flowlog와 겹치는 점**: Android 네이티브, 카테고리 버튼으로 빠른 시작, 위젯·알림, 오프라인 우선, 1인 개발.
- **Flowlog에 없는 것**: 여러 활동 동시 기록(검색 요약 근거), Wear OS 앱, CSV 내보내기·자동 백업 파일, 목표(일·주 단위), F-Droid·Play 배포.
- **Flowlog에만 있는 것**: 서버 동기화 + 웹 대시보드(이 앱 사용자가 요청 중인 바로 그것: #237, #427), Todo에 시간 누적, 강의 계획표, 규칙 기반 제목 추천, 기상·식사 후 알림.
- **Flowlog가 배울 점**
  1. **기기 파일로 내보내기·자동 백업**(CSV/백업 파일). Firebase가 끊겨도 기록이 남는다는 안심을 준다. 이 앱은 이것만으로 동기화 없이도 신뢰를 얻었다.
  2. **F-Droid/IzzyOnDroid 배포.** 이 앱의 주 유입 경로다. Flowlog가 Firebase 없이도 도는 빌드(동기화 끔)를 만들면 같은 길로 첫 사용자를 얻을 수 있다.
- **확신도**: 높음 — 핵심 숫자와 비판 3개를 GitHub에서 직접 열어 봤다. 호평 2·3은 검색 요약뿐.

---

### A2. ActivityWatch
- **종류**: 오픈소스(MPL-2.0) / **플랫폼**: Windows, macOS, Linux, Android(iOS 없음) + 브라우저 확장 / **가격**: 무료, 기부로 운영 / **개발 주체**: 소규모 팀(Erik·Johan Bjäreholt 형제 중심 + 기여자)
- **규모 지표**
  - GitHub 별 19.3k, 포크 1.0k — [열어 봄] https://github.com/ActivityWatch/activitywatch
  - 최근 커밋 2026-10-18(v0.14.2 고정 등) — [열어 봄] https://github.com/ActivityWatch/activitywatch/commits/master
  - 이슈 929건 — [열어 봄] https://github.com/ActivityWatch/activitywatch/issues?q=is%3Aissue+sort%3Areactions-%2B1-desc
- **핵심 기능**: 지금 쓰는 앱·창 제목·브라우저 탭 **자동 기록**, 키보드·마우스로 자리 비움 감지, 데이터는 내 기기에만, 웹 화면 대시보드·타임라인·질의, 직접 만드는 '감시기(watcher)'로 확장.
- **호평**
  1. "AW를 개발해 줘서 고맙다… 여기 뭔가 있다고 확신한다" — 레딧 사용자 피드백을 옮긴 이슈. [열어 봄] https://github.com/ActivityWatch/activitywatch/issues/144
  2. 데이터를 내 기기에만 저장 — 사생활 보호가 핵심 장점. [열어 봄] https://github.com/ActivityWatch/activitywatch (README)
  3. 오픈소스·무료·설치 쉬움, RescueTime의 강한 대안 — AlternativeTo 리뷰 요약. [검색 요약 · 열지 못함] https://alternativeto.net/software/activitywatch/reviews
- **비판**
  1. **기기 간 동기화가 9년째 미완성** — 2017-03 연 이슈가 아직 열림(반응 103, 1위). 동기화 도구는 터미널 창을 계속 띄워야 한다는 불만(2024-09). [열어 봄] https://github.com/ActivityWatch/activitywatch/issues/35
  2. "켜는 걸 늘 잊는다", "내 경향을 분석하기 어렵다", 첫 화면에 통계 대신 환영 문구 — [열어 봄] https://github.com/ActivityWatch/activitywatch/issues/144
  3. 지속 가능한 자금이 없다 — 개발자: 기부가 "현재 비용을 겨우 덮는다", 개발비는 못 덮음. [열어 봄] https://github.com/ActivityWatch/activitywatch/issues/259
  - 그 밖에 macOS 권한 경고 반복(#334, #380), URL로 분류 불가(#352). [열어 봄] 위 이슈 목록.
- **Flowlog와 겹치는 점**: "실제로 시간을 어디 썼나"를 보여 주는 대시보드, 사생활 중시.
- **Flowlog에 없는 것**: PC 자동 기록, 자리 비움 감지, 사용자 확장(플러그인).
- **Flowlog에만 있는 것**: 손으로 하는 의도적 기록(공부·운동·식사 같은 PC 밖 활동), Todo 연결, 동작하는 동기화.
- **Flowlog가 배울 점**
  1. **"켜는 걸 잊는다"는 문제를 정면으로**: 자동 기록 앱조차 이것이 1순위 불만이다. Flowlog의 기상·식사 후 알림이 바로 이 지점이므로, "기록 안 된 빈 시간"을 하루 끝에 한 번 보여 주고 한 번에 채우게 하는 흐름을 다듬을 가치가 크다.
  2. 대시보드 첫 화면은 **오늘 숫자부터**(환영 문구 X).
- **확신도**: 높음 — GitHub에서 숫자·비판·호평을 직접 확인.

---

### A3. Super Productivity
- **종류**: 오픈소스(MIT) / **플랫폼**: Windows, macOS, Linux, Android, iOS, 웹 / **가격**: 무료(후원). 자체 암호화 동기화 'SuperSync'는 직접 호스팅 가능 / **개발 주체**: 사실상 1인 중심(johannesjo) + 큰 기여자 공동체
- **규모 지표**
  - GitHub 별 23.0k, 포크 2.2k, 커밋 약 22,574, 열린 이슈 1.3k — [열어 봄] https://github.com/super-productivity/super-productivity
  - 최근 커밋 2026-10-19(집중 모드 한 번에 시작 등) — [열어 봄] https://github.com/super-productivity/super-productivity/commits/master
- **핵심 기능**: 할 일·하위 할 일·프로젝트, 할 일마다 시간 기록과 근무 요약 내보내기, 포모도로·Flowtime 집중 모드와 휴식 알림, Jira·GitHub·GitLab 등 연동, Dropbox·WebDAV·SuperSync 동기화. 계정 불필요.
- **호평**
  1. 오픈소스라 전체 기능이 무료, 앱 안 결제 없음 — TechNewsWorld/LinuxInsider 리뷰. [검색 요약 · 열지 못함] https://linuxinsider.com/story/super-productivity-app-the-closest-ive-come-to-a-workflow-that-sticks-177717.html
  2. 방식을 강요하지 않는 유연함("내 작업 흐름이 처음으로 붙었다"는 제목의 리뷰) — 같은 출처 [검색 요약 · 열지 못함].
  3. 오프라인·계정 없음, 나중에 동기화 — Linux Mint 소프트웨어 목록. [검색 요약 · 열지 못함] https://community.linuxmint.com/software/view/com.super_productivity.SuperProductivity
- **비판**
  1. 동기화를 Dropbox·WebDAV 등 바깥 서비스로 직접 설정해야 한다 — Toolradar. [검색 요약 · 열지 못함] https://toolradar.com/tools/super-productivity/review . GitHub에도 "로컬 파일 동기화"(#690, #2001), "OneDrive"(#2109), "충돌 없는 다기기 동기화"(#4857) 요청이 많다. [열어 봄] https://github.com/super-productivity/super-productivity/issues?q=is%3Aissue+android+sort%3Areactions-%2B1-desc
  2. 기능이 많아 배우기 어렵고, 오래된 기기에선 무겁다 — SaaSHub. [검색 요약 · 열지 못함] https://www.saashub.com/compare-atracker-vs-super-productivity
  3. Android 쪽 빈틈: 알림이 안 온다(#3773, 반응 30), 홈 위젯 요청(#3818, #5139), Google 캘린더 연동이 Google에 막힘(#7221). [열어 봄] 위 이슈 목록.
- **Flowlog와 겹치는 점**: 할 일에 시간 누적(Flowlog의 Todo 연결과 같은 생각), 집중 모드, 루틴/반복.
- **Flowlog에 없는 것**: 데스크톱·웹에서 기록, 개발 도구 연동, 근무 시간표 내보내기, 칸반.
- **Flowlog에만 있는 것**: 할 일 밖의 생활 시간(수면·식사·운동)까지 한 줄 시간표로, 휴대폰 우선 빠른 버튼, 강의 계획표, 규칙 추천.
- **Flowlog가 배울 점**
  1. **할 일별 "예상 시간 vs 실제 시간"** 비교. Flowlog는 이미 실제 시간을 쌓으니 예상만 받으면 된다(학생이 과제 시간을 과소평가하는지 보여 줌).
  2. 1인 중심 프로젝트도 **"계정 없이 바로 쓰기"**로 문턱을 낮춰 2만 별을 모았다. Flowlog도 로그인 전 체험을 기본으로.
- **확신도**: 중간 — 숫자·Android 비판은 열어 봤지만 호평은 검색 요약뿐.

---

### A4. Loop Habit Tracker (iSoron/uhabits)
- **종류**: 오픈소스(GPL-3.0) / **플랫폼**: Android(iOS 판 요청은 닫힘) / **가격**: 무료, 광고·앱 안 결제 없음 / **개발 주체**: 1인(Álinson Santos Xavier) + 기여자
- **규모 지표**
  - GitHub 별 10.3k, 포크 1.3k — [열어 봄] https://github.com/iSoron/uhabits
  - 최근 커밋 2026-10-19(자동 백업 시간대 버그 수정, 1x2 위젯) — [열어 봄] https://github.com/iSoron/uhabits/commits/dev
  - 이슈 762건 — [열어 봄] https://github.com/iSoron/uhabits/issues?q=is%3Aissue+sort%3Areactions-%2B1-desc
- **핵심 기능**: 습관 체크, '습관 강도' 점수(며칠 빠져도 긴 연속 기록이 한 번에 0이 되지 않음), 유연한 일정(주 3회 등), 알림에서 바로 체크, 홈 위젯, CSV/SQLite 내보내기, 계정·인터넷 불필요.
- **호평**
  1. 가볍고 오래된 폰에서도 잘 돈다, 습관 수 제한·광고·앱 안 결제 없음 — README. [열어 봄] https://github.com/iSoron/uhabits
  2. "부담 없이 습관을 기록하는 데 정말 잘한다", "대안 앱이 없다", 동기화가 생기면 "기꺼이 돈을 내겠다"(2025-01) — 사용자 댓글. [열어 봄] https://github.com/iSoron/uhabits/issues/702
  3. 연속 기록 대신 '습관 강도'로 한 번 실수에 무너지지 않게 한 설계 — 리뷰 요약. [검색 요약 · 열지 못함] https://macaron.im/blog/loop-habit-tracker-review-simple-tracking
- **비판**
  1. **기기 간 동기화 없음.** 2021-01 이슈가 5년간 열려 있다가 2026-10-19 "오래된 이슈라 닫지만 계획은 있다"며 '계획 없음'으로 닫힘. "데이터를 잃을까 봐 무섭다"(2024-09). [열어 봄] https://github.com/iSoron/uhabits/issues/702
  2. iOS·여러 플랫폼판 요청(반응 33, 24)이 받아들여지지 않음 — [열어 봄] 위 이슈 목록(#486, #487).
  3. 이미 입력했는데도 알림이 또 묻는다(#1573, 열림), 색 구분·첫 사용 안내가 없다는 리뷰 — [열어 봄] 이슈 목록 / [검색 요약 · 열지 못함] macaron.im 위 링크.
- **Flowlog와 겹치는 점**: Flowlog의 루틴 블록·Daily Cues(하루 가벼운 할 일) 추적, 위젯, 알림, Android·1인.
- **Flowlog에 없는 것**: 실패해도 무너지지 않는 '강도' 점수, 주 n회 같은 유연한 목표, 알림에서 바로 완료 표시.
- **Flowlog에만 있는 것**: 습관을 '했나/안 했나'가 아니라 **실제 걸린 시간**으로 기록, 동기화·웹 루틴 추적.
- **Flowlog가 배울 점**
  1. 루틴 추적(웹 `/routine/`)에 **연속 기록 대신 '강도' 점수**: 하루 빠져도 의욕이 꺾이지 않게. 학생 시험 기간처럼 일정이 흔들리는 사용자에게 특히 맞다.
  2. **알림에서 바로 "했음/건너뜀"** — 앱을 열지 않고 끝나는 기록이 '기록 마찰을 줄인다'는 Flowlog 목표와 같다.
- **확신도**: 높음 — 숫자와 핵심 비판을 GitHub에서 직접 확인. (시간 기록 앱이 아니라 습관 앱이라 직접 경쟁은 아님.)

---

### A5. Kimai
- **종류**: 오픈소스(AGPL-3.0) + 유료 클라우드(kimai.cloud) / **플랫폼**: 웹(직접 서버 설치, PHP·MySQL) / **가격**: 직접 설치 무료, 클라우드 유료(가격은 열어 보지 못함), 유료·무료 플러그인 시장 / **개발 주체**: 소규모(주 개발자 Kevin Papst 중심 조직)
- **규모 지표**
  - GitHub 별 5.1k, 포크 863, 열린 이슈 307 — [열어 봄] https://github.com/kimai/kimai
  - 최근 커밋 2026-10-19 — [열어 봄] https://github.com/kimai/kimai/commits/main
  - Capterra 3.6점(7개, 대부분 2018–2019) — [검색 요약 · 열지 못함] https://www.capterra.com/p/182440/Kimai/reviews/
- **핵심 기능**: 여러 사람·팀용 시간 기록, 고객·프로젝트·활동별 요율, 청구서·내보내기, JSON API, LDAP·SAML·2단계 인증, 예산.
- **호평**
  1. 직접 설치해서 데이터가 내 서버에 남는다, 작은 팀에 안정적 — Capterra 리뷰 요약. [검색 요약 · 열지 못함] 위 Capterra 링크
  2. 무료·오픈소스인데 청구서·API·플러그인까지 — 같은 출처.
  3. 사용자: "거의 모든 사용자에게 도움이 될 필수 기능"이라며 오래 요청할 만큼 계속 쓰는 충성 사용자층(아래 #963) — [열어 봄]
- **비판**
  1. **일시정지 버튼이 없다** — 2019-07 요청, 아직 열림. 전화 한 통에 기록이 여러 개로 쪼개져 고치는 일이 늘어난다. 한 사용자는 Clockify로 옮겼다. 논쟁이 격해져 2023-08 댓글 잠금. [열어 봄] https://github.com/kimai/kimai/issues/963
  2. 화면이 투박하고 오래된 느낌, 고객-프로젝트-활동 구조가 고정 — [검색 요약 · 열지 못함] Capterra
  3. 기본 고객·프로젝트 지정(#403, 반응 14), 캘린더(CalDAV) 동기화(#361) 같은 입력 편의 요청이 상위 — [열어 봄] https://github.com/kimai/kimai/issues?q=is%3Aissue+sort%3Areactions-%2B1-desc
- **Flowlog와 겹치는 점**: 거의 없음(기록·통계라는 큰 틀만).
- **Flowlog에 없는 것**: 청구·요율·팀 권한.
- **Flowlog에만 있는 것**: 휴대폰 빠른 기록, 생활 시간 전체, 개인 루틴.
- **Flowlog가 배울 점**: **일시정지/이어 하기** — 여러 오픈소스(Kimai #963, Simple Time Tracker #173)에서 반복되는 요청. Flowlog가 Todo 시간 누적을 하므로 "같은 Todo로 이어 하기"는 이미 반쯤 된다. 쉬는 시간이 끼어도 한 Todo의 기록이 자연스럽게 이어지는지 확인할 가치.
- **확신도**: 중간 — 대상이 기업·프리랜서라 Flowlog와 거리가 멀다. 비교의 쓸모는 '반복되는 요청' 확인 정도.

---

### A6. TimeTagger
- **종류**: 오픈소스(GPL-3.0) + 유료 호스팅(timetagger.app) / **플랫폼**: 웹(반응형, 휴대폰 브라우저 가능), 직접 설치(pip·Docker) / **가격**: 직접 설치 무료, 호스팅 월 €3 / **개발 주체**: 1인(Almar Klein)
- **규모 지표**
  - GitHub 별 1.8k, 포크 169 — [열어 봄] https://github.com/almarklein/timetagger
  - 최근 커밋 2026-09-28(오타 수정), 그 전 2026-05-17 — 활동이 뜸해짐 — [열어 봄] https://github.com/almarklein/timetagger/commits/main
  - 호스팅 가격 "계정은 월 €3" — [열어 봄] 위 README
- **핵심 기능**: 타임라인을 끌어서 보는 화면, 프로젝트 대신 태그(#공부 #수학), PDF·CSV 보고서, 일·주·월 목표, 실험적 포모도로, 기기 간 동기화.
- **호평**
  1. 타임라인 화면과 태그 방식이 간단하다 — README 소개. [열어 봄]
  2. 직접 설치로 사생활 보호가 강하고, 낭비 시간을 찾는 데 도움 — MakeTechEasier 개인 사용기. [검색 요약 · 열지 못함] https://maketecheasier.com/timetagger-time-tracker-improves-productivity
  3. 간단한 조작으로 작업 내용과 시간을 기록 — GIGAZINE 체험기. [검색 요약 · 열지 못함] https://gigazine.net/gsc_news/en/20210723-timetagger
- **비판**
  1. 지금 기록이 돌고 있는지 잘 안 보였다 — 한 번 고쳤는데 "여전히 너무 은은하다"며 다시 열림, 두 번째에 해결(2022-02~03). [열어 봄] https://github.com/almarklein/timetagger/issues/159
  2. 타이머를 끄는 걸 잊는다 → "x시간 넘게 돌면 알려 달라" 요청이 2021-02부터 '아이디어'로 열려 있음. [열어 봄] https://github.com/almarklein/timetagger/issues/55
  3. 팀 지원 없음(#142, 댓글 19), 배경 동기화 안 됨(#439) — [열어 봄] https://github.com/almarklein/timetagger/issues?q=is%3Aissue+sort%3Areactions-%2B1-desc
- **Flowlog와 겹치는 점**: 1인 개발 + 동기화 + 웹 화면, 하루 타임라인, 일 목표.
- **Flowlog에 없는 것**: 유료 호스팅 수익 모델, PDF 보고서, 태그 자유 입력.
- **Flowlog에만 있는 것**: 네이티브 Android(알림·위젯·방해 금지), Todo 연결, 규칙 추천.
- **Flowlog가 배울 점**
  1. **"너무 오래 돌고 있는 타이머" 알림** — 모든 시간 기록 앱의 공통 고장 지점. Flowlog는 이미 '무활동 알림'이 있으니, 반대 방향(평소보다 훨씬 긴 활동)도 잡으면 된다(카테고리별 평소 길이는 이미 데이터에 있음).
  2. **1인 개발 유료 모델의 실제 예**: 오픈소스 + 월 €3 호스팅. Flowlog가 Firebase 비용을 사용자에게 넘기는 방식의 참고점.
- **확신도**: 높음(숫자·비판) / 수익 규모는 확인 못 함.

---

### A7. Toggl Track (상용)
- **종류**: 상용 / **플랫폼**: 웹, Windows, macOS, Linux(Flatpak), iOS, Android, watchOS / **가격**: 무료(최대 5명) + 유료 구독(팀 대상) / **개발 주체**: 회사(Toggl OÜ, 에스토니아 탈린, 창업자 Alari Aho "처음부터 외부 투자 없이 자체 자금")
- **규모 지표**
  - 회사 정보·플랫폼 — [열어 봄] https://en.wikipedia.org/wiki/Toggl_Track
  - Google Play 4.61점, 리뷰 24,957, 다운로드 100만+ (AppBrain, 2026-07-30 기준) — [검색 요약 · 열지 못함] https://www.appbrain.com/app/com.toggl.giskard
  - 예전 오픈소스 데스크톱 앱 toggldesktop(별 1.9k)은 2023-06 보관(archived) — [열어 봄] https://github.com/toggl-open-source
- **핵심 기능**: 시작/정지 한 번, 손 입력·캘린더에서 끌어 만들기, 프로젝트·고객·태그, 보고서, 여러 기기 같은 계정.
- **호평**
  1. 배우기 쉽고 한 번 눌러 타이머 시작 — Capterra 사용자 리뷰 요약. [검색 요약 · 열지 못함] https://www.capterra.com/p/247745/Toggl/reviews/
  2. 폰+PC를 한 계정으로 — 같은 출처.
  3. 무료 요금제로 기본 기록·보고는 충분하다(프리랜서) — 같은 출처.
- **비판**
  1. 모바일 앱에서 지난 기록 고치기·뒤늦게 세부 넣기가 투박하다, 시간 고치면 날짜가 바뀌어 기록이 틀어졌다는 리뷰 — [검색 요약 · 열지 못함] Capterra 위 링크
  2. **무료 기능을 예고 없이 줄였다**는 불만(보고서 보기 제한, 2025-11 API 호출 제한 무료 시간당 20회) — [검색 요약 · 열지 못함] https://community.toggl.com/t/could-you-please-consider-making-the-report-view-unlimited-again-for-free-plan-users/4479 , https://www.mediaatelier.com/en-CH/Posts/Toggl-Limits
  3. 기기 간 동기화 문제·무거워진 화면 — [검색 요약 · 열지 못함] Capterra
- **Flowlog와 겹치는 점**: 빠른 시작/정지, 여러 기기 동기화 + 웹 보고서.
- **Flowlog에 없는 것**: 데스크톱·브라우저 확장, 캘린더에서 끌어 만들기, 팀·청구.
- **Flowlog에만 있는 것**: 생활 시간(수면·식사) 중심, 학생 강의 계획표, 알림 기반 부드러운 유도, 규칙 추천.
- **Flowlog가 배울 점**
  1. **지난 기록 고치기**를 쉽게 — 가장 큰 회사 앱의 모바일 불만 1위가 "뒤늦게 고치기". Flowlog 시간표에서 블록을 끌어 늘이고 줄이는 편집이 있으면 차별점.
  2. 무료 기능을 줄일 때 반발이 크다 → 처음부터 **무료로 줄 것과 아닐 것을 정해** 두기.
- **확신도**: 중간 — 회사 사실은 열어 봤으나 리뷰는 모두 검색 요약.

---

### A8. Clockify (상용)
- **종류**: 상용 / **플랫폼**: 웹, 데스크톱, iOS, Android, 브라우저 확장 / **가격**: 무료(인원 무제한이 핵심 판매점) + 유료 기능 / **개발 주체**: 회사(CAKE.com)
- **규모 지표**
  - 사용자 "수백만"(자사 홈페이지), "200만+"(GetLatka 추정), 2019 보도자료 "35만+ 회사" — [검색 요약 · 열지 못함] https://clockify.me/de/ , https://getlatka.com/companies/clockify
- **핵심 기능**: 무제한 무료 시간 기록, 시간표(timesheet), 보고서, 프로젝트·청구, 팀 관리.
- **호평**
  1. 무료 요금제가 가장 큰 매력(프리랜서·작은 팀) — Timely 블로그. [검색 요약 · 열지 못함] https://www.timely.com/blog/clockify-reviews/
  2. 단순하고 직관적, 비기술직도 쉽게 — BuddyPunch 리뷰. [검색 요약 · 열지 못함] https://buddypunch.com/blog/clockify-review/
  3. 보고서와 지원이 좋다 — G2 요약. [검색 요약 · 열지 못함] https://www.g2.com/products/clockify/reviews?page=7
  - (경쟁사 블로그가 많아 치우칠 수 있음)
- **비판**
  1. **모바일 앱 안정성**: 버그, 동기화 지연, 자주 튕기고 로그아웃 — G2·Capterra 요약. [검색 요약 · 열지 못함] 위 G2 링크, https://www.capterra.com/p/169607/Clockify/reviews/?page=81
  2. 매번 프로젝트를 골라야 하는 번거로움, 화면 맞춤 부족 — [검색 요약 · 열지 못함] Capterra
  3. 큰 팀엔 급여 연동 등 기능 부족 — [검색 요약 · 열지 못함] BuddyPunch
- **Flowlog와 겹치는 점**: 기록 + 웹 보고.
- **Flowlog에 없는 것**: 팀·청구·근무표, 브라우저 확장.
- **Flowlog에만 있는 것**: 개인 생활 리듬, 학생 일정, 오프라인 우선(Clockify는 모바일 동기화 불만이 큼).
- **Flowlog가 배울 점**: **"매번 프로젝트 고르기"가 불만** → Flowlog의 제목 추천·자주 쓰는 버튼 승격이 바로 이 문제를 푼다. 이걸 차별점으로 말할 수 있다(근거: Clockify·Toggl 리뷰 모두 입력 마찰을 지적).
- **확신도**: 낮음~중간 — 모든 출처가 검색 요약이고, 경쟁사 블로그 비중이 크다.

---

### A9. RescueTime (상용)
- **종류**: 상용 / **플랫폼**: Windows, macOS, Linux, 모바일, 브라우저 / **가격**: Lite 무료(자동 기록, 기록 보관 12개월) + Premium 월 $12 또는 연 $78, Team 1인당 월 $9 / **개발 주체**: 회사
- **규모 지표**
  - 요금 — 공식 도움말. [검색 요약 · 열지 못함] https://help.rescuetime.com/article/387-rescuetime-plans
  - G2 약 4.2점(93개), Capterra 4.6(141개, 2026-03) — [검색 요약 · 열지 못함] https://www.g2.com/products/rescuetime/reviews_and_filters
  - en.wikipedia 문서 없음(404) — [열어 봄] https://en.wikipedia.org/wiki/RescueTime
- **핵심 기능**: PC·브라우저 사용 **자동 기록**, 생산성 점수, 방해 사이트 차단(FocusTime), 목표·주간 보고, Zapier 등 연동.
- **호평**
  1. 손대지 않아도 배경에서 기록 — G2 요약. [검색 요약 · 열지 못함] 위 G2 링크
  2. 앱뿐 아니라 방문한 웹사이트별 보고 — 같은 출처.
  3. 집중 시간에 방해 사이트 차단 — ClickUp 블로그. [검색 요약 · 열지 못함] https://clickup.com/blog?p=142766
- **비판**
  1. **사생활**: 모든 데이터를 회사 서버로 보낸다 — G2·ClickUp. [검색 요약 · 열지 못함] 위 링크들
  2. **PC 밖 활동(회의·통화·공부·운동)은 못 잡는다**, 손으로 넣어야 함 — [검색 요약 · 열지 못함] 같은 출처
  3. 자동 분류가 자주 틀려 고치는 데 시간이 든다 — [검색 요약 · 열지 못함] https://www.memtime.com/blog/rescuetime-alternatives-reviewed
- **Flowlog와 겹치는 점**: "시간이 실제로 어디 갔나" 돌아보기, 집중 모드.
- **Flowlog에 없는 것**: 자동 기록, 웹사이트 차단.
- **Flowlog에만 있는 것**: PC 밖 생활 활동을 손으로 정확히(자동 추적의 빈틈이 바로 Flowlog의 영역), 데이터 최소 수집.
- **Flowlog가 배울 점**: **주간 요약 메일/알림**("이번 주 공부 12시간, 지난주보다 +2시간") — RescueTime이 오래 살아남은 핵심 습관 고리. Flowlog는 7일 평균이 있으니 주 1회 요약만 더하면 된다.
- **확신도**: 중간 — 요금은 공식 도움말 요약이지만 직접 열지 못함.

---

### A10. ATracker (상용)
- **종류**: 상용 / **플랫폼**: iOS, Android / **가격**: 무료판 + PRO 일회 구매(iOS $4.99, Android $2.99로 보도) / **개발 주체**: 소규모 회사(Wonderapps AB, 스웨덴 추정)
- **규모 지표**: Android 설치 10만+, 평균 4.49점·약 3천 평가(AppBrain 개발자 페이지) — [검색 요약 · 열지 못함] https://www.appbrain.com/dev/Wonderapps+AB/ . iOS 4.6~4.7(출처마다 다름) — [검색 요약 · 열지 못함] https://apps.apple.com/app/atracker-daily-task-time-tracking/id522008611
- **핵심 기능**: 할 일(작업) 버튼을 눌러 시간 기록, 원형·막대 차트, 캘린더·기록 보기, 목표, 일일 보고.
- **호평**
  1. 한 번 눌러 시작, 설정이 거의 없다 — [검색 요약 · 열지 못함] https://jibble.io/reviews/atracker
  2. 맞춤 설정과 여러 기기 접근 — 같은 출처
  3. 일회 구매(구독 아님) — 같은 출처
  - (출처 Jibble은 경쟁사)
- **비판**
  1. 보기 방식이 캘린더·기록 두 가지뿐 — [검색 요약 · 열지 못함] https://www.jibble.io/reviews/atracker/5-ways-atracker-sucks
  2. 버그와 동기화 문제로 기록이 위험 — 같은 출처
  3. iOS와 Android 품질이 다르다, 모바일 캘린더 글씨가 작다 — 같은 출처
- **Flowlog와 겹치는 점**: 버튼 눌러 시작하는 개인 시간 기록, 원형 통계, Android.
- **Flowlog에 없는 것**: 일회 구매 모델, iOS.
- **Flowlog에만 있는 것**: Todo 시간 누적, 루틴·알림, 웹 대시보드, 추천.
- **Flowlog가 배울 점**: **일회 구매** — 개인용 시간 기록 앱은 구독 반발이 크다(아래 Forest 사례). Flowlog가 돈을 받는다면 일회 구매 + 동기화 서버비만 별도 같은 구조가 이 시장의 관례.
- **확신도**: 낮음 — 경쟁사가 쓴 리뷰가 주 출처.

---

### A11. aTimeLogger (상용)
- **종류**: 상용 / **플랫폼**: iOS, Android / **가격**: 무료판 + Pro(구독 여부는 출처마다 다름) / **개발 주체**: 소규모(BGCI)
- **규모 지표**: Android(Pro) 다운로드 약 11만, 4.72점·약 1,650 평가(Chrome-Stats), iOS 4.75점·1.4천 평가(AppGoblin) — [검색 요약 · 열지 못함] https://chrome-stats.com/d/io.timetrack.timetrackapp , https://appgoblin.info/apps/576718804
- **핵심 기능**: 활동 버튼 한 번으로 시작, **일시정지·이어 하기**, 여러 타이머 동시, 일·주·월 그래프, 목표, 포모도로.
- **호평**
  1. 쓰기 쉽고 보고서를 메일로 보내기 쉽다 — [검색 요약 · 열지 못함] https://justuseapp.com/en/app/576718804/atimelogger-time-tracker/reviews
  2. 일시정지·이어 하기, 여러 타이머 동시 — [검색 요약 · 열지 못함] https://trashbox.ru/link/atimelogger-android
  3. 그래프 보고가 좋다 — [검색 요약 · 열지 못함] https://sugggest.com/software/atimelogger
- **비판**
  1. 데이터 수집 고지와 개인정보처리방침이 서로 맞지 않는다는 의심 — [검색 요약 · 열지 못함] justuseapp 위 링크
  2. 다른 도구와 연동이 적다 — [검색 요약 · 열지 못함] https://www.saashub.com/compare-atracker-vs-atimelogger
  3. 데이터가 많아지면 걸러 보기 어렵다 — 같은 출처
- **Flowlog와 겹치는 점**: 거의 같은 핵심(활동 버튼 → 타이머 → 통계), 학생·개인 대상, Android.
- **Flowlog에 없는 것**: 일시정지, 동시 타이머, iOS, 보고서 메일.
- **Flowlog에만 있는 것**: Todo 연결, 강의 계획표, 루틴 알림, 웹 대시보드, 규칙 추천.
- **Flowlog가 배울 점**: **개인정보 설명을 짧고 정확하게** — 같은 부류 앱이 사생활 의심을 받는다. Flowlog는 이미 `/privacy/`가 있으니, 앱 안에 "무엇을 어디에 저장하나"를 한 화면으로.
- **확신도**: 낮음 — 전부 집계 사이트 검색 요약.

---

### A12. Structured — Daily Planner (상용)
- **종류**: 상용 / **플랫폼**: iOS·iPadOS·Mac 중심, Android, 웹(기능 적음) / **가격**: 기본 무료(광고 없음) + Pro 월 $6.99·연 $29.99·평생 $99.99(미국, 2026 리뷰) / **개발 주체**: 작은 회사(unorderly GmbH, 독일)
- **규모 지표**: 매출 약 $25만·설치 약 15만(제3자 추정, 기간 불명) — [검색 요약 · 열지 못함] https://mwm.ai/apps/ordered-daily-task-master/6605927545 (원 페이지 목록에 섞여 있어 신뢰 낮음). App Store 페이지는 열지 못함.
- **핵심 기능**: 하루를 **세로 시간 막대(타임라인)**로 보여 주는 시간 블록 계획, 색 블록, 음성·글로 말하면 AI가 일정으로 바꿔 줌, 캘린더·미리 알림 가져오기, 반복 일정(유료).
- **호평**
  1. 하루 전체가 색 블록 타임라인으로 보이고 빈 시간이 한눈에 — [검색 요약 · 열지 못함] https://blog.saner.ai/structured-review/
  2. 말로 쭉 늘어놓으면 일정으로 바꿔 주는 AI — 같은 출처
  3. 광고 없음 — 같은 출처(개발사 FAQ 인용)
- **비판**
  1. **반복 일정·캘린더 가져오기가 유료** — 무료판은 "하루 계획엔 괜찮고 반복되는 한 주엔 어색" — [검색 요약 · 열지 못함] 위 링크
  2. 동기화 불만이 "가장 흔한 불만" — 같은 출처
  3. Android·웹은 iOS보다 기능이 적다(미리 알림 가져오기·다시 계획 없음) — 같은 출처, https://habitbox.app/blog/structured-app-review
- **Flowlog와 겹치는 점**: 하루 시간표(타임라인) 화면, 루틴 블록, 일정 자동 배치(Flowlog의 '추천 활동 오늘 시간표에 자동 배치').
- **Flowlog에 없는 것**: 계획 중심 화면 디자인 완성도, AI 입력, iOS.
- **Flowlog에만 있는 것**: **계획과 실제 기록을 같이** 가진다(Structured는 계획만, 실제로 얼마나 걸렸는지는 모름). 학생 강의 계획표.
- **Flowlog가 배울 점**
  1. **계획 블록 위에 실제 기록을 겹쳐 보여 주기** — Structured가 못 하는 것이고 Flowlog는 데이터가 다 있다. "계획 3시간 / 실제 1시간 40분"이 학생에게 가장 와닿는 화면일 수 있다.
  2. 반복 일정을 유료로 막으면 반발 — 학생 대상이면 반복(시간표)은 무료가 맞다.
- **확신도**: 중간 — 리뷰 내용은 일관되나 모두 검색 요약.

---

### A13. Forest (상용, 한국 학생층도 많이 씀)
- **종류**: 상용 / **플랫폼**: iOS, iPadOS, Android, Chrome·Firefox 확장 / **가격**: 원래 유료 앱 → **2025-12 무료 + Forest Plus 구독으로 전환** / **개발 주체**: 회사(Seekrtech, 대만)
- **규모 지표**
  - 2014-05 iOS 출시, 진짜 나무 심기 200만 그루 이상 — [열어 봄] https://en.wikipedia.org/wiki/Forest_(app)
  - 약 4.4점·85.5만 리뷰(제3자 요약) — [검색 요약 · 열지 못함] https://marlvel.ai/apps/forest-focus-for-productivity
- **핵심 기능**: 타이머 동안 나무가 자라고 다른 앱으로 나가면 나무가 죽음, 세션 타임라인·태그, 코인으로 아이템·실제 나무 심기, 같이 집중 모드, 앱 차단.
- **호평**
  1. Common Sense Media 4/5, Mashable 4.5/5 — [열어 봄] 위 위키백과
  2. 실제 나무 심기와 연결되는 보상 — [열어 봄] 위 위키백과
  3. "같이 집중"으로 친구와 함께 — [열어 봄] 위 위키백과(기능 설명)
- **비판**
  1. 코인 보상이 작다 "앱 안에서 돈을 내지 않으면" — Mashable 리뷰(위키백과 인용). [열어 봄] 위 위키백과
  2. **구독 전환이 예전에 돈 내고 산 오랜 사용자를 떠나게 했다** — [검색 요약 · 열지 못함] https://marlvel.ai/apps/forest-focus-for-productivity
  3. 30분 넘는 타이머 설정 같은 기능이 유료라는 불만(2024 Google Play 리뷰 모음) — [검색 요약 · 열지 못함] https://kimola.com/reports/exclusive-forest-app-user-feedback-analysis-report-google-play-en-us-151945
- **Flowlog와 겹치는 점**: 집중 세션(Flowlog는 방해 금지 켜기), 세션 기록·태그.
- **Flowlog에 없는 것**: 게임 같은 보상(나무·코인), 친구와 같이 집중, 앱 사용 차단.
- **Flowlog에만 있는 것**: 집중 외 생활 시간 전부, Todo 시간 누적, 웹 통계.
- **Flowlog가 배울 점**
  1. **기록이 쌓이는 걸 눈에 보이는 무언가로**(숲) — Flowlog의 '도시 모양 시간표 막대'(`ui/city/`)가 이미 같은 방향이다. 하루 기록이 도시를 짓는다는 은유를 더 밀어 볼 가치.
  2. **유료 전환 경고 사례**: 한 번 판 기능을 구독으로 돌리면 리뷰가 무너진다. 처음부터 모델을 정할 것.
- **확신도**: 중간~높음 — 위키백과에서 핵심 사실과 비판 1개를 직접 확인.

---

### A14. 열품타 YPT — 열정품은타이머 (상용, 한국)
- **종류**: 상용 / **플랫폼**: Android, iOS(+ Wear OS 언급) / **가격**: 무료(광고) + 앱 안 결제 / **개발 주체**: 회사(주식회사 팔로 Pallo, 서울)
- **규모 지표**
  - Google Play 500만+ 다운로드, 4.6점·약 8.09만 리뷰 — [검색 요약 · 열지 못함] https://play.google.com/store/apps/details?id=com.pallo.passiontimerscoped&hl=en_US
  - 제3자 추정 690만~770만 설치(2026-10-13 Chrome-Stats 7,652,174) — [검색 요약 · 열지 못함] https://chrome-stats.com/d/com.pallo.passiontimerscoped , https://www.appbrain.com/app/ypt-yeolpumta/com.pallo.passiontimerscoped
  - 한국 Android 교육 무료 2위(Similarweb, 7월 26일 스냅샷) — [검색 요약 · 열지 못함] https://www.similarweb.com/top-apps/google/korea-republic-of/education/top-free/
- **핵심 기능**: 과목별 공부 시간 스톱워치, 일·주·월 통계, **스터디 그룹(지금 누가 공부 중인지 실시간)**, 같은 시험 분야 순위, 플래너, 방해 앱 막기.
- **호평**
  1. 친구와 공유하고 경쟁하며 공부 시간을 늘린다 — 학생 후기(Lemon8). [검색 요약 · 열지 못함] https://www.lemon8-app.com/@alyssuhr/7268166388613710338?region=sg
  2. 스스로 책임지게 만드는 장치(자기 책임감) — 싱가포르 학생 신문 기사. [검색 요약 · 열지 못함] https://rafflespress.com/2025/02/13/yawns-pains-and-tears-on-ypt/
  3. 그룹 순위가 동기를 준다 — 폴란드 리뷰. [검색 요약 · 열지 못함] https://www.instalki.pl/news/software/ypt-yeolpumta-pouczmy-sie-razem-recenzja/
- **비판**
  1. **비교·압박**: 실시간으로 남의 공부를 보는 구조가 낙담을 주고, "꼴찌가 될까 봐" 공부하게 만든다 — [검색 요약 · 열지 못함] rafflespress 위 링크
  2. 광고·앱 안 결제 — [검색 요약 · 열지 못함] https://www.itechguides.com/products/ypt-yeolpumta/
  3. 정한 시간을 넘어 타이머가 계속 돈다, 일부 화면 글이 한국어로만 — [검색 요약 · 열지 못함] 같은 출처
- **Flowlog와 겹치는 점**: 학생 대상, 공부 시간 기록, 통계, 플래너.
- **Flowlog에 없는 것**: 사회적 기능(그룹·순위) — 열품타 성장의 핵심.
- **Flowlog에만 있는 것**: 공부 밖 생활 시간(수면·식사·운동)까지, Todo 시간 연결, **강의 계획표로 과목 자동 생성**, 비교 없는 개인 돌아보기.
- **Flowlog가 배울 점**
  1. 한국 학생 시장에서 '공부 시간 측정'은 **이미 500만+ 앱이 차지**했다. 정면 경쟁 대신 **"남과 비교 안 하는 공부+생활 기록"**이 빈자리일 수 있다(비교 압박 비판이 있으므로). 단 이 빈자리의 크기는 확인 못 함.
  2. 과목별 기록을 **강의 계획표에서 자동으로 만든 과목**과 붙이면 열품타의 수동 과목 설정보다 편하다 — 이미 웹 쪽에 강의 연결이 있으니 앱 버튼으로까지.
- **확신도**: 중간 — 규모 숫자는 여러 검색 결과가 대체로 일치하나 직접 열지 못함. 비판은 학생 신문 한 편이 주 근거.

---

### A15. 투두메이트 todo mate (상용, 한국)
- **종류**: 상용 / **플랫폼**: iOS, Android, 웹, Windows·Mac / **가격**: 무료(광고 포함 표기) + 프리미엄(미국 월 $1.99·연 $7.49) / **개발 주체**: 한국 회사(개발사 표기 미확인)
- **규모 지표**
  - App Store 4.8점(평가 수는 페이지마다 1.4천~10만으로 다름) — [검색 요약 · 열지 못함] https://apps.apple.com/kr/app/%ED%88%AC%EB%91%90-%EB%A9%94%EC%9D%B4%ED%8A%B8-todo-mate-%ED%95%A0-%EC%9D%BC-%EC%9C%84%EC%A0%AF-%EC%95%8C%EB%A6%BC/id1505220130
  - 누적 가입 27만+, 일간 사용자 약 12만, Android 사용자 10대 30%·20대 47%, App Store 전체 2위까지(기사, 발행 연도 미확인) — [검색 요약 · 열지 못함] https://www.jobplanet.co.kr/contents/news-1899
- **핵심 기능**: 날짜별 할 일 체크, **친구 피드(서로의 할 일·완료 보기)**, 루틴, 타이머, 일기, AI 추천, 위젯.
- **호평**
  1. 10~20대에게 인기, 스토어 상위 — [검색 요약 · 열지 못함] jobplanet 위 링크
  2. 높은 평점 4.8 — [검색 요약 · 열지 못함] App Store 위 링크
  3. 여러 기기(웹·데스크톱) 동기화 — 같은 출처
- **비판**
  1. Mac 앱에서 한/영 전환이 업데이트 뒤에도 안 된다는 리뷰 — [검색 요약 · 열지 못함] https://apps.apple.com/kr/app/%ED%88%AC%EB%91%90%EB%A9%94%EC%9D%B4%ED%8A%B8-for-desktop/id1567807901?mt=12
  2. 위젯·워치에서 체크한 할 일이 완료 처리 안 되던 문제(업데이트 노트에서 고쳤다고 밝힘) — [검색 요약 · 열지 못함] App Store 위 링크
  3. 광고 포함, 추적에 쓰일 수 있는 데이터 수집 표기 — [검색 요약 · 열지 못함] 같은 출처
  - (실제 불만 리뷰를 충분히 찾지 못함)
- **Flowlog와 겹치는 점**: 학생층, 할 일 + 루틴 + 타이머, 위젯.
- **Flowlog에 없는 것**: 친구 피드(가벼운 사회적 동기), 일기, 다양한 플랫폼.
- **Flowlog에만 있는 것**: 할 일에 **실제 걸린 시간** 누적, 생활 시간표, 강의 계획표.
- **Flowlog가 배울 점**: 한국 학생 앱의 공통점은 **가벼운 사회적 장치**(열품타 그룹, 투두메이트 피드). Flowlog는 1인 도구로 남되, 최소한 "오늘 기록 한 장 이미지로 공유" 정도는 비용 대비 효과가 클 수 있다. [추정]
- **확신도**: 낮음 — 비판 근거가 약하고 규모 기사의 날짜를 모른다.

---

## B. 시장 조사

### B1. 시장 규모와 성장률 (모두 [검색 요약 · 열지 못함])

시장조사 회사 보고서는 "시간 추적 소프트웨어"의 범위를 서로 다르게 잡아서 숫자가 2배 넘게 벌어진다. **대부분 회사용(B2B) 근태·청구 소프트웨어를 센 숫자**라서 Flowlog 같은 개인용 앱 시장과는 거리가 있다.

| 출처 | 기준 연도 규모 | 성장률(연평균) | 링크 |
|---|---|---|---|
| Straits Research | 2024 71.3억 달러 → 2025 83.6억 | 17.26%(2025–2033) | 검색 요약 내 인용(원 링크 미표시) |
| SkyQuest | 2024 81.6억 → 2033 370.4억 | 약 18.3% | https://www.skyquestt.com/report/time-tracking-software-market |
| Market Research Future | 2024 33.8억 | 16.52%(2025–2035) | https://www.marketresearchfuture.com/reports/time-tracking-software-market-9579 |
| Business Research Company(OpenPR 보도) | 2024 33.5억 → 2025 39.3억, 2029 74.7억 | 17.4~17.5% | https://www.openpr.com/news/3856102/global-time-tracking-software-market-projected-to-surpass-7-47 |
| FACT.MR | 2025 38억 | 15.5%(~2035) | https://www.factmr.com/report/time-tracking-software-market |
| Wise Guy Reports(온라인 시간 추적만) | 2024 43.7억 | 7.8%(2026–2035) | https://www.wiseguyreports.com/reports/online-time-tracking-software-market |

- **정리**: 2024년 33억~82억 달러, 연 15~18% 성장이라는 추정이 많고, 좁게 잡으면 7~8%. 서로 크게 다르므로 "수십억 달러, 두 자릿수 성장" 정도로만 쓰는 게 안전하다.
- **모바일 생산성 앱 전체**: 2025년 App Store+Google Play 생산성 분류 매출 91억 달러(전체의 약 6%), 전년 대비 +79.3%로 주요 분류 중 가장 큰 성장 — AppTweak. [검색 요약 · 열지 못함] https://www.apptweak.com/en/reports/app-market-size-by-app-category
  - [추정] 이 급성장은 ChatGPT 같은 AI 앱이 '생산성'으로 분류된 영향이 클 것이다. 시간 기록 앱이 그만큼 큰 건 아니다.

### B2. 수익 모델 분포

- **구독이 주류**: 생산성 앱 구독 매출에서 **주간 결제가 66%**(2023년 61%), 월간은 줄어드는 중 — Adapty 2026 벤치마크(1.6만 개 앱, 30억 달러 구독 매출). [검색 요약 · 열지 못함] https://adapty.io/blog/productivity-app-subscription-benchmarks/
- 이번 조사 후보 15개의 모델(조사자 집계):

| 모델 | 해당 후보 |
|---|---|
| B2B 구독(인원당) + 무료 | Toggl Track, Clockify, RescueTime(Team), Kimai 클라우드 |
| 개인 구독 + 무료판 | RescueTime, Structured(평생 구매도 있음), Forest(2025-12부터), 투두메이트, TimeTagger(월 €3 호스팅) |
| 일회 구매 + 무료판 | ATracker PRO, aTimeLogger Pro(구독 여부 출처마다 다름), Forest(2025-12 전환 전) |
| 무료 + 광고 + 앱 안 결제 | 열품타 YPT, 투두메이트 |
| 완전 무료(기부·후원) | Simple Time Tracker, Loop, ActivityWatch, Super Productivity, Kimai(직접 설치) |

- **포화도 [추정]**: 매우 높다. 회사용은 Toggl·Clockify 같은 무료 요금제 강자가 바닥 가격을 0으로 만들었고, 개인용 Android는 무료 오픈소스(Simple Time Tracker, Loop)가 '광고 없는 무료'의 기준을 세웠다. 한국 학생 공부 시간은 열품타(500만+)가 차지.

### B3. 1인 개발 시간 기록 앱이 차지하는 현실적 위치

**성공 사례 (수익이나 사용자 규모가 공개된 1인·초소형)**
1. **Super Productivity** — 사실상 1인 중심 오픈소스가 GitHub 별 23.0k, 모든 주요 스토어 배포. 수익은 GitHub 후원(금액 미공개). [열어 봄] https://github.com/super-productivity/super-productivity
2. **Loop Habit Tracker** — 1인, 별 10.3k, 광고·결제 없이 유지. [열어 봄] https://github.com/iSoron/uhabits
3. **Rize** — 2인 창업, 외부 투자 없이 2022년 "월 매출 1.1만 달러" 자기 보고(Indie Hackers). [검색 요약 · 열지 못함] https://www.indiehackers.com/post/hello-ih-i-cofounded-rize-where-we-got-1-on-product-hunt-in-may-and-just-reached-11-000-in-monthly-sales-ama-97f4c8f30e
4. **Timing(Mac)** — 독일 1인 개발자 Daniel Alm, 외부 투자 없음, Setapp 수익이 "사업 안정에 확실히 도움". 매출 숫자는 확인 못 함. [검색 요약 · 열지 못함] https://setapp.com/developers/timing
5. **TimeTagger** — 1인, 오픈소스 + 월 €3 호스팅. 매출 미공개. [열어 봄] https://github.com/almarklein/timetagger

**실패·정체 사례**
1. **Watson**(명령줄 시간 기록, 별 2.5k) — 마지막 커밋 2022-07-15, 4년 넘게 멈춤. [열어 봄] https://github.com/jazzband/Watson/commits/master
2. **Timecop**(Flutter 시간 기록, 별 886, 1인) — 의미 있는 마지막 변경 2025-01-24, 이후 웹사이트 링크 수정 하나(2026-08). [열어 봄] https://github.com/hamaluik/timecop/commits/master
3. **ActivityWatch** — 별 19.3k로 크게 성공했지만 개발자 말로 기부가 "현재 비용을 겨우 덮는다", 핵심 기능(동기화)이 9년째 미완성. 인기와 지속 가능성은 별개라는 사례. [열어 봄] https://github.com/ActivityWatch/activitywatch/issues/259 , https://github.com/ActivityWatch/activitywatch/issues/35
4. **Loop의 동기화** — 1인 개발자가 5년 끌다 2026-10-19 '계획 없음'으로 닫음. 1인 앱이 서버 기능을 유지하기 어렵다는 직접 증거. [열어 봄] https://github.com/iSoron/uhabits/issues/702
5. (회사 사례) Toggl의 오픈소스 데스크톱 앱 2023-06 보관 처리. [열어 봄] https://github.com/toggl-open-source

**[추정] 위치 요약**: 1인 시간 기록 앱이 '살아남는' 길은 두 가지로 보인다 — (가) 무료 오픈소스로 사용자 신뢰를 쌓고 후원으로 버티기(STT, Loop, SP), (나) 좁은 틈(Mac 자동 기록, 프리랜서)을 찾아 일회 구매·작은 구독으로 소액 수익(Timing, TimeTagger, Rize). 둘 다 **서버 동기화는 1인에게 가장 비싼 기능**이라는 공통점이 있다.

### B4. Flowlog의 시장 가치 — 메인 판단용 재료

**차별점이 될 수 있는 것**
1. **학생 강의 계획표 → 강의별 일정 + 활동 기록 + Todo 시간 누적**을 한 데이터로 묶는 조합. 이번 15개 후보 중 이 조합을 가진 앱은 **찾지 못했다**. 가장 가까운 것: 열품타(공부 시간+플래너, 계획표 자동 생성 없음), 투두메이트(할 일+타이머, 실제 시간 누적 약함), Structured(계획만, 실제 기록 없음), Super Productivity(할 일+시간, 생활 시간·학생 일정 없음). [추정, 한국 앱 조사가 약해서 놓친 앱이 있을 수 있음]
2. **"계획 vs 실제"를 한 화면에**: 계획 앱(Structured)은 실제를 모르고, 기록 앱(STT, aTimeLogger, Toggl)은 계획이 약하다. Flowlog는 루틴 블록·시간표와 실제 기록을 둘 다 가진다.
3. **로컬 규칙 추천으로 입력 마찰 줄이기**: 큰 회사 앱의 불만 1순위가 입력·수정 마찰(Clockify "매번 프로젝트 선택", Toggl "뒤늦게 고치기 투박"). Flowlog의 제목 추천·버튼 승격은 이 문제를 직접 겨냥하고, 외부 AI가 없어 사생활 부담도 없다.
4. **동작하는 동기화 + 웹 대시보드**: 오픈소스 경쟁자(STT, Loop, ActivityWatch) 사용자들이 가장 많이 요청하는 것이 바로 동기화다(STT #237, Loop #702, AW #35 반응 103).

**약점**
1. **스토어 미출시 + 직접 빌드 + 자기 Firebase 설정** — 사실상 일반 사용자는 설치할 수 없다. 이번 조사의 모든 성공 사례는 최소한 F-Droid나 Play에 있다.
2. **1인 + Firebase 의존**: 동기화는 1인에게 가장 비싼 기능(B3). Firebase 무료 한도를 넘으면 비용이 생기고, Google 정책 변화에 묶인다(Super Productivity의 Google 캘린더 연동이 Google에 막힌 사례, #7221 [열어 봄]).
3. **Android 전용**: 학생층의 iPhone 비중을 생각하면 반쪽. (한국 학생 iPhone 비율은 확인 못 함)
4. **사회적 장치 없음**: 한국 학생 앱의 성장 엔진(열품타 그룹·순위, 투두메이트 친구 피드)이 없다. 장점(비교 압박 없음)이 될 수도 있다.

**비슷한 포지셔닝의 앱 수 [추정]**
- "개인 생활 시간 기록 + 통계"(넓게): 이번 조사만으로 10개 이상(ATracker, aTimeLogger, STT, Toggl 개인 사용, TimeTagger, Forest 등) — 매우 붐빈다.
- "학생 공부 시간 측정"(한국): 열품타가 지배적(500만+).
- "학생 일정(계획표) + 실제 시간 + Todo 연결"(좁게): 이번 조사에서 0개. 다만 영어 검색이 미국 위주라 한국·일본 앱을 충분히 못 봤다.

---

## C. 공통 교훈

### C1. 호평이 반복되는 특성 5개
1. **한 번 눌러 바로 시작** — Toggl("타이머가 한 번 클릭"), ATracker, aTimeLogger, Simple Time Tracker("one-click"), Super Productivity("one-click time tracking").
2. **계정·인터넷 없이 바로 씀 / 데이터가 내 기기에** — Simple Time Tracker, Loop, ActivityWatch, Super Productivity(모두 README·리뷰에서 반복).
3. **무료·광고 없음·기능 잠금 없음** — Loop, Simple Time Tracker, Super Productivity, Clockify(무료 요금제가 최대 매력), Toggl(무료로 충분).
4. **한눈에 보이는 시각화** — Structured(색 블록 타임라인), TimeTagger(타임라인), Forest(나무·숲), ATracker·aTimeLogger(원형·막대 그래프).
5. **실패해도 무너지지 않는 동기 장치** — Loop(습관 강도 점수), Forest(나무 보상), 열품타(그룹·순위).

### C2. 비판이 반복되는 특성 5개
1. **동기화가 없거나 불안정** — Simple Time Tracker(#237), Loop(#702 5년 끝 '계획 없음'), ActivityWatch(#35, 9년째), Super Productivity(바깥 서비스 설정), Clockify·Toggl·Structured·ATracker(동기화 지연·불만).
2. **타이머 켜기/끄기를 잊음** — ActivityWatch("켜는 걸 늘 잊는다" #144), TimeTagger(너무 오래 도는 기록 알림 요청 #55, 돌고 있는지 안 보임 #159).
3. **끼어든 일(중단) 처리와 지난 기록 고치기** — Kimai(일시정지 #963, 2019년부터), Simple Time Tracker(일시정지 #173), Toggl(모바일 사후 수정 투박).
4. **무료 기능 축소·구독 전환 반발** — Forest(2025-12 구독 전환), Toggl(보고서·API 제한), Structured(반복 일정 유료).
5. **사생활·데이터 수집 의심** — RescueTime(서버 전송), aTimeLogger(고지 불일치), ActivityWatch 사용자(민감 정보 걸러 내기·비밀번호 요청 #144, #1199).

### C3. "시간 기록 앱을 그만두게 하는 이유" 상위 5개
시간 기록 앱만 다룬 연구는 찾지 못했다. 아래는 자기 기록(self-tracking)·활동량계·생활 앱 연구 + 위 후보들의 반복 불만을 합친 것이다.

1. **기록하는 수고(귀찮음)** — CHI 2016 자기 기록 중단 연구: 기록이 "번거롭다", "귀찮다", "흥미를 잃었다". [검색 요약 · 열지 못함] https://www.smunson.com/portfolio/projects/lifelogs/life_after_tracking_chi16.pdf / 위키백과 '정량화된 자아': "자기 기록은 시간이 들어 부담스러울 수 있다". [열어 봄] https://en.wikipedia.org/wiki/Quantified_self
2. **동기 저하와 생활 변화(루틴이 깨짐)** — 착용형 기기 중단 연구 검토: 1순위 내적 동기 저하, 다음이 기록 습관 붕괴, 우선순위·생활 변화. 많은 사람이 몇 달 안에 멈춘다. [검색 요약 · 열지 못함] https://www.sciencedirect.com/science/article/abs/pii/S0747563219303127 ; 독일 159명 조사: 의욕 저하·외부 생활 요인·정확성 의심. [검색 요약 · 열지 못함] https://www.researchgate.net/publication/360361258_Why_Do_People_Abandon_Activity_Trackers_The_Role_of_User_Diversity_in_Discontinued_Use
3. **잊음 → 빈 기록 → 데이터 신뢰 상실** — "타이머 켜는/끄는 걸 늘 잊는다"(ActivityWatch #144 [열어 봄], 프리랜서 사례 [검색 요약 · 열지 못함] https://www.producthunt.com/p/tabtime-io-track-time-by-google-group/tabtime-io), 정확성 의심(위 159명 조사).
4. **기술 문제·사용 경험 나쁨**(동기화·버그·앱 튕김) — 생활·정신건강 앱 18개 연구 검토: 처음 100일 안에 **중앙값 70%가 사용 중단**, 이유 6묶음(기술 문제, 사생활, 사용 경험, 내용·기능, 시간·돈 비용, 필요 변화). [검색 요약 · 열지 못함] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11694054/ ; 후보 사례: Clockify·Toggl 모바일 불만.
5. **궁금증이 풀림 / 얻는 게 안 보임** — CHI 2016: 도구가 호기심을 채우면 멈춘다(위 링크). ActivityWatch 사용자: "내 경향을 분석하기 어렵다" [열어 봄] #144.
   - (6위 후보: 사생활 걱정, 비용·유료 전환 — 위 검토 연구의 묶음과 C2-4·5)

**Flowlog에의 함의 [추정]**: 1·3번은 Flowlog의 핵심 가치(낮은 마찰, 기상·식사 후 알림, 제목 추천)가 정면으로 겨냥한다. 2·5번(동기 저하, 얻는 게 안 보임)은 아직 약하다 — 주간 요약, 계획 vs 실제, '강도' 점수 같은 **돌아보기에서 얻는 것**이 다음 숙제로 보인다.
