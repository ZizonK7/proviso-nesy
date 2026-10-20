# Flowlog 완성도 점검 (코드 기준)

- 대상: `/home/user/Flowlog` (얕은 클론, 최신 커밋 `98b3039`, 2026-10-02). 앱 버전 `versionName 0.5.9` / `versionCode 26`.
- 방법: 문서 6개를 먼저 읽고, grep·wc·짧은 Python 스크립트로 코드를 셌다. **빌드·테스트·기기 실행은 하지 않았다**(지시대로 `./gradlew` 미실행). 따라서 "동작한다"는 판정은 모두 "코드가 그렇게 짜여 있다"는 뜻이다.
- **기준 시점 주의**: 점검 도중(2026-10-20 00:27~00:29 UTC) 다른 세션이 대상 작업 폴더에 커밋 안 된 변경을 넣었다(수정 5파일: `ActivityViewModel.kt` +88줄, `HomeScreen.kt`, `RecentRecordsSection.kt`, `EditActivityDialog.kt`, `strings.xml` +31항목 / 새 파일: `shortcut/` 폴더, `ManualActivitySection.kt`, `ActivityExportFormatter.kt`, `ManualActivityValidator.kt`). 이 보고서의 숫자는 **커밋 `98b3039` 기준**이다 — `git show HEAD:<파일> | wc -l`로 대조해 메인 159파일·37,872줄, `ActivityViewModel.kt` 3,138줄, `HomeScreen.kt` 661줄, strings 294개가 정확히 일치함을 확인. 새 변경은 평가하지 않았다(수동 기록 입력·내보내기·바로가기로 보이며, CHANGELOG:23의 "CSV 내보내기 없음" 문구와 곧 어긋날 수 있음).
- 경로 표기: `…/flowlog/` = `app/src/main/java/com/example/flowlog/`. 줄 번호는 위 커밋 기준.
- 용어: **삼킨 예외** = 오류가 나도 기록·표시 없이 그냥 넘어가는 코드. **죽은 코드** = 어디서도 부르지 않는 코드. **오프라인 우선** = 폰에 먼저 저장하고 서버는 나중에 맞추는 방식.

## 1. 한눈 표

| 기준 | 점수 (1–5) | 한 줄 근거 | 확신도 |
|---|---|---|---|
| 1. 기능 완성도 | 4 | README 기능 20개 중 18개 완전·2개 일부(재부팅 복원, 백그라운드 네트워크 복귀). 죽은 코드: 추천 엔진 1개, 동기화 함수 5개, Room 표 6개 | 높음 (동작은 미실행) |
| 2. 구조·코드 품질 | 2 | 폴더 계층·revision 정책은 좋으나 3,138줄 ViewModel, 678줄 composable, 쪼갠 파일마다 import 206줄 복사, Activity 안 동기화 로직, 문자열 카테고리 465곳, 결과 버린 `runCatching` 99곳 | 높음 |
| 3. 테스트 | 2 | 실질 단위 88 + 계측 4, 거의 순수 규칙 함수. ViewModel·동기화·마이그레이션·UI 0, CI 없음 | 높음 (통과 여부 미실행) |
| 4. 문서 정합성 | 4 | 경로 13개·동기화 조건·추천 공식이 코드와 정확히 일치. 어긋남 6건(재부팅 범위, 네트워크 조건, 타이머 중 보류, HomeScreen 크기, 문자열 이전 범위, 죽은 파일 언급) + 공개 저장소에 uid | 중간~높음 |
| 5. 동기화·데이터 안전 | 3 | 오프라인 우선 실제 준수, 활동은 트랜잭션+revision+충돌 UI. 마이그레이션 23개 전부 있고 파괴적 폴백 없음. 그러나 스키마 내보내기·마이그레이션 테스트 0, Todo는 덮어쓰기, Room 쓰기 실패 삼킴 | 중간 |
| 6. 알림·백그라운드 | 3 | 정확 알람 폴백·Doze·`setAlarmClock`·Android 12+ 부팅 수신기 처리됨. 정확 알람 설정 화면을 매 실행 강제 이동, 알림 권한 거절 무처리, 일부 알람 부팅 복원 누락, FGS 없음 | 중간 |
| 7. 접근성·현지화 | 2 | strings.xml 294개로 이전 시작했으나 표시용 하드코딩 한국어 약 330개, 영어 리소스 없음, 한/영 혼재, contentDescription null 47/77, 색 308곳 테마 우회 | 중간 |
| 8. 릴리즈 준비 | 2 | targetSdk 36·Crashlytics 릴리즈 전용은 됨. `com.example` 네임스페이스, 축소 꺼짐, 키 없으면 디버그 서명, 개발자 기능·샘플이 릴리즈 포함, CI 없음, 미출시 | 높음 |
| 9. 의존성 최신성·위험 | 3 | AGP 9.2·Gradle 9.4·SDK 36은 최신권. serialization 1.6.0·coroutines 1.8.1·Room 2.7.1·Kotlin 2.2.10 뒤처짐, lifecycle 2.10.0/2.8.7 갈라짐, AGP9+KSP 우회 옵션 | 낮음~중간 |

**단순 평균 2.8 / 5.** 한 사람이 실제로 쓰면서 키운 기능 많은 개인 앱. 기능과 문서는 4점대, 구조·테스트·현지화·릴리즈 준비는 2점대다.

## 2. 기준별 상세

### 2.1 기능 완성도 — 4/5 (확신도: 높음 — 코드 존재 여부 기준. 실제 동작은 확인 못 함)

README 기능 목록에서 20개를 골라 구현 위치를 대조했다.

| # | README 약속 (줄) | 구현 위치 | 판정 |
|---|---|---|---|
| 1 | 빠른 타이머 (README:31) | `…/ui/screen/home/QuickTimerSection.kt:211` `QuickTimerSection`, `…/ui/viewmodel/ActivityViewModel.kt:548` `startActivity` | 있음 |
| 2 | 세션 시작·정지·편집·삭제 (README:33-34) | `ActivityViewModel.kt:1074` `stopActivity`, `:1348` `deleteActivity`, `:1412` `startEditActivity`, `…/ui/component/EditActivityDialog.kt` | 있음 |
| 3 | 카테고리별 제목 추천 5개, 시간 감쇠 (README:35-36, 216-232) | `…/data/recommendation/ActivityTitleSuggestionRanker.kt:9-15` 상수(40/60/3/14/7/5)가 README 공식과 정확히 일치, 호출 `…/ui/screen/home/TimerSection.kt:1254` | 있음, 문서와 일치 |
| 4 | 며칠 꾸준히 쓰면 빠른 타이머 버튼 추천 (README:37-38) | `…/data/recommendation/ExistingButtonRecommendationEngine.kt:40-41` (28일 창, 서로 다른 3일), 호출 `ActivityViewModel.kt:2291` | 있음 |
| 5 | 운동 세트·횟수 기록 (README:39) | `…/ui/screen/home/ExerciseSection.kt:1026`, `ActivityViewModel.kt:651` `updateExerciseSets` | 있음 |
| 6 | Todo·Daily Cues (README:43) | `…/ui/screen/TodoScreen.kt`, `…/data/repository/DailyCueRepository.kt:29`, `…/ui/viewmodel/TodoViewModel.kt:818` | 있음 |
| 7 | Todo에 실제 작업 시간 누적 (README:44-45) | `ActivityViewModel.kt:744` `startTodoActivity`, `…/data/local/entity/TodoEntity.kt:32` `accumulatedWorkMillis` | 있음 (단, 전용 표 `TodoWorkSessionEntity`는 안 쓰임 — 아래 죽은 코드) |
| 8 | 반복 루틴 블록·학교/회사 고정 타이머 (README:46-47) | `…/ui/screen/home/RoutineManagerSection.kt`, `QuickTimerSection.kt:268` (SCHOOL/COMPANY 고정) | 있음 |
| 9 | 추천 활동 자동 배치 + 알람 별도 토글 (README:48-49) | `…/data/local/TimetablePlanSettingsStore.kt:5`, 사용 `…/data/repository/DailyGoalRepository.kt:299`, `…/notification/PlannedTodoReminderScheduler.kt:77` | 있음 |
| 10 | 기상 후·식후·취침 전 넛지 (README:50-51) | `…/data/recommendation/FlowRecommendationEngine.kt:91-110` (`AFTER_MEAL`, `BEFORE_LONG_SLEEP`, `justWokeUp`) | 있음 |
| 11 | 어제 비교·최근 7일 평균 (README:56) | `…/ui/screen/home/AnalyticsReportSection.kt:293` `YesterdayComparisonReport`, `:651` `AverageRows` | 있음 |
| 12 | 빈 시간 수면으로 채우기 (README:57) | `…/ui/screen/SleepFillDialog.kt:61`, `ActivityViewModel.kt:703` `saveSleepActivity` | 있음 |
| 13 | 집중 모드 + 방해 금지(DND) (README:61) | `…/notification/FocusDndController.kt:13-69`, `ActivityViewModel.kt:2955` | 있음 |
| 14 | 알림: 계획 Todo·루틴 목표·무활동·양치/식사 (README:62-63) | `PlannedTodoReminderScheduler.kt`, `RoutineGoalAlarmScheduler.kt`, `InactivityReminderScheduler.kt`, `ReminderScheduler.kt` | 있음 |
| 15 | **재부팅·앱 업데이트 후 예약 알림 복원** (README:63) | 부팅 수신기 2개가 복원하는 것: 자동 버튼·학습 계획·양치/식사(`…/notification/AutoButtonBootReceiver.kt:23-27`), 계획 Todo(`PlannedTodoReminderBootReceiver.kt:24`). **루틴 목표·무활동·집중 종료·자정 동기화 알람은 부팅 때 복원 안 됨** (무활동은 앱을 열면 `ActivityViewModel.kt:283`에서 복원) | **일부만** |
| 16 | 홈 화면 위젯 (README:64) | `…/widget/FlowStatusWidgetProvider.kt:34`, 매니페스트 `AndroidManifest.xml:88-98` | 있음 |
| 17 | Google 로그인 + Firestore 동기화, 오프라인 기록 나중 업로드 (README:68) | `…/MainActivity.kt:560-568` Credential Manager, `…/data/sync/FirebaseSyncDataSource.kt:105-186` PENDING 행 업로드 | 있음 |
| 18 | 삭제 즉시 동기화 + WorkManager 재시도 (README:159-162) | `…/data/sync/DeleteSyncTrigger.kt:33-57`, `DeleteSyncWorker.kt` | 있음 |
| 19 | 웹 수정 충돌 시 둘 다 보관하고 선택 (README:177-182) | 저장 `FirebaseSyncDataSource.kt:150-166`, 화면 `MainActivity.kt:234-272` (`AlertDialog` "기록 수정 충돌") | 있음 |
| 20 | 앱 안 "AI messenger"는 로컬 제안 피드 (README:100-101) | `…/data/model/AiMessage.kt`, `ActivityViewModel.kt:2172-2204` | 있음 |

**약속만 있고 없는(또는 덜 된) 것**
- 재부팅 복원이 일부 알람에만 적용(위 15번).
- "네트워크가 돌아오면 업로드"(README:156)는 **앱 화면이 보일 때만**: 콜백을 `onStart`에서 등록하고 `onStop`에서 해제(`MainActivity.kt:542-551`). 앱이 백그라운드면 이 경로는 없다(삭제만 WorkManager가 대신함).

**코드에만 있고 README엔 없는 것(숨은 기능)**
- 타이머가 돌고 있으면 시작·로그인·네트워크 복귀·자정 업로드를 통째로 미룸: `…/data/sync/FirebaseSyncSupport.kt:122-127` (`SyncOutcome(deferred = true)`).
- 개발자 모드를 켜면 홈 타임테이블이 **가짜 샘플 데이터로 바뀜**: `…/ui/screen/HomeScreen.kt:483-492`.
- 간식 타이머·"양치 후 먹기 허용" 실험 타이머: `…/notification/ReminderScheduler.kt:61,98,109`.
- 오늘의 할 일 부담 점수(Todo burden)로 정렬: `…/data/recommendation/TodoBurdenCalculator.kt` (README:98에 한 단어로만 언급).

**죽은 코드(어디서도 안 부름)**
- `…/data/recommendation/ButtonRecommendationEngine.kt` (232줄, 한국어 키워드 사전 224개) — 메인 코드 참조 0, 테스트 6개만 붙어 있음. README:331-333은 이 파일을 "의도적으로 한국어"인 예로 들고 있어 **문서가 죽은 파일을 가리킨다**.
- `…/data/remote/FirestoreSyncRepository.kt:37-68,121-124` `syncActivities`·`syncActivity`·`syncActivityByDocId`·`syncTodos`·`syncTodo` — 호출 0. 앞의 셋은 revision 없는 활동 쓰기라 현재 Firestore 규칙에선 거부될 경로(README:279-281).
- Room 표 23개 중 6개를 앱이 전혀 읽거나 쓰지 않음: `DailySummaryEntity`, `NotificationLogEntity`, `UserEntity`, `InstallationEntity`, `TodoWorkSessionEntity`, `MigrationErrorEntity`. 여기에 퇴역한 시험 기능 표 `ExamStrategyCheckEntity` 1개(PROJECT_CONTEXT:208-217에 정리 계획 있음).
- 명령: `grep -rlw --include=*.kt <이름> …/flowlog | grep -v <정의 파일>` 로 0건 확인.

**점수 이유**: 고른 20개 중 18개가 온전히, 2개가 일부 구현. 죽은 코드가 꽤 있지만 "약속한 기능이 있나"라는 기준엔 거의 다 맞는다. 5점이 아닌 이유는 재부팅 복원과 백그라운드 네트워크 복귀가 문구보다 좁기 때문.

### 2.2 구조·코드 품질 — 2/5 (확신도: 높음)

**좋은 점**
- 폴더 계층은 분명하다: `data/`(local·remote·sync·repository·recommendation) / `notification/` / `ui/`(screen·component·viewmodel·theme) / `widget/`. 폴더별 파일 수: notification 26, data/local/entity 23, ui/screen/home 14, data/local/dao 13, data/sync 9.
- ViewModel 두 개가 `MutableStateFlow`로 상태를 낸다(`ActivityViewModel.kt` 9개, `TodoViewModel.kt` 12개). 활동 revision 처리는 순수 함수(`…/data/remote/ActivityRevisionPolicy.kt`, `ActivityRevisionContent.kt`)로 떼어 테스트까지 붙였다 — 이 저장소에서 가장 잘 짠 부분.
- 빈 `catch {}`는 0개. 전통적 `catch`는 12개뿐이고 모두 로그를 남기거나 기본값을 돌려준다.

**거대 파일 상위 10개** (`find app/src/main/java -name "*.kt" | xargs wc -l | sort -rn | head -11`)

| 줄 수 | 파일 |
|---|---|
| 3,138 | `ui/viewmodel/ActivityViewModel.kt` |
| 2,974 | `ui/screen/TodoScreen.kt` |
| 1,540 | `MainActivity.kt` |
| 1,380 | `ui/screen/home/RoutineManagerSection.kt` |
| 1,366 | `ui/screen/home/TimetableCardSection.kt` |
| 1,340 | `ui/viewmodel/TodoViewModel.kt` |
| 1,266 | `ui/screen/home/TimerSection.kt` |
| 1,206 | `ui/screen/home/ExerciseSection.kt` |
| 1,133 | `data/repository/DailyGoalRepository.kt` |
| 1,110 | `ui/screen/home/AutoButtonSheetsSection.kt` |

상위 10개가 16,453줄로 메인 코드 37,872줄의 43 %.

**거대 함수** (중괄호 짝 맞추기 스크립트 `funlen.py`, 아래 3장. 함수 952개 중 100줄 이상 53개, 200줄 이상 17개)
- `ExerciseSection.kt:366` `ExerciseAddSetSheet` 678줄
- `TodoScreen.kt:187` `TodoScreen` 508줄
- `HomeScreen.kt:213` `HomeScreen` 447줄
- `MainActivity.kt:734` `HeaderActions` 422줄
- `MainActivity.kt:161` `onCreate` 380줄

**복사된 import 덩어리**: "God 파일 쪼개기"(커밋 `b678145`) 때 import 목록을 통째로 복사했다. `ui/screen/HomeScreen.kt`와 `ui/screen/home/*.kt` 15개 파일이 **각각 206~209줄의 import**를 가진다(`grep -c '^import'`). 248줄짜리 `HomeStyleConstants.kt`도 import가 206줄. 합치면 약 3,100줄이 중복 import다. 파일을 나눴지만 의존은 나누지 않았다는 신호.

**계층 위반**
- `MainActivity.onCreate` 안에서 DB 직접 호출·익명 사용자 재할당·복원 판단·충돌 해결을 한다(`MainActivity.kt:240-330`). `FlowlogDatabase.getInstance`를 `data/` 밖에서 16번, `FirebaseAuth.getInstance`를 ui·MainActivity에서 18번 부른다.
- 의존성 주입(DI) 도구 없음. ViewModel은 손으로 만든 Factory(`…/ui/viewmodel/ActivityViewModelFactory.kt`)와 `remember { ViewModelProvider(...) }`(`MainActivity.kt:180-191`)로 만든다. 화면 전환도 Navigation 라이브러리 없이 문자열 `currentScreen`(`MainActivity.kt:176`).
- 화면 상태 수집: `collectAsState()` 19회, `collectAsStateWithLifecycle` 0회.
- 설정·타이머 상태가 Room과 SharedPreferences(`getSharedPreferences` 41회)로 나뉘어 있다.

**에러 처리 — 삼킨 예외**
- `runCatching {` 227곳 (스크립트 `rc.py`): 결과 처리(onFailure·getOrElse 등) 107, 실패 시 null 20, 결과 사용 1, **결과를 버리고 로그도 없는 것 99**.
- 많이 삼키는 파일: `data/repository/TodoRepository.kt` 23, `TodoViewModel.kt` 17, `ActivityViewModel.kt` 13, `MainActivity.kt` 10, `ActivityRepository.kt` 9.
- 예: `…/data/repository/TodoRepository.kt:75,78,87,89,98,101,107` — **Room 쓰기(완료·취소·수정) 자체를** `runCatching`으로 감싸고 버린다. 저장이 실패해도 사용자는 모른다.
- `runCatching`은 코루틴 취소 신호(`CancellationException`)까지 잡아먹어 취소가 제대로 안 퍼질 수 있다(일반론, 이 앱에서 실제 문제가 났는지는 확인 못 함).

**하드코딩**
- 카테고리가 enum(정해진 값 목록 타입) 없이 문자열이다: `"SLEEP"`·`"EXERCISE"`·`"TODO"` 등 11개 키 문자열이 465번 등장(`grep -rhoE '"(SLEEP|EXERCISE|…)"' | wc -l`). 오타 하나가 조용한 버그가 된다.
- 색: `Color(0x…)` 339곳, 테마 폴더 밖 308곳. 글자 크기 `fontSize = N.sp` 352곳, `MaterialTheme.typography` 사용 0곳. `.dp` 숫자 1,287곳.
- 시간 상수는 `const val` 357개로 대체로 이름이 붙어 있다. 이름 없이 박힌 밀리초 계산은 37곳.
- 같은 "다음 자정 계산"이 `MainActivity.kt:608-614`과 `FirebaseSyncSupport.kt:99-107`에 따로 있고, "정확 알람 → 부정확 알람으로 물러서기" 분기가 스케줄러 8곳에 복사돼 있다(`setAndAllowWhileIdle` 8파일).

**TODO/FIXME**: 주석 TODO 3개뿐(`grep -E '//\s*(TODO|FIXME|HACK|XXX)'`). 그중 `…/data/local/entity/ActivityEntity.kt:43`은 "스키마 바꾸면 Migration 추가" 메모라 사실상 할 일이 아니다. (단순 `grep TODO`는 카테고리 이름 "TODO" 때문에 120건이 나오니 주의.)

**기타 위험**
- 사용자 uid를 info 로그로 남김 7곳(`FirebaseSyncDataSource.kt:49,67,82,100`, `FirebaseRestoreDataSource.kt:79` 등). 릴리즈에서 축소(minify)가 꺼져 있어 로그가 그대로 남는다.
- 테스트 코드 스타일 붕괴: `…/test/…/ActivityRevisionDaoTest.kt:13-50`은 한 줄에 문장 여러 개를 `;`로 이어 쓴다.

**점수 이유**: 계층 폴더와 revision 정책은 좋다. 그러나 3천 줄 ViewModel, 600줄 composable, 복사된 import 3천 줄, Activity 안의 동기화 로직, 문자열 카테고리, 삼킨 예외 99곳은 채용 담당자가 첫 파일을 열자마자 보는 문제다.

### 2.3 테스트 — 2/5 (확신도: 높음 — 테스트 수와 대상은 셈. 테스트가 통과하는지는 이번에 돌리지 않아 확인 못 함)

`for f in $(find app/src/test app/src/androidTest -name "*.kt"); do grep -c '@Test' $f; done`

| 종류 | 파일 | @Test | 줄 |
|---|---|---|---|
| 단위(JVM) | 13 | 89 (자리만 채운 `ExampleUnitTest` 1개 포함 → 실질 88) | 1,422 |
| 계측(기기) | 2 | 5 (`ExampleInstrumentedTest` 1개 포함 → 실질 4) | 98 |

테스트 줄 수는 메인 코드의 약 4 % (1,520 / 37,872).

**덮는 것**: 거의 전부 순수 함수다.
- 추천 규칙: `ActivityTitleSuggestionRankerTest` 16, `ExistingButtonRecommendationEngineTest` 18, `TodoBurdenCalculatorTest` 9, `FlowRecommendationEngineTest` 8, `ReviewRecommendationPolicyTest` 3, `ButtonRecommendationEngineTest` 6(**죽은 코드를 시험**).
- revision·충돌: `ActivityRevisionPolicyTest` 5, `ActivityRevisionContentTest` 7, `ActivityRevisionDaoTest` 6 — 이 마지막은 실제 SQL이 아니라 손으로 만든 메모리 가짜 DAO(`…/test/…/data/recommendation/ActivityRevisionDaoTest.kt:13-31`)로 트랜잭션 메서드의 분기만 본다. 패키지도 `data.recommendation`에 잘못 들어가 있다.
- 화면 계산 도우미: `TimetableActivityUtilsTest` 3, `AnalyticsActivityUtilsTest` 5, `DailyGoalRecommendedBlockVisibilityTest` 2.
- 계측: `…/androidTest/…/ActivityConflictObservationTest.kt` 4 — 메모리 Room DB로 충돌 관찰 쿼리를 실제로 돌린다. 유일한 진짜 DB 테스트.

**비어 있는 곳**
- ViewModel(`ActivityViewModel` 3,138줄, `TodoViewModel` 1,340줄): 0.
- 동기화 데이터 소스(`FirebaseSyncDataSource`, `FirebaseRestoreDataSource`, `FirebaseCalendarPullDataSource` 750줄, `StudySyncDataSource`, `DeleteSyncWorker`): 0. Firestore 에뮬레이터 검증은 `tools/study-integration/`의 Node 스크립트가 맡는다고 README:315-318에 적혀 있으나 안드로이드 테스트는 아님.
- DAO SQL 13개 중 실제로 도는 것은 충돌 관찰 1개.
- Room 마이그레이션 23개: 0 (`MigrationTestHelper` 없음, `exportSchema = false`라 붙일 수도 없음).
- 알림·알람 스케줄러 26파일: 0.
- Compose UI 테스트: 0 (의존성 `ui-test-junit4`만 선언, `app/build.gradle.kts:127`).
- CI(자동 빌드·테스트): 없음 (`.github/` 없음).

**점수 이유**: 순수 규칙 테스트는 꼼꼼하고(제목 추천 16개 등) 회귀 테스트를 버그와 함께 넣은 흔적도 있다(CHANGELOG:7-9). 그러나 앱의 위험이 몰린 곳(동기화, 마이그레이션, ViewModel, 알람)이 비어 있고 CI가 없다.

### 2.4 문서 정합성 — 4/5 (확신도: 중간~높음)

README·CHANGELOG·PROJECT_CONTEXT 세 문서의 역할 분담이 명시돼 있고(PROJECT_CONTEXT:9-31), 최근 커밋들이 "README가 코드와 안 맞는 곳 고침"(CHANGELOG:20-27)을 직접 했다. 개인 앱치고 문서가 매우 성실하다. 대조 결과:

**맞는 곳 (8건)**
1. Firestore 경로 13개(README:198-212) ↔ 코드의 `.collection(…)`/`.document(…)` 이름 전부 일치(`grep -rhoE '\.collection\("[A-Za-z]+"\)|\.document\("[A-Za-z]+"\)' | sort | uniq -c`; `…/data/remote/FirestoreSyncRepository.kt:148,242-254,335-427`, `…/data/sync/StudySyncDataSource.kt:29,56,74`).
2. 저장 후 즉시 전체 업로드 조건 "10분 이상 또는 운동 세트"(README:165-166) ↔ `ActivityViewModel.kt:2763-2767,3134`.
3. 시작·로그인·네트워크 복귀는 `syncEligible`(어제 이전만)(README:164-165) ↔ `MainActivity.kt:576,645`, `FirebaseSyncDataSource.kt:113`.
4. 삭제 WorkManager 재시도(README:159-162) ↔ `DeleteSyncTrigger.kt:47-57`.
5. 제목 추천 공식과 상수(README:222-226) ↔ `ActivityTitleSuggestionRanker.kt:9-15`.
6. Crashlytics는 릴리즈에서만(README:248) ↔ `MainActivity.kt:163`.
7. 메인 버튼 10개 상한(CHANGELOG:33) ↔ `ExistingButtonRecommendationEngine.isWithinCap`, `ActivityViewModel.kt:2001-2021`.
8. 시험 기능 잔여물 계획(PROJECT_CONTEXT:210-217) ↔ `FlowlogDatabase.kt:73`, `TodoDao.kt:108` 실제로 남아 있음.

**어긋나는 곳 (6건)**
1. **재부팅 복원**: README:62-63은 루틴 목표·무활동 알림까지 "재부팅 후 복원"이라 읽히지만, 부팅 수신기는 자동 버튼·학습 계획·양치/식사·계획 Todo만 복원(`AutoButtonBootReceiver.kt:23-27`, `PlannedTodoReminderBootReceiver.kt:24`). 자정 동기화 알람도 부팅 후 앱을 열 때까지 없음(`MainActivity.kt:166`에서만 예약).
2. **네트워크 복귀 업로드**(README:156): 화면이 보일 때만(`MainActivity.kt:542-551`). 문서엔 조건이 없다.
3. **타이머 실행 중 업로드 보류**(`FirebaseSyncSupport.kt:122-127`): README "Data & Sync"에 없음. 자정 업로드도 이 때문에 미뤄질 수 있다.
4. **"HomeScreen.kt는 의도적으로 작게"**(README:139-142): 실제 661줄, 그중 `HomeScreen` 함수 하나가 447줄.
5. **"TodoScreen.kt·MainActivity.kt 문자열은 strings.xml에"**(README:328-330): `MainActivity.kt`에 한국어 문자열 12개(충돌 대화상자 `:268-271` 등), `TodoScreen.kt:397` `"Petites"`, `MainActivity.kt:1523` `"Todo"` 리터럴.
6. **README:331-333**이 한국어 키워드 사전 예로 든 `ButtonRecommendationEngine.kt`는 앱이 안 쓰는 죽은 코드.

**문서 규칙 위반 1건**: PROJECT_CONTEXT:40-42는 "개인 ID를 커밋하지 말 것"이라 하지만, `…/data/local/UserRoleStore.kt:10-11`에 유지보수자 Firebase uid가 문자열로 박혀 있다(값은 이 보고서에 옮기지 않음). 비밀번호는 아니지만 공개 저장소 원칙과 어긋난다.

**기타**: CHANGELOG에 버전 제목이 없고 전부 "Unreleased"다(CHANGELOG:3). README Architecture 표(README:109-137)는 `data/model`, `data/repository`, `ui/component`, `ui/theme`을 빠뜨린다.

**점수 이유**: 핵심 사실(경로, 동기화 조건, 공식)이 정확히 맞아 신뢰할 만하다. 어긋남은 대부분 "조건을 빠뜨림" 수준. 다만 공개 저장소에 uid가 있는 것은 문서가 스스로 금한 일이다.

### 2.5 동기화·데이터 안전 — 3/5 (확신도: 중간)

**잘 된 것**
- **오프라인 우선은 실제로 지켜진다.** 기록은 Room에 먼저 쓰고 `syncStatus = PENDING`으로 표시(`…/data/local/entity/ActivityEntity.kt:45`), 업로드는 PENDING 행을 모아 보낸다(`FirebaseSyncDataSource.kt:109-186`). 로그인 전 기록은 로그인 후 실제 uid로 옮긴다(`MainActivity.kt:303-310` `reassignAnonymousUser`).
- **활동 충돌 처리가 탄탄하다.** Firestore 트랜잭션 + revision 번호로 낙관적 동시성 제어(남이 먼저 바꿨으면 쓰지 않음)를 한다(`FirestoreSyncRepository.kt:134-185` `runTransaction`). 업로드 중 로컬 수정이 생기면 ACK(완료 표시)를 하지 않고 PENDING 유지(`FirebaseSyncDataSource.kt:146-147` `ackActivityUpload` 조건부). 충돌이면 양쪽 내용을 저장해 사용자에게 고르게 한다(`:150-166`, 화면 `MainActivity.kt:234-272`). 테스트도 이 부분에 몰려 있다.
- **동기화 겹침 방지**: 전역 뮤텍스(동시에 한 작업만 들어가게 하는 자물쇠) `FirebaseSyncSupport.kt:157`.
- **Room 마이그레이션**: 버전 24, 1→2 … 23→24 **23개 전부 등록**, `fallbackToDestructiveMigration`(맞지 않으면 DB를 지우는 옵션) **없음**(`…/data/local/db/FlowlogDatabase.kt:81,122`; `grep -n fallback` 0건). 사용자 데이터를 지우지 않는 쪽을 택했다.
- **삭제 재시도**: 삭제 즉시 1회 시도 + `NetworkType.CONNECTED` 조건의 WorkManager 작업, 지수 백오프(실패할수록 간격을 늘림), `ExistingWorkPolicy.KEEP`(`DeleteSyncTrigger.kt:33-57`). 앱이 죽어도 남는다.

**약한 것**
- **마이그레이션 검증 수단이 없다**: `exportSchema = false`(`FlowlogDatabase.kt:84`, 주석 "개발 편의상 보류"), 스키마 JSON 폴더 없음, 마이그레이션 테스트 0. 23개 SQL 마이그레이션이 손으로만 검증됐다.
- **Todo에는 충돌 처리가 없다**: `SetOptions.merge()`로 덮어쓰기(마지막에 쓴 쪽이 이김)(`FirestoreSyncRepository.kt:192-195`). 웹에서 Todo를 바꾸는 경로가 있다면 조용히 덮일 수 있다(웹 쪽 동작은 확인 못 함).
- **로컬 쓰기 실패를 삼킴**: `TodoRepository.kt:75-108`의 Room 쓰기 실패가 버려진다(2.2 참조). "폰에 저장됐다"는 전제가 깨져도 알 길이 없다.
- **삭제 재시도 작업의 범위가 넓다**: `DeleteSyncWorker.kt:21-35`는 삭제뿐 아니라 **모든 PENDING Todo·활동**을 올리고, 하나라도 남으면 `Result.retry()`. 규칙에 계속 거부되는 행이 하나 있으면 영원히 재시도한다(추측: 백오프 상한 때문에 배터리 영향은 작을 것). 또 전역 뮤텍스를 거치지 않고 데이터 소스를 직접 불러(`DeleteSyncTrigger.kt:36-41`, `DeleteSyncWorker.kt:21-23`) 다른 동기화와 동시에 돌 수 있다. revision ACK가 덮어쓰기는 막지만 중복 업로드는 가능(추측, 확인 못 함).
- **백그라운드 동기화 경로가 얇다**: 네트워크 복귀는 화면이 보일 때만, 자정 알람은 부팅 후 앱을 열어야 다시 예약됨(2.4 참조), 타이머가 돌면 업로드 보류. 결과적으로 "오프라인 기록이 나중에 올라간다"는 약속은 **앱을 다시 열면** 지켜진다.
- **안 쓰는 표 6개**(2.1)가 스키마에 남아 마이그레이션 부담만 늘린다.
- **자동 백업**: `android:allowBackup="true"`인데 백업 규칙 파일은 템플릿 그대로(`AndroidManifest.xml:14-16`, `res/xml/backup_rules.xml`, `res/xml/data_extraction_rules.xml`). Room DB가 Google 백업으로 복원되면 "로컬이 비면 Firestore에서 복원"(`MainActivity.kt:311-322`) 판단과 겹칠 수 있다(추측, 확인 못 함).

**점수 이유**: 핵심인 활동 동기화는 포트폴리오에서 보여 줄 만한 수준(트랜잭션·revision·충돌 UI·테스트). 그러나 마이그레이션 검증 0, Todo 덮어쓰기, 로컬 쓰기 실패 삼킴, 백그라운드 경로가 앱 실행에 의존하는 점 때문에 3점.

### 2.6 알림·백그라운드 신뢰성 — 3/5 (확신도: 중간 — 기기 실행 없이 코드만 봄)

**잘 된 것**
- **정확 알람 권한**: 매니페스트에 `SCHEDULE_EXACT_ALARM`(`AndroidManifest.xml:9`). 알람을 거는 스케줄러 7곳 + 자정 동기화가 `canScheduleExactAlarms()`를 확인하고, 권한이 없으면 부정확 알람으로 물러선다(`grep -rln canScheduleExactAlarms` 8파일; `…/notification/ReminderScheduler.kt:271-311`은 `recoverCatching` 3단 폴백). 커밋 기록에도 Android 13+ 정확 알람 크래시 수정이 있다(CHANGELOG:156).
- **Doze(화면 꺼진 절전 상태) 대응**: `setExactAndAllowWhileIdle` 9곳, 양치/식사 알림은 `setAlarmClock`(시스템 알람시계 취급, Doze가 미루지 못함)(`ReminderScheduler.kt:313-327`).
- **재부팅·업데이트**: `BOOT_COMPLETED` + `MY_PACKAGE_REPLACED`, 시스템 방송을 받으려고 `exported="true"`(`AndroidManifest.xml:63-78`). 복원 대상은 일부(2.1-15번).
- **Android 13+ 알림 권한**: `POST_NOTIFICATIONS` 선언(`AndroidManifest.xml:5`), 첫 실행에 요청(`MainActivity.kt:694-708`).
- **타이머 알림**: 상시 알림 + 크로노미터(`setUsesChronometer`)(`…/notification/ActivityTimerNotifier.kt:36-47`). 타이머 상태는 저장소(`TimerStateStore`)에 시작 시각으로 남아, 프로세스가 죽어도 시간 계산은 맞는다.

**약한 것**
- **정확 알람 설정 화면을 설명 없이, 앱을 열 때마다 띄운다**: 권한이 없으면 `onCreate`마다 `ACTION_REQUEST_SCHEDULE_EXACT_ALARM`으로 바로 이동(`MainActivity.kt:710-723`, 호출 `:172`). 사용자가 거절해도 매번 반복. 권한 허용 후 다시 예약하는 수신(`SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED`)도 없다(grep 0건).
- **`USE_EXACT_ALARM` 미선언**: 스토어에 낸다면 `SCHEDULE_EXACT_ALARM`은 Play 정책상 알람·캘린더류 앱에만 허용되는 편이라 심사 이슈가 될 수 있다(정책 세부는 확인 못 함).
- **알림 권한 거절 처리 없음**: `onRequestPermissionsResult`·`shouldShowRequestPermissionRationale`·`areNotificationsEnabled` 모두 0건. 거절하면 알림 기능이 조용히 죽는다.
- **포그라운드 서비스(FGS) 없음**: `startForeground`·`foregroundServiceType` 0건. 시간 계산은 저장된 시작 시각으로 하니 정확도엔 문제가 없지만, Android 14+에선 FGS가 아닌 상시 알림을 사용자가 밀어 지울 수 있다(일반 플랫폼 동작, 이 앱에서 확인 못 함).
- **부팅 복원 누락**: 루틴 목표(`RoutineGoalAlarmScheduler`), 집중 종료(`FocusModeScheduler`), 무활동(`InactivityReminderScheduler`), 자정 동기화 알람이 부팅 수신기에 없다.
- **수신기 안의 긴 작업**: 자정 동기화 수신기는 `goAsync()` 안에서 Firestore 업로드 전체 + 캘린더 pull을 한다(`…/notification/FirebaseSyncReceiver.kt`). 방송 수신기의 짧은 시간 제한을 넘길 수 있다 — WorkManager가 맞는 도구(추측, 실제 초과 여부 확인 못 함).
- 배터리 최적화 예외 안내(`isIgnoringBatteryOptimizations`) 0건 — 제조사 절전이 강한 폰에서 알림 신뢰도가 떨어질 수 있다(추측).

**점수 이유**: 정확 알람·Doze·부팅·Android 12 exported 같은 까다로운 함정을 실제 버그를 겪으며 하나씩 고친 흔적이 뚜렷하다. 권한 UX(매번 강제 이동, 거절 무처리)와 부팅 복원 누락이 남아 3점.

### 2.7 접근성·현지화 — 2/5 (확신도: 중간 — 리터럴 수는 스크립트 추정치)

**현지화(다른 언어 지원)**
- `res/values/strings.xml` 항목 294개, 복수형(plurals) 0. 언어별 폴더(`values-en`, `values-ko`) **없음** — 기본 리소스 자체가 한국어라 영어 사용자는 한국어를 본다.
- 코드에서 리소스 사용(`stringResource(`·`R.string.`) 375곳 — 큰 화면(TodoScreen·home 섹션)은 상당 부분 옮겼다(커밋 `b678145`).
- Kotlin 안의 한국어 문자열 리터럴 **684개**(로그·주석 제외, `ko.py`). 그중 `\uXXXX`로 이스케이프한 한국어 74개(읽기도 어렵다, 예 `ActivityTimerNotifier.kt:58-59`).
  - 표시용이 아닌 것: 죽은 키워드 사전 `ButtonRecommendationEngine.kt` 224, 분류 키워드 `TodoBurdenCalculator.kt` 43(추정, 대부분 키워드), 개발자 샘플 `debug/` 83.
  - **표시용으로 추정되는 하드코딩: 약 330개.** 많은 곳: 알림 `ActivityTimerNotifier.kt` 37, `ActivityViewModel.kt` 34(상태 메시지), `ActivityItem.kt` 29(카테고리 이름 `:171` 등), `RecommendationSection.kt` 27, 위젯 `FlowStatusWidgetProvider.kt` 26, `AutoButtonScheduleUtils.kt` 19, `TodoViewModel.kt` 16, `AnalyticsReportSection.kt` 16, `MainActivity.kt` 12.
- **한/영 혼재**: 알림 제목 `"Flowlog timer"`(`ActivityTimerNotifier.kt:39`), 탭 `"Todo"`(`MainActivity.kt:1523`), `"Petites"`(`TodoScreen.kt:397`)가 한국어 UI 속에 영어로 섞인다. 의도된 브랜드 단어일 수 있으나 기준이 없다.

**접근성(시각 장애·큰 글씨 사용자 대응)**
- `contentDescription`(화면 낭독기가 읽는 설명) 77곳 중 `null` 47곳. `Icon(` 94회. 장식용이면 null이 맞지만, 버튼 안 아이콘까지 null인 곳이 있다(예 개발자 메뉴 `MainActivity.kt:899-903` — 글자가 옆에 있어 괜찮은 경우).
- `semantics` 2곳, `Role.` 사용 거의 없음. `Modifier.clickable` 36곳 + `pointerInput` 41곳 — 직접 만든 터치 영역이 많아 낭독기 역할 정보가 빠졌을 가능성(추측).
- 글자 크기: `fontSize = N.sp` 352곳. sp 단위라 시스템 글꼴 크기는 따라가지만, `MaterialTheme.typography` 0곳이라 큰 글씨에서 고정 `.dp` 높이(1,287곳)와 부딪혀 잘릴 수 있다(`maxLines`/`TextOverflow` 69곳). 실제 큰 글씨 화면은 확인 못 함.
- 색: 테마(`…/ui/theme/Theme.kt:14-46`)는 다크·동적 색을 지원하는 템플릿인데, 화면은 `Color(0x…)` 308곳을 직접 써서 **다크 모드에서 테마가 거의 적용되지 않을 것**(추측, 화면 확인 못 함). 개발자 메뉴 글자도 `Color(0xFF10182C)` 고정(`MainActivity.kt:898`).
- `@Preview` 0개 — 화면을 크기·언어·다크별로 미리 볼 장치가 없다.

**점수 이유**: 큰 화면 문자열 이전은 시작했지만 알림·위젯·ViewModel 메시지가 하드코딩이고, 영어 리소스가 없으며, 색·글꼴이 테마를 우회한다. 한국어 사용자 1명을 위한 앱으로선 문제없지만 "완성도" 기준으로는 2점.

### 2.8 릴리즈 준비 — 2/5 (확신도: 높음)

| 항목 | 상태 | 근거 |
|---|---|---|
| 패키지 이름 | 코드 네임스페이스 `com.example.flowlog`, 설치 ID `org.pfkfks.flowlog` | `app/build.gradle.kts:25,33`. README:265-267이 "맞출 필요 없음"이라 설명. 동작엔 문제없지만 `com.example`은 "템플릿에서 안 바꿨다"로 읽힌다. 위젯 방송 액션도 `com.example.flowlog.widget.FLOW_STATUS_REFRESH`(`AndroidManifest.xml:93`) |
| 코드 축소·난독화 | 꺼짐 | `isMinifyEnabled = false`, `isShrinkResources = false`(`app/build.gradle.kts:63-64`), `proguard-rules.pro`는 템플릿 주석뿐 |
| 서명 | `keystore.properties` 있으면 **디버그·릴리즈 모두 같은 릴리즈 키**, 없으면 기본 디버그 키 | `app/build.gradle.kts:42-62`. 키가 없어도 릴리즈 빌드가 조용히 디버그 서명으로 나간다 |
| 버전 | `versionCode 26`, `versionName 0.5.9` | `app/build.gradle.kts:36-37`. CHANGELOG엔 버전별 제목 없음 |
| SDK | `minSdk 24`, `targetSdk 36`, `compileSdk 36.1` | `app/build.gradle.kts:26-35` — 최신 기준 충족 |
| 스토어 | 미출시, 소스 빌드로만 설치 | README:11-12 |
| 개발자 기능 | 릴리즈에도 포함. 런타임에 **하드코딩된 uid 한 개**로만 잠금 | `…/data/local/UserRoleStore.kt:10-11`, `BuildConfig.DEBUG`로 막는 곳은 Crashlytics 1곳뿐(`MainActivity.kt:163`). 샘플 데이터 `debug/` 패키지(83개 문자열)가 `src/main`에 있어 릴리즈 APK에 들어간다 |
| 로그 | `Log.*` 155곳(uid 포함 7곳), 릴리즈에서 제거 장치 없음 | `grep -rn 'Log\.(d|i|w|e|v)\('` |
| 백업 규칙 | 템플릿 그대로 | `res/xml/backup_rules.xml`, `data_extraction_rules.xml` |
| CI·자동 서명 빌드 | 없음 | `.github/` 없음 |
| 개인정보 | 웹에 `/privacy/` 정책 페이지가 있다고 README:91 | 페이지 내용은 확인 못 함 |

**점수 이유**: targetSdk·Crashlytics·버전 관리 등 기본은 됐지만, 축소 꺼짐·서명 폴백·개발자 기능과 샘플이 릴리즈에 포함·`com.example`이 남아 "출시 직전" 상태는 아니다. 출시를 목표로 하지 않는 개인 앱이라는 점(README:11)은 감안할 것.

### 2.9 의존성 최신성·위험 — 3/5 (확신도: 낮음~중간 — 내 지식은 2026년 중반까지라 2026-10 기준 최신판은 확인 못 함. 인터넷 조회 안 함)

`gradle/libs.versions.toml:1-21`, `gradle/wrapper/gradle-wrapper.properties`

| 라이브러리 | 선언 버전 | 판단 (알고 있는 범위) |
|---|---|---|
| Gradle | 9.4.1 | 최신권 |
| AGP(안드로이드 빌드 도구) | 9.2.1 | 최신권(AGP 9 계열) |
| Compose BOM | 2026.02.01 | 약 8개월 전 판. 조금 뒤처짐 |
| core-ktx 1.18.0 / activity-compose 1.13.0 | | 최신권 |
| Kotlin | 2.2.10 | 2025년 8월 판. 2.3 계열이 이미 나왔으므로 한 단계 이상 뒤처짐 |
| KSP | 2.2.10-2.0.2 | Kotlin에 묶여 같이 뒤처짐 |
| kotlinx-coroutines | 1.8.1 | 2024년 판. 1.10 계열 존재 — 두 단계 뒤처짐(다른 라이브러리가 더 높은 판을 끌어와 실제로는 올라갔을 가능성, 확인 못 함) |
| kotlinx-serialization | **1.6.0** | 2023년 판. Kotlin 2.2 플러그인과 짝으로는 매우 오래됨 — **가장 눈에 띄는 노후** |
| Room | 2.7.1 | 2025년 봄 판. 2.8 계열 존재 |
| lifecycle-runtime-ktx / **lifecycle-viewmodel-compose** | **2.10.0 / 2.8.7** | **같은 묶음을 서로 다른 버전으로 선언** — 위험한 조합. lifecycle은 Gradle이 버전을 맞춰 주는 장치가 있어 실제로는 2.10으로 올라갈 가능성이 높지만(확인 못 함), 선언이 헷갈린다 |
| credentials | 1.3.0 | 2024년 판. 1.5 계열 존재 |
| work-runtime | 2.10.0 | 2024년 판. 조금 뒤처짐 |
| Firebase BOM | 34.7.0 | 2025년 말 판. 조금 뒤처짐 |
| Crashlytics 플러그인 3.0.1 / google-services 4.4.4 / googleid 1.1.1 | | 대체로 무난 |
| JUnit 4.13.2 / espresso 3.7.0 / androidx junit 1.3.0 | | 무난 |

**위험한 조합·설정**
- `gradle.properties`의 `android.disallowKotlinSourceSets=false` — AGP 9의 내장 Kotlin과 KSP가 충돌해 넣은 우회 옵션(파일 주석). AGP나 KSP를 올릴 때 깨질 지점.
- `org.gradle.parallel=false`, `org.gradle.workers.max=1` — 빌드 안정용으로 병렬을 끔. 빌드가 느리다.
- Java 11 대상(`app/build.gradle.kts:20-22,71-74`) — AGP 9 자체는 JDK 17 이상으로 돌므로 문제는 없지만 오래된 설정.
- 루트 `build.gradle.kts`에 KSP 플러그인 선언이 없음(모듈에서만 alias) — 동작엔 문제없음.

**점수 이유**: 빌드 도구·SDK는 최신인데 Kotlin 생태계 라이브러리(serialization·coroutines·Room·credentials)가 1~3년 묵었고 lifecycle 버전이 갈라져 있다.

## 3. 숫자 모음

모든 명령은 `/home/user/Flowlog/app/src`(또는 그 아래 `main/java/com/example/flowlog`)에서 돌렸다. 스크립트 3개는 `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/tools/`에 있다(`rc.py`, `funlen.py`, `ko.py`, `python3 -I <스크립트> <폴더>`).

| 항목 | 값 | 명령 |
|---|---|---|
| 메인 Kotlin 파일 / 줄 | 159 / 37,872 | `find main/java -name "*.kt" \| wc -l`; `… \| xargs cat \| wc -l` |
| 단위 테스트 파일 / 줄 / @Test | 13 / 1,422 / 89 (실질 88) | `find test -name "*.kt"`, `grep -c '@Test'` |
| 계측 테스트 파일 / 줄 / @Test | 2 / 98 / 5 (실질 4) | 위와 같음, `androidTest` |
| 테스트/메인 줄 비율 | 약 4 % | 1,520 / 37,872 |
| 상위 10개 파일 합 | 16,453줄 (43 %) | `wc -l \| sort -rn \| head` |
| 함수 수 / 100줄 이상 / 200줄 이상 | 952 / 53 / 17 | `funlen.py` (중괄호 짝 맞추기 근사. 추상 메서드 1건 오검출 포함) |
| home 섹션 파일당 import 줄 | 206~209 (16파일) | `grep -c '^import'` |
| 빈 `catch {}` | 0 | `grep -E 'catch\s*\([^)]*\)\s*\{\s*\}'` + 여러 줄 패턴 |
| `catch (…)` 전체 | 12 | `grep -E 'catch\s*\('` |
| `runCatching {` 전체 / 결과 버림·로그 없음 | 227 / 99 | `rc.py` |
| 주석 TODO/FIXME | 3 | `grep -E '//\s*(TODO\|FIXME\|HACK\|XXX)'` |
| `Log.*` / uid 포함 | 155 / 7 | `grep -E 'Log\.(d\|i\|w\|e\|v)\('` |
| `!!`(널 강제) | 4 | `grep -o '!!'` |
| 카테고리 문자열 리터럴 | 465 | `grep -rhoE '"(SLEEP\|EXERCISE\|MEAL\|STUDY\|WORK\|SCHOOL\|COMPANY\|REST\|TODO\|ETC\|DEVELOPMENT)"'` |
| `Color(0x` (테마 밖) | 339 (308) | `grep -rhoE 'Color\(0x'` |
| `fontSize = N.sp` / `MaterialTheme.typography` | 352 / 0 | grep |
| strings.xml 항목 / 리소스 사용 | 294 / 375 | `grep -c '<string '`; `grep -E 'stringResource\(\|R\.string\.'` |
| Kotlin 한국어 리터럴 / 표시용 추정 | 684 / 약 330 | `ko.py` (로그·주석 제외), 키워드 사전·debug 제외 |
| `contentDescription` / 그중 null | 77 / 47 | grep |
| Room 버전 / 마이그레이션 / 표 / 안 쓰는 표 | 24 / 23 / 23 / 6(+퇴역 1) | `FlowlogDatabase.kt:81,122`; `grep -rlw` |
| 매니페스트 수신기 | 14 (exported 3) | `AndroidManifest.xml` |
| SharedPreferences 사용 | 41 | `grep getSharedPreferences` |
| 커밋(얕은 클론에 보이는 것) | 57 | `git log --oneline \| wc -l` (`git rev-parse --is-shallow-repository` = true, 전체 이력은 확인 못 함) |

## 4. 포트폴리오 관점 (채용 담당자가 저장소를 열었을 때)

### 강점 5개
1. **진짜 쓰는 앱이고 실제 문제를 풀었다.** 소스 3.8만 줄, 기능 20개 대조 중 18개 완전 구현. 버그 수정 기록이 구체적이다 — 예: 캘린더 연결 Todo가 업로드 전에 SYNCED로 표시돼 영영 안 올라가던 버그(CHANGELOG:68-73), 알림 채널 통합 중 `setTimeoutAfter`가 빠진 버그(CHANGELOG:44-47). "직접 써 보며 다듬었다"를 증명한다.
2. **오프라인 우선 + 충돌 해결 동기화를 직접 설계.** Firestore 트랜잭션·revision·조건부 ACK·충돌 선택 UI(`FirestoreSyncRepository.kt:134-185`, `FirebaseSyncDataSource.kt:136-166`, `MainActivity.kt:234-272`)와 그 테스트(`ActivityRevision*Test` 18개 + 계측 4개). 주니어 포트폴리오에서 보기 드문 주제다.
3. **안드로이드 플랫폼 함정을 아는 코드.** 정확 알람 권한 폴백, `setAlarmClock`으로 Doze 회피, Android 12+ 부팅 수신기 `exported="true"` 이유를 주석으로 설명(`AndroidManifest.xml:58-62`), WorkManager로 삭제 재시도. 면접에서 이야기할 거리가 많다.
4. **문서가 성실하고 정직하다.** README(사용자용/개발자용 분리), PROJECT_CONTEXT(과장 금지 문구 목록까지, PROJECT_CONTEXT:177-204), CHANGELOG. 동기화 조건·Firestore 경로·추천 공식이 코드와 정확히 맞는다. 제품 판단(무엇을 약속하지 않을지)을 글로 남긴 점은 시니어 감각으로 읽힌다.
5. **현대 스택 + 웹 동반 서비스까지 끝까지 연결.** Kotlin·Compose·Material 3·Room(KSP)·StateFlow·WorkManager·Credential Manager·Firebase·Crashlytics, targetSdk 36, AGP 9. 안드로이드 앱 → Firestore → 실제 운영 웹 대시보드까지 한 사람이 이은 "풀 루프" 제품이다.

### 약점 5개
1. **거대 파일·거대 함수.** `ActivityViewModel.kt` 3,138줄, `TodoScreen.kt` 2,974줄, composable 하나 678줄(`ExerciseSection.kt:366`). 리뷰어가 처음 여는 파일이 이것이면 "구조를 못 나눈다"로 읽힌다. 쪼갠 파일마다 import 206줄 복사(2.2)도 금방 눈에 띈다.
2. **테스트가 얕고 CI가 없다.** 실질 단위 88 + 계측 4, 대부분 순수 규칙 함수. ViewModel·동기화·마이그레이션·UI 0. GitHub Actions 배지가 없다. 6개는 죽은 코드를 시험한다.
3. **아키텍처 관례 부재.** DI 없음, Navigation 없음, `MainActivity.onCreate` 380줄 안에 DB·인증·동기화·충돌 처리, 카테고리를 문자열 465곳으로 다룸, `runCatching` 결과를 버리는 곳 99개(Room 쓰기 포함). 안드로이드 채용에서 흔히 묻는 "계층·의존성·에러 처리" 질문에 약하다.
4. **템플릿 흔적과 릴리즈 미준비.** `com.example.flowlog` 네임스페이스, 축소 꺼짐, 템플릿 백업 규칙·proguard, `ExampleUnitTest`, 스토어 미출시. 개발자 기능이 하드코딩 uid로만 잠긴 채 릴리즈에 들어가고, 그 uid가 공개 저장소에 있다(`UserRoleStore.kt:10-11`).
5. **사용자 대상이 사실상 1명(한국어 사용자 본인).** 영어 리소스 없음, 하드코딩 한국어 약 330개, 테마를 우회한 색 308곳(다크 모드 미검증), 접근성 설명 부족, 스크린샷·데모 영상·설치 가능한 APK가 README에 없음(README 전체에 이미지 0개). 외부인이 앱을 직접 보기 어렵다.

## 5. 가장 먼저 고치면 완성도가 크게 오르는 것 5개

| 순위 | 할 일 | 난이도 | 이유 |
|---|---|---|---|
| 1 | **CI + 테스트 바닥 깔기**: GitHub Actions로 `-PofflineValidation=true testDebugUnitTest` 돌리기(README:305-308에 이미 방법이 있음), `exportSchema = true` + `MigrationTestHelper`로 마이그레이션 시험, `FirebaseSyncDataSource`의 PENDING→ACK 흐름을 가짜 저장소로 시험 | 중 | 비용 대비 포트폴리오 효과가 가장 크다(배지 하나로 "검증하는 개발자"가 됨). 마이그레이션 23개는 지금 무방비인 사용자 데이터 위험 1순위 |
| 2 | **죽은 코드·템플릿 흔적 정리**: `ButtonRecommendationEngine`+그 테스트, revision 없는 `syncActivity*`·`syncTodo*` 5개, 안 쓰는 Room 표 6개(다음 마이그레이션 때), `ExampleUnitTest`/`ExampleInstrumentedTest`, uid 하드코딩을 원격 설정·커스텀 클레임 등으로 이동 | 소 | 하루 안에 끝나고, README:331-333 오류와 공개 저장소 uid 문제까지 같이 풀린다 |
| 3 | **삼킨 예외 정리**: Room 쓰기를 감싼 `runCatching`(TodoRepository 23곳 등)을 실패 시 로그+사용자 메시지로 바꾸고, 코루틴 취소 예외는 다시 던지기. uid 로그 7곳 제거 | 소~중 | "폰에 저장됨"이라는 앱의 핵심 약속을 지키는 일. 리뷰어가 grep 한 번으로 찾는 냄새를 없앤다 |
| 4 | **거대 파일 분해**: `ActivityViewModel`을 타이머·추천·버튼 설정·집중 모드 등 역할별 클래스로, `MainActivity.onCreate`의 동기화·충돌 로직을 ViewModel/Coordinator로, home 섹션의 복사 import를 실제 필요한 것만 남기기, 카테고리를 enum으로 | 대 | 구조 점수를 올리는 유일한 길이지만 회귀 위험이 커서 1번(테스트) 뒤에 해야 한다 |
| 5 | **백그라운드·권한 신뢰성 마무리**: 루틴 목표·집중·무활동·자정 동기화를 부팅 수신기에 추가, 자정 동기화를 WorkManager 주기 작업으로, 정확 알람 설정 이동을 "설명 후 한 번"으로 바꾸고 권한 변경 방송 수신, 알림 권한 거절 처리. 그 뒤 README:62-63·156 문구를 실제와 맞추기 | 중 | README 약속과 코드의 남은 어긋남 대부분이 여기 몰려 있다. 사용자가 매번 설정 화면으로 끌려가는 UX 문제도 같이 해결 |

(그다음 후보: 릴리즈 축소 켜기 + proguard 규칙(중), Kotlin·serialization·Room·lifecycle 버전 정리(소~중), README에 스크린샷·데모 GIF(소), 영어 리소스(중).)
