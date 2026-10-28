# 2026-10-29 — movie_game 환경 2차 · 메타휴먼 인물 걷기 (병렬 작업자 둘) + DX12 재확인 · 메타휴먼 빌드 스크립트 (PC 세션)

에이전트: 메인(PC 세션, Fable 5.1) + 세션 안 Opus 5.5 high 둘 동시(p105 env2, p106 mhnpc). 사용자 지시: "병렬로 할 거 있으면 하고 할 거 진행해줘. 내가 해야 할 거 있으면 말하고."
커밋·push: movie_game main(아래), 이 저장소는 이 보고서 + 기록(p105·p106, 배치 36).
이야기 내용은 봉인(결정 21) — 여기는 소품 종류·구조만.

## 한 일 (메인)
- **UE 잠금** `ue/tools/uelock.py`(새로): 작업자 둘과 메인이 같은 프로젝트에서 커맨드릿·게임·C++ 빌드를 번갈아 쓰므로, `mkdir`이 원자적인 것을 이용한 잠금 폴더 `ue/.uelock`. `acquire <이름>`은 풀릴 때까지 15초마다 기다리고(최대 1시간), 40분 넘게 묵은 잠금은 넘겨받는다. `ue/tools/build.ps1`(새로: build.cmd와 같되 pause 없음, `-NoCpp`로 C++ 건너뜀, 잠금 자동)과 `ue/tools/photo/shoot.ps1`(잠금 추가)이 알아서 건다.
- **build_level.py 맨 아래 hook**: `env2`·`mh_npc` 모듈을 import해 `build(globals())`를 부르되, 없거나 깨져도 빌드가 계속되게 try/except. 작업자 둘이 같은 파일의 같은 자리를 고치지 않게 메인이 먼저 넣었다.
- **DX12 크래시 원인을 좁혀 닫음**: 환경 2차 전에는 같은 레벨·같은 대본(9시점, 참호 팩 메시 포함)이 DX12로 2회 완주했는데, 환경 2차(새 재질·소품 60개)가 들어간 뒤에는 **4/4 모두 2~3프레임째 GPU 페이지 폴트**. `-dpcvars`로 cvar 하나씩 바꿔 가며 9회 실행: `r.Nanite=0` 완주 / `r.Nanite.Streaming.ReservedResources=0` 죽음 / **`r.Nanite.Streaming.AsyncCompute=0` 완주 2/2** → `Config/DefaultEngine.ini` `[ConsoleVariables]`에 넣고 기본 인자(DX12)로 다시 완주 확인(로그 `Set CVar [[r.Nanite.Streaming.AsyncCompute:0]]`). 즉 RTX 4060 드라이버(2026-07)에서 Nanite 스트리밍의 비동기 컴퓨트 경로가 죽는다. `-d3ddebug`는 이 PC에 D3D12 디버그 레이어(Graphics Tools)가 없어 못 썼다. play.cmd는 DX12 그대로 둔다. 성능 영향은 재지 않았다.
- **메타휴먼 빌드 스크립트**(새로, 재현 가능하게 저장소에): `ue/tools/mh_remote.py`(열린 에디터에 스크립트를 보내는 원격 실행 러너, `KEY=VAL` 인자를 환경변수로 넘김) + `ue/tools/mh_build.py`(프리셋 복제 → 머리·눈썹·수염·옷 wardrobe item 끼우기 → 자동 리깅·질감(Epic 서버, 로그인) → 빌드 OPTIMIZED/MEDIUM → `/Game/Baker/MH/Build/<이름>`). 헤드리스 커맨드릿에서 `DRY=1`로 로그인 전 단계를 두 번 돌려 확인: 프리셋 복제 7초, `try_add_item_from_wardrobe_item`이 `MetaHumanPaletteItemKey`를 돌려주고 `default_instance.set_single_slot_selection(slot, key)`로 선택된다(슬롯 이름: Hair·Eyebrows·Beard·Mustache·Eyelashes·Peachfuzz·Outfits·Top Garment·Bottom Garment·SkeletalMesh·Character). 리깅·질감·빌드 단계는 로그인이 필요해 **미확인**.
- **프리셋 얼굴 사진 뽑기 시도 — 실패**: 프리셋 에셋 29개(`/MetaHumanCharacter/Optional/Presets/`)의 .uasset 안에 든 PNG는 1024×1024 얼굴 질감 맵(법선 비슷한 보라색)뿐, 갤러리 썸네일이 아니다. 프리셋 고르기는 사용자가 에디터 갤러리에서 본다.
- 계산기 vs 손 예측: 계산기는 둘 다 '다른 일' 13.9–27.7분(바퀴 몫·항목 수를 모름), 손은 둘 다 '신경 끄기'(40–80 / 35–70분).

## 작업자 보고 — env2 (p105, Opus 5.5 high, 30.3분·118턴·22.4M)
작업자가 쓴 보고서 그대로(제목 단계만 내림). 8개 중 7개 됨, Fab 2차는 방향 확인만.
#### 한 일
새 파일
- `ue/tools/env2.py` — `build(g)` 하나. 항목별 함수(fireplace·paintings·lamps·books·tools·tea_and_bottles·weather)를 각각 `attempt`로 감싸 하나가 깨져도 나머지는 선다. 맨 위 `WEATHER = True`로 비·안개 손질을 끄고 켠다.
- `ue/tools/blender/make_props.py` — 블렌더 5.2 스크립트(`blender -b -P make_props.py -- ue/tools/furniture`). 소품 23종 → `ue/tools/furniture/Prop*.fbx`(합계 약 0.5MB). 원점은 바닥 가운데(액자만 뒷면 가운데), 블렌더 -Y가 앞(UE에선 +Y). 재질은 슬롯 이름으로 고른다(env2.py `SLOTS`).
- `ue/tools/textures/painting_{fogstreet,seascape,portrait,country}_d.jpg` — 로컬 그림 모델 Z-Image-Turbo로 만든 유화 4장(1024x768, 초상 768x1024, 각 120~170KB).
- `ue/tools/photo/env2_check.txt`(항목별 확인 대본 15장), `ue/tools/photo/env2_rooms.txt`(마무리 대본: 거실 4·술청 2·뒷방 3·거리 2).
- 확인 사진 묶음 `ue/shots/2026-10-29_env2_room.jpg`(167KB) · `_pub_back.jpg`(248KB) · `_street.jpg`(167KB).

고친 파일
- `ue/tools/build_level.py` `house_221b()`만: 벽난로 선반 위 소품(시계·해골·촛대)이 블렌더 벽난로로 바뀐 뒤 가슴벽 속(x 649~659)에 묻혀 있었다 → 선반 위 x = BX1+14 = 684로 옮김(`MX` 변수, 벽난로 FBX가 없으면 예전 자리). 맨 아래 hook은 안 건드림.

항목별
1. 벽난로 불 — **됨, 방법 (나)**. (가) Niagara는 시도하지 않았다: Python으로 모듈 값을 못 고치는 데다 (나)가 한 번에 불처럼 보여서. 참고로 참호 팩에 Cascade(옛 파티클) `P_Fire`·`T_Fire_SubUV`가 있지만 연기가 방으로 나올 위험과 팩 의존 때문에 안 씀.
   - 불꽃: 세로 평면 5장(x 643~653, y -1063~-1047, 높이 RZ0+20~78, 엇갈린 각도)에 `M_E2_Fire` — 무조명 가산(additive) 재질, Custom 노드에서 값 노이즈 두 겹이 시간(Time)에 따라 위로 흐르고 혀 모양으로 흔들림, 장마다 위치로 씨앗이 달라 서로 다르게 움직인다. 1초 간격 두 장에서 모양이 바뀐 것을 확인.
   - 장작: `PropFireLogs`(통나무 셋 + 붉게 빛나는 숯 바닥) at (649, -1055, RZ0+14). 기존 석탄 구·쇠살대는 그대로, 기존 상자 불꽃 `Flame` 5개와 `FireLight`는 지움.
   - 깜빡이는 빛: 점광원 `FireLightE2`(9cd, (692,-1055,RZ0+48), 반경 1500, 그림자 켬) + 화구 안 `FireInnerLight`(0.6cd, 그림자 끔). 둘 다 라이트 펑션(빛에 곱해지는 재질) `M_E2_FireFlicker`(사인 넷을 섞어 0.6~1.0)로 깜빡임. 벽지·바닥 양탄자·안락의자·선반 대리석에 따뜻한 빛이 듦(사진).
2. 액자 그림 — **됨**. 금박 몰딩 액자 2종(`PropFrameL` 97x77cm, `PropFrameP` 65x81cm, 그림 면 UV). 221B: 벽난로 위(가로, 안개 낀 거리 — 예전 어두운 상자 그림과 놋쇠 테 `Painting`·`Frame`(Room 폴더)을 바꿈), 뒷벽 책장 왼쪽(초상, (692,-1329.5,RZ0+165)), 오른쪽 벽 책상 위(바다, (1234.5,-872,RZ0+185)). 그레이프스 술청 서쪽 벽(풍차 시골, (3115.5,1010,190)). 그림이 바로(거울상 아님) 보이는 것 확인.
3. 기름등 — **됨**. `PropOilLamp`(놋쇠 받침·기름통·심지 고리·젖빛 갓·유리 굴뚝·불꽃, 높이 50cm, 그림자 끔 — 갓이 안의 빛을 막지 않게). 221B 받침 탁자 위 1(예전 구·원통 기름등 4개 + `OilLampLight` 대체, 2.2cd), 술청 카운터 위 2((3362,1142,106)·(3562,1148,106), 각 2.5cd). 처음 갓 발광 2.2에선 하얗게 타서 0.8로 낮춤. 세기는 방의 기존 등(벽등 0.6cd, 불 6~9cd) 기준으로 맞췄다 — 지시서의 160cd는 이 방 기준으로 수십 배 밝아 쓰지 않음.
4. 책 — **됨**. 책장 칸 다섯에 `PropBooks0..4`(한 열 약 2.5m, 권마다 높이·두께가 다르고 책등에 `ai_books_spines_d`의 한 칸을 UV로 붙임, 윗면은 종이색, 나머지는 가죽색). 예전 색 상자 `Book`(Books 폴더) 전부 지움. 누운 책 세 권 묶음 `PropBookStack`: 책상 위 (1125,-885), 벽난로 왼쪽 구석 바닥 (710,-1262).
5. 뒷방 연장 — **됨**. 벽의 임시 상자 연장 줄 `Tool`·`ToolHandle` 12개를 같은 자리(x 3385~3515, 벽 y 1745, z 156~162)에 진짜 모양 끌 4·망치·나무망치(손잡이 위로)로 바꿈. 톱(벽 x 3262, z 178, 못 하나) · 직각자(x 3335, z 150). 작업대 위(z 92): 대패 (3396,1688), 망치 (3452,1657), 못 상자 (3503,1703) — 핫스팟 H·J·K·L 자리와 단서 소품은 피함.
6. 찻잔·병 — **됨**. 221B 탁자에 찻잔+받침 2세트((743,-1082)·(801,-1030)). 술청 뒷벽 판 앞에 선반 두 단(x 3330~3660, z 140·186) + 받침쇠, 병 18개(포도주병·진병·납작병·돌병, 짙은 초록·갈색 유광, 일부 호박색 반투명, 라벨은 바랜 종이색). 예전 원통 `Bottle` 9개는 지움.
7. 비·안개·하늘 — **됨(약하게)**. `environment()`가 만든 액터 값을 env2에서 고침: 안개 밀도 0.06→0.07, 높이 감쇠 0.1→0.12, 산란색 더 어둡고 푸르게, 부피 안개 소광 4→4.5·앞방향 산란 0.3→0.45(가스등 둘레 번짐), 달빛 0.12→0.07, 하늘빛 0.6→0.45, 거리 가스등 7개의 부피 산란 8→10. 처음 0.085/0.55/14로 했더니 거리가 빛 덩어리로 뭉개져 되돌려 낮춤. 전후 차이는 크지 않다(사진 `_street.jpg` 왼쪽 위가 전). 빗줄기 재질 `rain_material`은 그대로.
8. Fab 2차 — **일부만**. `FabCabinet`(SM_WoodenShelf_02) 방향 확인: 방 안에서 찍으니 열린 선반 쪽이 방(-X)을 본다 → 앞은 메시 +Y, 지금 배치(yaw 90)가 맞다. `fab_props.py`는 안 고침. 소파(SM_Couch 289x220x169cm, 이끼 낀 폐가풍 질감)와 큰 책장(SM_WoodenShelf_04 321x77x271cm, 노점 진열대 같은 모양)은 221B에 놓지 않았다: 거실(610x540cm)이 벽난로·책장·책상·장·창으로 이미 차 있고, 가운데에 두면 '에이다' 살펴보기 시점과 플레이어 동선을 막는다. 남은 팩 메시 목록은 아래 '다음 작업자에게'.

#### 확인한 것 (어떻게)
- 레벨 빌드: PowerShell `Set-Location ...\ue; .\tools\build.ps1 -NoCpp` 3회 → 마지막: `[env2] fireplace/paintings/lamps/books/tools/tea & bottles(18 bottles)/weather(street lamps 7) done`, `[build] done: 2438 actors`, `[build] no problems`.
- 사진: `Set-Location ...\ue\tools\photo; .\shoot.ps1 -Auto .\env2_check.txt -Extra '-dx11' -MaxMinutes 8` 2회, `.\shoot.ps1 -Auto .\env2_rooms.txt -Extra '-dx11' -MaxMinutes 8` 1회 → 대본 35개 명령이 `quit`(t=37.0)까지 돌고 55초에 종료, 11장.
- 재질 컴파일: 게임 로그 `ue\MovieGame\Saved\Logs\MovieGame.log`에서 `Failed to compile Material` 0건(마지막 실행 뒤 grep).
- 그림 생성: venv `C:\ai\venvs\image`, `HF_HOME=C:\ai\hf-cache`, 임시 스크립트가 `C:\ai\scripts\gen_image.py`의 `load("zimage")`를 불러 9단계·시드 7로 4장(모델 올리기 61초, 장당 23초). GPU를 UE와 같이 쓰지 않게 이 동안 `uelock.py`로 잠금.
- 블렌더: `make_props.py`가 23종 모두 `SAVED`(크기·면 수·슬롯 출력)하고 `DONE`.
- 눈으로 본 것: 불꽃 1초 간격 두 장에서 모양 변화, 그림 방향·비율, 책 열이 칸에 맞게 서고 책등 글씨가 보임, 연장 걸린 방향, 병 선반, 기름등 빛, 장 방향.

#### 확인 못 한 것
- DX12에서의 모습(지금 DX12는 GPU 크래시라 전부 `-dx11`로만 찍음).
- 불빛 깜빡임은 사진 두 장으로만 — 실제 움직임의 자연스러움(속도·세기 폭)은 사람이 플레이로 봐야 한다.
- 라이트 펑션은 직접광에만 걸린다(Lumen 간접광은 안 깜빡임) — 눈에 띄는지 플레이로 확인 필요.
- 성능(프레임): 재는 도구가 없어 안 쟀다. 추가는 반투명·가산 평면 몇 장, 점광원 5개(그림자 켠 것 4개), 소품 약 60개.

#### 알려진 문제
- 221B 천장이 밝은 크림색으로 떠 보이는 시점이 있다(벽등·기름등·불빛이 겹쳐 위를 비춤 + 자동 노출). 이번에 기름등을 3→2.2cd로 낮췄지만 여전히 밝은 편.
- 화구 안쪽(쇠살대 뒤 벽)이 불꽃의 가산 발광 때문에 밝은 베이지로 보인다 — 안쪽 빛은 0.6cd로 낮췄음. 더 어둡게 하려면 불꽃 세기(`fire_material(..., 7.0)`)를 5 정도로.
- 술청·뒷방 벽(기존 `M_AI_PlasterPub`)이 아주 하얗고, 술청 큰 유리창 `PubGlass`가 안에서 보면 흰 판으로 탄다(기존 문제, 이번에 안 건드림).
- 오른쪽 벽 바다 그림은 그 구석에 빛이 거의 안 들어 어둡다.
- 날씨 손질은 효과가 약하다(세게 하면 거리가 뭉개짐). 하늘은 아직 맑은 남색이라 '비 오는 밤' 느낌은 하늘 쪽에서 더 손볼 여지가 있다.
- `env2.py`는 build_level에서 import 실패만 나면 `[env2] import failed` 경고만 남기고 `problems`엔 안 들어간다(hook이 그렇게 돼 있음) — 빌드 출력에서 `[env2] done` 줄을 꼭 확인할 것.

#### 다음 작업자에게
- 소품을 고치려면 `make_props.py`를 고치고 `blender -b -P make_props.py -- <movie_game>/ue/tools/furniture` 후 빌드. 슬롯 이름을 바꾸면 env2.py `SLOTS`도.
- 그림을 바꾸려면 `textures/painting_<키>_d.jpg`만 바꾸면 된다(env2.py `paintings()`의 키).
- 남은 Fab 옛 가구 팩 메시와 크기: SM_Couch 289x220x169, SM_WoodenShelf_01 144x91x110, SM_WoodenShelf_03 109x56x207, SM_WoodenShelf_04 321x77x271, SM_Carpet_02 360x223, SM_CabinetDoor_L/R 60x4x87, SM_Table_01/02(술청에 이미 씀). 전부 Nanite, 질감이 낡고 얼룩진 편이라 221B보다 뒷방·창고가 어울린다. 참호 팩엔 나무 상자(SM_Mil_Trench_Storage_Box_Wood_S, Crate_Wood_S_01/02 등)·쇠통·모래주머니가 있다.
- 참호 팩 `MilitaryTrench/Particles/P_Fire`(Cascade 불·연기·열 왜곡·빛 모듈)와 `T_Fire_SubUV`(불꽃 플립북 질감)가 있다 — 거리 화로나 굴뚝 연기에 쓸 수 있을지 모름.
- 이번 일의 모든 액터는 아웃라이너 폴더 `Env2/Room`, `Env2/Grapes`(빛은 `Lights`)에 있다.

## 작업자 보고 — mhnpc (p106, Opus 5.5 high, 51.6분·167턴·32.7M)
작업자의 답장 보고(도구가 보고서 파일 쓰기를 막아 답장으로 받음)를 경로만 가려 옮긴다. 목표 넷 다 됨 + 사건 1 자동 플레이 끝까지 통과.

**요약**: 221B의 `ada`, 거리의 `ada_street`, 뒷방의 `ada_back`은 Ada_mh(몸·얼굴·머리털·기본 옷), 플레이어는 Holmes_mh로 나온다. 서 있으면 서기, 움직이면 걷기 애니. 단서 소품은 메타휴먼의 같은 이름 뼈에 붙고, 살펴보기 때 몸 숨김과 `body 0`도 그대로. C++ 빌드 성공, `[build] no problems`, 게임 로그 `[npc]` 0·`Failed to compile Material` 0, 사진 확인, 사건 1 자동 플레이 통과.

**알려 둘 동작 변화 둘**: ① 인물이 이제 실제로 걷는다 — 지금까지는 인물에 컨트롤러가 없어 걷기 명령(`AddMovementInput`)이 무시되고 감독이 마지막 지점으로 순간이동시켜 메워 왔다(`bRunPhysicsWithNoController = true`로 고침). 사람이 플레이하면 watson이 실제로 따라오고 ada_street가 앞서 걷는다. ② 나타날 때 벽·난간에 박혀 있으면 `FindTeleportSpot`으로 빈 자리로 살짝 옮긴다(ada_street 시작점이 거리 쇠 난간과 겹쳐 있었다: (1430,−680) → (1386,−623), watson 6cm).

#### 한 일
- **방식**: Python은 case01이 세운 인물 액터에 "메타휴먼 빌드 이름"만 적어 두고, 게임 시작 때 C++가 `BP_<이름>`을 스폰해 인물의 Mesh 자리에 붙인다. 마네킹 메시는 비우되 Mesh 컴포넌트는 남겨 몸 숨김(`SetVisibility(…, true)`, 자식까지 전파)이 MGDirector를 고치지 않아도 메타휴먼 전체에 먹는다. MGDirector.cpp 등 다른 C++은 안 바꿈.
- **C++** `MGNpc.h/.cpp`: NPC·플레이어 공용 `namespace MGMetaHuman` — `Attach`(빌드 없으면 `FPackageName::DoesPackageExist`로 건너뜀 / 스폰·충돌 끔·Mesh에 붙임(메타휴먼도 마네킹처럼 +Y 앞·발바닥 원점이라 위치 조정 불필요) / Mesh 뼈의 소품을 Body의 같은 이름 뼈로 옮김(뼈 이름이 UE5 마네킹과 같아 매핑 불필요, 기준 자세 뼈 방향 차 0도) / 꼬리표 `mh:hide` 소품 숨김 / `/Game/Baker/MH/Anim/<이름>/AS_<이름>_Idle·_Walk` 읽음), `Animate`(애님 BP 없이 `PlayAnimation(루프)`로 서기·걷기 전환, 걷기는 15cm/s 넘으면 시작·멈춤은 5cm/s 미만 0.25초 뒤, 재생 배속 = 속도 ÷ WalkAnimSpeed). AMGNpc에 `FString MetaHuman`, `float WalkAnimSpeed = 185`; BeginPlay에서 붙이고 Tick에서 애니 선택; `SetHiddenNpc`가 붙은 액터도 숨김. `MGCharacter.h/.cpp`(플레이어): `MetaHuman = "Holmes_mh"`, Tick 추가; 빌드 없는 PC에서는 예전처럼 마네킹 + ABP_Unarmed + 코트.
- **Python** 새 `ue/tools/mh_npc.py`(`build(g)`): 표 `MH = {'ada': 'Ada_mh', 'holmes': 'Holmes_mh'}`(NpcId의 `_` 앞이 인물 이름; watson·harker·tom은 마네킹). 빌드된 BP 없으면 아무것도 안 함, 애니 없으면 `mh_anim.run()`. 마네킹용 치마 원통 3·맨손 구에 `mh:hide`. `_fix_right_arm`: case01이 팔뼈 X축이 손 쪽이라 보고 소품을 +X에 놓는데 오른팔 뼈(upperarm_r·lowerarm_r·hand_r)는 X축이 어깨 쪽 — 오른 소매가 어깨 위로 솟고 장갑·분필이 팔꿈치에 붙던 마네킹 시절 문제(10-28 사진에도 있음)를 메타휴먼에 한해 부호 반전. `MH_WALK_TEST=1`이면 ada가 (940,−1200)↔(1100,−1030) 왕복. 새 `ue/tools/mh_anim.py`: Ada·Holmes 몸 뼈대는 둘 다 `/Game/Baker/MH/Common/Female/Medium/NormalWeight/Body/metahuman_base_skel`이고 플러그인 애니는 다른 뼈대 에셋을 가리켜 그대로는 못 씀 → `AS_MH_Neutral_Stand_Idle_Loop`·`AS_MH_Neutral_Walk_Loop_F`를 복제한 뒤 **`RTG_MH_IKRig`로 인물마다 리타게팅**(`IKRetargetBatchOperation.duplicate_and_retarget`, `SKM_Body` → `SKM_<이름>_BodyMesh`), `AS_<이름>_Idle/_Walk`로 이름 바꾸고 원본 제거(플러그인 참조 없음). 둘 다 제자리 루프, 걷기 발 속도 Ada 184.3·Holmes 184.6cm/s → 기본값 185. `char_test.py`는 안 바꿈.

#### 확인한 것 (어떻게)
- C++: 잠금 걸고 `Build.bat MovieGameEditor Win64 Development … -WaitMutex -NoHotReload` → Succeeded(경고는 기존 MGDirector.cpp C4701 하나).
- 레벨: `.\tools\build.ps1` → `[mh_npc] metahuman on: ada=Ada_mh, ada_street=Ada_mh, ada_back=Ada_mh`, `[build] no problems`(마지막 빌드는 `MH_WALK_TEST` 없이).
- 게임 로그: `[mh] Ada_mh attached to MGNpc_0/2/5 (idle 1, walk 1)`, `Holmes_mh attached to MGCharacter_0`, 플레이어·거리 에이다·뒷방 에이다 모두 walk/idle 전환 로그.
- 사진(`shoot.ps1 -Extra '-dx11'`): `look ada` 2.25m 시점에 얼굴이 프레임 안 / 3인칭 뒷모습·앞모습 / 걷는 중 얼굴·머리털·옷·소매 소품·왼손 전보가 몸을 따라옴 / `body 0`으로 전체 숨김·복귀 / 맨발이 바닥에 닿음. `<movie_game>/ue/shots/2026-10-29_mh_{look_ada,holmes_back,holmes_front,walk_back,walk_look,ada_feet_body0}.jpg`.
- 사건 1 전체 자동 플레이(지난 세션 대본, `-dx11`): 225초에 마지막 상태 `beat=5 D1=1 D2=1`, `PlayLogs/case01_2026-10-29_0555.json`. 10-27 로그와 키 구성 같음, 이벤트 159 = 159, 핫스팟 13 = 13. `STUCK` 0·`is stuck` 0·`[npc]` 0·`Failed to compile Material` 0. (메인이 대본을 `ue/tools/autoplay/case01_full.txt`로 저장소에 넣음.)

#### 확인 못 한 것
- 플레이어가 걷는 사진(대본 `walk`는 걷는 동안 시계를 멈춰 못 찍음 — 전환은 로그로, NPC 걷기 사진이 같은 코드). 거리·뒷방 에이다 사진(로그만). DX12 모습(DX11에서 `LogMetaHumanCore: Unsupported RHI. Set RHI to DirectX 12` 경고 1회 — 메인이 뒤에 DX12로 전체 자동 플레이를 돌렸다, 아래). 표정·입 모양, 먼 거리 LOD.

#### 알려진 문제
- 캡슐에 붙은 단서 소품(옷깃 꽃·주머니 책·굽 진흙·치맛단 톱밥)은 마네킹 몸 기준 자리라 메타휴먼에서 조금 떠 있고 걸을 때 안 흔들린다. 오른손 장갑은 손에 든 상자처럼 보임.
- 프리셋 얼굴이 나이 든 얼굴·흰머리, 옷은 기본 셔츠·반바지·맨발(결정 24대로 통로 확인용).
- 걷기 배속 NPC 1.24·플레이어 1.4라 잰걸음. 회전 애니·전환 블렌드 없음.
- `duplicate_and_retarget`은 deprecated 경고(RunBatchRetarget 권장), 동작은 함. 고친 C++ 네 파일이 LF — 커밋 때 CRLF 정규화. 생성 애니는 git 제외 폴더(`Content/Baker/MH/`) — 빌드 때 저절로 다시 만들어짐.

#### 다음 작업자에게
- 새 메타휴먼(예: 왓슨): 에디터에서 `Watson_mh`로 빌드(로그인 필요) → `mh_npc.py` 표에 `'watson': 'Watson_mh'` 한 줄 → `.\tools\build.ps1 -NoCpp`(애니 자동 생성, `watson_*` 액터 전부에 붙음). 플레이어 몸은 `AMGCharacter::MetaHuman` 기본값 + 표의 'holmes'.
- 같은 이름으로 다시 빌드한 뒤 애니 다시 만들기: 잠금 걸고 `$env:MH_ANIM_FORCE='1'`로 `UnrealEditor-Cmd … -run=pythonscript -script=<movie_game>\ue\tools\mh_anim.py -unattended -nopause -nosplash -stdout`. 로그 `foot_speed`가 185에서 많이 벗어나면 `mh_npc.py`의 `WALK_ANIM_SPEED`.
- 걷기 사진: `MH_WALK_TEST=1`로 빌드해 찍은 뒤 **반드시 환경변수 없이 다시 빌드**(안 그러면 221B 에이다가 계속 왕복).
- case01_level.py 담당자에게: `sleeves()` 오른쪽과 `hand_r` 장갑·`lowerarm_r` 분필의 X 부호를 −로(고치면 `_fix_right_arm`은 저절로 무동작) / 캡슐에 붙은 꽃·책·진흙·톱밥은 뼈(spine_05/clavicle_l, pelvis, foot_r)에 / ada_street 첫 웨이포인트 (1430,−680)를 난간에서 떼기.

## 확인한 것 (어떻게)
- DX12: `tools\photo\shoot.ps1 -Auto <대본> [-Extra '-dpcvars=<cvar>=<값>']` 11회(환경 2차 전 2회 완주, 뒤 4회 죽음, Nanite 끄기 완주, 예약 리소스 끄기 죽음, 비동기 컴퓨트 끄기 2회 완주, ini 반영 뒤 기본 인자 완주). 판정은 게임 로그의 `GPU Crashed or D3D Device Removed` 유무와 `[mgauto] ... quit` 도달.
- 메타휴먼 API 이름: 커맨드릿 probe 스크립트로 `dir(unreal.MetaHumanCharacterEditorSubsystem)` 등을 덤프(25초). 빌드 스크립트 DRY 두 번(27초·23초).

## 확인 못 한 것
- 메타휴먼 자동 리깅·질감·빌드 단계(로그인 필요) — 사용자가 에디터를 열고 로그인하면 `python ue\tools\mh_remote.py ue\tools\mh_build.py PRESET=<이름> NAME=<이름>_mh HAIR=<WI_>`로 돌린다.

## 알려진 문제
- `ue/.uelock`이 남아 있으면(작업자가 비정상 종료) 40분 뒤에야 풀린다 — `python ue/tools/uelock.py release`로 손으로 푼다.

## 다음 작업자에게
- 병렬 작업자에게 UE를 시킬 때는 build.ps1·shoot.ps1만 쓰게 하고, 직접 커맨드릿을 띄우면 uelock acquire/release를 지시서에 적는다.
