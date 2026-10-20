# Flowlog 디자인 조사 — 현재 UI/UX 평가 · 호평 사례 · 새 시안 방향 3가지

작성: 2026-10-20, 하위 에이전트(디자인 조사·UI 평가). 근거는 `/home/user/Flowlog` 코드(읽기만, 빌드·실행 안 함)와 실제로 열어 본 웹 페이지.
경로 표기 `파일:줄`의 기준 폴더: `app/src/main/java/com/example/flowlog/` (리소스는 `app/src/main/res/`).
확신도: 상 = 코드에서 직접 확인, 중 = 코드로 추론(실기기 화면은 안 봄), 하 = 짐작.

---

## A. 현재 UI/UX 한눈 표

| # | 항목 | 점수(1–5) | 한 줄 근거 | 확신도 |
|---|---|---|---|---|
| 1 | 시각 체계(테마·색·글꼴·간격) | **2** | 테마는 Android Studio 기본 보라 템플릿 그대로, 화면은 테마를 한 번도 안 읽고 색 170개·글자 크기 21가지·모서리 16가지를 직접 박음 | 상 |
| 2 | 정보 구조·내비게이션 | **2.5** | 탭 2개(홈·Todo)로 단순하지만 홈 한 화면에 카드 6개, 시트·다이얼로그 31개 | 상 |
| 3 | 핵심 흐름 마찰 | **4** | 타이머 시작 1탭, 저장 1탭(제목은 선택), Todo 연결 2탭 — 이 앱의 가장 큰 강점 | 상 |
| 4 | 타임라인·통계 표현 | **2.5** | 24시간을 30분 칸 48개 막대(높이 14dp)로 압축, 시간 눈금 4시간 간격 10sp. 도시/섬 시간표는 개발자 화면에만. 7일 평균은 앱에 안 보임 | 상 |
| 5 | 상태 표현(빈·로딩·오류·오프라인·동기화) | **2** | 빈 상태 문구는 있으나 "기록이 없습니다" 수준. 로딩 표시 0, 동기화·오프라인 표시 없음(토스트만) | 상 |
| 6 | 접근성 | **1.5** | 아이콘 94개 중 59개 설명 없음, `semantics` 0회, 정지 버튼은 설명 없는 상자, 터치 목표 30–36dp 다수(권장 48dp), 범주 색 글자 대비 1.6–2.8:1(권장 3:1 이상) | 상 |
| 7 | 다크 모드·동적 색·가로/큰 화면 | **1** | 다크·동적 색 코드는 있으나 화면이 흰색을 직접 칠해 사실상 라이트 전용. 창 크기 대응 코드 없음 | 상(코드) / 중(실제 화면) |
| 8 | 문구·톤 | **3** | 알림 톤은 부드럽고 좋음. 다만 한·영 혼재("Today's Flow", "Flowlog timer", "flowing"), 하드코딩 한글 61곳, 온보딩에 "Flowlog AI" 약속 | 상 |
| 9 | 위젯·알림 디자인 | **3** | 액체가 차오르는 알약 모양 위젯과 캐릭터는 개성 있음. 위젯에서 시작·정지 불가(탭 = 앱 열기), 1×5칸 고정 | 상 |
| 10 | 아이콘·브랜드 | **2.5** | 보라 3D 소용돌이+눈금 앱 아이콘은 직접 만든 것. 배경은 템플릿 초록(#3DDC84) 그대로, 단색(테마) 아이콘도 컬러 그림 재사용 | 상 |

**평균 약 2.4 / 5.** 기록 흐름(3번)은 잘 만들어졌고, 나머지는 "기능을 빠르게 쌓은 개인 앱"의 흔적 — 디자인 체계(토큰)가 없어서 생기는 문제가 대부분이다.

## A. 상세

### A1. 시각 체계 — 2점 (확신도 상)
- **테마는 템플릿 그대로.** `ui/theme/Color.kt:5-11`은 Android Studio 새 프로젝트의 `Purple80/PurpleGrey80/Pink80/Purple40…` 그대로, `ui/theme/Theme.kt:13-31`의 색 구성표도 템플릿 주석까지 남아 있다. `ui/theme/Type.kt:8-15`는 `bodyLarge` 하나만 정의(템플릿 원본). `res/values/colors.xml`은 `purple_200/500/700, teal_200/700`(템플릿), `res/values/themes.xml:4`는 `android:Theme.Material.Light.NoActionBar`(Material 3 아님, 라이트 고정).
- **화면은 테마를 읽지 않는다.** `MaterialTheme.colorScheme` 사용 0회, `MaterialTheme.typography` 사용 0회(ui/ 전체 grep). 대신 `Color(0x…)` 직접 지정 339곳(서로 다른 색 170개), `Color.White` 133곳.
- **보라만 다섯 가지.** 홈 `FlowPurple #5140D8`(`ui/screen/home/HomeStyleConstants.kt:210`), Todo `Purple #6757E7`(`ui/screen/TodoScreen.kt:170`), 버튼 테두리 `#7D68EA`(`ui/component/CategoryButton.kt:60`), 보조 글씨 `#6B4FE8`(같은 파일 97), 테마 `Purple40 #6650a4`(`ui/theme/Color.kt:9`). 눈으로는 비슷하지만 화면마다 조금씩 다르다.
- **범주 색이 두 벌.** 버튼·통계용 `categoryColor()`(`ui/component/ActivityItem.kt:179-201`, Material 2 원색: 공부 #4CAF50, 식사 #FF9800 …)와 시간표용 `timetableCategoryColor()`(`ui/screen/home/TimetableCardSection.kt:764-783`, 같은 범주를 채도 낮춘 별도 색). 같은 "공부"가 카드와 시간표에서 다른 초록이다.
- **글자 크기 21가지**(7sp~48sp; 13sp 78회, 12sp 63회, 14sp 61회 …), 굵기는 ExtraBold 125회·Bold 123회로 거의 모든 글자가 굵다 → 위계가 약하다(제목도 본문도 굵음).
- **모서리 16가지**(12dp 58회, 10dp 32회, 14dp 28회, 16dp 26회, 13dp·15dp·22dp도 있음). 간격도 카드마다 24dp(`ui/screen/home/HomeHeaderSection.kt:294` TodayFlowCard)·16dp(`TimetableCardSection.kt:292`, `AnalyticsReportSection.kt:218`)로 다르다.
- 좋은 점: 집중 모드에서 배경·강조색이 보라→주황(`FocusFire #FF7A2F`)으로 420ms 동안 바뀌는 연출(`ui/screen/HomeScreen.kt:330-334`)은 상태를 색으로 정직하게 알려 준다. 범주 아이콘은 Material 아이콘으로 통일(`ui/component/CategoryIcons.kt:22-41`).

### A2. 정보 구조와 내비게이션 — 2.5점 (확신도 상)
- **화면 2개**: 홈·Todo를 `HorizontalPager` 2쪽 + 하단 `NavigationBar` 2칸(`MainActivity.kt:400-405, 1485-1525`). 설정은 머리말 프로필 메뉴의 드롭다운·다이얼로그(`MainActivity.kt:849-935`).
- **떠 있는 창 31개**: `AlertDialog` 13, `ModalBottomSheet` 17, `Dialog` 1. 파일별 — AutoButtonSheetsSection 6, TimerSection 5, TodoScreen 5, RoutineManagerSection 4, ExerciseSection 3, MainActivity 3, EditActivityDialog 2, RecommendationSection 2, SleepFillDialog 1.
- **홈 한 화면에 쌓인 것** (`ui/screen/HomeScreen.kt:363-578`, 위에서 아래 순서):
  1. `HomeHeader`(364) — "Today's Flow" 제목, 날짜, 통계·AI 메신저·프로필 버튼.
  2. `TodayFlowCard`(385) — 멈춰 있으면 "활동 시작" 2열 버튼 격자(버튼당 84dp, 최대 10개 → 최대 5줄), 돌고 있으면 타이머 쪽(경과 시간·정지·제목 제안·집중 모드·운동 세트).
  3. `QuickTimerSection`(441) — "빠른 타이머": 양치 3분·간식 타이머 켜기/끄기, 순서 바꾸기.
  4. `TimetableCard`(481) — 오늘 24시간 막대 + 반복 루틴 칩 줄 + 추천 흐름 줄.
  5. `RecentRecordsCard`(532) + 더보기 버튼(547) — 최근 기록 3개(펼치면 30개), 수정·즐겨찾기·삭제.
  6. `AnalyticsCard`(573) — "통계 리포트": 오늘 한 일들(범주 막대) + 어제와 비교.
  그 밖에 `screen/home/*.kt`: `AutoButtonSheetsSection`(루틴·추천 할 일 시트, 메인 버튼 편집), `RoutineManagerSection`(반복 루틴 관리 시트·시간 선택), `ExerciseSection`(세트 추가·운동 종료), `RecommendationSection`(첫 실행 버튼 고르기, 시작 격자, 추천 시트, 충돌 다이얼로그), `FlowProgressSection`(운동 세트용 진행 링; `ExperimentSection`은 어디서도 안 부름), `DevScreens`(개발자 전용 도시 시간표), `HomeStyleConstants`(색·상수).
- **판단**: 홈은 "기록하기"와 "돌아보기"와 "계획(루틴·추천)"이 한 스크롤에 섞였다. 메인 버튼이 8–10개면 시작 카드만으로 화면 절반 이상(84dp×5줄+여백 ≈ 480dp, `ui/screen/home/RecommendationSection.kt:489`)을 차지해 시간표는 접힌 아래(스크롤 필요)에 있다(실기기 높이는 미확인 → 확신도 중).
- Todo 화면은 탭 5개(전체·오늘·과제·복습·일반, `ui/screen/TodoScreen.kt:150-156`) + Petites + Daily Cues가 한 목록에 있다.

### A3. 핵심 흐름의 마찰 — 4점 (확신도 상)
코드로 따라간 탭 수(앱을 열어 홈이 보인 상태 기준):
| 흐름 | 탭 수 | 경로 |
|---|---|---|
| 타이머 시작 | **1** | 범주 버튼 탭 → `onStart(category)`(`ui/screen/home/RecommendationSection.kt:563-572`) → `ActivityViewModel.startActivity()`(`ui/viewmodel/ActivityViewModel.kt:548-588`)가 바로 시작, 묻는 창 없음 |
| 위젯에서 시작 | 2 | 위젯 탭은 앱을 열기만 함(`widget/FlowStatusWidgetProvider.kt:84-94`) → 버튼 1탭. 위젯 문구는 "· 탭해서 시작"(126)이라 기대와 다름 |
| 활동 저장 | **1** (+0~1) | 정지 원형 버튼 탭(`ui/screen/home/TimerSection.kt:550-571`) → `stopActivityAndSave()`가 확인 없이 저장(`ActivityViewModel.kt:1087-1104`). 제목은 선택: 제안 칩 1탭(최대 5개) 또는 직접 입력+"적용". 빈 제목이면 범주 이름이 기본값 |
| 운동 저장 | 2 + 세트 입력 | 정지 → `ExerciseFinishDialog` → 저장 |
| 다른 활동으로 바꾸기 | 2 | 진행 중엔 시작 격자가 숨겨지고 `startActivity`가 무시됨(`ActivityViewModel.kt:559`) → 정지 1 + 새 버튼 1 |
| Todo 연결 | **2** | 하단 Todo 탭(또는 밀기) 1 → 할 일 카드의 ▶ 1(`ui/screen/TodoScreen.kt:2518-2528`) → 자동으로 홈 타이머로 돌아옴(`MainActivity.kt:203, 440-445`) |
| 새 Todo 만들고 연결 | 3 + 입력 | 추가 → 제목 입력 → 추가 버튼(제목 필수, `TodoScreen.kt:2225-2227`) → ▶ |
- 감점 이유: 진행 중 바꾸기가 2탭, 위젯에서 바로 시작 불가, 정지 버튼은 실수로 눌러도 되돌리기가 "최근 기록"의 되돌리기 버튼(`RecentRecordsSection.kt:262`)까지 내려가야 함(스낵바 없음 — 추천 할 일 완료에만 스낵바 있음, `HomeScreen.kt:303-313`).

### A4. 타임라인·통계 표현 — 2.5점 (확신도 상)
- **TimetableBar**(`ui/screen/home/TimetableCardSection.kt:850-1172`): 하루를 0–24시 **30분 칸 48개**로 나눈 높이 14dp 막대(997-999), 칸 사이 2dp. 시간 눈금은 4시간마다 `%02d:00` 10sp(1138-1144), 아래에 범주 범례 점 8dp + 11sp. 추천 할 일은 점선 테두리와 말풍선(1173 `drawRecommendedTodoBubble`)으로 막대 위/아래 번갈아 표시. **빈 곳을 길게 누르면 수면으로 채우기**(985-989, 카드 쪽 처리 361-372) — 화면에 안내가 없는 숨은 동작. 루틴 블록은 길게 눌러야 메뉴.
  - 읽기 쉬움: 30분 칸에 15분짜리 활동이 섞이면 칸 하나에 한 색만 들어가 정확도가 떨어지고, 휴대폰 폭(약 360dp)에서 칸 하나가 약 5.5dp라 탭 대상이 되기 어렵다. "지금" 표시 선은 코드에서 찾지 못함(확신도 중).
- **CityTimetableBar**(`ui/city/CityTimetableBar.kt:226-569`): 도시·섬·보트 그림(타일 198장 + 큰 PNG)으로 활동 길이를 가로 스크롤 장면으로 그리는 실험. **개발자 화면(`ui/screen/home/DevScreens.kt:358`)에서만** 쓰이고 일반 사용자에게 안 보인다. 그림 PNG가 장당 0.4–1.4 MB(`res/drawable/timetable_*.png`, `island_*.png`) — APK 무게 부담.
- **AnalyticsReportSection**(`ui/screen/home/AnalyticsReportSection.kt:211-716`): "오늘 한 일들"(범주별 가로 막대 + 시간, 4개 넘으면 접기, 254-291), "어제와 비교"(오늘 보라/어제 회색 두 막대 + 증감, 293-369). 막대 최소 길이 8%(410, 481, 486)로 작은 값도 보이게 한 배려는 좋다.
  - **7일 평균이 앱에 없다.** `AverageRows`(651)는 정의만 있고 호출이 없으며 `AnalyticsState`에는 오늘·어제만 있다(`ui/viewmodel/ActivityViewModel.kt:97-100`). README·PROJECT_CONTEXT는 "recent 7-day averages in the app"이라고 쓴다 → 문서와 코드 불일치(정직한 리뷰 원칙과 어긋남).
  - 시간 숫자를 범주 색으로 칠함(`AnalyticsReportSection.kt:436-441`) → 노랑·주황·하늘 범주는 흰 바탕에서 거의 안 읽힘(A6 대비표).

### A5. 상태 표현 — 2점 (확신도 상)
- 빈 상태: "아직 기록된 활동이 없습니다."(`TimetableCardSection.kt:350`), "아직 표시할 기록이 없습니다."(`RecentRecordsSection.kt:283`), "오늘 기록된 활동이 없습니다."(`AnalyticsReportSection.kt:272`), "비교할 활동 기록이 없습니다."(339). 글자 한 줄뿐, 다음 행동(어느 버튼을 누르라는지)이나 그림이 없다. 반면 위젯의 빈 상태는 캐릭터 4장 + 문구가 있어 오히려 앱보다 풍부하다.
- 로딩: `CircularProgressIndicator`/`LinearProgressIndicator` 0회. 첫 화면은 Room이 빠르니 문제 적지만 로그인·복원 중에는 안내가 없다.
- 동기화·오프라인: 기록마다 동기화 상태를 보여 주는 표시 없음. 로그인 상태는 프로필 메뉴의 "Signing in..." 문구(`MainActivity.kt:348, 1535`)와 토스트(344-396)뿐. 오프라인 우선 앱인데 "이 기록은 아직 안 올라감"을 알 방법이 없다. 동기화 충돌만 다이얼로그(`MainButtonConflictDialog`)로 보여 준다.
- 오류: 실패는 토스트(`MainActivity.kt:361`)로만.

### A6. 접근성 — 1.5점 (확신도 상)
- 아이콘 `Icon(` 94개 중 설명(contentDescription) 없음 59개, 있음 35개. `Modifier.semantics`·`Role` 사용 0회.
- **가장 중요한 정지 버튼**이 `Box(...).clickable{}`에 흰 네모만 그린 것(`ui/screen/home/TimerSection.kt:550-571`) → 화면 낭독기(TalkBack)에서 이름 없는 버튼.
- 터치 목표(같은 지침: 최소 48×48dp): Todo 완료 30–34dp·시작 32–36dp 원(`ui/screen/TodoScreen.kt:2508-2528`), 최근 기록 아이콘 버튼 34dp·36dp(`ui/screen/home/RecentRecordsSection.kt:390, 416`), **크기 0dp짜리 숨은 IconButton**(403, 409 — 보이지 않지만 낭독기 초점이 잡힐 수 있음, 확신도 중). 시간표 30분 칸 약 5.5dp.
- 글자 크기 확대: 글자는 sp라 커지지만, 버튼 높이 84dp 고정(`ui/component/CategoryButton.kt:51`)·격자 높이를 줄 수×84dp로 계산(`RecommendationSection.kt:489`)·입력칸 46dp 고정(`TimerSection.kt:653`)·`maxLines = 1`이라 큰 글씨 설정에서 잘림 가능(확신도 중).
- 색 대비. Android 접근성 지침(https://developer.android.com/guide/topics/ui/accessibility/apps, 열어 확인)은 18sp 미만 글자(굵으면 14sp 미만)에 4.5:1, 그 밖에 3:1을 권한다. 통계의 시간 숫자는 14sp Bold라 3:1이 기준인데, 범주 색을 흰 바탕 글자로 쓸 때 간식 #FFC107 **1.63**, 식사 #FF9800 **2.16**, 휴식 #00BCD4 **2.30**, 공부 #4CAF50 **2.78** → 4개 범주 미달(양치 3.00 경계). 같은 색을 13sp 보통 굵기 글자에 쓰면(4.5:1 기준) 운동 3.12·씻기 3.68까지 7개 미달. 반대로 어두운 바탕(#121212)에서는 개발 #3949AB 2.42, 회사 #455A64 2.59, 수면 #9C27B0 2.97 미달 → **라이트·다크 각각 다른 범주가 안 보인다.** 위젯 보조 글씨 #887AA5 on #F9F6FF 3.66.
- 햅틱(진동 피드백): Todo 끌어 옮기기에만(`TodoScreen.kt:746, 822`). 시작·정지에는 없음.

### A7. 다크 모드·동적 색·가로/큰 화면 — 1점 (확신도 코드 상 / 실제 모습 중)
- `FlowlogTheme`은 `isSystemInDarkTheme()`과 `dynamicColor = true`(Android 12+ 배경화면 색)를 지원하도록 되어 있다(`ui/theme/Theme.kt:36-56`). 그러나 바탕은 `Color(0xFFF8F8F9)`(`MainActivity.kt:423`, `HomeScreen.kt:331`), 카드·버튼·시트는 `Color.White`를 직접 칠한다. AlertDialog 13개 중 12개, 바텀시트 17개 전부가 바탕색을 직접 지정. → **다크 모드에서도 거의 흰 화면**이고, 테마를 따르는 일부(기본 버튼·텍스트 색 일부)만 어둡게 바뀌어 섞일 위험. 동적 색은 효과가 거의 없다.
- `themes.xml`이 `Theme.Material.Light`라 앱이 뜨는 순간(스플래시)도 라이트 고정.
- 가로·태블릿: `WindowSizeClass`·`BoxWithConstraints`·`LocalConfiguration` 사용 0회. 매니페스트에 방향 고정은 없으니 가로로 돌면 세로 화면이 늘어난 모양이 된다(확신도 중).

### A8. 문구·톤 — 3점 (확신도 상)
- 좋은 점: 알림 톤이 부드럽고 강요하지 않는다. 기록 공백 알림 "꼭 뭔가를 하고 있지 않아도 괜찮아요. 오늘의 흐름만 가볍게 남겨볼까요?"(`notification/InactivityReminderReceiver.kt:162`), "목표 시간에 도달했어요."(`notification/ActivityTimerNotifier.kt:206`), 자동 전환 알림에 "되돌리기" 버튼(362). `strings.xml`에 문자열 294개, `stringResource` 356회로 상당 부분은 리소스화.
- 문제:
  - 한·영 혼재: 홈 제목 "Today's Flow"(`ui/screen/home/HomeHeaderSection.kt:229`), 하단 탭 "Todo"(`MainActivity.kt:1523`), "Petites"(`TodoScreen.kt:397`), 알림 제목 "Flowlog timer"(`ActivityTimerNotifier.kt:39`) + 한국어 본문, 위젯 " · flowing "(`widget/FlowStatusWidgetProvider.kt:146`), `duration_none` = "No timer"(`res/values/strings.xml:9`).
  - 하드코딩 한글 `Text("…")` 61곳, `\uXXXX` 이스케이프 한글 42줄(`ui/component/ActivityItem.kt:153-176` 범주 이름 등) — 범주 이름 표가 앱(`ActivityItem.kt`)·위젯(`FlowStatusWidgetProvider.kt:171-188`)·문자열 리소스(`HomeScreen.kt:338-352`)에 세 벌.
  - 원칙 위반 가능: 첫 실행 화면 "나중에 Flowlog AI가 더 맞는 버튼을 추천해 드려요."(`ui/screen/home/RecommendationSection.kt:369`)와 머리말 "Flowlog AI"(`MainActivity.kt:1258`) — PROJECT_CONTEXT는 "현재 Android 앱에는 AI 기능이 없다"고 함.
  - 위젯 빈 상태가 시간이 지날수록 "아직 흐르지 않는 하루예요"(30–60분) → "빈 흐름이 기다리고 있어요"(60분+)(`FlowStatusWidgetProvider.kt:208-211`)로 바뀐다. 은근한 재촉으로 읽힐 수 있음(판단은 사용자 몫).
  - 집중 완료 알림 "정말 잘했어요 👏 이제 휴식을 취해볼까요?"(`ActivityTimerNotifier.kt:169`)는 칭찬형 — 나쁘진 않지만 앱 철학("코치하지 않는다")과 결이 약간 다르다.

### A9. 위젯·알림 디자인 — 3점 (확신도 상)
- 위젯(`res/layout/flow_status_widget.xml`, `res/xml/flow_status_widget_info.xml`): 5×1칸 알약 모양, 진행 중엔 보라 그라데이션 "액체"가 경과에 따라 차오르고 목표 초과·완료·멈춤마다 색이 바뀜(`widget/FlowStatusWidgetProvider.kt` 렌더러 359-372: 보라 #8464FF→#B38BFF, 초과 분홍→주황, 완료 노랑, 집중 완료 초록). 빈 상태엔 캐릭터 4장이 번갈아(`res/drawable/widget_char_empty_1..4.png`). 개성은 확실하다.
- 한계: 크기 조절은 가로만(`resizeMode="horizontal"`), 버튼 없음(정지·바로 시작 불가), 다크 모드 색 고정(#50466E 글씨), Android 12+ 위젯 모서리·동적 색 미적용. Glance(Compose 위젯) 아님 → RemoteViews.
- 알림: 범주별 단색 알림 아이콘 16종(`ui/component/CategoryIcons.kt:46-64`, `res/drawable/ic_activity_*.xml`) — 상태 표시줄에서 무엇이 도는지 알 수 있어 좋다. 진행 중 알림 제목이 영어 고정 "Flowlog timer".

### A10. 아이콘·브랜드 — 2.5점 (확신도 상)
- 앱 아이콘(`res/mipmap-*/ic_launcher*.webp`): 흰 바탕에 보라 3D 소용돌이 + 시계 눈금·바늘 — 직접 만든 그림이고 "흐름+시간"이 읽힌다. 그러나 적응형 아이콘 배경이 템플릿의 초록 격자 `#3DDC84`(`res/drawable/ic_launcher_background.xml`)라 모서리에 초록이 비침(축소 이미지로 확인). 테마 아이콘용 `monochrome`에 컬러 그림을 그대로 넣어(`res/mipmap-anydpi-v26/ic_launcher.xml`) Android 13+ 테마 아이콘에서 덩어리로 보일 수 있다(확신도 중). `res/drawable/ic_launcher_foreground.xml`은 템플릿 안드로이드 로봇(쓰이지 않음).
- 이름 "Flowlog"와 "Today's Flow", 위젯 "flowing", 집중 모드 "불꽃" — "흐름"이라는 은유는 일관된다. 다만 앱 안 강조색(보라)과 집중(주황), 도시/섬/보트 캐릭터, 위젯 말랑 캐릭터가 서로 다른 세계관이라 브랜드가 한 목소리로 모이지 않는다.

---

## B. 호평 받은 사례 — 한눈 표

**조사 환경 한계(중요):** 이 세션의 네트워크는 대부분의 사이트를 막았다. 실제로 열린 곳은 `developer.apple.com`, `developer.android.com`, `en.wikipedia.org` 세 곳뿐이다. m3.material.io, design.google, blog.google, apps.apple.com, play.google.com, 각 앱 공식 사이트(structured.app, toggl.com, finch.care 등), 언론(The Verge, MacStories, Android Authority 등), namu.wiki는 **모두 열지 못함**(프록시 403 또는 DNS 실패). 그래서:
- "인정받은 근거"는 열어 본 페이지에 적힌 것만 썼다.
- "디자인 특징"에서 출처에 없는 내용은 **[일반 지식]** 표시를 붙였다(이 모델이 알고 있는 내용, 이번에 확인 못 함). 메인이 시안에 쓰기 전 실물(앱·스크린샷)로 한 번 확인하길 권한다.

| # | 사례 | 플랫폼 | 인정받은 근거(열어 확인) | Flowlog에 옮길 핵심 |
|---|---|---|---|---|
| 1 | Structured | iOS·iPadOS·macOS·watchOS | Apple Design Award 2026 Inclusivity 파이널리스트 — https://developer.apple.com/design/awards/ | 세로 하루 타임라인, "쉬는 시간도 일정" |
| 2 | Things 3 | Apple 전 기기 | Apple Design Award 2017 (Things 1.1도 2009) — https://en.wikipedia.org/wiki/Things_(software), https://en.wikipedia.org/wiki/Apple_Design_Awards | 절제된 색, 빠른 입력 |
| 3 | Streaks | iOS | Apple Design Award 2016 — https://en.wikipedia.org/wiki/Apple_Design_Awards | 큰 원형 타일 격자, 길게 눌러 완료 |
| 4 | Flighty | iOS·macOS | ADA 2023 Interaction 수상 — https://developer.apple.com/design/awards/2023/, https://en.wikipedia.org/wiki/Flighty | 진행 중 상태를 잠금화면·알림에 |
| 5 | Gentler Streak | iPhone·iPad·Watch | ADA 2024 Social Impact 수상 — https://developer.apple.com/design/awards/2024/ | 다그치지 않는 톤, "비교 아닌 진행" 요약 |
| 6 | Tiimo | iPhone·iPad·Watch | ADA 2024 Inclusivity 파이널리스트 — https://developer.apple.com/design/awards/2024/ | 시각적 하루 계획, 남은 시간 표현 |
| 7 | Rise: Energy & Sleep | iOS | ADA 2023 Innovation 파이널리스트 — https://developer.apple.com/design/awards/2023/ | 하루 곡선 위에 "지금" 표시 |
| 8 | Opal | iPhone·iPad | ADA 2025 Social Impact 파이널리스트 — https://developer.apple.com/design/awards/2025/ | 위젯·단축어, 햅틱 보상 |
| 9 | (Not Boring) Habits | iPhone·iPad | ADA 2022 Delight and Fun 수상 — https://developer.apple.com/design/awards/2022/ | 장난스러운 햅틱·질감 |
| 10 | Bears Gratitude | iPhone·iPad·Mac | ADA 2024 Delight and Fun 수상 — https://developer.apple.com/design/awards/2024/ | 캐릭터를 "입구"로 쓰기 |
| 11 | Forest | iOS·Android·브라우저 | Common Sense Media 4/5, Mashable 4.5/5(위키 인용) — https://en.wikipedia.org/wiki/Forest_(app) | 쌓인 시간을 그림으로 보는 기록 |
| 12 | Toggl Track | 웹·데스크톱·iOS·Android·watchOS | 상 기록은 출처에 없음. 시작/정지 버튼 + 달력 블록 끌기 — https://en.wikipedia.org/wiki/Toggl_Track | 끌어서 고치는 달력 보기 |
| 13 | Todoist | 웹·모든 OS·Wear OS | 상 기록은 출처에 없음. 2015 자연어 입력 — https://en.wikipedia.org/wiki/Todoist | 문장 한 줄로 입력 |
| 14 | Google Calendar (Android) | Android·iOS·웹 | 2015 Material 개편 때 CNET "cleaner", "colorful graphics" — https://en.wikipedia.org/wiki/Google_Calendar | 범주별 삽화, 일정 보기 |
| 15 | Daylio | iOS·Android | 노트르담대 연구자가 "탭으로 기록" 설계를 칭찬(위키 인용) — https://en.wikipedia.org/wiki/Daylio | 아이콘 탭만으로 기록, Year in Pixels |
| 16 | Samsung Health | Android(삼성)·iOS | 상 기록은 출처에 없음. 대시보드 한 화면 + 사용자 편집 — https://en.wikipedia.org/wiki/Samsung_Health | 카드 순서·표시를 사용자가 고름 |
| 17 | Duolingo (반면교사) | iOS·Android | ADA 2023 Delight and Fun 수상 — https://developer.apple.com/design/awards/2023/ ; 죄책감 유발 알림 비판(위키가 인용한 2018 The Verge 기사 제목) — https://en.wikipedia.org/wiki/Duolingo | 옮기지 말 것: 연속 기록 압박 |
| 18 | **Material 3 Expressive**(지침) | Android 16·Wear OS 6 | Google 공식 문서 — https://developer.android.com/develop/ui/compose/designsystems/material3, https://developer.android.com/design/ui/wear/guides/get-started, https://developer.android.com/reference/kotlin/androidx/compose/material3/MotionScheme, https://developer.android.com/jetpack/androidx/releases/compose-material3, https://en.wikipedia.org/wiki/Material_Design | 모양·움직임·색·글자 크기로 주 행동을 돋보이게 |

**열지 못해 표에서 뺀 후보:** Fantastical(위키 문서 없음, flexibits.com 차단), Timery(공식 사이트 차단), Finch(finch.care 차단), Habitify(차단), 열품타(공식·나무위키 차단), Google Play "Best of"(play.google.com 차단 — 위키 Google_Play 문서는 어워드 제도만 있고 생산성 앱 수상작 이름이 없음). Material 3 Expressive의 연구 수치(연구 46건·참가자 1.8만 명·"주 행동을 최대 4배 빨리 찾음")는 검색 요약에만 나왔고 원문(design.google·blog.google)을 **열지 못함** → 근거로 쓰지 말 것.

## B. 상세

표기: (출처) = 열어 본 페이지에 적힌 것, [일반 지식] = 이번에 확인 못 한 이 모델의 지식. "옮길 것" 2개 / "옮기면 안 되는 것" 1개는 Flowlog 철학("낮은 마찰·정직한 리뷰", PROJECT_CONTEXT: 습관 코치 아님, 데이터가 받쳐 주는 것만 말함) 기준.

### B1. Structured — iOS·iPadOS·macOS·watchOS
- 근거: ADA 2026 Inclusivity 파이널리스트. Apple 설명(출처): "Visually sharp and easy to scan… prioritizes downtime as much as productivity… helping you find time to take breaks", 신경다양성(neurodivergent) 사용자들이 "simple layout"을 칭찬. https://developer.apple.com/design/awards/
- 디자인 특징: ① (출처) 훑어보기 쉬운 단순 배치 ② (출처) 쉬는 시간을 일정과 같은 무게로 다룸 ③ [일반 지식] 하루를 **세로 타임라인**으로, 각 일은 둥근 아이콘 + 길이에 비례한 캡슐, 사이를 선으로 잇는다 ④ [일반 지식] 일마다 색 하나, 지금 시각에 진행 표시 ⑤ [일반 지식] 빈 시간에 "자유 시간"처럼 이름 붙여 보여 줌.
- 옮길 것: (a) 오늘 기록을 세로 타임라인 + 길이 비례 캡슐로 — Flowlog의 14dp 가로 막대보다 읽기 쉽고 탭하기 쉽다. (b) 빈 시간을 "기록 없음"으로 정직하게 보여 주되 비난하지 않는 표현.
- 옮기면 안 되는 것: 계획을 미리 짜 넣는 "플래너" 중심 — Flowlog는 실제 한 일을 기록하는 앱이라 계획 블록이 실제 기록보다 커 보이면 리뷰가 흐려진다.

### B2. Things 3 — Apple 전 기기
- 근거: ADA 2017(Things 1.1은 2009). https://en.wikipedia.org/wiki/Things_(software), https://en.wikipedia.org/wiki/Apple_Design_Awards
- 디자인 특징: ① (출처) 수집(Inbox)·정리(Projects/Areas)·일정(Today/Upcoming/Anytime/Someday) 구조 ② (출처) Mac Quick Entry·위젯·단축어 등 시스템 연동 ③ [일반 지식] 거의 흰 바탕에 파랑 하나만 강조색, 여백이 넓다 ④ [일반 지식] "Magic Plus" 버튼을 끌어 원하는 위치에 새 항목 삽입 ⑤ [일반 지식] 완료 체크에 작은 튕김 애니메이션·소리.
- 옮길 것: (a) 강조색 하나 원칙 — Flowlog의 보라 5종을 하나로. (b) 어디서든 부를 수 있는 빠른 입력(Flowlog라면 위젯·알림·바로가기에서 범주 시작).
- 옮기면 안 되는 것: GTD식 5단계 분류 — Flowlog Todo는 이미 탭 5개, 더 쪼개면 마찰이 늘어난다.

### B3. Streaks — iOS
- 근거: ADA 2016. https://en.wikipedia.org/wiki/Apple_Design_Awards
- 디자인 특징 [모두 일반 지식]: ① 한 화면에 큰 원형 타일 최대 12개 격자 ② 길게 눌러 완료(실수 방지) + 링이 차오름 ③ 강한 단색 테마를 사용자가 고름 ④ 햅틱 ⑤ 위젯·워치 컴플리케이션.
- 옮길 것: (a) 범주 버튼을 크게, 아이콘 중심 타일로 — 현재 84dp 가로 카드 2열보다 한눈에 들어옴. (b) "정지"처럼 되돌리기 어려운 행동엔 길게 누르기 또는 정지 후 스낵바 되돌리기.
- 옮기면 안 되는 것: 연속 일수(streak) 강조 — 끊기면 실패처럼 느껴져 "정직한 기록"보다 "기록을 지키려는 기록"을 부른다.

### B4. Flighty — iOS·macOS
- 근거: ADA 2023 Interaction 수상, App of the Year 파이널리스트. Apple 설명(출처): "incredible Live Activities and Dynamic Island integration… key information where you need it most… a look that mirrors time-honored airport design conventions." https://developer.apple.com/design/awards/2023/, https://en.wikipedia.org/wiki/Flighty
- 디자인 특징: ① (출처) 진행 중 정보를 잠금화면·다이내믹 아일랜드에 ② (출처) 공항 안내판 관례를 따른 시각 언어 ③ (출처) 필요한 곳에 핵심 정보 ④ (출처) 평생 통계 "Passport" ⑤ [일반 지식] 어두운 바탕 + 상태별 색(정시 초록·지연 노랑/빨강), 고정폭 숫자.
- 옮길 것: (a) Android의 진행 중 알림(Live Update/진행 알림)에 경과 시간·범주·정지 버튼 — 앱을 안 열어도 됨. (b) 시간 숫자는 고정폭(tabular) 숫자로, 상태별 색 규칙을 하나로.
- 옮기면 안 되는 것: 예측("지연될 것") 기능 — Flowlog는 확정 기록만 말한다는 원칙.

### B5. Gentler Streak — iPhone·iPad·Apple Watch
- 근거: ADA 2024 Social Impact 수상. Apple 설명(출처): "powered not by insistent reminders but an optimistic and encouraging vibe… a subtle and consistently pleasing design language… Monthly Summary view… is less about hard comparisons and more about progress." https://developer.apple.com/design/awards/2024/
- 디자인 특징: ① (출처) 다그치는 알림 대신 낙관적 톤 ② (출처) 은은하고 일관된 디자인 언어 ③ (출처) 자기 과거와 비교하는 월간 요약 ④ [일반 지식] 파스텔 배경 + 캐릭터(Yorhart) ⑤ [일반 지식] "활동 경로" 띠 그래프(권장 범위 안/밖).
- 옮길 것: (a) "어제와 비교"를 승패(±)가 아니라 **자기 평소 범위** 안/밖으로 — 7일 평균을 띠로 그리고 오늘을 점으로. (b) 알림·빈 상태 문구 원칙을 문서화(이미 부드러운 톤을 체계로).
- 옮기면 안 되는 것: 건강 "권장량" 제시 — Flowlog는 최적 루틴을 안다고 말하지 않는다.

### B6. Tiimo — iPhone·iPad·Apple Watch
- 근거: ADA 2024 Inclusivity 파이널리스트(Apple 설명 없음). https://developer.apple.com/design/awards/2024/
- 디자인 특징 [모두 일반 지식]: ① 시각적 하루 일정(아이콘+색 블록) ② 남은 시간을 줄어드는 원/막대로 ③ 부드러운 파스텔 ④ 큰 글자·아이콘 ⑤ 일정 시작 시 알림+시각 타이머.
- 옮길 것: (a) 목표가 있는 타이머(양치 3분·루틴)는 남은 시간을 원형으로. (b) 범주마다 아이콘+이름을 늘 같이(색에만 의존하지 않기 — 색약 대응).
- 옮기면 안 되는 것: 하루 전체를 미리 시각 계획 — B1과 같은 이유.

### B7. Rise: Energy & Sleep Tracker — iOS
- 근거: ADA 2023 Innovation 파이널리스트. https://developer.apple.com/design/awards/2023/
- 디자인 특징 [모두 일반 지식]: ① 하루 에너지 곡선 위 "지금" 점 ② 어두운 남색 바탕 + 형광 강조 ③ 수면 빚을 큰 숫자 하나로 ④ 다음 할 일 한 줄 ⑤ 위젯.
- 옮길 것: (a) 오늘 타임라인에 **지금 선**(현재 시각)과 진행 중 블록이 자라는 표시. (b) 홈 맨 위에 "지금 하는 일" 큰 숫자 하나만.
- 옮기면 안 되는 것: 생체 리듬 "예측 곡선" — 데이터가 받쳐 주지 않는 주장.

### B8. Opal — iPhone·iPad
- 근거: ADA 2025 Social Impact 파이널리스트. Apple 설명(출처): "full of helpful tools like widgets, Shortcuts, and easy-to-set-up customizations… haptics when unlocking 'gems'." https://developer.apple.com/design/awards/2025/
- 디자인 특징: ① (출처) 위젯·단축어 ② (출처) 쉬운 설정 ③ (출처) 보상 순간의 햅틱 ④ [일반 지식] 어두운 바탕 + 보석 그래픽 ⑤ [일반 지식] 집중 세션 중 큰 원형 타이머.
- 옮길 것: (a) 시작·정지·저장에 짧은 햅틱 — 지금은 Todo 끌기에만 있음. (b) 집중 모드 설정을 한 화면(시트 하나)에서.
- 옮기면 안 되는 것: 보석·레벨 보상 — 기록을 "점수"로 만들면 정직한 기록이 흔들린다.

### B9. (Not Boring) Habits — iPhone·iPad
- 근거: ADA 2022 Delight and Fun 수상. Apple 설명(출처): "sensational designs, playful haptics, and elegant gamification… a journey through forests and mountains." https://developer.apple.com/design/awards/2022/
- 디자인 특징: ① (출처) 장난스러운 햅틱 ② (출처) 숲·산 여행 은유 ③ [일반 지식] 3D 질감 아이콘 ④ [일반 지식] 큰 굵은 글꼴 ⑤ [일반 지식] 한 화면 한 가지 동작.
- 옮길 것: (a) Flowlog의 "흐름(물)" 은유를 위젯처럼 앱 안에도 — 진행 중 타이머 카드에 물이 차오르는 표현을 통일. (b) 3D 앱 아이콘과 맞는 질감을 한두 곳(빈 상태 그림)에만.
- 옮기면 안 되는 것: 게임화 여정(레벨·지도) — 코치·습관 형성 약속에 가깝다.

### B10. Bears Gratitude — iPhone·iPad·Mac
- 근거: ADA 2024 Delight and Fun 수상. Apple 설명(출처): 캐릭터가 "serve as a welcoming way into the content… a simple way to encourage and embrace honest self-reflection." https://developer.apple.com/design/awards/2024/
- 디자인 특징: ① (출처) 캐릭터가 내용으로 들어가는 입구 ② (출처) 정직한 자기 돌아보기 ③ (출처) 생각해서 배치한 접점들 ④ [일반 지식] 손그림 질감 ⑤ [일반 지식] 따뜻한 크림색 바탕.
- 옮길 것: (a) 이미 있는 위젯 캐릭터(`res/drawable/widget_char_empty_*.png`)를 앱 빈 상태에도 — "아직 기록이 없어요 + 버튼 하나". (b) 하루 끝 "오늘 돌아보기" 한 장 요약.
- 옮기면 안 되는 것: 매일 써야 하는 의례(감사 일기 같은 숙제) — 기록 공백을 죄로 만들 수 있다.

### B11. Forest — iOS·Android·브라우저
- 근거: 위키 인용 리뷰 Common Sense Media 4/5("visual representation of time as a growing tree"), Mashable 4.5/5. 상 기록은 출처에 없음. https://en.wikipedia.org/wiki/Forest_(app)
- 디자인 특징: ① (출처) 집중하는 동안 나무가 자람 ② (출처) 앱을 떠나면 나무가 죽음 ③ (출처) 끝낸 나무가 숲 = 시각적 기록 ④ (출처) 활동 태그 ⑤ [일반 지식] 큰 원형 타이머 + 초록 단색.
- 옮길 것: (a) 쌓인 기록을 "그림으로 된 하루"로(도시/섬 시간표 실험의 방향이 바로 이것 — 개발자 화면에서 꺼낼 가치). (b) 범주 태그를 기록 후에도 쉽게.
- 옮기면 안 되는 것: 실패 시 벌(죽는 나무) — Flowlog의 "꼭 뭔가 하지 않아도 괜찮아요" 톤과 정반대.

### B12. Toggl Track — 웹·데스크톱·iOS·Android·watchOS
- 근거: 상 기록은 출처에 없음(위키). 시작/정지 버튼, 수동 입력, **달력 보기에서 블록을 끌고 늘려 고치기**(출처). https://en.wikipedia.org/wiki/Toggl_Track
- 디자인 특징: ① (출처) 시작/정지 한 버튼 ② (출처) 달력에서 끌어 만들기·고치기 ③ (출처) 수동 입력 ④ [일반 지식] 분홍/보라 강조, 큰 타이머 숫자 ⑤ [일반 지식] 유휴 감지 후 "그 시간 버릴까?" 묻기.
- 옮길 것: (a) 오늘 타임라인에서 블록 가장자리를 끌어 시작·끝 고치기(지금은 수정 다이얼로그). (b) 빈 시간을 길게 눌러 채우는 기능(이미 수면 채우기)을 "아무 범주로 채우기"로 넓히고 화면에 안내.
- 옮기면 안 되는 것: 프로젝트·고객·청구 금액 같은 업무용 칸 — 개인 경량 앱에 과함.

### B13. Todoist — 웹·모든 OS·Wear OS
- 근거: 상 기록은 출처에 없음. 2015 자연어로 반복 일정 해석, Karma 게임화(출처). https://en.wikipedia.org/wiki/Todoist
- 디자인 특징: ① (출처) 문장 입력 → 날짜·반복 인식 ② (출처) Karma 점수 ③ (출처) Upcoming 보기 ④ [일반 지식] 빨강 강조 하나, 흰 바탕 ⑤ [일반 지식] 우선순위 색 4단계.
- 옮길 것: (a) Todo 추가를 한 줄 입력 + 칩(오늘·과제·복습)으로 — 지금은 시트에 칸 여러 개. (b) 강조색 하나 + 우선순위만 별도 색.
- 옮기면 안 되는 것: Karma 같은 생산성 점수.

### B14. Google Calendar(Android) — Android·iOS·웹
- 근거: 2015 Material 개편 때 CNET "cleaner", "colorful graphics"; 일정 종류별 삽화(영화 → 팝콘), 계절 그림(출처). https://en.wikipedia.org/wiki/Google_Calendar
- 디자인 특징: ① (출처) 일정 종류별 삽화 ② (출처) 달마다 계절 그림 ③ (출처) Material 기반 ④ [일반 지식] 일정 보기(Schedule)·일·3일·주 보기 전환 ⑤ [일반 지식] 동적 색 적용, 지금 시각 빨간 선.
- 옮길 것: (a) 타임라인 보기 확대 단계(오늘/3일/주)를 핀치로. (b) 지금 시각 선.
- 옮기면 안 되는 것: 삽화가 공간을 많이 먹는 것(iMore 비판: "graphics wasted space", 출처) — 홈은 기록 버튼이 먼저.

### B15. Daylio — iOS·Android
- 근거: 위키 인용 — 노트르담대 연구자가 단순한 탭 기록 설계를 칭찬, LifeHacker "private and fast micro journal". 반대로 2020 연구(Hussain 등)는 가입 화면·권한·iOS/Android 불일치·**아이콘 과밀**을 비판(출처). https://en.wikipedia.org/wiki/Daylio
- 디자인 특징: ① (출처) 기분 5단계 + 활동 아이콘 탭, 글은 선택 ② (출처) 자동 갱신 차트 ③ (출처) Year in Pixels(하루 = 색 칸 하나) ④ (출처) CSV 내보내기 ⑤ (출처) 연속 기록·업적.
- 옮길 것: (a) Year in Pixels처럼 **날마다 한 칸** 달력 히트맵(주 범주 색) — 7일 평균보다 정직하고 한눈에. (b) "글은 선택" 원칙 유지(Flowlog 제목 선택과 같음).
- 옮기면 안 되는 것: 아이콘을 많이 늘어놓은 화면(연구가 비판한 과밀) — 메인 버튼 10개 상한도 재검토 근거.

### B16. Samsung Health — Android(삼성)·iOS
- 근거: 상 기록은 출처에 없음. 대시보드가 첫 화면, 최근 데이터를 한 쪽에, **구성과 배치를 사용자가 바꿈**; 걸음 수 24시간 막대 그래프(출처). https://en.wikipedia.org/wiki/Samsung_Health
- 디자인 특징: ① (출처) 한 쪽 대시보드 ② (출처) 사용자 편집 가능한 카드 ③ (출처) 24시간 막대 그래프 + 일·주·월 평균 ④ (출처) 동물 테마 챌린지 ⑤ [일반 지식] One UI의 큰 제목·아래쪽 손 닿는 영역 배치.
- 옮길 것: (a) 홈 카드(빠른 타이머·시간표·최근 기록·통계)를 사용자가 숨기고 순서 바꾸기. (b) 일·주 전환 막대 그래프.
- 옮기면 안 되는 것: 챌린지·배지.

### B17. Duolingo — 반면교사
- 근거: ADA 2023 Delight and Fun 수상(출처, "endearingly tenacious mascot"). https://developer.apple.com/design/awards/2023/ ; 위키는 2018 The Verge 기사 "Duolingo redesigned its owl to guilt-trip you even harder"를 인용하고 마스코트가 사용자를 쫓는 밈을 소개(출처). https://en.wikipedia.org/wiki/Duolingo
- 디자인 특징: ① 마스코트 ② 연속 기록(불꽃) ③ 퀘스트·리더보드 ④ 맞춤 알림 시점(밴딧 알고리즘, 출처) ⑤ 밝은 원색.
- 옮길 것: (a) 마스코트의 "성격"을 문구 톤 기준으로 — Flowlog 캐릭터는 다그치지 않는 쪽. (b) 알림 시점을 사용자 기록에 맞추는 생각(이미 식후·기상 후 넛지 있음).
- 옮기면 안 되는 것: **죄책감 알림·불꽃 연속 기록** — Flowlog 위젯 빈 상태의 시간 따라 바뀌는 문구("빈 흐름이 기다리고 있어요")도 이 방향으로 가지 않게.

### B18. Material 3 Expressive — Google 지침 (Android 16, Wear OS 6)
- 근거(열어 확인): Compose 문서 "M3 Expressive is an expansion of Material Design 3, including research-backed updates to theming, components, motion, typography… supports Material You personalization features like dynamic color… complements the Android 16 visual style" — https://developer.android.com/develop/ui/compose/designsystems/material3 ; Wear 지침 "Expressive design elevates each UI layer with thoughtful shape, animation, color, and typography… Premium motion and springs… Motion now spatially connects surfaces" — https://developer.android.com/design/ui/wear/guides/get-started ; 위키: 2025년 5월 The Android Show: I/O Edition에서 발표, 2025년 9월 Pixel부터 배포 — https://en.wikipedia.org/wiki/Material_Design
- Compose 구현 상태(열어 확인): `MotionScheme.expressive()`/`standard()` — "expressive scheme is Material's recommended motion scheme for prominent UI elements and hero interactions", **material3 1.5.0-beta01에서 추가**(https://developer.android.com/reference/kotlin/androidx/compose/material3/MotionScheme). 릴리스 노트: 최신 안정판 1.4.0, 1.5.0-beta01(2026-10-07); `ButtonGroup`·`FloatingToolbar`·FAB 메뉴·`SplitButton`·`ToggleButton` 등이 1.5.0 알파 동안 실험 딱지를 뗐고, `MaterialShapes`·`LoadingIndicator`의 안정 승격은 한 번 되돌려졌다(https://developer.android.com/jetpack/androidx/releases/compose-material3). API 목록에 `MaterialExpressiveTheme`, `expressiveLightColorScheme`, `WavyProgressIndicator`, `LoadingIndicator`, `MaterialShapes` 존재(https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary).
- Flowlog 현황: Compose BOM `2026.02.01`(`gradle/libs.versions.toml`) — 이 BOM의 material3 버전은 확인 못 함(아마 1.4.x). Expressive 전면 적용엔 1.5.0으로 올리는 작업이 따라온다.
- 디자인 특징: ① 모양(둥근 정도의 범위, 모양 바꿈) ② 스프링 움직임 ③ 색(동적 색 + 강조 대비) ④ 크기·글자(큰 제목, 주 행동 크게) ⑤ 담기(containment: 묶음을 컨테이너로 분명히).
- 옮길 것: (a) 주 행동(시작/정지) 하나를 크고 독특한 모양으로 — 정지 버튼을 `ButtonGroup`/큰 FAB 모양으로. (b) `MaterialTheme` 토큰(색·글자·모양·움직임)을 실제로 쓰게 바꾸기 — 다크·동적 색·접근성이 한꺼번에 따라온다.
- 옮기면 안 되는 것: 장식적 모양 바꿈·흔들리는 움직임을 기록 화면 곳곳에 — 빠른 기록에선 움직임이 기다림이 된다(expressive는 "hero"에만, 나머지 standard).

---

## C. 새 시안 방향 3가지

### 공통 0단계 (어느 방향이든 먼저)
A에서 본 문제 대부분(다크 모드 안 됨, 보라 5종, 범주 색 두 벌, 대비 미달, 글자 크기 21종)은 **디자인 토큰이 없어서** 생긴다. 세 방향 모두 다음을 전제로 한다.
- `ui/theme/`에 진짜 `ColorScheme`(라이트·다크) + 범주 색 표 하나(`CategoryPalette`, 라이트·다크 쌍) + `Typography`(실제로 쓰는 6–7단계) + `Shapes`(3–4단계).
- 화면 코드의 `Color(0x…)`·`Color.White`·`fontSize = n.sp`를 토큰으로 바꾼다. 범주 이름 표 세 벌(`ActivityItem.kt`·위젯·strings)을 하나로.
- 아래 범주 8개 색은 모두 스크립트로 대비를 계산했다: 라이트는 흰 표면에서 **4.5:1 이상**(글자로 써도 됨), 다크는 각 방향의 어두운 표면에서 **7:1 이상**. 범주는 색만으로 구분하지 않고 늘 아이콘+이름을 붙인다.
- 범주 8개: 수면·휴식·공부·업무·학교·식사·운동·할일(README의 기본 타이머 범주). 나머지 범주(개발·독서·이동·씻기·간식·양치·취미·기타)는 이 8색의 명도 변형 또는 중립색으로.

---

### 방향 ① "Flowlog Calm" — 지금 구조를 지키며 다듬기
**컨셉 한 문장:** 화면 배치와 손에 익은 흐름은 그대로 두고, 색·글자·간격·접근성·다크 모드를 하나의 체계로 정리해 "같은 앱인데 훨씬 정돈된" 느낌을 만든다.

**근거 사례:** Things 3(B2, 강조색 하나·여백), Gentler Streak(B5, 은은하고 일관된 디자인 언어), Streaks(B3, 큰 타일), Material 3 토큰 문서(B18).

**색 팔레트**
| 역할 | 라이트 | 다크 |
|---|---|---|
| 바탕 | #F7F7FA | #12131A |
| 표면(카드) | #FFFFFF | #1C1D26 |
| 글자 | #151A2D | #ECEDF3 |
| 보조 글자 | #5E6577 (바탕 대비 5.45) | #A3A7B7 (7.73) |
| 주 강조(브랜드 보라, 하나만) | #5140D8 (흰 글자 6.83) | #B9AEFF (진한 글자 #1B1060과 8.19) |
| 집중 모드 강조 | #C2410C | #FFB599 |

| 범주 | 라이트(흰 표면 대비) | 다크(#1C1D26 대비) |
|---|---|---|
| 수면 | #3F4BA8 (7.55) | #A8B2F0 (8.21) |
| 휴식 | #0E7C86 (4.95) | #5FD3DB (9.44) |
| 공부 | #2E7D32 (5.13) | #81C784 (8.33) |
| 업무 | #4F5B66 (6.95) | #B0BEC5 (8.79) |
| 학교 | #C2185B (5.87) | #F48FB1 (7.51) |
| 식사 | #B85C00 (4.60) | #FFB74D (9.68) |
| 운동 | #0277BD (4.80) | #81D4FA (10.16) |
| 할일 | #5140D8 (6.83) | #B9AEFF (8.43) |
동적 색(배경화면 색)은 설정에서 켜는 선택지로(기본은 브랜드 색) — 범주 색은 동적 색과 무관하게 고정.

**타이포:** Pretendard(OFL 라이선스, 한글·영문 고른 무게) 또는 시스템 기본(Roboto + 기기 한글 글꼴) 유지. 숫자는 `fontFeatureSettings = "tnum"`(고정폭 숫자)로 타이머가 흔들리지 않게. 단계: 제목 24/Bold, 섹션 18/SemiBold, 본문 15/Regular, 보조 13/Regular, 라벨 12/Medium, 타이머 40/SemiBold tnum — 7단계. *(Pretendard 배포처·Google Fonts 수록 여부는 이번에 확인 못 함: fonts.google.com·github 접속 차단.)*

**핵심 화면 5개** (폭 360dp 기준, 위→아래)
```
[홈 — 멈춤]                         [타이머 진행 중]
┌──────────────────────────┐        ┌──────────────────────────┐
│ 오늘의 흐름      ⟳ ☰ (●) │        │ 오늘의 흐름        ⟳ ☰ (●) │
│ 10월 20일 (월)            │        │ ┌──────────────────────┐ │
│ ┌──────────────────────┐ │        │ │ 📖 공부 · 선형대수    │ │
│ │ 무엇을 하고 있나요?   │ │        │ │ 00:42:17   (■ 정지)  │ │ ← 정지 56dp, 이름 "기록 끝내기"
│ │ [🛏수면] [☕휴식]      │ │        │ │ ▓▓▓▓▓▓░░░ 목표 60분   │ │
│ │ [📖공부] [💼업무]      │ │        │ │ 제목: [선형대수][과제]│ │
│ │ [🏫학교] [🍽식사]      │ │        │ │ 바꾸기: 휴식 식사 …   │ │ ← 새: 탭 1번으로 전환
│ └──────────────────────┘ │        │ └──────────────────────┘ │
│ 빠른 타이머  양치3분 간식 │        │ (아래 시간표·기록 동일)   │
│ 오늘 시간표 ▁▃▅▇▅▃  지금│        └──────────────────────────┘
│ 최근 기록 3              │
│ 통계 리포트              │
├──────────────────────────┤
│   🏠 홈        ☑ 할 일    │
└──────────────────────────┘
[오늘 타임라인 — 홈 카드 확대]       [통계]                         [Todo]
┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│ 오늘 시간표   반복 루틴 › │ │ 오늘 한 일   어제 · 7일   │ │ 할 일              ＋ 추가│
│ 0   4   8  12  16  20  24│ │ 📖 공부  ████████  3h10m │ │ [전체][오늘][과제][복습]  │
│ ▆▆▆▆▆░░▆▆▆▃▃▆▆▆│░░░░░░░ │ │ 💼 업무  █████     1h40m │ │ ┌ ○ 선형대수 3장  ▶ ✓ ┐ │ ← ▶·✓ 48dp
│ 막대 높이 28dp, 칸 15분 ↑지금│ │ 🍽 식사  ██         45m │ │ └ 누적 1h20m          ┘ │
│ 범례 아이콘+이름          │ │ 평소(7일) 범위 ▒▒  오늘 ● │ │ Petites ✦ …             │
│ 빈 곳 길게: "채우기" 안내 │ │ "평소보다 공부 +40분"     │ │ Daily Cues …            │
└──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
```
**바뀌는 흐름(탭 수):** 시작 1 → 1, 저장 1 → 1(정지 뒤 5초 스낵바 "되돌리기" 추가), **활동 바꾸기 2 → 1**(진행 중 카드의 "바꾸기" 칩), 위젯에서 시작 2 → 1(위젯에 즐겨찾기 범주 3개 버튼), Todo 연결 2 → 2. 7일 평균이 실제로 보이게 됨(지금은 코드만 있고 안 보임).

**구현 난이도: 중.** 화면 구조는 그대로라 위험은 낮지만, `Color(0x…)` 339곳·`fontSize` 352곳을 토큰으로 바꾸는 넓은 기계적 작업. 접근성(설명·48dp·semantics)도 같이.

**위험:** 사용자가 "달라진 게 없다"고 느낄 수 있음(투자 대비 체감 작음). 범주 색이 조금씩 바뀌어(예: 공부 #4CAF50 → #2E7D32) 기존 기록 색에 익숙한 눈이 잠깐 헷갈림. 홈에 카드 6개가 쌓인 근본 문제(정보 과밀)는 남는다.

---

### 방향 ② "Flowlog River" — 오늘 타임라인 중심 재구성
**컨셉 한 문장:** 홈을 "오늘이라는 강"으로 바꾼다 — 화면 전체가 위에서 아래로 흐르는 세로 타임라인이고, 지금 하는 일은 맨 아래 '지금 선'에서 자라나며, 시작 버튼은 엄지가 닿는 아래쪽 독(dock)에 둔다.

**근거 사례:** Structured(B1, 세로 타임라인·쉬는 시간도 일정), Rise(B7, 하루 위 "지금" 표시), Toggl Track(B12, 블록 끌어 고치기), Google Calendar(B14, 지금 선·보기 전환), Daylio(B15, 날마다 한 칸), Forest(B11, 쌓인 시간을 그림으로). Flowlog 자체의 "흐름" 은유와 위젯의 물 차오르는 표현을 앱 본체로 끌어온다.

**색 팔레트** (물·종이 느낌: 차분한 파랑 강조, 범주 색은 채도 낮게)
| 역할 | 라이트 | 다크 |
|---|---|---|
| 바탕 | #F4F7F9 | #0F161D |
| 표면 | #FFFFFF | #17212B |
| 글자 | #14202B | #E6EDF2 |
| 보조 글자 | #5B6873 (5.31) | #9DAAB5 (7.68) |
| 주 강조(물빛 파랑) | #1F6FB5 (흰 글자 5.25) | #8CC4F5 (진한 글자 #0B2540과 8.37) |
| 지금 선·진행 중 | #6B4FD8(브랜드 보라를 "지금"에만) | #B8A6FF |

| 범주 | 라이트(흰 표면 대비) | 다크(#17212B 대비) |
|---|---|---|
| 수면 | #3D4FA8 (7.29) | #9AA8F0 (7.16) |
| 휴식 | #2F7F95 (4.57) | #7CC8DA (8.64) |
| 공부 | #2E7D4F (5.05) | #7FD1A0 (8.95) |
| 업무 | #5C6670 (5.85) | #AEB8C2 (8.10) |
| 학교 | #B03A6B (5.73) | #F29BC0 (7.93) |
| 식사 | #B35A1F (4.77) | #F2A877 (8.26) |
| 운동 | #1F6FB5 (5.25) | #8CC4F5 (8.79) |
| 할일 | #6B4FD8 (5.62) | #B8A6FF (7.71) |
(운동과 주 강조가 같은 파랑 — 시안에서 운동을 #0E7490 계열로 옮길지 메인이 판단. 블록 채움은 범주색 16% 투명 + 왼쪽 4dp 실선으로 칠해 글자 대비를 지킨다.)

**타이포:** IBM Plex Sans KR(본문·제목) + IBM Plex Mono 또는 tnum 숫자(시각·경과 시간). 시각 눈금은 12/Medium, 블록 제목 15/SemiBold, 블록 시간 13/Regular tnum, 지금 경과 34/SemiBold tnum. *(두 글꼴 모두 Google Fonts 수록으로 알고 있으나 이번에 확인 못 함.)*

**핵심 화면 5개**
```
[홈 = 오늘 타임라인, 멈춤]            [타이머 진행 중]
┌──────────────────────────┐        ┌──────────────────────────┐
│ 10월 20일 월   일│3일│주  ☰│        │ 10월 20일 월   일│3일│주  ☰│
│ 07 ─┬ 🛏 수면  7h05m      │        │ 13 ─┬ 📖 공부  1h10m      │
│     │                    │        │ 14 ─┤ ☕ 휴식  15m         │
│ 08 ─┼ 🍽 식사  25m        │        │     │ ░ 기록 없음 20m  ＋ │ ← 탭하면 범주 칩
│     │ ░ 기록 없음 40m ＋  │        │ 15 ─┼ 💼 업무 ┃자라는 중  │
│ 09 ─┼ 🏫 학교  3h00m      │        │━━━━━┿━ 지금 15:42 ━━━━━━━│ ← 지금 선(보라)
│ 12 ─┼ 🍽 식사  40m        │        │ ┌──────────────────────┐ │
│━━━━━┿━ 지금 12:58 ━━━━━━━│        │ │ 💼 업무 · 보고서      │ │
│ (예정 루틴은 점선 블록)   │        │ │ 00:42:17 tnum  [■ 끝] │ │ ← 독이 "진행 카드"로 변신
├──────────────────────────┤        │ │ [회의][보고서] 바꾸기› │ │
│ 독: [🛏][☕][📖][💼][⋯]   │ ← 64dp │ └──────────────────────┘ │
│      할 일 ▾  · 오늘 4h20 │        ├──────────────────────────┤
├──────────────────────────┤        │  🌊 오늘   📊 돌아보기  ☑ │
│  🌊 오늘   📊 돌아보기  ☑ │        └──────────────────────────┘
└──────────────────────────┘
[오늘 타임라인 — 블록 편집]          [돌아보기(통계)]               [Todo]
┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│ 09 ─┬ 🏫 학교  3h00m      │ │ 오늘│이번 주│달           │ │ 할 일              ＋     │
│     │  ◉ 위 가장자리 끌기 │ │ 🍩 오늘 범주 비율(도넛)   │ │ 오늘 (3)                 │
│     │  ◉ 아래 가장자리 끌기│ │ 범주별: 오늘 ● vs 평소▒  │ │ ○ 선형대수 3장  1h20 ▶  │
│ 12 ─┤ 길게 눌러: 범주 바꾸기│ │ 날마다 한 칸 달력(주 범주)│ │ ○ 장보기          ▶     │
│     │ 나누기 · 지우기      │ │ ■■■□■■■ ■■■■□■■        │ │ 과제 · 복습 · 일반 ›     │
│ (확정 기록만 실선,        │ │ "확정 기록 12일 기준"     │ │ 홈 독의 "할 일 ▾"에서도  │
│  진행 중은 빗금)          │ │ (데이터 적으면 그렇다고)  │ │ 바로 시작 가능           │
└──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
```
**바뀌는 흐름(탭 수):** 시작 1 → 1(독, 엄지 영역), 저장 1 → 1, **활동 바꾸기 2 → 1**(독의 다른 범주 탭 = 전환 + 되돌리기 스낵바), **Todo 연결 2 → 2(탭 이동 없이)**: 독 "할 일 ▾" → 할 일 하나, **빈 시간 채우기: 숨은 길게 누르기 + 수면만 → "기록 없음 ＋" 탭 1 + 범주 1 = 2탭, 아무 범주나**, 기록 시간 고치기: 다이얼로그(4–6 입력) → 가장자리 끌기 1동작. 홈 스크롤 길이: 카드 6개 → 타임라인 1개 + 독.

**구현 난이도: 대.** 세로 타임라인(가상화 목록 + 끌기 편집 + 지금 선 + 겹침 처리)과 독을 새로 만들어야 하고, 기존 `TimetableCard`의 병합 규칙(`MERGE_THRESHOLD_MILLIS`, 보호 범주 등 `TimetableCardSection.kt:476-760`, `ui/screen/TimetableActivityUtils.kt:13`)을 세로 표현으로 옮겨야 함. 통계를 별도 탭으로 분리. 0단계 토큰 작업 포함.

**위험:** 손에 익은 "카드 맨 위 2열 큰 버튼"이 사라지고 아래 독으로 이동 — 버튼 10개를 쓰던 사용자는 독(4–5개)+더보기로 한 탭 늘 수 있음. 24시간 가로 막대로 "하루 전체 모양"을 한눈에 보던 것은 세로 스크롤로 바뀌어 한눈에 안 들어옴(→ 돌아보기 탭의 하루 띠로 보완). 가장 큰 변경이라 버그·회귀 위험이 큼. 빈 시간을 "기록 없음"으로 드러내는 표현이 일부에겐 압박일 수 있음 — 문구는 중립("기록 없음 20분")으로, 비난 없이.

---

### 방향 ③ "Flowlog Expressive" — Material 3 Expressive 전면 적용
**컨셉 한 문장:** Android 16의 새 디자인 언어를 그대로 입어, 주 행동(시작·정지) 하나를 크고 모양이 바뀌는 "주인공" 버튼으로 만들고 나머지는 차분하게 — 동적 색·스프링 움직임·큰 글자로 "Pixel 기본 앱 같은" 완성도를 노린다.

**근거 사례:** Material 3 Expressive 지침(B18: "주 행동을 돋보이게", hero에만 expressive 움직임), Flighty(B4, 진행 중 상태를 시스템 표면에), Opal(B8, 위젯·햅틱), Streaks(B3, 큰 타일), Gentler Streak(B5, 차분한 톤).

**색 팔레트** (기본 = 동적 색 켬. 아래는 동적 색이 없을 때(Android 11 이하·사용자가 끔)의 브랜드 대체 구성. 범주 색은 동적 색과 관계없이 고정)
| 역할 | 라이트 | 다크 |
|---|---|---|
| 바탕(surface) | #FDF7FF | #141218 |
| 표면 컨테이너 | #F3EDF7 | #211F26 |
| 글자 | #1D1B20 | #E7E0EC |
| 보조 글자 | #5F5B68 (6.26) | #B0A9BA (8.17) |
| primary | #5B3FD9 (흰 글자 6.65) | #C7B8FF (진한 글자 #2A1A7A와 7.68) |
| tertiary(집중 모드·정지) | #C2410C (4.91) | #FFB599 (10.91) |

| 범주 | 라이트(#FFFBFF 대비) | 다크(#1D1B20 대비) |
|---|---|---|
| 수면 | #3F51B5 (6.71) | #A9B4FF (8.67) |
| 휴식 | #00796B (5.19) | #6DD5C5 (9.74) |
| 공부 | #2E7D32 (5.00) | #8FD694 (9.93) |
| 업무 | #546E7A (5.27) | #B7C6CE (9.74) |
| 학교 | #C2185B (5.73) | #FFADC9 (9.82) |
| 식사 | #B45300 (4.91) | #FFB77A (10.01) |
| 운동 | #0B63C9 (5.63) | #9DC8FF (9.87) |
| 할일 | #7B4CC2 (5.61) | #D9BAFF (10.10) |

**타이포:** Roboto Flex(가변 글꼴: 굵기·폭을 숫자로 조절 — 타이머 숫자를 크게·좁게) + Noto Sans KR(한글). 제목은 Expressive의 큰 display/headline(32–45sp), 본문 16, 라벨 12–14. *(Google Sans Flex의 공개 배포 여부와 두 글꼴의 현재 Google Fonts 상태는 확인 못 함.)*

**쓰는 Compose 부품(열어 확인한 API 이름):** `MaterialExpressiveTheme` + `MotionScheme.expressive()`(주인공 버튼만) / `standard()`(나머지), `ButtonGroup`(범주 선택), `FloatingToolbar`(아래 떠 있는 도구줄), FAB 메뉴, `SplitButton`(시작 ▾ 할 일), `LoadingIndicator`·`WavyProgressIndicator`(진행 중 표시), `MaterialShapes`(모양 바꿈).

**핵심 화면 5개**
```
[홈 — 멈춤]                          [타이머 진행 중]
┌──────────────────────────┐        ┌──────────────────────────┐
│ 오늘                (●)  │        │ 오늘                (●)  │
│ 4시간 20분 기록됨         │ ← 45sp │      ╭─────────╮         │
│ ┌ 오늘 띠 ▆▆▆▃▃▆▆│░░░ ┐  │        │     ╱  ✿ 모양   ╲        │ ← 모양이 천천히 회전·숨쉼
│ └──────────────────────┘  │        │    │   00:42:17  │ 56sp   │   (MaterialShapes)
│ ┌────────┐┌────────┐     │        │     ╲  💼 업무   ╱        │
│ │  🛏    ││  📖    │     │ ← 큰  │      ╰─────────╯         │
│ │  수면  ││  공부  │     │  모양 │  〰〰〰〰〰〰〰 목표 60분  │ ← WavyProgressIndicator
│ └────────┘└────────┘     │  타일 │  제목 [보고서][회의] ✎    │
│ ┌────────┐┌────────┐     │        │                          │
│ │  💼    ││  ☕    │     │        │ ╭────────────────────────╮│
│ │  업무  ││  휴식  │     │        │ │ ■ 끝내기 │ ⇄ 바꾸기 │ ⏸ ││ ← ButtonGroup, 끝내기가 넓게
│ └────────┘└────────┘     │        │ ╰────────────────────────╯│
│ ╭──────────────────────╮ │        └──────────────────────────┘
│ │ 🍽 🏫 🏃 ☑할일▾  ⋯   │ │ ← FloatingToolbar(엄지 영역)
│ ╰──────────────────────╯ │
└──────────────────────────┘
[오늘 타임라인]                       [통계]                          [Todo]
┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│ ← 오늘 기록               │ │ 돌아보기   [오늘|주|달]    │ │ 할 일        ╭──────╮    │
│ 둥근 컨테이너 묶음:        │ │ ┌ 큰 숫자 카드 ┐ ┌──────┐ │ │ [오늘●][과제][복습]│ ＋ ││
│ ╭ 오전 ─────────────────╮ │ │ │ 공부 3h10m  │ │평소±  │ │ │ ╭ 선형대수 3장 ──────╮│
│ │ 🛏 수면  00:00–07:05  │ │ │ └─────────────┘ └──────┘ │ │ │ 1h20m 누적  [▶ 시작]│ │ ← 48dp 이상
│ │ 🍽 식사  07:30–07:55  │ │ │ 범주 막대(둥근 끝, 두꺼움)│ │ ╰────────────────────╯│
│ ╰───────────────────────╯ │ │ 날마다 한 칸 달력         │ │ 밀어서: 완료 / 미루기   │
│ ╭ 오후 ─ 지금 ─────────╮ │ │                          │ │                          │
└──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
```
알림: Android 16 진행 알림(Live Update 계열)에 범주·경과·[끝내기] 버튼 *(정확한 API는 이번에 확인 못 함)*. 위젯: Glance(Compose 방식 위젯)로 다시 만들어 동적 색·모서리·[시작/끝내기] 버튼.

**바뀌는 흐름(탭 수):** 시작 1 → 1(큰 타일 또는 도구줄), 저장 1 → 1(아래 버튼 묶음, 엄지 영역), 활동 바꾸기 2 → 2(⇄ 바꾸기 → 범주) 또는 1(도구줄 범주 직접), Todo 연결 2 → 2(도구줄 "할일▾" 분할 버튼 → 할 일, 탭 이동 없음), 알림에서 끝내기 1(앱 안 열고), 위젯에서 시작 2 → 1.

**구현 난이도: 대.** material3를 1.5.0(2026-10-07 현재 beta01, 안정판은 1.4.0)으로 올려야 Expressive 부품 대부분을 실험 딱지 없이 쓸 수 있고, `MaterialShapes`·`LoadingIndicator`는 안정 승격이 한 번 되돌려진 이력이 있다(B18 릴리스 노트) → 베타 의존 위험. 0단계 토큰 작업 + 화면 전체 재배치 + 위젯 Glance 재작성.

**위험:** "Pixel 앱처럼" 되면서 Flowlog만의 개성(보라·주황 불꽃·물 차오르는 위젯·캐릭터)이 동적 색에 묻혀 사라질 수 있음(삼성 등 제조사 기기에서는 동적 색 결과가 다름). 움직임이 많아지면 "1탭 기록"의 빠름이 애니메이션 대기로 느려질 수 있음 → 기록 버튼엔 standard 움직임. 베타 라이브러리 의존. 사용자가 보던 버튼 위치·크기가 모두 바뀜.

---

### 세 방향 비교 요약
| | ① Calm(다듬기) | ② River(타임라인 중심) | ③ Expressive(전면 적용) |
|---|---|---|---|
| 바뀌는 정도 | 작음(구조 유지) | 큼(홈 재구성) | 큼(모든 화면 모양) |
| 고치는 약점 | 시각 체계·접근성·다크 | + 돌아보기(타임라인·통계)·정보 과밀 | + 시스템 연동(알림·위젯)·현대적 완성도 |
| 탭 수 변화 | 바꾸기 2→1, 위젯 2→1 | 바꾸기 2→1, 빈 시간 채우기 숨김→2, Todo 탭 이동 없이 | 알림·위젯에서 1탭, Todo 탭 이동 없이 |
| 구현 난이도 | 중 | 대 | 대(+베타 라이브러리) |
| 사용자 익숙함 잃음 | 적음 | 중간(버튼이 아래로) | 큼(전부 새 모양) |
| 철학 적합 | 좋음 | 가장 좋음("어디에 시간이 갔나"를 정직하게) | 보통(꾸밈이 늘 위험) |

**하위 에이전트 추천: ② River.** 이유 — Flowlog의 기록 마찰은 이미 1탭으로 낮아(A3 4점) 더 줄일 여지가 작고, 약한 곳은 "돌아보기"(14dp 가로 막대, 숨은 길게 누르기, 앱에 안 보이는 7일 평균)인데 ②가 바로 그 핵심 가치("실제로 어디에 시간이 갔나")를 화면 중심에 놓는다. ①의 토큰 정리는 ②의 0단계로 그대로 들어가고, ③의 부품(ButtonGroup·FloatingToolbar)은 1.5.0 안정판이 나온 뒤 ②의 독에 부분 도입하면 된다. HTML 목업으로 만들 때도 셋 중 차이가 가장 분명하게 보인다.
