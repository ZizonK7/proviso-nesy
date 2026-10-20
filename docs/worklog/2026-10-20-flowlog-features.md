# 2026-10-20 — Flowlog 기능 3개 구현 (직접 추가 · 내보내기 · 바로가기)

에이전트: 기능 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상은 사용자 앱 Flowlog(`/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`)다. 작업 트리의 파일만 고쳤다. 사용자용 설명(기능별 쓰는 법, 철학과의 관계)은 저장소 밖 `/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/reports/06-features-implemented.md`에 있다. 여기에는 다음 작업자가 이어받는 데 필요한 것만 적는다.

## 한 일
- **A. 지난 활동 직접 추가.** 먼저 코드를 확인했다. `insertActivity`를 부르는 곳은 타이머, 자동 버튼, 루틴, 그리고 시간표 빈칸을 수면으로 채우는 `saveSleepActivity`뿐이었다. 일반적인 손 입력 경로는 없었다. 그래서 만들었다.
  - `ui/viewmodel/ManualActivityValidator.kt`(새 파일, 순수 로직): 막는 오류는 끝 ≤ 시작, 24시간 초과, 미래 세 가지다. 겹침은 막지 않고 경고로 돌려준다. `resolveTimes`는 끝 시각이 시작보다 이르면 다음 날로 본다(같으면 길이 0 → 오류).
  - `ActivityViewModel.addManualActivity`: 타이머 정지 저장과 같은 뒤처리를 따른다.
    - 따른 것: insertActivity(Room PENDING + `ACTIVITY_SAVED` 이벤트 로그), 되돌리기 칸, `ensureTodayTimePlan`, 10분 이상이면 즉시 동기화. `sourceType = MANUAL`.
    - 뺀 것과 이유: 양치 알림(이미 끝난 식사). 비활동 알림은 타이머가 없고 마지막 활동보다 늦게 끝났을 때만 옮긴다. 위젯 갱신은 추천 관찰 코드가 이미 부른다.
  - `ui/screen/home/ManualActivitySection.kt`(새 파일): 다이얼로그. 기존 부품을 다시 썼다.
    - 카테고리 칩(`EditCategoryPicker`): `EditActivityDialog.kt`에서 `private` → `internal`로 바꿨다. 입력칸 색 함수(`editTextFieldColors`)도 같이 바꿨다.
    - 시각 선택 시트 `TimePickerSheet`, 제목 추천 `buildTitleSuggestions`, Material3 `DatePickerDialog`.
  - `RecentRecordsSection.kt`: "직접 추가" 버튼. `HomeScreen.kt`: 연결과 토스트.
- **B. 기록 내보내기.**
  - `ui/viewmodel/ActivityExportFormatter.kt`(새 파일, 순수 로직): CSV(지시서 열 11개, 지역 시각 ISO 8601, RFC 4180 이스케이프, CRLF)와 JSON(`ActivitySession` 직렬화), 기본 파일 이름.
  - `ActivityViewModel.exportActivities`: `repository.getAllActivities().first()`로 읽는다. 이 경로는 DAO에서 `isDeleted = 0`과 현재 계정으로 거른다. `contentResolver.openOutputStream(uri, "wt")`로 쓴다.
  - `MainActivity.kt` 설정 창: "기록 내보내기" 묶음, `CreateDocument` 런처 2개, 성공·실패 토스트. 설정 창 Column에 세로 스크롤도 붙였다.
  - **지시서 밖**: CSV 앞에 UTF-8 BOM을 붙였다(엑셀 한글 깨짐 방지).
- **C. 앱 바로가기.**
  - `shortcut/TimerShortcutRules.kt`(새 파일, 순수 로직): 메인 버튼 순서대로 앞 4개 카테고리를 고른다. 인텐트는 정확한 action + 알려진 카테고리일 때만 받고, 최근 앱 목록에서 다시 연 인텐트는 무시한다.
  - `shortcut/TimerShortcutPublisher.kt`(새 파일): `ShortcutManagerCompat.setDynamicShortcuts`로 등록한다. 아이콘은 카테고리 색 바탕에 기존 흰색 `ic_activity_*`를 그린 adaptive bitmap이다.
  - `MainActivity.kt`:
    - 인텐트를 `onCreate`(savedInstanceState가 null일 때만)와 `onNewIntent`에서 받는다.
    - 화면 쪽에서 한 번 소비한다. 타이머가 이미 돌고 있으면 시작하지 않고 토스트로 알린다. 아니면 기존 `startActivity(category)`를 부른다.
    - 메인 버튼 설정이 바뀌면 바로가기를 다시 등록한다.
- 문서:
  - `README.md`: Features 3항목, Architecture에 `shortcut/`. README에는 "CSV 내보내기 없음" 문장이 이미 없었다. 그 말은 CHANGELOG의 과거 항목에만 있어서 그대로 두었다.
  - `CHANGELOG.md`: Unreleased 맨 위에 3항목.
  - `strings.xml`: 새 문구 31개.
  - 버전은 그대로(0.5.9 / 26).
- 바뀐 파일(`git diff --stat`): 수정 8개, 332줄 추가, 7줄 삭제.
  - 수정: CHANGELOG.md, README.md, MainActivity.kt, EditActivityDialog.kt, HomeScreen.kt, RecentRecordsSection.kt, ActivityViewModel.kt, strings.xml.
  - 새 파일(untracked) 8개: 위 순수 로직·UI·바로가기 5개와 테스트 3개(`ManualActivityValidatorTest` 11개, `ActivityExportFormatterTest` 9개, `TimerShortcutRulesTest` 5개).
- **후속 1회차** (메인 지시, 같은 규칙):
  - `MainActivity.kt` `HeaderActions`: 로그아웃 상태에서 "로그인" 버튼 옆에 톱니 `IconButton`(`Icons.Filled.Settings`, 설명 문구 `main_activity_settings`)을 두었다. 누르면 `showSettingsDialog = true`.
    - 설정 창 항목(알림 소리, 비활동 알림, 시간표 추천 2개, 방해 금지 권한, 기록 내보내기)에는 원래 로그인 조건이 없어서 그대로 다 보인다.
    - 개발자 메뉴는 설정 창이 아니라 프로필 드롭다운에 있고, 로그인했을 때만 뜨는 기존 조건 그대로다.
  - 직접 추가 저장 토스트: 시작 시각이 오늘이 아니면 "M월 d일 기록에 저장했어요."로 날짜를 알린다(`HomeScreen.kt`). 오늘이면 기존 문구.
    - 날짜 판정은 `ManualActivityValidator.isSameLocalDay`(순수 함수, 테스트 1개 추가).
    - 새 문구 2개: `manual_activity_saved_on_date`, `manual_activity_saved_date_format`.
  - README 내보내기 줄과 CHANGELOG 내보내기 항목에 비로그인 진입점을 반영했다.

## 확인한 것 (어떻게)
- 환경: `ANDROID_HOME=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/android-sdk`, `cd /home/user/Flowlog`.
- 메인이 먼저 돌린 `logs/unit-tests.log`: 테스트까지 가지 못했다. KSP 플러그인을 못 받아 `BUILD FAILED`, `EXIT=1`.
- 내가 다시 돌린 기준선(고치기 전), `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL, **89개 통과, 실패 0**.
  - 처음 두 번은 Maven Central `429 Too Many Requests`로 실패했다. 그래서 실패하면 45초 쉬고 다시 시도하는 감싸개를 썼다: `scratchpad/bin/gradle-retry.sh`(저장소 밖).
- 최종 결과:
  - `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL, `e:` 0줄. 바뀐 파일에서 새 경고도 없었다.
  - `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. `app/build/test-results/testDebugUnitTest/*.xml` 합계: **16개 묶음, 114개, 실패 0, 오류 0, 건너뜀 0**(기존 89 + 새 25).
- **후속 1회차**:
  - `bash ./gradlew :app:compileDebugKotlin -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL, `e:` 0줄.
  - `bash ./gradlew :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL, **115개, 실패 0, 오류 0**(같은 날짜 판정 테스트 1개 추가).
  - `git diff --stat`: 수정 8개, 372줄 추가, 16줄 삭제. untracked 새 파일 8개는 변화 없음.
  - 톱니 버튼 표시와 토스트 문구는 기기에서 확인하지 못했다.
- 새 코드에 개인정보·비밀값이 없는지 grep으로 훑었다. 계정 식별자·이메일·키는 없다.

## 확인 못 한 것
- 기기·에뮬레이터에서 실행한 것이 없다. 다음은 모두 확인하지 못했다:
  - 다이얼로그 모양.
  - AlertDialog 위에 시각 선택 시트(ModalBottomSheet)가 겹쳐 뜨는지.
  - DatePicker 동작.
  - 파일 저장 창과 실제 파일 쓰기.
  - 엑셀에서 BOM이 붙은 CSV가 어떻게 열리는지.
  - 런처 바로가기 표시와 아이콘.
  - 바로가기 인텐트 수신(콜드 스타트, 이미 열린 상태).
  - 타이머가 돌 때의 토스트.
- `assembleDebug`(APK 빌드), lint는 돌리지 않았다.

## 알려진 문제
- (후속 1회차에서 해결) 비로그인 사용자의 내보내기 진입점, 어제 이전 날짜 저장 위치 안내.
- "최근 기록" 목록은 여전히 오늘 시작한 기록만 보여 준다. 다만 저장 토스트가 날짜를 알려 준다.
- 운동을 세트 없이 직접 넣을 수 있다. 하지만 기존 `EditActivityDialog`는 운동 기록을 고칠 때 세트가 1개 이상이어야 저장된다(91행). 손대지 않았다.
- JSON 내보내기는 내부 동기화 칸(modifiedTime, remoteRevision, localActivityId 등)까지 포함한다.

## 다음 작업자에게
- 기기에서 먼저 볼 것:
  1. 직접 추가 → 시각 칸 → 시트가 대화창 위에 뜨는지
  2. 23:30 → 07:00 입력 시 "(다음 날)" 표시와 저장
  3. 설정 → CSV 저장 → 파일 열기
  4. 아이콘 길게 누르기 → 바로가기 → 타이머 시작. 이미 타이머가 돌 때는 토스트.
- 이 컨테이너의 Maven Central은 429를 자주 낸다. gradle이 실패하면 로그에서 429를 먼저 확인하고 잠시 뒤 다시 돌린다.
- 커밋할 때는 untracked 새 파일 8개를 빠뜨리지 않는다(`shortcut/` 폴더 2개 포함).
