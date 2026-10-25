# Flowlog 방향·유지보수·기능 아이디어 조사 (2026-10-20)

대상: `/home/user/Flowlog` (main, 버전 0.5.9 / versionCode 26, targetSdk 36, minSdk 24, AGP 9.2.1, Kotlin 2.2.10).
읽기만 했고 빌드(`./gradlew`)는 돌리지 않았다. 코드 위치는 `파일:줄`로 적었다(`app/src/main/java/com/example/flowlog/` 아래는 `…/`로 줄임).

**줄 번호 기준**: 커밋된 HEAD `98b3039`. 조사 도중 같은 작업 트리(브랜치 `ccr-2a22e640-e8dn8n`)에 다른 에이전트의 **미커밋 변경**이 생겼다 — 지난 활동 직접 추가, 기록 내보내기(CSV/JSON), 앱 바로가기(`shortcut/`), `MainActivity.kt`·`ActivityViewModel.kt` 등 8개 파일 수정(`git status`, `git diff --stat`로 확인, 보고서 `docs/worklog/2026-10-20-flowlog-features.md`). 그래서 `MainActivity.kt` 줄 번호는 작업 트리에서 약 10–125줄 뒤로 밀려 있다(예: 정확 알람 요청 HEAD `:172` → 작업 트리 `:185`). 아래 C3·C5는 그 진행 중 작업을 반영해 표시했다.

**출처 표시 규칙**
- (열어 확인) = 이 조사에서 실제로 페이지를 열어 내용을 읽은 것.
- (검색 결과로만, 열지 못함) = 이 환경의 네트워크가 막혀(firebase.google.com, developers.google.com, docs.github.com, f-droid.org, support.google.com, 각 앱 회사 사이트 등) 검색 결과 요약만 본 것. 메인이 다시 확인해야 한다.
- 근거 없는 내 판단은 "판단"이라고 쓴다.

---

## A. 플랫폼 변화가 Flowlog에 미치는 영향 (2025–2026)

### 요약 표 (급한 순)

| # | 항목 | Flowlog 상태 | 급한 정도 | 기한 |
|---|---|---|---|---|
| A1 | 정확 알람(exact alarm) 사용 정리 | 8곳에서 정확 알람, 매 실행마다 권한 화면 띄움 | **높음** | 정책은 이미 시행 중(Android 14~) |
| A2 | 타이머 알림: Android 14 "지울 수 있는 ongoing" + Android 16 Live Update | 타이머 알림이 밀어서 지워지면 다시 안 뜸, 정지 버튼 없음 | **높음** | 없음(사용성) |
| A3 | 사이드로드 개발자 인증(developer verification) | 앱스토어 없이 직접 빌드 배포 | **중~높음**(배포 방식에 따라) | 2026-09-30 일부 국가, **2027 전 세계** |
| A4 | 의존성 노후 + lifecycle 버전 섞임 | Room 2.7.1, credentials 1.3.0, lifecycle 2.10.0/2.8.7 혼용 | 중 | 없음 |
| A5 | Google 로그인(Credential Manager) 마무리 | 이미 전환됨. 로그아웃 시 자격 상태 안 지움 | 중 | 레거시 GSI 제거일 미정 |
| A6 | Firebase(요금·규칙·App Check·BoM) | BoM 34.7.0, 전체 조회 복원, App Check 없음 | 중 | 없음 |
| A7 | 백업 규칙(allowBackup) | 템플릿 그대로(무엇이 백업되는지 미정) | 중 | 없음 |
| A8 | predictive back(뒤로 가기 미리 보기) | 뒤로 가기 처리 코드 0곳 | 낮음~중 | targetSdk 36에서 이미 기본 켜짐 |
| A9 | targetSdk 요구(Play) | 36으로 이미 충족 | 낮음 | 2026-08-31(지남, 충족) / 다음은 API 37 |
| A10 | 16KB 페이지 크기 | 네이티브 코드 없을 가능성 높음(미확인) | 낮음(확인 1회) | 2027-02-01(Play 업데이트) |
| A11 | 엣지 투 엣지 강제 | 이미 대응(`enableEdgeToEdge`) | 낮음 | 이미 시행 |
| A12 | 집중 모드 방해 금지(DND) — Android 15 Modes | 동작은 유지됨, 개선 여지 | 낮음 | 이미 시행 |
| A13 | Glance 위젯 / Material 3 Expressive / 온디바이스 AI / Health Connect / Wear OS / 바로가기·빠른 설정 타일 | 없음 | 기능 기회(C절) | 없음 |

---

### A1. 정확 알람(exact alarm) 정책 — 가장 급함

**무엇이 바뀌었나**
- Android 14부터 `SCHEDULE_EXACT_ALARM`(정확한 시각 알람 권한)은 Android 13 이상을 목표로 하는 새 설치 앱에 **기본 거부**. `setExact()`·`setExactAndAllowWhileIdle()`·`setAlarmClock()`은 권한 없으면 `SecurityException`. 권한 상태가 바뀌면 `ACTION_SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED`를 받아 다시 예약하라고 권장. 매번 `canScheduleExactAlarms()` 확인, 거부되면 설정 화면으로 보내고 `onResume()`에서 다시 확인. (열어 확인: https://developer.android.com/about/versions/14/changes/schedule-exact-alarms)
- 정확 알람은 "사용자가 보는 기능이 정확한 시각을 요구할 때만". 주기적 작업·업로드는 WorkManager, 대략적 시각이면 `setWindow()`(최소 10분 창)·`setAndAllowWhileIdle()`. (열어 확인: https://developer.android.com/develop/background-work/services/alarms)
- `USE_EXACT_ALARM`(설치 시 자동 허용)은 알람시계·캘린더 앱 전용이고 Play 정책 대상. Flowlog는 해당 안 됨(판단). Play 정책 원문은 열지 못함(검색 결과로만: 2022 정책 안내 https://services.google.cn/fh/files/misc/play_policy_handout_202208.pdf).

**Flowlog 코드**
- `AndroidManifest.xml:9` `SCHEDULE_EXACT_ALARM` 선언.
- `…/MainActivity.kt:172`, `:710-723` — **앱을 열 때마다** 설명 없이 정확 알람 설정 화면으로 보낸다(`requestExactAlarmPermission()`가 `onCreate`에서 호출). `onResume` 재확인 없음.
- 권한 상태 변경 브로드캐스트 수신기 없음(`SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED` grep 0건) → 나중에 권한을 줘도 이미 부정확하게 예약된 알람은 다음 재예약 전까지 그대로.
- 정확 알람을 쓰는 곳 8곳: `…/notification/ReminderScheduler.kt:224-226,316-324`(양치·식사, `setAlarmClock`), `FocusModeScheduler.kt:16-31`(집중 종료), `PlannedTodoReminderScheduler.kt:102-117`(할 일 알림), `RoutineGoalAlarmScheduler.kt:61-76`, `AutoButtonScheduler.kt:124-139`(자동 시작), `StudyPlanAutoStartScheduler.kt:46-61`, `InactivityReminderScheduler.kt:45-53`(무활동 알림), `…/data/sync/FirebaseSyncSupport.kt:34-70`(자정 동기화).
- `ReminderScheduler.kt:224-226` 주석은 "setAlarmClock은 Doze에서 면제"라고만 쓰여 있으나 `setAlarmClock`도 권한이 필요하다(코드는 `:322-324`에서 예외를 잡아 약한 알람으로 내려가므로 동작은 안전). 주석이 오해를 부른다.

**해야 할 일**
1. 자정 동기화(`FirebaseSyncSupport.kt:34`)를 정확 알람에서 **WorkManager 주기 작업**(네트워크 조건)으로 옮긴다. 이미 WorkManager를 쓰고 있다(`DeleteSyncWorker`). 정확한 자정일 이유가 없다.
2. 무활동 알림(`InactivityReminderScheduler.kt:45`)은 `setWindow`(10분 창)로. 넛지(가벼운 알림)는 몇 분 늦어도 된다.
3. 정확해야 하는 것(양치 3분·식사 타이머 끝, 집중 종료, 사용자가 시각을 정한 할 일 알림)만 정확 알람 유지.
4. 권한 요청을 **처음 그 기능을 켤 때** 이유와 함께(예: "양치 타이머 끝을 정확히 알리려면 필요해요"). `onCreate` 무조건 요청 제거.
5. `ACTION_SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED` 수신기 추가 → 모든 스케줄러 `rescheduleAll()`.
- 비용: 반나절~하루. 기한: 없음(이미 시행). 이유: 사용자 경험(매번 설정 화면) + 배터리 + 나중에 Play에 올릴 때 심사 부담.

### A2. 타이머 알림 — Android 14 "지울 수 있는 ongoing", Android 16 Live Update

**무엇이 바뀌었나**
- Android 14: `FLAG_ONGOING_EVENT`(진행 중 표시) 알림도 사용자가 밀어서 지울 수 있다(잠금 화면, "모두 지우기"는 예외). (열어 확인: https://developer.android.com/about/versions/14/behavior-changes-all)
- Android 16: **Live Update(승격된 진행 중 알림)** — 사용자가 시작한, 진행 중이고 시간이 중요한 일(운동, 길안내 등)을 알림창 맨 위·잠금 화면·**상태 표시줄 칩**으로 띄운다. 조건: `POST_PROMOTED_NOTIFICATIONS`(설치 시 권한), `setRequestPromotedOngoing(true)`, `setOngoing(true)`, 제목 필수, 커스텀 뷰·colorized 금지. 칩에는 `setShortCriticalText` 또는 `setUsesChronometer`로 경과 시간. 사용자가 지우면 다시 올리지 말고 `setDeleteIntent`로 감지. (열어 확인: https://developer.android.com/develop/ui/views/notifications/live-update)
- Android 16 `ProgressStyle`(진행 중심 알림) 추가. (열어 확인: https://developer.android.com/about/versions/16/features)

**Flowlog 코드**
- `…/notification/ActivityTimerNotifier.kt:24-49` 실행 중 타이머 알림: `setOngoing(true)` + `setUsesChronometer(true)`, **정지·전환 버튼 없음, `setDeleteIntent` 없음**(grep 0건). Android 14+에서 밀어서 지우면 타이머는 계속 도는데 알림만 사라진다.
- 카운트다운(간식·식사·양치) `ActivityTimerNotifier.kt:280-310`: `setChronometerCountDown`.
- 포그라운드 서비스(FGS)를 쓰지 않고 시작 시각만 저장하는 방식(`data/local/TimerStateStore.kt`) — **좋은 설계**. Android 15의 FGS 시간 제한·부팅 시 FGS 금지 등에 영향받지 않는다(열어 확인: https://developer.android.com/about/versions/15/behavior-changes-15). 이 방식은 유지 권장.

**해야 할 일**
- 실행 중 타이머 알림에 "정지" 액션(브로드캐스트 → 저장) 추가, `setDeleteIntent`로 지워짐을 감지(다시 띄울지, 그냥 둘지 결정).
- Android 16 기기에서 Live Update 요청(`POST_PROMOTED_NOTIFICATIONS`, `setRequestPromotedOngoing`, `setShortCriticalText("공부")` 같은 짧은 분류명). 상태 표시줄에 "공부 1:23"처럼 보이면 "가볍게 기록" 철학에 바로 맞는다(판단).
- 비용: 하루. 기한 없음. (C절 아이디어 1과 같음)

### A3. 사이드로드 개발자 인증 (developer verification) — 배포 방식이 바뀌면 급함

**무엇이 바뀌었나** (열어 확인: https://developer.android.com/developer-verification, https://developer.android.com/developer-verification/guides/faq)
- 2026-08: 개발자 API, 제한 배포 계정, 고급 설치 흐름 시작. 2026-09-30: 브라질·인도네시아·싱가포르·태국의 참여 스토어 설치부터 보호 시작. **2027년 이후 전 세계 인증 기기 전체로 확대.**
- **ADB 설치는 인증 없이 가능**("As a developer, you are free to install apps without verification with ADB"). Android Studio 설치는 보통 ADB 경유지만 문서가 명시하지는 않음.
- 학생·취미 개발자용 **제한 배포 계정(Limited Distribution)**: 신분증·등록비 없이 **최대 20대 기기**까지 공유. 전체 배포 계정은 25달러.
- 패키지 이름과 서명 키를 등록해야 한다. **서명 키를 잃으면 그 패키지를 등록할 수 없다.**
- 한국 시행 시점은 문서에 없음(확인 못 함).

**Flowlog**
- 패키지 `org.pfkfks.flowlog`(`app/build.gradle.kts:33`), 서명은 로컬 `keystore.properties`(`app/build.gradle.kts:13-18,42-51`). 지금처럼 본인 PC에서 Android Studio/ADB로만 설치하면 영향 없음.
- GitHub Releases APK·Obtainium·F-Droid로 **다른 사람에게** 나눠 주면 2027년부터 인증이 필요.

**해야 할 일**: (1) 키스토어를 PC 밖에 안전하게 백업(지금 당장, 비용 10분). (2) 남에게 배포할 계획이 생기면 제한 배포 계정으로 `org.pfkfks.flowlog` 등록(B절 3번 참고).

### A4. 의존성 노후와 lifecycle 버전 섞임

**Flowlog 코드** (`gradle/libs.versions.toml`)
- `:7` `lifecycleRuntimeKtx = "2.10.0"`과 `:13` `viewmodel = "2.8.7"`(lifecycle-viewmodel-compose)이 **다른 lifecycle 버전**. 같은 lifecycle 묶음은 한 버전으로 맞추는 게 원칙(판단; 런타임 충돌은 Gradle이 높은 쪽으로 올려 대개 숨겨지지만 혼란의 원인).
- Room `2.7.1`(`:12`) → 최신 안정 2.8.5(2026-09-09). 2.8.0부터 minSdk 23(Flowlog 24라 문제없음). Room 3(`androidx.room3`) 계열도 나와 있음. (열어 확인: https://developer.android.com/jetpack/androidx/releases/room)
- credentials `1.3.0`(`:19`) → 최신 안정 1.6.0(2026-04-08). (열어 확인: https://developer.android.com/jetpack/androidx/releases/credentials)
- Firebase BoM `34.7.0`(`:16`) → 검색상 34.16.0(2026-07-09)·34.17.0까지 나옴(검색 결과로만, 열지 못함: https://firebase.google.com/support/release-notes/android).
- coroutines `1.8.1`, serialization `1.6.0`, work `2.10.0`도 Kotlin 2.2와 함께 쓰기엔 오래됨(판단; 최신 버전은 확인 못 함).
- Room 스키마 내보내기 꺼짐: `…/data/local/db/FlowlogDatabase.kt:84` `exportSchema = false` → 마이그레이션 자동 시험 불가(B절 4번).

**해야 할 일**: Dependabot/Renovate로 묶음 갱신(B절 1번). 첫 정리는 lifecycle 통일 → Room 2.8.x → credentials 1.6 → Firebase BoM 순. 비용: 반나절 + 기기 확인.

### A5. Google 로그인 — Credential Manager 전환 상태

**무엇이 바뀌었나**
- 레거시 Google Sign-In(`play-services-auth`의 `GoogleSignInClient`)은 **지원 중단(deprecated), "향후 릴리스에서 제거"**, 날짜는 미정. 조용한 로그인은 `filterByAuthorizedAccounts=true` + `setAutoSelectEnabled(true)`. 권한(드라이브 등)은 `AuthorizationClient`로 분리. (열어 확인: https://developer.android.com/identity/sign-in/legacy-gsi-migration, https://developer.android.com/identity/sign-in/credential-manager-siwg)

**Flowlog 코드**
- 이미 Credential Manager + `GetGoogleIdOption` 사용: `…/MainActivity.kt:554-569`. 레거시 GSI 의존 없음(`libs.versions.toml`에 `play-services-auth` 없음). **전환 완료.**
- 남은 빈틈: 로그아웃 `…/MainActivity.kt:342`가 `auth.signOut()`만 하고 `CredentialManager.clearCredentialState()`를 부르지 않음. 공식 페이지에서 이 권장을 직접 읽지는 못했다(WebFetch 요약이 "일반 지식"이라고 밝힘) → 확인 필요.
- `setFilterByAuthorizedAccounts(false)`로 바로 시작 — 이미 로그인했던 계정 자동 선택(true 먼저 → false 재시도) 흐름이 아님. nonce 없음.

**해야 할 일**: 로그아웃 시 `clearCredentialState`, 로그인 2단계(authorized 먼저), credentials 1.6.0. 비용: 2시간.

### A6. Firebase 쪽 변화 (요금·규칙·App Check)

**확인한 것**
- Firestore Standard 무료 할당(열어 확인, https://cloud.google.com/firestore/pricing): 저장 1 GiB, 읽기 **50,000/일**, 쓰기 20,000/일, 삭제 20,000/일, 전송 10 GiB/월. 리스너(실시간 구독)는 오프라인 지속성이 켜진 상태에서 30분 넘게 끊겼다 다시 붙으면 새 쿼리처럼 읽기 과금. Enterprise 에디션이 별도로 있음.
- App Check(Play Integrity 제공자): 검색 결과가 엇갈림 — 최신 문서는 "Play 밖 배포도 지원(PLAY_RECOGNIZED·LICENSED 검사 생략 설정)", 예전 문서는 "Play 배포만" (검색 결과로만, 열지 못함: https://firebase.google.com/docs/app-check/android/play-integrity-provider). Play Integrity 자체는 기본 하루 10,000 요청, 앱 무결성 기본 검사가 `PLAY_RECOGNIZED`라서 직접 빌드한 APK는 이 검사를 통과 못 함(열어 확인: https://developer.android.com/google/play/integrity/overview).

**Flowlog 상태**
- `…/data/sync/` 복원은 아직 **전체 조회**, 일반 동기화는 15분 간격 제한(`docs/study-integration/IMPLEMENTATION_STATUS.md:19`). 사용자 1명이면 무료 할당 안. 기록이 몇 년 쌓이거나 웹 쪽 사용자가 늘면 읽기 수가 먼저 문제(판단).
- 웹 달력 실시간 구독 `…/MainActivity.kt:545`(`startCalendarSubscription`) — `onStop`에서 해제(`:548-551`), 좋음.
- 규칙: `docs/study-integration/firestore.proposed.rules`는 이 저장소에 있고, 실제 배포 규칙은 웹 저장소(pfkfks-main)에 있음 → **두 곳이 어긋날 위험**. 2026-09-29 기준 "운영에는 배포하지 않았다"(`IMPLEMENTATION_STATUS.md:13-15`). 지금 배포 여부는 확인 못 함.
- App Check 없음(grep 0건).
- 관리자 판별을 앱 코드의 uid 문자열로 함(`…/data/local/UserRoleStore.kt:11`), 같은 값이 `tools/study-integration/rules-test.cjs:19`에도 있음. uid는 비밀번호가 아니지만 `PROJECT_CONTEXT.md:40-42`의 "private IDs 커밋 금지" 원칙과 어긋날 수 있음(판단). 규칙 쪽 `isAdmin()`(proposed.rules:4)과 앱 쪽 판별이 따로 있다.

**해야 할 일**: (1) 규칙 원본을 한 곳(웹 저장소)으로 정하고 이 저장소는 사본+시험만 둔다는 걸 PROJECT_CONTEXT에 명시. (2) 증분 복원(서버 시각 기준) — 데이터가 커지기 전. (3) App Check는 Play 미출시인 동안 **강제(enforce)하지 않는다**(직접 빌드 APK가 막힐 수 있음). (4) 관리자 판별은 Firebase 사용자 지정 클레임(custom claim)으로 옮기는 걸 검토.

### A7. 백업 규칙 (allowBackup)

- `AndroidManifest.xml:14-16` `allowBackup="true"`, `res/xml/data_extraction_rules.xml`·`backup_rules.xml`은 **템플릿 그대로(TODO 주석)**. 즉 Room DB와 SharedPreferences(대기 중 알림, 타이머 상태, 사용자 역할 등)가 기본 규칙대로 Google 클라우드 백업·기기 이전 대상(판단: 기본 자동 백업 동작 기준, 이번에 문서는 열지 않음).
- 위험(판단): 새 폰에 Room이 복원되면 `README.md:172-173`의 "로컬이 비었을 때만 Firestore 복원" 조건이 안 맞아 동기화 상태(`syncStatus`)가 섞인 채 시작할 수 있다. 정확 알람 권한은 백업 복원 시 거부 상태(A1 페이지).
- 해야 할 일: 무엇을 백업할지 결정 — 추천은 "Room·설정은 Firestore가 원본 복사본이니 클라우드 백업에서 제외, 기기 이전(device-transfer)만 허용" 또는 반대로 "로그인 안 하는 사용자를 위해 Room 포함". 사용자 판단 필요. 비용: 1시간 + 이전 시험.

### A8. Predictive back (뒤로 가기 미리 보기)

- Android 16(targetSdk 36)부터 기본 켜짐: `onBackPressed` 안 불림, `KEYCODE_BACK` 안 옴. 끄려면 `enableOnBackInvokedCallback="false"`. (열어 확인: https://developer.android.com/about/versions/16/behavior-changes-16) Compose는 `activity-compose` 1.8+ 와 `BackHandler`/`PredictiveBackHandler`. (열어 확인: https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture)
- Flowlog: `onBackPressed`·`BackHandler` **0곳**(grep). 화면은 홈/할 일 두 쪽 `HorizontalPager`(`…/MainActivity.kt:401-434`). activity-compose 1.13.0이라 요건 충족. 깨지는 코드는 없음.
- 할 일(선택): 할 일 탭에서 뒤로 가면 앱이 닫히는 대신 홈으로(`BackHandler(enabled = currentScreen == "todo")`). 10분.

### A9. targetSdk 요구 (Play)

- 2026-08-31부터 **새 앱·업데이트는 Android 16(API 36) 이상** 목표 필수, 기존 앱은 API 35 이상이어야 새 사용자에게 보임, 연장 신청 시 2026-11-01. (열어 확인: https://developer.android.com/google/play/requirements/target-sdk — 페이지 갱신일 2026-10-16)
- Flowlog `app/build.gradle.kts:35` `targetSdk = 36` → **이미 충족**. Play에 없으니 당장은 무관.
- 다음 단계(판단: 매년 8월 갱신 관례상 2027년 여름 API 37 요구 예상, 공식 발표 아님). Android 17 대상 변경(열어 확인: https://developer.android.com/about/versions/17/behavior-changes-17, 페이지 기준 아직 베타로 보임): 큰 화면 방향 고정 해제 옵트아웃 제거(Flowlog는 `screenOrientation` 없음 → 영향 없음), `RemoteViews` 비트맵 메모리 상한(위젯 비트맵 900×180 ARGB ≈ 0.65 MB, `…/widget/FlowStatusWidgetProvider.kt:288-293` → 상한보다 훨씬 작음), `IntentSender` 백그라운드 실행 제한, 백그라운드 오디오는 FGS 필요(Flowlog 알림음 `KakaoStyleAlertPlayer.play`는 화면 안 `TimerSection.kt:270-273`에서만 → 영향 없음).

### A10. 16KB 페이지 크기

- Play: **2027-02-01부터** 16KB 미지원 업데이트는 출시 불가(API 35+ 대상, 64비트 기기). Java/Kotlin만 쓰는 앱(라이브러리 포함)은 이미 지원. 확인: APK Analyzer의 `lib` 폴더, `zipalign -c -P 16 -v 4 APK`. AGP 8.5.1+ 권장. Android 16은 4KB 정렬 앱에 호환 모드 + 경고창. (열어 확인: https://developer.android.com/guide/practices/page-sizes, https://developer.android.com/about/versions/16/behavior-changes-all)
- Flowlog: 자체 NDK 코드 없음, AGP 9.2.1. 의존성 중 `.so`를 넣는 것이 있는지는 **확인 못 함**(빌드 금지). Compose UI 계열이 작은 네이티브 라이브러리를 끌어올 가능성은 있다(판단, 미확인).
- 할 일: 다음 릴리즈 APK에서 `zipalign -c -P 16` 한 번. 5분.

### A11. 엣지 투 엣지 강제

- Android 15(target 35) 강제, Android 16(target 36)에서 옵트아웃 속성 무효. (열어 확인: https://developer.android.com/develop/ui/views/layout/edge-to-edge, behavior-changes-16)
- Flowlog: `…/MainActivity.kt:173` `enableEdgeToEdge()`, `:425-426` Scaffold `safeDrawing`(위·옆), `:1483` 아래 내비게이션 바 인셋, `res/values/themes.xml`에 옵트아웃 없음 → **대응됨**.
- 할 일: 키보드(IME) 인셋 — 제목 입력 대화상자(`ui/component/ActivityTitleDialog.kt`)·할 일 입력에서 키보드가 입력칸을 가리는지 3버튼 내비게이션 기기에서 한 번 확인. 확인 못 함.

### A12. 집중 모드 방해 금지(DND) — Android 15 Modes

- target 35+ 앱은 전역 DND를 직접 못 바꾸고, `setInterruptionFilter()` 호출이 **암묵적 AutomaticZenRule**(앱 이름의 모드)을 만든다. 다른 주체가 켠 규칙을 끄려는 경우에만 동작 차이. (열어 확인: https://developer.android.com/about/versions/15/behavior-changes-15)
- Flowlog `…/notification/FocusDndController.kt:37-47`: 이전 필터 저장 → PRIORITY로, 복원 시 이전 값으로. 사용자가 이미 켠 DND는 안 건드림(좋음). **기능은 그대로 동작**(판단).
- 개선(선택): 명시적 `AutomaticZenRule`("Flowlog 집중")로 바꾸면 시스템 설정의 모드 목록에 이름이 보이고 사용자가 예외(전화 등)를 직접 고를 수 있다. 낮은 우선순위.

### A13. 기능 기회가 되는 플랫폼 변화 (상세는 C절)

- **Health Connect**: Android 14+ 프레임워크 내장, SDK는 **Android 8(API 26)+** → Flowlog minSdk 24라 **minSdk를 26으로 올려야** 함. 수면 `SleepSessionRecord`, 운동 `ExerciseSessionRecord`, 마음챙김 `MindfulnessSessionRecord`, 활동 강도(Android 16) 있음. 개인정보처리방침 액티비티 필수(Android 14+는 `VIEW_PERMISSION_USAGE` activity-alias). 권한 부여 30일 이전 기록은 별도 권한. (열어 확인: https://developer.android.com/health-and-fitness/health-connect/get-started, https://developer.android.com/health-and-fitness/health-connect/data-types)
- **Glance 위젯**: 안정 1.2.0(2026-08-26), 1.2부터 minSdk 23, 생성 미리보기(위젯 고르기 화면), 1.3 알파는 compileSdk 37·AGP 9.2 필요, 레거시 Wear 라이브러리는 `androidx.glance.wear`로 대체 중. (열어 확인: https://developer.android.com/jetpack/androidx/releases/glance) Flowlog 위젯은 RemoteViews + 직접 그린 비트맵 + AlarmManager 갱신(`…/widget/FlowStatusWidgetProvider.kt:247-271`), 누르면 앱 열기만(`:94`) — 위젯에서 바로 시작·정지 불가.
- **Wear OS 타일**: ProtoLayout·Tiles 라이브러리, 무거운 일은 WorkManager로. (열어 확인: https://developer.android.com/training/wearables/tiles) 별도 Wear 모듈·폰-시계 통신(Data Layer) 필요(판단, 해당 페이지 미열람).
- **Material 3 Expressive**: Compose material3 안정 1.4.0, 1.5.0-beta01(2026-10-07)에서 ButtonGroup 등 승격 진행 중 — **1.5 안정판까지 기다리는 게 맞다**. (열어 확인: https://developer.android.com/jetpack/androidx/releases/compose-material3, https://developer.android.com/develop/ui/compose/designsystems/material3) Flowlog는 BoM 2026.02.01 + 동적 색(`ui/theme/Theme.kt:40-46`).
- **온디바이스 AI**: Gemini Nano(AICore) + ML Kit GenAI(요약·교정·재작성·이미지 설명·음성 인식·프롬프트). 지원 기기·언어(한국어)·상태는 그 페이지에 없음 → 확인 못 함. (열어 확인: https://developer.android.com/ai/gemini-nano; 상세 https://developers.google.com/ml-kit/genai 는 열지 못함)
- **바로가기(App Shortcuts)**: 정적·동적·고정, 런처는 보통 4개까지. (열어 확인: https://developer.android.com/develop/ui/views/launch/shortcuts) Flowlog 없음.
- **빠른 설정 타일(Quick Settings Tile)**: `TileService`, Android 13+ `requestAddTileService()`로 추가 요청. (열어 확인: https://developer.android.com/develop/ui/views/quicksettings-tiles) Flowlog 없음.
- **NFC**: NDEF 태그 + AAR(앱 레코드)로 앱 실행. Android 16부터 첫 태그 인텐트 때 사용자에게 알림·차단 가능, Android 17 대상 앱은 NFC로 여는 액티비티에 `DISPATCH_NFC_MESSAGE` 보호 필요, http(s) 태그는 Android 16부터 `ACTION_VIEW`. (열어 확인: https://developer.android.com/develop/connectivity/nfc/nfc)

---

## B. 유지보수 모델 제안 (1인 개발자가 지속 가능하게)

원칙(판단): **사람이 기억해야 하는 일을 기계가 알려 주게** 만들고, 사람은 한 달에 한 번 묶어서 처리한다. 지금 Flowlog에는 `.github/` 폴더가 없다(CI·의존성 봇 0). 아래는 비용(처음 설정 / 매달) 순.

| # | 제안 | 처음 비용 | 매달 비용 | 효과 |
|---|---|---|---|---|
| B1 | CI(단위 테스트·컴파일 + 규칙 시험) | 1–2시간 | 0 | 상: 깨진 push를 바로 앎 |
| B2 | 의존성 갱신 봇(Dependabot) | 30분 | 30–60분(PR 묶음 검토) | 상: A4 같은 노후를 막음 |
| B3 | 릴리즈 경로 정하기(ADB 유지 + GitHub Releases 기록) | 1시간 + 키 백업 | 릴리즈마다 10분 | 중 |
| B4 | 테스트: Room 마이그레이션 시험 최우선 | 2–3시간 | 스키마 바꿀 때만 | 상: 기록 앱에서 가장 무서운 "업데이트 후 데이터 손실" 방지 |
| B5 | Crashlytics 실제로 받기 + 조용한 실패 기록 | 1–2시간 | 월 10분 확인 | 중 |
| B6 | 문서: CHANGELOG 버전 구역, 규칙 원본 위치 | 30분 | 릴리즈마다 5분 | 중 |
| B7 | 버전 태그·번호 습관 | 0 | 릴리즈마다 5분 | 중 |

### B1. CI — GitHub Actions 초안 (`.github/workflows/android-ci.yml`)

확인한 사실(코드): `-PofflineValidation=true`이면 `processDebugGoogleServices`를 끄고 가짜 웹 클라이언트 ID를 넣는다(`app/build.gradle.kts:56-59,82-84`). Gradle 데몬 JVM은 21(`gradle/gradle-daemon-jvm.properties`), 컴파일 툴체인은 11(`app/build.gradle.kts:20-22`, foojay 자동 다운로드 `settings.gradle.kts:14-16`). **`gradlew`가 git에 실행 권한 없이(100644) 저장돼 있어** 리눅스 러너에서 `./gradlew`가 "Permission denied"로 실패한다(`git ls-files -s gradlew`로 확인) → 아래 초안은 `chmod +x`를 넣었다. 근본 해결은 `git update-index --chmod=+x gradlew` 한 번.

```yaml
name: android-ci
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  unit-test:
    runs-on: ubuntu-latest
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: |
            11
            21
      - uses: gradle/actions/setup-gradle@v4   # 캐시 + wrapper 검증
      - run: chmod +x gradlew
      - name: Unit tests and compile without google-services.json
        run: ./gradlew --no-daemon testDebugUnitTest assembleDebug -PofflineValidation=true
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: |
            app/build/reports/tests
            app/build/test-results
          retention-days: 14

  firestore-rules:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - uses: actions/setup-java@v4      # Firestore 에뮬레이터가 Java로 돈다
        with:
          distribution: temurin
          java-version: 21
      - run: node tools/study-integration/prepare-rules.cjs
      - name: Rules tests on the local emulator (demo project, no production access)
        working-directory: app/build/study-validation
        run: npx --yes firebase-tools@14 emulators:exec --only firestore --project demo-flowlog-study --config firebase.json "node rules-test.cjs"
```

메모
- 액션·firebase-tools 버전 번호는 이번에 공식 문서를 열어 확인하지 못했다(docs.github.com 접속 불가). 처음 돌릴 때 확인. `firebase-tools@14`는 예시.
- `lintDebug`는 처음엔 빼 두고, 경고 수를 한 번 본 뒤 기준선(baseline)을 만들어 넣는 걸 추천(판단).
- `tools/study-integration/`의 `model-store.test.cjs`·`migration-test.cjs`·`browser-test.cjs`는 웹 저장소(`STUDY_WEBSITE`) 코드가 필요해서 이 CI에 넣지 않았다(`IMPLEMENTATION_STATUS.md` "실행 방법"). 규칙 시험(`rules-test.cjs`)만 이 저장소 안에서 혼자 돈다.
- `gradle.properties:7-8`의 `org.gradle.parallel=false`, `workers.max=1`은 CI를 느리게 하지만 안정성 이유로 둔 것 같으니 그대로(판단).

### B2. 의존성 갱신 — Dependabot(추천) 또는 Renovate

비교(판단; 두 도구 공식 문서는 열지 못함):
- **Dependabot**: GitHub 기본 기능, 설치 없음. Gradle 버전 카탈로그(`libs.versions.toml`)를 읽는다(검색 결과로만). 묶음(groups)으로 PR 수를 줄일 수 있다. 1인에게 충분.
- **Renovate**: 앱 설치 필요. Kotlin과 KSP처럼 **같이 올려야 하는 것**(`libs.versions.toml:9-10` `kotlin = "2.2.10"`, `ksp = "2.2.10-2.0.2"`)을 규칙으로 묶기 쉽고, 대시보드 이슈 하나로 전체 현황을 본다.
- 추천: Dependabot 월 1회 + Kotlin/KSP/AGP 같은 큰 묶음은 분기마다 손으로.

`.github/dependabot.yml` 초안:
```yaml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 5
    groups:
      androidx:
        patterns: ["androidx.*"]
      firebase-google:
        patterns: ["com.google.firebase*", "com.google.gms*", "com.google.android.libraries.identity*"]
      kotlin-toolchain:
        patterns: ["org.jetbrains.kotlin*", "com.google.devtools.ksp*"]
      kotlinx:
        patterns: ["org.jetbrains.kotlinx*"]
    ignore:
      # AGP 주 버전은 손으로 올린다(빌드 스크립트 변경 동반)
      - dependency-name: "com.android.application"
        update-types: ["version-update:semver-major"]
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

Renovate를 쓸 경우 `renovate.json` 초안:
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended", ":dependencyDashboard"],
  "schedule": ["before 9am on the first day of the month"],
  "packageRules": [
    { "groupName": "kotlin + ksp", "matchPackageNames": ["/^org\\.jetbrains\\.kotlin/", "/^com\\.google\\.devtools\\.ksp/"] },
    { "groupName": "androidx", "matchPackageNames": ["/^androidx\\./"] },
    { "groupName": "firebase", "matchPackageNames": ["/^com\\.google\\.firebase/", "/^com\\.google\\.gms/"] },
    { "matchPackageNames": ["com.android.application"], "matchUpdateTypes": ["major"], "enabled": false }
  ]
}
```
- 매달 할 일: 봇 PR이 CI 초록이면 합치고, 기기에 업데이트 설치(`PROJECT_CONTEXT.md:159-162` 규칙대로 **지우고 다시 깔지 말고 덮어 설치**)로 하루 써 본다.

### B3. 릴리즈(배포) 경로 비교

| 경로 | 장점 | 단점 | 1인에게 |
|---|---|---|---|
| **지금 방식: Android Studio/ADB로 내 폰에 설치** | 비용 0, 개발자 인증 **면제**(ADB, A3) | 남에게 못 줌, 빌드 기록이 안 남음 | **본인 사용엔 최선, 유지** |
| **GitHub Releases에 서명 APK 첨부** | 버전별 APK가 남음(되돌리기 쉬움), 공개 저장소와 잘 맞음 | 2027년부터 남이 설치하려면 개발자 인증 필요(A3), 자동 업데이트 없음, `google-services.json`이 APK 안에 들어감(원래 공개돼도 되는 값이지만 규칙이 제대로여야 함) | 기록·백업용으로 추천 |
| **Obtainium**(GitHub Releases를 감시해 업데이트해 주는 앱) | 스토어 없이 자동 업데이트 알림 | 결국 사이드로드 → 인증 문제 동일. 사용자가 Obtainium을 깔아야 함 | 친구 몇 명에게 줄 때 |
| **F-Droid** | 오픈소스 사용자층, 무료 | Firebase·Crashlytics·Play 서비스 같은 **비자유 의존성**은 메인 저장소에 받아들여지지 않거나 '안티 기능' 표시(판단, 정책 페이지 열지 못함: https://f-droid.org/docs/Inclusion_Policy/). Firebase 없는 빌드 변형(flavor)을 따로 만들어야 → 동기화·웹 대시보드가 빠짐 | **비현실적**(철학상 동기화가 핵심 기능 중 하나) |
| **Play 내부 테스트(internal testing)** | Play가 서명·업데이트·개발자 인증을 자동 처리(Play 앱 약 99% 자동 등록, A3 FAQ), App Check Play Integrity가 자연스럽게 됨 | 개발자 계정 25달러·신원 확인, targetSdk 요구 매년 따라가야(A9), 정책 신고(정확 알람·Health Connect 등) | 다른 사람에게 줄 계획이 생기면 가장 덜 귀찮음 |

추천(판단): **지금은 ADB 설치 유지 + 버전 올릴 때마다 GitHub Releases에 서명 APK와 태그.** 다른 사람이 쓰게 되면 그때 Play 내부 테스트로. F-Droid는 하지 않는다. 키스토어 백업은 지금 바로(A3).

### B4. 테스트 전략

현재: JVM 단위 테스트 파일 13개(`app/src/test`, `@Test` 89개 — grep 개수), 기기 테스트 1개(`app/src/androidTest/.../ActivityConflictObservationTest.kt`, 메모리 Room). 상태 문서는 "단위 테스트 98개"(`IMPLEMENTATION_STATUS.md` 검증 절, 2026-09-29)라 지금 숫자와 다름 — 시험 기능 삭제(2026-09-30) 때 줄었을 가능성(확인 못 함).

1. **Room 마이그레이션 시험 (최우선)** — 효과 상, 비용 2–3시간.
   - 지금 `exportSchema = false`(`FlowlogDatabase.kt:84`), 마이그레이션 24단계(`:122`) 중 자동 시험 없음. 23→24는 SQL을 손으로 돌려 봄(`IMPLEMENTATION_STATUS.md` 검증 절).
   - 할 일: `exportSchema = true` + KSP 인자 또는 Room Gradle 플러그인 `schemaDirectory("$projectDir/schemas")`, `app/schemas/`를 git에 넣기, `room-testing`의 `MigrationTestHelper.runMigrationsAndValidate()`로 **v24부터** 시험(과거 스키마 JSON은 없으니 v24를 기준선으로). (열어 확인: https://developer.android.com/training/data-storage/room/migrating-db-versions)
   - 다음 스키마 변경 때 시험 기록 남은 정리(`PROJECT_CONTEXT.md:208-217`의 exam 잔재 삭제)를 이 시험으로 보호.
   - 기기 테스트라 CI에서 돌리려면 에뮬레이터가 필요 → 처음엔 로컬에서만, CI는 나중(판단).
2. **Firestore 규칙 시험** — 이미 `tools/study-integration/rules-test.cjs`(15개 검사) + `prepare-rules.cjs`가 있음 → B1의 `firestore-rules` 작업으로 CI에 올리면 끝. 단, 시험하는 규칙 파일이 이 저장소의 `docs/study-integration/firestore.proposed.rules`라서 **웹 저장소의 실제 규칙과 같은지**는 따로 확인해야 한다(A6).
3. **순수 로직 단위 테스트 유지** — 추천 엔진·리비전 정책은 이미 잘 돼 있음(`app/src/test/.../data/recommendation/`). 새 기능은 같은 방식(작은 순수 파일 + 테스트, README "Architecture" 설명대로).
4. **Compose 스크린샷 시험** — Google 플러그인 `com.android.compose.screenshot`은 **알파이고 AGP 9.5.0-alpha03부터 지원 중단, AGP 테스트 스위트로 이전 권장**. (열어 확인: https://developer.android.com/studio/preview/compose-screenshot-testing) → 지금 도입하면 곧 갈아타야 함. **보류 추천**, 꼭 하려면 화면 3개(홈 타이머, 오늘 기록 목록, 할 일)만.
5. 알람·알림은 자동 시험보다 **기기 점검표**(재부팅 후 알림 복원, 권한 거부 상태, 3버튼 내비게이션)가 1인에게 현실적(판단).

### B5. 모니터링 — Crashlytics 사용 현황

- `…/MainActivity.kt:163` `setCrashlyticsCollectionEnabled(!BuildConfig.DEBUG)` → **릴리즈 빌드에서만 수집**. 그런데 README의 빌드 안내는 `assembleDebug`(`README.md:288-289`)이고, 디버그 빌드도 릴리즈 키로 서명한다(`app/build.gradle.kts:55`). 사용자가 평소 디버그 빌드를 깔아 쓰면 **Crashlytics에 아무것도 안 온다**(판단 — 실제로 어떤 빌드를 쓰는지 확인 못 함). 사용자에게 물을 것: "폰에 깔린 게 debug인가 release인가?"
- 오류를 조용히 삼키는 곳이 많다: `runCatching` 256곳(grep 합계). 동기화 실패·알람 강등 같은 "앱은 안 죽지만 기능이 조용히 실패"하는 경우가 Crashlytics에 안 잡힘.
- 할 일: (1) 본인 폰에는 release 빌드를 깔거나, debug에서도 수집하도록 바꾸는 것 중 결정. (2) 핵심 경로 3곳(동기화 실패, 알람 예약 강등 `ReminderScheduler.kt:322-324` 같은 곳, Room 마이그레이션 오류 `MigrationErrorDao`)에 `recordException` + 사용자 지정 키(동기화 종류). (3) 월 1회 콘솔 확인. 비용 1–2시간.

### B6. 문서 유지 — 역할 분담 평가

`PROJECT_CONTEXT.md:9-31`에 README(현재 동작)·PROJECT_CONTEXT(방향·규칙)·CHANGELOG(이력)·상태 문서(진행 중 작업) 역할이 적혀 있다.
- **잘 되는 점**: README가 실제 코드와 맞는지 고친 기록이 있다(`CHANGELOG.md:20-27`, "no CSV export exists" 등). 과장 금지 목록(`PROJECT_CONTEXT.md:177-204`)이 구체적이다. Firestore 경로 목록을 README 한 곳에만 둔다.
- **아쉬운 점**
  1. CHANGELOG에 **버전 구역이 없다** — 모든 게 `## Unreleased` 아래(`CHANGELOG.md:3`). 0.5.9라는 버전이 본문(`:8`)에만 나온다. → `## 0.5.9 (2026-10-xx)`처럼 versionName 올릴 때 구역을 닫는다.
  2. git 태그 0개(`git tag` 결과 없음) → 어떤 커밋이 0.5.9인지 알 수 없다.
  3. 상태 문서는 날짜가 박힌 기록이라 숫자가 낡는 건 설계상 괜찮지만(테스트 98개 vs 지금 89개), 맨 위에 "이 문서는 2026-09-29 기준"을 이미 적어 둔 점은 좋다.
  4. 웹 저장소와의 경계(규칙 원본이 어디인가)가 문서에 없다(A6).
- 비용: 30분. 효과: 중(나중에 "언제부터 이랬지?"를 찾는 시간 절약).

### B7. 버전·브랜치 전략

- 현재: `main` 통합 + 작업 브랜치(`PROJECT_CONTEXT.md:35-37`), versionCode 26 / versionName 0.5.9 손으로 올림(`app/build.gradle.kts:36-37`).
- 제안(판단): (1) 기능 묶음 = 0.x 올림(0.6.0), 고침만 = 0.5.10. (2) 올릴 때 한 커밋에서 versionCode+1, versionName, CHANGELOG 구역 닫기, 태그 `v0.5.10`. (3) 릴리즈 브랜치는 만들지 않는다(1인·스토어 없음). (4) Room 스키마 버전이 바뀌는 릴리즈는 CHANGELOG에 "스키마 v24→v25" 한 줄 필수(되돌리기 불가 표시).
- 비용 0(습관), 효과: 중.

---

## C. 새 기능 아이디어 (22개)

평가 기준(판단): **철학 적합도** = "가볍게 기록하고, 확정된 데이터로 정직하게 돌아본다"에 맞는가. 기록 마찰을 줄이면 상, 확정 안 된 추정을 사실처럼 보이게 하거나 코칭에 가까우면 하. **가치** = 매일 쓰는 1인 사용자(개발자 본인) 기준. 근거 URL 표시는 맨 위 규칙과 같다.

### 한눈에 보기

| # | 아이디어 | 난이도 | 가치 | 적합도 | 비고 |
|---|---|---|---|---|---|
| C1 | 알림에서 정지·전환 + 상태 표시줄 칩(Live Update) | 소 | 상 | 상 | A2와 같은 작업 |
| C2 | 빠른 설정 타일: 마지막 활동 시작/정지 | 소 | 중 | 상 | |
| C3 | 앱 아이콘 길게 누르기 바로가기(상위 3개 분류) | 소 | 중 | 상 | **미커밋 구현 있음** |
| C4 | 위젯에서 바로 시작·정지(Glance로 재작성) | 중 | 상 | 상 | |
| C5 | 내보내기·가져오기(CSV/JSON) | 소~중 | 상 | 상 | **내보내기 미커밋 구현 있음**, 가져오기는 없음 |
| C6 | 태그 입력 UI(데이터 칸은 이미 있음) | 소 | 중 | 중 | |
| **C7** | **계획 대 실제 거울(내 예상 오차)** | 중 | 상 | 상 | **신박 1** |
| **C8** | **기록 정확도 무작위 점검(경험 표집)** | 중 | 중 | 상 | **신박 2** |
| **C9** | **어제 재구성 5분(빈 구간 정리 화면)** | 중 | 상 | 상 | **신박 3** |
| C10 | 기록 출처 표시(실시간/나중 입력/자동) | 소 | 중 | 상 | |
| C11 | 화면 꺼짐 이력으로 수면 구간 **후보** 제안 | 중~대 | 중 | 중 | 확정은 사용자 |
| C12 | Health Connect 수면·운동 연결 | 중 | 중 | 중 | minSdk 26 필요 |
| C13 | 주간 돌아보기 카드(이미지 공유) | 중 | 중 | 중~상 | 문구 규칙 필수 |
| C14 | 최근 기준선 대비(시간 예산의 순한 버전) | 소~중 | 중 | 중 | |
| C15 | NFC 태그로 시작 | 소~중 | 하~중 | 상 | 태그 구입 필요 |
| C16 | 끝난 캘린더 일정 → 기록 제안 | 중 | 중 | 중~상 | |
| C17 | Wear OS 타일(시작·정지) | 대 | 중 | 상 | 시계 필요 |
| C18 | 카운트다운에 진행 막대(ProgressStyle) | 소 | 하 | 상 | Android 16 |
| C19 | 집중 모드를 시스템 '모드'로 | 소~중 | 하 | 중 | A12 |
| C20 | 음성으로 메모·시작 | 중 | 하~중 | 중 | |
| C21 | 사진 한 장 붙이기(기기 안에만) | 중 | 하 | 중 | |
| C22 | 온디바이스 주간 요약 문장(선택 실험) | 중~대 | 하 | 하~중 | AI 원칙과 긴장 |

### 상세

**C1. 알림에서 정지·전환 + 상태 표시줄 칩**
- 한 줄: 실행 중 타이머 알림에 [정지] [최근 분류로 전환] 버튼, Android 16에선 상태 표시줄에 "공부 1:23" 칩.
- 근거: Live Update 조건·칩(열어 확인: https://developer.android.com/develop/ui/views/notifications/live-update), Android 14부터 ongoing 알림도 지워짐(열어 확인: https://developer.android.com/about/versions/14/behavior-changes-all). 지금 알림엔 버튼·지움 감지 없음(`…/notification/ActivityTimerNotifier.kt:24-49`). 자동 시작 알림엔 이미 [되돌리기] 액션 선례(`:345-364`).
- 난이도 소: 알림 빌더 + 브로드캐스트 수신기 1개, 저장 로직은 기존 ViewModel 경로 재사용(수신기에서 쓸 수 있게 저장소 함수로 빼는 정도).
- 가치 상: 앱을 열지 않고 멈추기 = 기록 마찰의 가장 큰 부분(판단). 적합도 상.
- API: `NotificationCompat.Action`, `POST_PROMOTED_NOTIFICATIONS`, `setRequestPromotedOngoing`, `setShortCriticalText`, `setDeleteIntent`.

**C2. 빠른 설정 타일**
- 한 줄: 알림창을 내려 타일 한 번 = 마지막 활동 이어 시작 / 실행 중이면 정지.
- 근거: 공식 문서(열어 확인: https://developer.android.com/develop/ui/views/quicksettings-tiles). 경쟁 앱이 위젯·Wear 타일·NFC·자동 시작을 갖춘다는 소개(검색 결과로만, 열지 못함: https://timesheet.io/en/blog/how-to-automate-time-tracking). 빠른 설정 타일을 가진 시간 기록 앱 사례는 찾지 못함.
- 난이도 소: `TileService` 하나. 잠금 화면에선 `unlockAndRun()`.
- 가치 중, 적합도 상. API: `TileService`, `StatusBarManager.requestAddTileService()`(Android 13+).

**C3. 앱 바로가기(App Shortcuts)**
- 한 줄: 아이콘 길게 누르면 "공부 시작 / 운동 시작 / 정지" 3개. 동적 바로가기 순서는 이미 있는 버튼 추천 순위(`…/data/recommendation/ButtonRecommendationEngine.kt`)를 그대로.
- 근거: 공식 문서, 런처 보통 4개까지(열어 확인: https://developer.android.com/develop/ui/views/launch/shortcuts). F-Droid 시간 기록 앱이 "quick actions"를 제공(검색 결과로만: https://f-droid.org/ko/packages/de.killi199.timetracking/).
- 난이도 소. 가치 중. 적합도 상. API: `ShortcutManagerCompat`, 정적 `shortcuts.xml`.
- **상태**: 작업 트리에 미커밋 구현 있음 — `…/shortcut/TimerShortcutPublisher.kt`(메인 버튼 앞쪽 분류로 동적 바로가기, 최대 4개 `TimerShortcutRules.kt:12`). 이 조사에서는 검토하지 않았다.

**C4. 위젯에서 바로 시작·정지 (Glance)**
- 한 줄: 지금 위젯(누르면 앱 열기만, `…/widget/FlowStatusWidgetProvider.kt:94`)을 버튼 있는 위젯으로. 정지 + 추천 분류 2개.
- 근거: Glance 1.2.0 안정, 생성 미리보기(열어 확인: https://developer.android.com/jetpack/androidx/releases/glance). 오픈소스 Simple Time Tracker가 위젯·백업을 기본으로 제공(검색 결과로만: https://f-droid.org/packages/com.razeeman.util.simpletimetracker).
- 난이도 중: 지금 위젯은 비트맵을 직접 그리고 AlarmManager로 갱신(`:247-271`, `:288-293`) → Glance로 다시 짜야 함. 또는 RemoteViews 그대로 버튼만 추가(소)도 가능.
- 가치 상, 적합도 상. API: Glance `actionRunCallback`, 또는 `RemoteViews.setOnClickPendingIntent`.

**C5. 내보내기·가져오기 (CSV/JSON)**
- 한 줄: 설정에서 "내 기록 내보내기" → 파일 선택 화면으로 CSV(표 계산용)·JSON(완전 백업) 저장, JSON 가져오기.
- 근거: README에서 "CSV 내보내기 없음"을 바로잡은 기록(`CHANGELOG.md:22-24`) = 사용자가 한때 기대했던 기능. 웹에는 본인 데이터 내보내기가 있음(`IMPLEMENTATION_STATUS.md` 검증 절) → 로그인 안 한 사용자·오프라인 사용자는 못 씀. Simple Time Tracker가 CSV·ICS 내보내기, 자동 백업 제공(검색 결과로만: https://github.com/pipe01/Android-SimpleTimeTracker).
- 난이도 소~중: 내보내기는 소, 가져오기는 중(중복·리비전 충돌 처리 — 기존 `IMPORTED` 출처 상수 `…/data/constants/ActivitySourceType.kt` 활용).
- 가치 상: 기록 앱의 신뢰 = "언제든 가지고 나갈 수 있다"(판단). 적합도 상.
- API: Storage Access Framework(`ActivityResultContracts.CreateDocument`/`OpenDocument`), kotlinx.serialization(이미 있음).
- **상태**: 내보내기는 작업 트리에 미커밋 구현 있음(`…/ui/viewmodel/ActivityExportFormatter.kt` + 테스트). 남은 것은 **가져오기**와, 웹 내보내기와 형식 맞추기(D-3).

**C6. 태그 입력 UI**
- 한 줄: 기록에 자유 태그(예: "#과제A")를 붙이고 통계에서 태그별 합계.
- 근거(코드): 모델·DB·동기화에 칸이 이미 있음 — `…/data/model/ActivitySession.kt` `tags`, `ActivityEntity.kt:34` `tagsJson`, `FirebaseRestoreDataSource.kt:149` 복원. 그런데 저장 경로는 모두 `tags = emptyList()`(`…/ui/viewmodel/ActivityViewModel.kt:688,1111,1266,1334,1437`) → **UI만 없음**.
- 난이도 소. 가치 중. 적합도 중: 입력 칸이 늘면 기록이 무거워짐 → 기본 숨김, 최근 태그 칩만.
- API: 없음(Compose).

**C7. 계획 대 실제 거울 — 신박 1**
- 한 줄: 할 일·추천 블록에 잡았던 **계획 시간**과 실제로 연결된 **기록 시간**을 나란히 쌓아, "내 예상은 보통 실제의 0.6배"처럼 **내 예상 오차**만 보여 준다. 조언·점수 없음.
- 근거: 계획 오류(planning fallacy) — 졸업논문 학생들의 평균 예상 33.9일, 실제 55.5일, 예상 안에 끝낸 비율 약 30%(Buehler 외 1994). 과거 비슷한 일의 실제 결과로 예측하는 "참조 집단 예측(reference class forecasting)"이 교정 방법으로 제시됨(열어 확인: https://en.wikipedia.org/wiki/Planning_fallacy). 원 논문 PDF는 열지 못함(검색 결과로만: https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf).
- 데이터는 이미 있음(코드): 추천 블록의 `plannedStartMillis`·`plannedEndMillis`·`recommendedDurationMinutes`(`…/data/model/TodoItem.kt:38-40`), 할 일의 실제 누적 `accumulatedSeconds`(`:17`), 기록의 `linkedTodoId`.
- 왜 신박한가: 보통 시간 기록 앱은 "얼마나 썼나"를 보여 준다. 이건 **"내가 시간을 얼마나 잘 예상하나"**를 기록으로 정직하게 보여 준다 — 사용자의 다음 계획을 바꾸는 건 사용자 몫. 과장 없이 "확정 데이터로 돌아보기"를 한 단계 더 미는 기능(판단). 이 저장소(proviso)의 agent_usage가 하는 "예측 → 실측 → 오차"와 같은 고리라는 점도 흥미롭다.
- 난이도 중: 계산은 쉬움, 표본이 적을 때 숫자를 숨기는 기준(예: 짝 10개 미만이면 "아직 모름")과 화면 설계가 일.
- 가치 상, 적합도 상(단, "개선해 드립니다" 문구 금지).
- API: 없음(Room 쿼리 + Compose).

**C8. 기록 정확도 무작위 점검 (경험 표집) — 신박 2**
- 한 줄: 하루 0~1번, 무작위 시각에 "지금 Flowlog에 '공부'로 기록 중이에요. 맞나요? [맞아요] [아니에요→바로 전환]". 응답이 쌓이면 "기록 일치율 87% (최근 30회)"를 통계 옆에 작게.
- 근거: 경험 표집법(ESM) — 그 순간에 묻기 때문에 회상 오류를 피한다, 대신 응답 부담이 있다(열어 확인: https://en.wikipedia.org/wiki/Experience_sampling_method). 하루를 다음 날 재구성하는 방법(DRM)은 합계 수준에선 ESM과 맞지만 개인 안의 차이는 덜 맞는다는 후속 연구(검색 결과로만: https://pubmed.ncbi.nlm.nih.gov/15576620/, https://pmc.ncbi.nlm.nih.gov/articles/PMC2990978).
- 왜 신박한가: 시간 기록 앱은 기록이 정확하다고 **가정**한다. 이건 앱이 자기 데이터의 정확도를 **재서 보여 준다**. "정직하게 돌아본다"를 데이터 품질에까지 적용(판단). 틀렸을 때 바로 고칠 수 있으니 기록 품질도 올라간다.
- 난이도 중: 무작위 시각 알림(부정확 알람 `setWindow`로 충분 — A1과 맞음), 응답 저장, 비율 표시.
- 가치 중: 부담이 있으니 **기본 꺼짐**, 켜는 사람만. 적합도 상.
- API: `AlarmManager.setWindow`, 알림 액션.

**C9. 어제 재구성 5분 — 신박 3**
- 한 줄: 아침 첫 실행 때 한 번, 어제 타임라인에서 **빈 구간·1분짜리 기록·겹친 기록**만 모아 카드로 보여 주고 "채우기 / 그대로 두기 / 수면으로"를 한 손으로 처리. 처리 안 한 빈 구간은 통계에서 "기록 없음"으로 정직하게 남긴다.
- 근거: 하루 재구성법(Day Reconstruction Method) — 전날을 구조적으로 되짚어 회상 편향을 줄이고 응답 부담이 ESM보다 낮다(검색 결과로만: https://pubmed.ncbi.nlm.nih.gov/15576620/, 문서 https://m3ewb-research.media.uconn.edu/wp-content/uploads/sites/3234/2024/01/drm_documentation_july_2004.pdf). 개인 기록 연구에서 "수집 → 통합 → 돌아보기 → 행동" 단계마다 장벽이 있다는 모델(검색 결과로만: https://courses.cs.washington.edu/courses/cse440/15au/readings/PersonalInformatics-Li2010.pdf). Flowlog엔 이미 "빈 구간을 수면으로 채우기"(`…/ui/screen/SleepFillDialog.kt`, `SleepFillUtils.kt`)가 있음 → 그 일반화.
- 왜 신박한가: 대부분의 앱은 빈 구간을 그냥 두거나(통계가 조용히 틀림) 자동으로 채운다(추정이 사실처럼 보임). 이건 **사용자가 확정하게 만들되 5분 안에 끝나게** 설계 — "확정된 데이터" 원칙을 지키면서 기록 누락을 줄이는 중간 길(판단).
- 난이도 중. 가치 상. 적합도 상.
- API: 없음(Compose + 기존 타임라인 유틸 `…/ui/screen/TimetableActivityUtils.kt`).

**C10. 기록 출처 표시**
- 한 줄: 통계에 "실시간 타이머 72% · 나중에 입력 20% · 자동 시작 8%", 기록 상세에 "웹에서 수정됨" 같은 표시.
- 근거(코드): 출처가 이미 저장됨 — `ActivitySourceType`(`TIMER`, `MANUAL`, `AUTO_BUTTON`, `DAILY_CUE_*`, `STUDY_PLAN`, `IMPORTED`), `originalCategory`, `remoteRevision`(`…/data/model/ActivitySession.kt`). 자기 기록 데이터는 사람의 맥락 없이는 의미가 약하다는 비판(열어 확인: https://en.wikipedia.org/wiki/Quantified_self).
- 난이도 소. 가치 중. 적합도 상. API: 없음.

**C11. 화면 꺼짐 이력으로 수면 구간 후보**
- 한 줄: 밤사이 화면이 가장 오래 꺼져 있던 구간을 "수면 후보 23:40–07:10?"으로 제안, 누르면 확정.
- 근거: 화면 켜짐·꺼짐만으로 수면 시간 평균 오차 7%(14명, 스마트워치 기준)라는 소규모 연구, 반면 수면 일기 기준 178분 오차였다는 2023 논문도 있음 → **정확도 편차가 큼**(검색 결과로만: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6547769/, https://www.scitepress.org/Papers/2023/118951/118951.pdf).
- 난이도 중~대: `PACKAGE_USAGE_STATS`(사용 정보 접근, 사용자가 설정에서 직접 허용하는 특수 권한)와 `UsageEvents` 화면 이벤트 — 해당 API 상세 페이지는 끝까지 읽지 못함(확인 못 함). Play 정책상 이 권한은 까다로움(판단).
- 가치 중, 적합도 중: 추정치를 **후보로만** 보여 주고 확정은 사용자. C9의 입력 중 하나로 쓰면 가장 자연스럽다.

**C12. Health Connect 수면·운동**
- 한 줄: (읽기) 워치가 잰 수면 세션을 수면 기록 후보로, (쓰기) Flowlog 운동 타이머·세트를 `ExerciseSessionRecord`로 내보내 다른 건강 앱과 공유.
- 근거: 열어 확인(https://developer.android.com/health-and-fitness/health-connect/get-started, https://developer.android.com/health-and-fitness/health-connect/data-types). SDK minSdk 26, 개인정보처리방침 액티비티 필수, 권한 부여 30일 이전 기록은 추가 권한.
- 난이도 중: minSdk 24→26 결정(사용자 판단), 권한 화면, 매핑. 가치 중(워치 사용 여부에 달림). 적합도 중(남이 잰 데이터 = '확정'인가? 후보로 보여 주면 상).

**C13. 주간 돌아보기 카드(이미지 공유)**
- 한 줄: 일요일 밤 "지난 7일 확정 기록: 공부 14시간(지난주보다 +2) …" 카드 1장, 이미지로 저장·공유.
- 근거: 직접 찾은 공식·연구 근거 없음(판단). 철학 문서의 권장 문구("최근 리듬 확인", "확정된 기록 기반 통계", `PROJECT_CONTEXT.md:195-204`)를 그대로 쓰면 과장 위험을 막을 수 있음.
- 난이도 중(Compose → 비트맵, 공유 시트). 가치 중. 적합도 중~상.
- API: Compose `GraphicsLayer` 캡처, `Intent.ACTION_SEND`, `FileProvider`.

**C14. 최근 기준선 대비 (시간 예산의 순한 버전)**
- 한 줄: 목표를 정하라고 하지 않고, 분류별로 "지난 4주 평균 대비 이번 주"만 막대로. 원하는 사람만 주간 목표 숫자를 적을 수 있게.
- 근거: aTimeLogger가 목표 기능을 제공(검색 결과로만: https://apps.apple.com/us/app/atimelogger-daily-time-tracker/id1087340819). 앱에 이미 7일 평균 비교가 있음(`README.md:55-56`).
- 난이도 소~중. 가치 중. 적합도 중(목표 강요는 코칭에 가까움 → 기준선 비교가 기본).

**C15. NFC 태그로 시작**
- 한 줄: 책상·헬스장 입구에 붙인 태그에 폰을 대면 해당 분류 타이머 시작/정지.
- 근거: 공식 NFC 문서(열어 확인: https://developer.android.com/develop/connectivity/nfc/nfc), NFC·와이파이·위치로 자동 시작하는 경쟁 앱(검색 결과로만: https://timesheet.io/en/blog/how-to-automate-time-tracking), NFC로 상태 전환하는 F-Droid 앱(검색 결과로만: https://f-droid.org/ko/packages/de.killi199.timetracking/).
- 난이도 소~중: AAR + 커스텀 스킴 URI(`flowlog://start?category=STUDY`), Android 16의 첫 태그 알림, Android 17 대상 시 `DISPATCH_NFC_MESSAGE` 보호. 태그에 쓰는 화면도 필요.
- 가치 하~중(태그를 사야 함), 적합도 상(마찰 최소화, 사용자가 직접 대는 행동 = 확정).

**C16. 끝난 캘린더 일정 → 기록 제안**
- 한 줄: 캘린더 일정이 끝났는데 그 시간에 기록이 없으면 "회의 14:00–15:00 기록할까요?" 한 번.
- 근거(코드): 웹에서 만든 일정은 이미 앱으로 당겨옴(`…/data/sync/FirebaseCalendarPullDataSource.kt`, `README.md:174-175`) → 기기 캘린더 권한 없이 웹 일정부터 시작 가능. 기기 캘린더까지는 `READ_CALENDAR`.
- 난이도 중. 가치 중. 적합도 중~상(계획을 사실로 바꾸지 않고 묻기만).

**C17. Wear OS 타일**
- 한 줄: 시계 타일에서 현재 타이머 보기·정지·최근 분류 시작.
- 근거: 공식 문서(열어 확인: https://developer.android.com/training/wearables/tiles), Simple Time Tracker가 Wear OS 앱·컴플리케이션 제공(검색 결과로만: https://f-droid.org/packages/com.razeeman.util.simpletimetracker).
- 난이도 대: 새 `wear` 모듈, 폰-시계 데이터 전달, 실기기 필요. 가치 중(시계가 있을 때만). 적합도 상.

**C18. 카운트다운 진행 막대 (ProgressStyle)**
- 한 줄: 식사·양치 카운트다운 알림을 Android 16 진행 막대 알림으로.
- 근거: 열어 확인(https://developer.android.com/about/versions/16/features). 코드 `ActivityTimerNotifier.kt:280-310`.
- 난이도 소. 가치 하. 적합도 상. API: `Notification.ProgressStyle`(API 36).

**C19. 집중 모드를 시스템 '모드'로**
- 한 줄: 집중 세션 동안 시스템 설정의 "Flowlog 집중" 모드가 켜지고, 예외(연락처 등)는 사용자가 시스템에서 고름.
- 근거: Android 15 DND 변경(열어 확인: https://developer.android.com/about/versions/15/behavior-changes-15). 코드 `…/notification/FocusDndController.kt:37-47`.
- 난이도 소~중. 가치 하(지금도 동작). 적합도 중.

**C20. 음성으로 메모·시작**
- 한 줄: 타이머 카드 마이크 버튼 → "수학 과제" 말하면 제목 입력.
- 근거: ML Kit GenAI에 음성 인식(온디바이스) 포함(열어 확인: https://developer.android.com/ai/gemini-nano), 지원 기기·한국어 여부 확인 못 함. 대안: 기본 `SpeechRecognizer`/`RecognizerIntent`(문서 미열람).
- 난이도 중. 가치 하~중(제목 추천이 이미 마찰을 줄임 — `ActivityTitleSuggestionRanker`). 적합도 중.

**C21. 사진 한 장 붙이기**
- 한 줄: 운동·공부 기록에 사진 1장(필기 사진 등), 기기 안에만 저장.
- 근거: 직접 찾은 근거 없음(판단). Firestore 무료 할당은 문서 수 기준이라 사진은 Cloud Storage가 따로 필요(요금 페이지 열어 확인: https://cloud.google.com/firestore/pricing) → 동기화 범위 밖으로 두는 게 현실적.
- 난이도 중. 가치 하. 적합도 중(기록이 무거워짐). API: Photo Picker(권한 불필요, 문서 미열람).

**C22. 온디바이스 주간 요약 문장 (선택 실험)**
- 한 줄: 지난주 메모들을 기기 안 모델로 3줄 요약. 기본 꺼짐, 실패하면 숨김.
- 근거: Gemini Nano + ML Kit GenAI 요약(열어 확인: https://developer.android.com/ai/gemini-nano). 지원 기기 범위 확인 못 함. `PROJECT_CONTEXT.md:164-175` "AI는 로컬 규칙 위의 선택적 보조, AI를 이유로 마케팅하지 않음".
- 난이도 중~대. 가치 하. 적합도 하~중(요약은 '해석'이 들어가 확정 데이터와 거리가 있음).

### 지시서의 씨앗 중 넣지 않은 것과 이유
- **포모도로**: 집중 세션이 이미 있음(`README.md:61`). 효과 근거도 엇갈림 — 25명/35명 학생 비교에서 과제 완료 차이 없음, 2025 리뷰는 좁은 범위(열어 확인: https://en.wikipedia.org/wiki/Pomodoro_Technique). 집중 세션에 "25/5 프리셋" 하나 추가 정도(소)로 충분.
- **멀티 타이머**: 학교·회사 고정 타이머의 겹침이 이미 있음(`CHANGELOG.md:144`). 일반 멀티 타이머는 "지금 무엇을 하나"라는 단일 기록 모델을 흐림(판단).
- **와이파이/위치로 자동 분류**: 상태 문서가 "위치 수집은 별도 후속 단계"로 보류(`IMPLEMENTATION_STATUS.md:17`). 와이파이 이름 읽기도 위치 권한이 필요(판단, 문서 미열람). C9·C16처럼 "묻기"형이 먼저.
- **데스크톱 위젯**: 웹 대시보드 영역(D절).

---

## D. 웹 대시보드 방향 (README 기준, 웹 코드는 보지 않음)

근거는 `README.md:20-25`(역할), `:72-93`(웹 페이지 목록), `:144-194`(동기화), `PROJECT_CONTEXT.md:108-129`(역할)뿐이다. 웹 저장소(pfkfks-main)는 이 환경에 없어 확인 못 함.

### 역할 분담이 맞는가
- 정해진 원칙: **앱 = 기록하는 곳, 웹 = 동기화된 기록을 돌아보는 동반자**(`README.md:24-25`), "앱은 웹 없이도 쓸모 있어야 한다"(`PROJECT_CONTEXT.md:119`). 이 원칙은 명확하고 좋다.
- 그러나 실제로는 웹이 **기록 수정**도 한다: 활동 블록 제목·메모·시간·분류 수정(`README.md:79-81`) → 앱과 동시에 고치면 충돌 화면(`README.md:177-182`, `PROJECT_CONTEXT.md:151-157`). 공부 연결은 **웹에서만** 편집(`README.md:183-186`). 즉 "웹은 보기만"이 아니라 "웹은 긴 기간 보기 + 정리·계획 도구"가 실제 역할. 문서의 한 줄 정의를 실제에 맞게 고치는 게 좋다(판단).

### 겹치는 것
| 기능 | 앱 | 웹 |
|---|---|---|
| 오늘·최근 분류 합계 | 오늘 합계, 어제 비교, 7일 평균(`README.md:55-56`) | 최근 이력·분류 합계(`:78`) |
| 활동 기록 수정 | 있음 | 있음(충돌 처리 필요) |
| 달력·일정 | 웹 일정을 당겨와 표시(`:174-175`) | 강의계획서 → 일정, ICS 내보내기(`:86-88`) |
| Daily Cues | 체크(기록) | 주간 완료 추적(`:89`) |

### 웹에만 있어 아쉬운 것 (폰에서 못 보는 것)
1. **긴 기간 추세**: 기록 일수가 쌓이면 열리는 추세(`README.md:78-79`), 분류별 시간 추세(`/activities/`, `:90`).
2. **운동 종목별 세트·반복 추세**(`/statistics/exercise/`, `:85`) — 운동 세트는 폰에서 기록하는데 추세는 웹에서만.
3. **Daily Cues 주간 완료표**(`:89`).
4. **하루 한 번 컨디션 체크인**(의욕·에너지·졸림, `:81-84`) — 웹 통계 페이지 팝업이라 웹을 안 여는 날은 빠진다. 이런 짧은 순간 응답은 폰 알림이 더 맞는 자리(판단, C8과 같은 이유).
5. **내 데이터 내보내기**(`IMPLEMENTATION_STATUS.md` 검증 절의 "본인 데이터 내보내기") — 로그인 안 한 사용자는 불가.
6. 짧은 기록(10분 미만)은 바로 올라가지 않아(`README.md:164-168`) 웹에 늦게 보임 → 웹에서 "이 화면은 언제까지의 기록인지"가 중요(`PROJECT_CONTEXT.md:127-129`, 열린 질문 `:227-228`).

### 추천 (판단)
1. **보기 전용 추세 2개를 폰으로**: "분류별 최근 4주 추세"와 "운동 종목 추세". 데이터가 Room에 이미 있고 계산은 순수 함수(`AnalyticsActivityUtils.kt` 방식)로 가능. 웹은 더 긴 기간·편집·계획 도구로 남긴다. "앱은 웹 없이도 쓸모 있어야 한다" 원칙을 실제로 채움.
2. **편집 창구를 더 늘리지 않는다**: 웹 수정은 충돌 처리라는 비싼 장치가 필요했다. 새 편집 기능은 한쪽(대부분 앱)에만 둔다. 공부 연결처럼 화면이 커야 하는 편집만 웹.
3. **내보내기는 앱에도**(C5) — 웹과 같은 형식(JSON 스키마)을 쓰면 두 곳 결과를 비교·검증할 수 있다.
4. **컨디션 체크인은 실험이 끝나면 위치를 다시 정한다**: 계속할 거면 폰 알림 1회(기본 꺼짐)로, 웹은 결과 보기만.
5. **웹 화면마다 "기준 시각" 표시**: "어제까지 확정된 기록 · 마지막 동기화 10/20 09:12". 동기화 지연(10분 규칙)으로 생기는 "왜 안 보이지?"를 없앰.
6. **규칙 원본 한 곳**(A6) — 웹 저장소가 원본, 이 저장소는 사본+시험이라고 양쪽 문서에 적기.
7. 관리자 전용 도우미(`/assistant`)와 `assistantSnapshots`(`README.md:188-194`)는 공개 문구에 넣지 않는 현재 방침 유지(`PROJECT_CONTEXT.md:87`).

---

## E. 로드맵 초안 (2026-10-20 기준)

원칙(판단): **안전망 → 매일 느끼는 불편 → 작은 진입점 → 데이터가 쌓여야 의미 있는 기능 → 큰 확장** 순.

### 0–3개월 (~2027-01)
| 순서 | 항목 | 왜 이 순서 |
|---|---|---|
| 1 | 키스토어 PC 밖 백업, `gradlew` 실행 권한 고정(A3, B1) | 10분짜리인데 잃으면 되돌릴 수 없다(키 분실 = 패키지 재등록 불가). |
| 2 | CI: 단위 테스트 + 규칙 시험(B1) | 이후 모든 변경의 안전망이라 맨 앞. |
| 3 | Room 스키마 내보내기 + v24 기준 마이그레이션 시험(B4) | 다음 스키마 변경(시험 기능 잔재 삭제, `PROJECT_CONTEXT.md:208-217`) 전에 있어야 의미가 있다. |
| 4 | 정확 알람 정리: 매 실행 권한 요청 제거, 자정 동기화 WorkManager로, 권한 변경 수신기(A1) | 사용자가 앱을 열 때마다 겪는 불편 + 배터리. |
| 5 | 타이머 알림 정지 버튼·지움 감지·Live Update(A2, C1) | 기록 마찰을 가장 크게 줄이는 작은 작업. 4번과 같은 알림 코드라 이어서. |
| 6 | Dependabot + lifecycle 통일 + Room 2.8 + credentials 1.6 + 로그아웃 시 자격 상태 지우기(B2, A4, A5) | CI가 생긴 뒤라야 갱신 PR을 안심하고 합칠 수 있다. |
| 7 | CHANGELOG 버전 구역·태그, Crashlytics debug/release 결정(B5–B7) | 위 변경들을 0.6.0으로 묶어 처음으로 "버전"을 남길 시점. |
| 8 | release APK로 16KB 정렬 한 번 확인(A10) | 5분짜리, 2027-02-01 기한 전에. |

### 3–6개월 (~2027-04)
| 순서 | 항목 | 왜 이 순서 |
|---|---|---|
| 9 | 가져오기 JSON(C5; 내보내기는 미커밋 구현 있음 → 먼저 검토·커밋) | 데이터 소유권. 이후 기능 실험 전에 "빠져나갈 길"을 먼저. |
| 10 | 빠른 설정 타일(C2; 바로가기 C3은 미커밋 구현 있음) | 알림(5번)·바로가기와 같은 "시작·정지" 로직을 재사용하는 작은 진입점. |
| 11 | 위젯 버튼(C4) | 진입점 중 가장 큰 작업이라 10번 뒤. RemoteViews 버튼 추가(소)부터, Glance 전환은 필요할 때. |
| 12 | 어제 재구성 5분 + 기록 출처 표시(C9, C10) | 진입점이 늘어 기록이 쌓인 뒤, 빈 구간을 정직하게 정리하는 화면. |
| 13 | 백업 규칙 결정 + 증분 복원 + 규칙 원본 위치 문서화(A6, A7, D-6) | 기기 바꿈·데이터 증가 전에. 사용자 판단 필요한 항목(무엇을 백업할지)이라 시간 여유를 둠. |
| 14 | 폰에서 4주 추세·운동 추세 보기(D-1) | 웹 없이도 쓸모 있는 앱 원칙. 12번의 정리된 데이터 위에서. |

### 6–12개월 (~2027-10)
| 순서 | 항목 | 왜 이 순서 |
|---|---|---|
| 15 | 계획 대 실제 거울(C7) | 계획·실제 짝이 몇 달 쌓여야 숫자가 의미 있다. 표본 적으면 "아직 모름". |
| 16 | 기록 정확도 무작위 점검(C8, 기본 꺼짐) | 15번과 같은 "내 데이터의 질" 화면에 함께. 응답 부담이 있어 선택 기능. |
| 17 | 배포 방식 결정: 남에게 줄 거면 제한 배포 계정 또는 Play 내부 테스트(A3, B3) | 2027년 전 세계 개발자 인증 확대 전. 본인만 쓰면 생략. |
| 18 | API 37(Android 17) 대상으로 올리기 준비(A9) | 2027년 여름 Play 요구가 올 가능성(관례 기반 추정). 영향 항목은 작음. |
| 19 | Health Connect(C12) — minSdk 26 결정과 함께 | 사용자 판단(minSdk 상향, 워치 사용 여부)이 먼저 필요. |
| 20 | Material 3 Expressive 적용 검토 | material3 1.5 안정판 이후. 기능이 아니라 겉모습이라 뒤로. |
| 21 | Wear OS 타일(C17), NFC(C15) | 기기·태그가 있을 때만 의미. 가장 큰/선택적 확장이라 마지막. |

넣지 않은 것: 온디바이스 AI 요약(C22)·사진(C21)·음성(C20) — 철학 적합도나 가치가 낮아 사용자 요청이 있을 때.
