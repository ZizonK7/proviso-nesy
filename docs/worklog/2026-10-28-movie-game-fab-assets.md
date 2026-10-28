# 2026-10-28 — movie_game Fab(메가스캔) 자산 받기와 1차 배치 (PC 세션, 저녁)

에이전트: 메인(PC 세션, Fable 5.1) 혼자. 하위 에이전트 호출: 없음.
커밋·push: movie_game main(코드·사진 도구·다시 구운 에셋), 이 저장소는 이 보고서 + 논리집 사실·관찰 1개씩(worktree에서 origin/main 위에).
사용자 결정: DECISIONS 26(무료로 담은 Fab 자산은 가리지 않고 쓴다). 사용자가 PC 앞에 있어서 런처 창은 직접 눌렀다.

## 한 일
- **Fab 담기·받기 길 뚫기**. 런처의 Fab 탭은 그 자체로 깨져 있다(런처 내장 브라우저가 크롬 90이라 fab.com 최신 JS의 `toSorted`가 없어 오류 페이지만 뜸). 디버그 포트(`-cefdebug=9222`)로 그 화면을 조종해 폴리필을 넣으면 검색까지는 되지만, 로그인·보안 검사(Cloudflare)를 자동으로 넘기는 일은 하지 않기로 하고 접었다 → 담기는 **일반 크롬에서 fab.com 로그인 뒤 "내 라이브러리에 추가"**. PC 쪽 런처는 "로그인 유지" 토큰으로 자동 로그인된다.
- **런처가 프로젝트를 못 찾는 문제**: 런처는 "최근에 연 프로젝트"를 로그에서 찾고도 목록에 올리지 않고, `문서/Unreal Projects/*/*.uproject`만 보여 준다. 사용자 레지스트리 `Builds` 등록은 런처가 "중복 경로"라며 지워 버린다. 해결: `문서/Unreal Projects/MovieGame` → 실제 프로젝트 폴더 **정션**(유지). 그 뒤 "프로젝트에 추가"가 됐다.
- **받은 것**: Marble Mug(15MB), Old Furniture Pack 01(102MB: 의자 2·탁자 2·소파·서랍·선반 4·양탄자 2·장 문 2), Military Trench Megascans 샘플(10.8GB, 989파일, 지도 20, 100MB 넘는 메시 2). 셋 다 `ue/.gitignore`(계정 라이브러리에서 다시 받을 수 있음).
- **샘플형 항목의 부작용**: Military Trench를 "프로젝트에 추가"하자 `Config/*.ini` 5개가 샘플 것으로 덮어써졌다(게임 모드 → AutomatedPerfTest, Hotspot 충돌 채널·시작 맵·bRemoteExecution 소실, 입력 설정 교체). `git show HEAD:` 로 되돌리고 줄 끝만 CRLF로 맞춤(샘플 설정은 scratchpad에 백업). `MilitaryTrench.uproject`(5.6용)도 프로젝트 폴더에 떨어져 있어 치웠다.
- **카탈로그**: `ue/tools/fab_catalog.py`(새로) — `FAB_CATALOG=<메시 목록 파일>`이면 build_level이 거리 남쪽 y=-9000 빈 땅에 메시를 한 줄로 세우고(이름표·크기·약한 등·어두운 벽돌 뒷벽) 자동 촬영 대본 `<목록>.auto.txt`를 써 준다. 40개(참호 소품 25 + 가구 14 + 머그)를 찍어 묶음 사진 7장으로 사용자에게 보냄.
- **배치 1차** `ue/tools/fab_props.py`(새로, build_level이 case01 뒤에 부름): 221B 양탄자(상자 양탄자 제거)·책상 의자(상자 의자 제거)·오른쪽 벽 장, 술청 탁자 둘·의자 넷(원통 탁자·걸상 제거)·머그 넷, 뒷방 서쪽 벽에 기댄 사다리·삽, 칸막이 앞 낮은 걸상·목재 더미·널빤지 더미·작업대 위 나무 상자, 거리 보도의 돌부스러기 둘. 메시 경계 중심을 좌표에 맞추는 `put()`, 참호 팩은 `find_trench(이름)`으로 경로를 찾는다. 시대에 안 맞는 것(녹슨 드럼통·철책·모래주머니·참호 벽)은 뺐다.
- **사진 도구** `ue/tools/photo/`(새로): `shoot.ps1`(게임을 `-mgauto` 대본으로 띄워 끝까지 기다림, `-Extra`로 엔진 인자), `sheet.py`(PNG → 이름표 묶음 JPG), `auto_rooms.txt`(거실 3·술청 2·뒷방 3·거리 1 시점), `fab_catalog_list.txt`.
- md: movie_game `CLAUDE.md`(구조·상태·다음 할 일), `DECISIONS.md` 26.

## 확인한 것 (어떻게)
- 레벨 빌드 `UnrealEditor-Cmd … -run=pythonscript -script=build_level.py` → `[fab_props] placed`, `[build] done: 2375 actors`, `[build] no problems`.
- 사진: `shoot.ps1 -Auto auto_rooms.txt -Extra '-dx11'` → 9장(`fabp_*.png`), 묶음 2장 사용자에게 보냄. 본 것: 양탄자·나무 의자·술청 탁자와 의자·뒷방 사다리는 어울린다. 221B 장의 앞뒤 방향은 확인 못 함, 거리 부스러기는 작아 거의 안 보임.
- 카탈로그 첫 촬영은 등 40개를 2500cd로 켜서 밤 장면 자동 노출이 타 버렸다(전부 흰색) → 160cd·반지름 700·뒷벽 추가로 해결.

## 확인 못 한 것
- **DX12 크래시의 원인**. 참호 팩 메시(Nanite, 8K 질감)가 든 레벨을 DX12로 띄우면 2~3프레임째 `PageFault`로 GPU가 죽는다(Aftermath 덤프, `CreatePlacedResource failed` 32MB). 가상 그림자 맵을 꺼도(`r.Shadow.Virtual.Enable 0`), 그림자 없는 등으로 바꿔도 같다. **`-dx11`이면 끝까지 돈다.** 첫 카탈로그 촬영(DX12)은 셰이더가 아직 준비 중일 때 시작돼 우연히 살았다. `play.cmd`는 DX12라 사용자 플레이 전에 잡아야 한다(후보: Nanite, 가상 질감 풀, 드라이버).
- 가구 팩의 앞뒤 방향(의자·장): 카탈로그 사진에서 장 세 개는 뒷판만 보였다(앞이 +Y). 의자는 추정으로 돌려 놓았다.
- 머그는 대리석이라 찻잔 대용으로는 어색할 수 있다.

## 알려진 문제
- 런처 Fab 탭은 Epic이 고치기 전까지 깨져 있다. 담기는 브라우저에서.
- `문서/Unreal Projects/MovieGame` 정션을 지우면 런처가 다시 프로젝트를 못 본다.
- 참호 팩 10.8GB는 대부분 안 쓴다(소품 7~8개만). 디스크가 아쉬우면 쓰는 메시만 다른 폴더로 옮기고(에디터 이동, 리디렉터) 나머지를 지울 수 있다.
- `__ExternalActors__/MilitaryTrench/`(샘플 지도의 액터)가 git 제외 폴더에 남아 있다. 무해.

## 다음 작업자에게
- 새 팩을 받으면: 크롬에서 담기 → 런처 라이브러리 탭 → 프로젝트에 추가(MovieGame, 버전 경고 무시) → **`git status ue/MovieGame/Config`와 `ls ue/MovieGame/*.uproject` 확인** → `ue/.gitignore`에 폴더 한 줄 → `fab_catalog_list.txt`에 경로를 넣고 `FAB_CATALOG`로 빌드해 사진으로 고른다 → `fab_props.py`에 `put()` 한 줄.
- 사진은 당분간 `-Extra '-dx11'`.
- DX12 크래시를 좁히는 순서 제안: ① `-ExecCmds="r.Nanite 0"` ② 참호 팩 메시를 `fab_props`에서 전부 빼고 가구 팩만 ③ 참호 팩 질감의 Virtual Texture Streaming 끄기(에디터 Python으로 일괄) ④ 드라이버 갱신.
