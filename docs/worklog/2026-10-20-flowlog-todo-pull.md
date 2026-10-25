# 2026-10-20 — Flowlog 웹에서 바뀐 할 일을 폰으로 가져오기

에이전트: 할 일 가져오기 구현 (Opus 5.5, effort high). 하위 에이전트 호출: 없음. 커밋·push: 안 함.

대상: `/home/user/Flowlog`, 브랜치 `ccr-2a22e640-e8dn8n`, 기준 커밋 `51828c1`(타이머 공유 뒤). 바뀐 파일은 모두 커밋하지 않은 작업 트리에 있다. 웹 저장소(`/home/user/pfkfks-main`)는 읽기만 했다.

## 한 일

### 1. 전수 조사 (코드 읽기)

| 무엇 | 어디 | 지금 동작 |
|---|---|---|
| 할 일 업로드 | `FirebaseSyncDataSource.syncPendingTodos` | Room의 PENDING 행을 올린다. 문서 id = `legacyId` 문자열, 없으면 `todoId`. 지운 행은 **문서 삭제**, 아니면 `TodoItem.toRemoteMap` 병합 쓰기(필드: `id, title, category, isCompleted, createdAt, completedAt, selectedDate, accumulatedSeconds, burdenLevel, burdenGroupKey, burdenScore, burdenReasonJson, updatedAt`). `modifiedTime`은 없고 `updatedAt`(폰 시계)이 수정 시각. 원격 상태를 보지 않고 덮어썼다. 업로드 뒤 SYNCED |
| 할 일 복원 | `FirebaseRestoreDataSource.restoreTodos` | 로컬 활동·할 일이 모두 0일 때(새 설치)만 전체 읽기. 이미 있는 행은 건너뜀. `id`가 0이 아니면 `legacy_todo_<id>`, 0이면 문서 id를 행 id로 |
| 삭제 업로드 | `DeleteSyncWorker` → `syncPendingTodos` | 위 업로드와 같은 경로 |
| 증분 기준점 | `RemotePullCursor` | 활동·공부 연결·결정 세 종류만. 할 일 갈래 없음 |
| 캘린더 쪽 | `FirebaseCalendarPullDataSource.applyTodoCalendarDocuments` | `calendarEvents`(type FLOWLOG_TODO)의 할 일 미러를 받아 Room에 넣는다(`updatedAt`이 늦으면 덮어씀, `deletedAt`이면 지움 표시). `calendar_petite_*`·`calendar_todo_*` 행은 todos 컬렉션과 별개 |
| 폰의 할 일 조작 | `TodoRepository`, `RoomTodoLocalDataSource` | 완료·수정·삭제·시간 더하기 전부 `legacy_todo_<숫자 id>`로 찾는다. 새 할 일은 시각 기반 숫자 id를 받는다 |
| 웹 쓰기 | `public-flowlog/app/app-store.js` | 추가: 자동 문서 id + `id: 0`, 필드는 폰과 같음, `updatedAt: Date.now()`. 완료: `isCompleted, completedAt, updatedAt` 갱신. 삭제: **문서 삭제**(되돌리기는 같은 id로 다시 씀, `updatedAt` 새로). 타이머 종료 때 `accumulatedSeconds`와 `updatedAt` 갱신. 열린 할 일은 `isCompleted == false`로 읽음 |

조사에서 나온 문제 둘(지시서 밖이지만 기능에 필요해 처리함):
- 웹이 만든 할 일은 `id: 0`이라 폰에서 `TodoItem.id = 0`이 된다. 폰은 모든 조작을 숫자 id로 하므로 **완료·수정·삭제가 조용히 안 되고**(`RoomTodoLocalDataSource.update`는 id 0이면 그냥 끝남), 이런 할 일이 둘이면 할 일 화면 목록 키 `active_0`이 겹친다(`TodoScreen.kt` 530·572·594행 — Compose에서 같은 키는 앱이 멈추는 오류). 지금도 새 설치 복원 때 생길 수 있고, 가져오기를 넣으면 늘 생긴다.
- 웹 코드 주석은 "웹에서 만든 할 일은 id 0(앱의 Room 할 일과 같음)"이라고 적었지만, 폰의 새 할 일은 0이 아니라 시각 기반 숫자 id다.

### 2. 새 파일
- `app/src/main/java/com/example/flowlog/data/sync/TodoMergePolicy.kt` — 순수 병합 규칙(안드로이드·Firebase 없음). `merge`, 삭제 후보(`deletionCandidates`), 커서 경계(`changedSince`), 문서 id↔행 id, 옮길 문서인지(`needsAdoption`).
- `.../data/sync/TodoRemotePull.kt` — 가져오기(`TodoRemotePull.pull`)와 업로드와 함께 쓰는 도우미(`TodoSyncSupport`: 문서→행 변환, 병합 적용, 업로드 전 맞추기, 완료 기록, 웹 문서 옮기기).
- `app/src/test/.../data/sync/TodoMergePolicyTest.kt` — 15개.

### 3. 고친 파일
- `FirebaseSyncSupport.kt`(`FirebaseSyncCoordinator.refreshStudy`): 활동 증분 가져오기 바로 뒤에 `TodoRemotePull.pull`. 성공해야 15분 간격 기록을 갱신한다.
- `FirebaseSyncDataSource.syncPendingTodos`: 올리기 전에 서버 문서를 한 번 읽고(캘린더 전용 행은 제외) 병합 규칙으로 맞춘다. 서버가 이기면 Room을 서버 것으로 바꾸고 올리지 않는다. 올린 뒤 "서버가 가진 완료 시각"을 기록한다.
- `TodoDao.kt`: 쿼리 셋 추가(`getSyncedLiveTodos`, `getMaxLegacyId`, `deleteTodoRow`). 표 구조는 그대로라 Room 버전·마이그레이션 변화 없음.
- README("Some data also flows from Firestore back to the app" 목록에 한 항목), CHANGELOG.

### 병합 규칙 (`TodoMergePolicy`)
1. **수정 시각(`updatedAt`)이 늦은 쪽이 할 일 전체를 이긴다.** 같으면 서버. 폰 행이 SYNCED면 더 새로운 서버 사본만 받는다. 폰에 PENDING이 있고 그쪽이 더 늦으면 폰 우선(그대로 올림), 아니면 서버 우선(Room을 서버 것으로, 올리지 않음).
2. **완료는 그것을 못 본 쪽이 되돌리지 못한다.** 이긴 쪽이 미완료고 진 쪽이 완료면 완료를 남긴다. 단 그 완료(`completedAt`)가 이미 서버에 있다고 폰이 알고 있으면(가져올 때 봤거나 폰이 올렸으면, 설치별 SharedPreferences `flowlog_todo_sync`) 이긴 쪽의 미완료는 일부러 되돌린 것으로 보고 따른다. 이것으로 "웹에서 완료 → 폰이 타이머 시간을 더해 더 늦은 수정 → 폰이 되살림"을 막고, 폰에서 본 완료를 일부러 되돌린 것은 살린다. 반대 방향도 같다(폰의 안 올린 완료는 더 늦은 웹 수정이 와도 남고 다시 올라감).
3. **웹 삭제**(문서 없음): 전체 읽기 때는 문서가 없는 SYNCED 행을, 증분 때는 열린 문서 목록과 바뀐 문서에 없는 **미완료** SYNCED 행을 후보로 잡고 직접 읽어 확인한 뒤 폰에서 지움 표시(soft delete, SYNCED)한다. **PENDING 행(안 올린 새 할 일, 안 올린 수정)은 건드리지 않는다.** 캘린더 전용 행(`calendarSourceId`, `calendar_*`)과 가져오기 시작 뒤 바뀐 행도 제외. 지울 때 `updatedAt`을 바꾸지 않아, 문서가 다시 나타나면 규칙 1로 되살아난다.
4. 폰이 지웠는데 서버 문서가 더 오래된 채 남아 있으면 지우기를 다시 올린다.
5. **웹이 만든 문서**(`id: 0` + 숫자가 아닌 문서 id): 한 트랜잭션으로 새 숫자 id 문서에 같은 내용을 쓰고(`id`=새 번호, `updatedAt`=지금) 옛 문서를 지운 뒤 폰에 넣는다. 옛 행(새 설치 복원으로 문서 id 행이 있으면)은 지운다. 옛 행에 안 올린 변경이 있으면 이번엔 건너뛴다.

### 받는 시점
활동 증분 가져오기와 같은 자리(`refreshStudy`): 로그인 직후·앱을 열 때·네트워크가 돌아올 때(`syncEligible`, 타이머가 돌면 미룸, 15분 간격), 자정 동기화, 할 일·활동 저장 뒤 전체 동기화(`syncAll`, 강제). 기준점은 `RemotePullCursor`의 새 키 `"todos"`(24시간 겹침, 첫 회·주 1회 전체 읽기). 기존 키(활동·공부)는 그대로.

## 확인한 것 (어떻게)
환경: `ANDROID_HOME=/tmp/claude-0/-home-user/7c40c1dc-b607-5f78-9497-ffe487ef55d0/scratchpad/android-sdk`, `cd /home/user/Flowlog`.
- `bash ./gradlew :app:compileDebugKotlin :app:testDebugUnitTest -PofflineValidation=true --console=plain` → BUILD SUCCESSFUL. 결과 XML 집계(파일 시각 확인) **180개 통과, 실패 0, 오류 0** = 기존 165 + `TodoMergePolicyTest` 15(원격 신규, 원격 완료, SYNCED는 같거나 오래된 사본 무시, 원격 삭제는 SYNCED 행만, 증분 때는 미완료만, 폰 PENDING이 더 새로움, 원격이 더 새로움, 동시 수정은 서버, 웹 완료 뒤 폰 타이머 시간으로 되살리지 않음, 본 완료를 일부러 되돌린 것은 유지, 안 올린 폰 완료는 새 웹 수정에도 유지, 안 올린 폰 삭제 대 새 웹 수정, 지움 표시 행의 문서가 돌아오면 복원, 커서 경계, 옮길 문서 판정과 id 변환).
- `git diff --stat`(새 파일 3개 제외): 5 files changed, 69 insertions(+), 8 deletions(-). Room 스키마 파일 변화 없음.

## 확인 못 한 것
- **기기와 실제 Firestore**: 설치·실행 안 함. 실제 쿼리(`updatedAt >=`, `isCompleted == false`), 웹 문서 옮기기 트랜잭션, 업로드 전 읽기, 화면 반영 모두 미확인. `TodoRemotePull`·`TodoSyncSupport`(안드로이드·Firebase 부분)는 단위 테스트가 없다 — 테스트는 순수 규칙뿐.
- 웹 앱이 폰이 옮긴 문서(옛 id 사라지고 새 숫자 id 생김)를 어떻게 보이는지. 웹은 할 일을 한 번 읽어 두므로(`loadTodos`), 옮겨진 뒤 새로고침 전에 옛 id로 완료하면 `updateDoc`이 없는 문서라 실패할 것으로 보인다(코드 읽기로 추정, 미확인).
- 규칙: 옮기기는 todos 문서 생성·삭제라 지금 규칙(소유자 쓰기)으로 될 것으로 보지만 에뮬레이터로 돌려 보지 않았다.

## 알려진 문제
- 수정 시각은 양쪽 기기 시계다. 시계가 크게 틀리면 "늦은 쪽" 판정이 밀린다.
- 할 일 단위로 이긴다. 같은 할 일을 양쪽에서 동시에 다른 칸을 고치면 진 쪽 칸 수정은 사라진다(완료만 따로 지킴). `accumulatedSeconds`도 진 쪽 더하기가 사라질 수 있다.
- 웹에서 지운 할 일을 폰에서 **아직 올리지 않은 수정**이 있는 상태로 가지고 있으면, 폰이 올릴 때 문서를 다시 만든다(웹의 문서 삭제는 시각이 남지 않아 "늦은 쪽"을 알 수 없음). 웹이 삭제 표시(tombstone) 방식으로 바꾸면 해결된다.
- 증분 때는 완료된 할 일의 웹 삭제는 다음 주 1회 전체 읽기 때 반영된다(미완료만 매번 확인).
- 웹 문서 옮기기는 서버 문서를 바꾸는 일이다(옛 문서 삭제). 웹의 진행 중 타이머가 옛 id를 `linkedTodoId`로 들고 있으면 그 연결은 끊긴다.
- 업로드마다 할 일 하나당 읽기 1회, 가져오기마다 열린 할 일 전체 읽기가 늘었다.

## 다음 작업자에게
- **웹 쪽에 권할 것**: 할 일을 만들 때 폰처럼 숫자 id(예: `Date.now()`)를 `id`에 넣고 문서 id를 `String(id)`로 쓰면 폰의 옮기기가 필요 없다. 삭제를 문서 삭제 대신 `isDeleted`·`deletedAt` 표시로 바꾸면 위 "되살리기" 문제와 완료된 할 일 삭제 지연이 없어진다(그때는 폰 규칙에 삭제 표시 읽기를 더할 것).
- 이 작업은 `RemotePullCursor` 기존 키, 계정 삭제·복원 흐름, 타이머 문서를 건드리지 않았다. 계정 삭제 때 앱 SharedPreferences가 비워지므로 할 일 기준점과 완료 기록도 함께 지워진다.
- 기기 확인 순서 제안: 웹에서 할 일 추가 → 폰 목록에 뜨고 완료·삭제가 되는지(옮기기), 웹에서 완료 → 폰 반영, 폰에서 그 할 일로 타이머를 돌려 시간 더하기 → 완료가 유지되는지, 웹에서 삭제 → 폰에서 사라지는지, 비행기 모드에서 폰에 새 할 일 → 가져오기 뒤에도 남는지.
