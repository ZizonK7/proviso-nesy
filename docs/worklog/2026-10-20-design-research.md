# 2026-10-20 — Flowlog 디자인 조사·UI 평가

에이전트: 디자인 조사·UI 평가 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

## 한 일
- 조사 결과 파일: `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/reports/04-design-research.md` (저장소 밖 임시 폴더). 순서: A 한눈 표 → A 상세(10항목, 근거 `파일:줄`) → B 사례 표(18개) → B 상세 → C 방향 3가지 + 비교 표 + 추천.
- A 점수(1–5): 시각 체계 2 · 정보 구조 2.5 · 핵심 흐름 마찰 4 · 타임라인·통계 2.5 · 상태 표현 2 · 접근성 1.5 · 다크/동적 색/큰 화면 1 · 문구·톤 3 · 위젯·알림 3 · 아이콘·브랜드 2.5 (평균 약 2.4).
- 주요 발견(코드로 확인):
  - 테마는 Android Studio 기본 보라 템플릿 그대로이고, 화면 코드는 `MaterialTheme.colorScheme`/`typography`를 한 번도 안 쓴다. 직접 지정한 색 339곳(서로 다른 색 170개), `Color.White` 133곳, 글자 크기 21가지, 모서리 16가지, 보라 5종, 범주 색 표 두 벌.
  - 그래서 다크 모드·동적 색 코드는 있어도 사실상 라이트 전용(바텀시트 17개 전부, 다이얼로그 13개 중 12개가 바탕색을 직접 칠함).
  - 기록 흐름은 강점: 시작 1탭, 저장 1탭(제목 선택), Todo 연결 2탭.
  - 앱 안에 7일 평균이 안 보인다: `AverageRows`는 정의만 있고 호출 없음, `AnalyticsState`엔 오늘·어제만. README·PROJECT_CONTEXT 설명과 다름.
  - 접근성: 아이콘 94개 중 59개 설명 없음, `semantics` 0회, 정지 버튼은 이름 없는 상자, 터치 목표 30–36dp 다수(권장 48dp), 0dp짜리 숨은 버튼, 범주 색 숫자 대비 1.63–2.78(권장 3:1).
  - 첫 실행 화면에 "나중에 Flowlog AI가 … 추천해 드려요" 문구 — 앱에 AI가 없다는 PROJECT_CONTEXT와 어긋남.
  - 도시/섬 시간표(`ui/city/`)는 개발자 화면에서만 쓰이고, 그림 PNG가 장당 0.4–1.4 MB.
- C 방향: ① Flowlog Calm(구조 유지·토큰 정리, 난이도 중) ② Flowlog River(세로 오늘 타임라인 중심 + 아래 독, 대) ③ Flowlog Expressive(Material 3 Expressive 전면, 대 + 베타 라이브러리). 방향마다 라이트·다크 팔레트와 범주 8색(대비를 스크립트로 계산: 라이트 흰 표면 4.5:1 이상, 다크 7:1 이상), 글꼴, 화면 5개 ASCII 와이어프레임, 탭 수 변화, 위험을 적었다. 추천은 ②.
- 저장소 파일은 이 보고서 하나만 만들었다. Flowlog 저장소는 읽기만 했다.

## 확인한 것 (어떻게)
- Flowlog 코드 읽기: `README.md`, `docs/PROJECT_CONTEXT.md`, `ui/theme/*`, `ui/component/*`, `ui/screen/HomeScreen.kt`, `ui/screen/home/*`(HomeHeader·Timer·Recommendation·Timetable·Analytics·RecentRecords·QuickTimer), `ui/screen/TodoScreen.kt` 일부, `ui/city/CityTimetableBar.kt`, `MainActivity.kt`(내비게이션·머리말), `widget/FlowStatusWidgetProvider.kt`, `res/values/*`, `res/layout/flow_status_widget.xml`, `res/xml/flow_status_widget_info.xml`, `res/mipmap-anydpi-v26/ic_launcher.xml`, 알림 문구(`notification/*.kt` grep).
- 개수 세기: `grep -c`/`grep -o … | sort | uniq -c` 로 `AlertDialog(`·`ModalBottomSheet(`·`Dialog(`, `Color(0x…)`, `fontSize`, `RoundedCornerShape`, `FontWeight`, `stringResource`, 하드코딩 한글 `Text("…")`; Icon 설명 유무와 다이얼로그 바탕색 지정 여부는 괄호 짝을 맞추는 짧은 Python 스크립트로 셌다.
- 탭 수: 버튼 `onClick` → `ActivityViewModel.startActivity()`/`stopActivityAndSave()` → 화면 전환(`showHomeMainTimer`)까지 코드로 따라감.
- 색 대비: WCAG 상대 휘도 공식으로 Python 계산(현재 범주 색 16개, 새 팔레트 3벌 × 범주 8색 × 라이트·다크).
- 앱 아이콘·위젯 캐릭터: Pillow로 축소 PNG를 만들어 눈으로 확인(아이콘 모서리에 템플릿 초록 배경 비침).
- 웹: 실제로 열린 곳만 출처로 씀 — `developer.apple.com/design/awards/`(2026·2025·2024·2023·2022 페이지, curl로 원문 받아 앱 설명 문장 확인), `developer.android.com`(Compose Material 3 문서, Wear Expressive 지침, `MotionScheme` 레퍼런스 "Added in 1.5.0-beta01", material3 릴리스 노트, 접근성 지침 48dp·대비 기준), `en.wikipedia.org`(Things, Apple Design Awards, Flighty, Forest, Toggl Track, Todoist, Google Calendar, Samsung Health, Daylio, Duolingo, Material Design, Google Play).

## 확인 못 한 것
- 앱을 빌드·실행하지 않았다(지시대로 `./gradlew` 안 돌림). 실제 화면 높이에서 무엇이 접히는지, 다크 모드에서 실제로 어떻게 보이는지, 큰 글씨 설정에서 잘리는지는 코드로 추론한 것(보고서에 확신도 "중"으로 표시).
- 웹 대부분이 막혔다(프록시 403·DNS 실패): m3.material.io, design.google, blog.google, apps.apple.com, play.google.com, 앱 공식 사이트들(structured.app, toggl.com, finch.care 등), 언론 사이트, namu.wiki, fonts.google.com, GitHub 저장소 API. 그래서
  - Fantastical·Timery·Finch·Habitify·열품타·Google Play "Best of"는 근거를 열지 못해 사례 표에서 뺐다.
  - 사례별 화면 특징 중 출처에 없는 것은 [일반 지식]으로 표시했다(이번에 확인 안 됨).
  - Material 3 Expressive 연구 수치(연구 46건·1.8만 명·"4배 빨리")는 검색 요약에만 있고 원문을 못 열었다 — 근거로 쓰지 말 것.
  - 제안 글꼴(Pretendard, IBM Plex Sans KR, Roboto Flex, Noto Sans KR)의 현재 배포처·라이선스는 확인 못 함.
- Flowlog의 Compose BOM `2026.02.01`이 가리키는 material3 버전은 확인 못 함.
- Android 16 진행 알림(Live Update)의 정확한 API는 확인 못 함.

## 알려진 문제
- 사례가 Apple Design Award 쪽에 몰려 있다(열린 출처가 developer.apple.com이라서). Android 쪽 호평 근거(Google Play 수상, Material Design Award)는 하나도 열지 못했다.
- 범주 8색 대비는 계산했지만 색약 시뮬레이션은 하지 않았다. ①의 수면(남색)·운동(파랑)·할일(보라), ②의 운동과 주 강조색(같은 파랑)은 서로 가까울 수 있다.
- C의 와이어프레임은 글·ASCII라 비율이 정확하지 않다.

## 다음 작업자에게
- HTML 목업은 보고서 C의 팔레트 표(hex)와 ASCII를 그대로 쓰면 된다. 추천 ②를 고른다면 홈(세로 타임라인 + 지금 선 + 아래 독)과 "기록 없음 ＋" 빈 시간 표현이 핵심.
- 어느 방향이든 0단계(테마 토큰 만들기, 범주 색·이름 표를 하나로)가 먼저다. 이것만으로도 다크 모드·대비 문제 대부분이 풀린다.
- 디자인과 별개로 바로 고칠 만한 것: 7일 평균 미표시(문서와 불일치), 첫 실행 "Flowlog AI" 문구, 정지 버튼 접근성 이름, 앱 아이콘 배경 초록. Flowlog 수정은 사용자 요청이 있을 때만.
- [일반 지식] 표시가 붙은 사례 특징은 시안에 쓰기 전 실물 스크린샷으로 확인할 것.
