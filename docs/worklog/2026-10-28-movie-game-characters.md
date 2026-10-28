# 2026-10-28 — movie_game 인물 두 길 시험: 메타휴먼 vs 로컬 AI(그림 → 3D → 리깅) (PC 세션)

사용자 지시: "지금은 디자인(보이는 것)만, 인물 먼저"(2026-10-28, md는 건드리지 않음). 플레이 판정은 뒤로.
에이전트: 메인(PC 세션, Fable 5.1) 혼자. 하위 에이전트 없음. 이야기 내용은 봉인(결정 21) — 여기는 인물의 겉모습만.

## 한 것

### 공통 준비
- `ue/tools/char_test.py`(새로): 환경변수 `CHAR_TEST="이름=에셋,kind,scale|h<키cm>,yaw,dz;…"`로 221B 에이다 자리(와 그 옆 95cm 간격)에 시험 인물을 세우고 마네킹 에이다를 숨긴다. kind: `skel`(스켈레탈 메시, AMGNpc + 새 `SetupBodyAsset`) / `static` / `bp`(메타휴먼 블루프린트). `h163`처럼 쓰면 메시 높이를 재서 키를 맞추고 발바닥을 바닥에 놓는다. `build_level.py`가 case01 뒤에 부른다(변수 없으면 아무것도 안 함).
- `AMGNpc::SetupBodyAsset(MeshPath, AnimPath, Scale, Offset, Yaw)`: 아무 스켈레탈 메시로 몸을 바꾼다.
- `ue/tools/import_mesh.py`(새로): GLB/FBX를 `/Game/Baker/Char/<이름>`으로 헤드리스 가져오기(`MESH_LIST`). Interchange가 UniRig GLB를 스켈레탈 메시 + 스켈레톤 + 피직스 + 질감으로 가져온다.
- 자동 검사 명령 `hud 0`(화면 글자 숨김), 사진 대본 `auto_char.txt`(hud 0 → look ada → shot).

### 길 1: 로컬 AI (사용자 샌드박스 `Desktop/Folder/sandbox` 도구 모음, `C:\ai\venvs\*` 그대로)
그림(Z-Image-Turbo NF4, Apache 2.0, 장당 33초) → 배경 제거(BiRefNet, CPU 10초) → TripoSR(MIT, 2.5GB, 3초) → 블렌더 5.2 정리(1만 2천 면, 정점색 → 1024 질감 굽기, 3초) → UniRig(MIT, 골격 50초 + 스킨 35초 + 합치기) → UE 가져오기 → 221B에 세움. **인물 하나 2분 30초**, 전부 로컬·무료·상업 가능 라이선스.
- 그림은 좋다(에이다: 남색 워킹드레스·보닛·한쪽 장갑까지 프롬프트대로). `ue/shots/2026-10-28_char_concept_{ada,holmes}.jpg`.
- 3D는 샌드박스 테스트 결과표의 평("형태 시안용, 표면 울퉁불퉁") 그대로: 실루엣은 읽히지만 **얼굴이 뭉개져** 살펴보기(1인칭 2m) 시점에는 못 쓴다. 뼈 28개, 모든 점에 가중치(check_rig). 4방향: `ue/shots/2026-10-28_char_local_{ada,holmes}_4view.jpg`, 221B: `ue/shots/2026-10-28_char_local_221b.jpg`.
- glTF 정면(+Z)이 UE에서 +X가 되어 yaw를 90 더 돌려야 했다(스크립트 인자로 해결).
- 로컬 그림 생성에는 이 PC의 `~/.cache/huggingface`가 아니라 `C:\ai\hf-cache`(120GB)를 `HF_HOME`으로 줘야 한다. 샌드박스 스크립트는 셸에서 그 변수를 잡고 돌린 것이라 내 드라이버(`local_pipeline.sh`, scratchpad)에서 명시했다.

### 길 2: 메타휴먼 크리에이터 (UE 5.8 내장 플러그인, Python API)
- 플러그인 `MetaHumanCharacter`를 프로젝트에 켬. 처음엔 Core Data(프리셋 29·머리 모양·피부 질감 모델·기본 옷 1벌, 6.5GB)가 없어 "limited features" — 사용자가 Epic Games Launcher에서 설치(엔진 옵션).
- 헤드리스(커맨드릿)에서 되는 것: 프리셋 복제(`EditorAssetLibrary.duplicate_asset`, 단 `scan_paths_synchronous('/MetaHumanCharacter')`를 먼저 해야 에셋 레지스트리가 플러그인 콘텐츠를 안다), 머리·눈썹·속눈썹·옷(wardrobe item) 끼우기, `assemble_for_preview`.
- 헤드리스에서 안 되는 것: **자동 리깅과 피부 질감은 Epic 서버**라 로그인이 필요한데, 로그인이 "브라우저에서 코드 입력"(EOS device code) 방식이라 커맨드릿은 10분 기다리다 `EOS_Auth_PinGrantExpired`. 로그에 코드도 안 찍힌다.
- 해결: 에디터를 열고 Python 원격 실행(`bRemoteExecution=True`, `remote_execution.py`)으로 같은 스크립트를 보냄 → 에디터에 로그인 창이 뜨고 사용자가 한 번 로그인 → 자동 리깅 약 35초, 질감(얼굴 11초 + 몸 15초), 빌드(OPTIMIZED·MEDIUM). 인물 하나 약 3분. 빌드 결과 `/Game/Baker/MH/Build/<이름>/…/BP_<이름>`(블루프린트, 몸·얼굴 스켈레탈 메시, 그룸, 옷) + `Common/`(얼굴 컨트롤 리그 등 공용) = **817MB** → `.gitignore`(스크립트로 재생성 가능).
- 에이다 빌드 때 "Cannot break link … CR_MetaHuman_HeadMovement_IK_Proc" 오류가 났지만 결과 에셋은 다 나왔다(공용 컨트롤 리그를 복사하면서 난 것으로 보임, 홈즈는 오류 없음).
- 빅토리아 옷은 없다. Fab에 메타휴먼용 빅토리아 드레스·하녀복·빈티지 탐정 묶음(긴 코트·조끼)이 있으나 가격·품질은 사용자가 브라우저에서 봐야 한다(fab.com이 에이전트 접근을 403으로 막음). 직접 만든 옷을 wardrobe item으로 넣는 공식 절차가 있다.

### 길 3 (사용자 결정 뒤): 메타휴먼 + 직접 만든 옷 — 통로 뚫기
사용자(2026-10-28): "사실풍에 시각적 품질 높게, 옷은 우선 직접 만들어 보자" → 메타휴먼 얼굴·몸에 직접 만든 빅토리아 옷을 입히는 통로를 만들었다.
- 구조(빌드된 BP를 스폰해 확인): `Body`(SkeletalMeshComponent, 뼈대 `metahuman_base_skel`, 성별·체형별 공용 폴더) ← `Face`(자식, 얼굴 뼈대·ABP_Face) ← 그룸 5(머리·눈썹·속눈썹·수염·콧수염), `Outfits` 스켈레탈 메시들은 Body의 자식 + **LeaderPose = Body**. 즉 옷 = 몸 뼈대에 가중치 붙인 스켈레탈 메시.
- 통로: ① 몸 메시 FBX 내보내기(`AssetTools.export_assets`, 커맨드릿은 **`-AllowCommandletRendering`** 필요 — 없으면 `Assertion failed: MeshObject`로 죽음) → ② 블렌더 5.2 `bl_garment.py`: 몸(LOD0) 복사 → 손·머리·범위 밖 지우고 법선 방향 1~2cm 부풀림(가중치는 몸 것 그대로) + 치마·코트 자락은 회전체를 Data Transfer(가장 가까운 면 보간)로 가중치 받음 + 보닛은 head 뼈에 100% → 옷 부품 + 아머추어만 FBX로(`ignore_leaf_bones=False` — head가 잎 뼈라 빠지지 않게) → ③ `import_mesh.py`에 `MESH_SKEL_FROM=<몸 메시>`를 주면 그 뼈대로 스켈레탈 메시 가져오기(legacy FBX 임포터, 여러 메시가 한 스켈레탈 메시의 재질 섹션으로 합쳐짐) → ④ `char_test.py` bp 항목의 6·7번째 칸: 옷 에셋들을 SkeletalMeshActor로 스폰해 Body에 붙이고 `set_leader_pose_component(Body)`, 기본 옷 컴포넌트(`SkeletalMesh`, `SkeletalMesh1`)는 숨김.
- 몸 메시는 머리가 없다(얼굴 메시가 목까지 덮음). 몸 메시 꼭대기 1.17m(에이다), 뼈 neck_01 1.31m. 앞 방향은 foot→ball 뼈로 잡았다.
- 함정: Git Bash에서 `CHAR_TEST=/Game/...` 같은 **환경변수 값도** `C:/Program Files/Git/Game/...`으로 바뀐다 → `MSYS_NO_PATHCONV=1`.
- 통로 증명: 코드로 지은 거친 드레스(보디스·종 치마·깃·보닛)와 프록코트(몸·자락·깃·바지)가 메타휴먼에 붙어 몸 뼈대를 따른다 — `ue/shots/2026-10-28_char_cloth_{ada,holmes}.jpg`. 여섯 번 돌려 고친 것: 빌드된 몸 메시는 기본 옷 아래(몸통·허벅지)가 잘려 있어 옷 바탕으로 못 씀 → 지오메트리 내보내기(`export_geometry`, Slate 필요라 에디터 `-unattended` + 원격)로 옷 없는 전신을 뽑음 / 회전체 법선 안쪽 / 만든 오브젝트를 아머추어에 붙일 때 부모 체인 0.01 스케일로 100배 축소(`matrix_parent_inverse`) / 허리 둘레를 재면서 A포즈 팔까지 포함해 치마가 집채만 해짐(몸통 가중치 점만) / 팔 소매로 살이 뚫고 나옴(LOD0 강제로도 안 잡힘 — 남은 문제, 표준 해법은 옷 아래 몸 숨김 마스크나 여유 2cm 이상).
- 사용자 결정(2026-10-28): 코드 생성 옷은 여기까지(품질 안 나옴). **옷은 블렌더로 직접 모델링**(유료 도구·구매보다 먼저). 넘긴 것: `art/metahuman_body/{Ada,Holmes}_body.blend`(옷 없는 전신 몸 + 뼈대, 미터 단위, Body 잠금, Clothes 컬렉션, READ_ME 텍스트), `ue/tools/blender/make_body_template.py`(바탕 만들기), `ue/tools/blender/export_garments.py`(Clothes 컬렉션 → 가중치 자동 이전 → FBX), 가져오기·입히기는 `import_mesh.py`(MESH_SKEL_FROM) + `char_test.py`.

### 길 4 (사용자 지시 "옷은 있는 걸로 대충, 다른 모델링부터"): 환경 — 질감·가구·종이 단서
- **AI 질감 타일**: Z-Image-Turbo(로컬)로 "seamless tileable, top-down, flat lighting" 프롬프트 12장(벽지 다마스크·참나무 마루·페르시아 양탄자·크림 회벽·런던 벽돌·젖은 자갈·초록 벨벳·마호가니·검은 대리석·책등·판석·더러운 회벽, 장당 33초) → `make_pbr.py`(가장자리 반 칸 밀어 섞기로 이음새 제거, 높이→법선(소벨), 밝기 반전 거칠기) → `ue/tools/textures/ai_<이름>_{d,r}.jpg·_n.png`(25MB). `build_level.py`의 `AI_MATS`가 있으면 기존 삼면투영 재질을 바꿔 끼운다(벽지·마루·회벽·벽돌 셋·자갈·판석·벨벳 초록/빨강·마호가니·대리석, 양탄자는 UV). 선술집은 `plaster_dirty`·마호가니 틴트 오크(case01_level `ai_tri`). 사진 수준으로 나온다 — 사실풍의 가장 싼 지렛대.
- **블렌더 가구**(`ue/tools/blender/make_furniture.py` → `ue/tools/furniture/*.fbx`, 400KB): 윙백 안락의자(베벨), 받침 탁자(회전체), 책장(코니스), 벽난로 둘레(필라스터·상인방·선반 몰딩·주철 테), 커튼(**재봉 핀 + 천 시뮬레이션 60프레임**으로 주름), 커튼 상자. `build_level.py`가 FBX를 가져와(`FURN`) 재질 슬롯 이름(Velvet·Mahogany·Marble·Iron·Curtain)으로 M을 끼우고 상자 가구 대신 놓는다(`furniture()`). 함정: **UE FBX 가져오기가 Y를 뒤집는다** — 블렌더에서 -Y가 앞이면 UE에서는 +Y가 앞. 책장이 벽을 보고 있었다.
- **종이 단서**(`make_papers.py`, PIL): 1887 우체국 전보 용지(Old English 머리글 + Lucida Handwriting 손글씨, 젖은 모서리), 치수 메모 + L의 쪽지(French Script, 다른 손), 전당표(Script MT). 텍스트는 scene01.json의 봉인 내용 그대로(전보 문구·이름). 플레인 메시에 양면 재질로 에이다 손·뒷방 벽·서랍에 끼움(`PLANE`, `M['paper_*']`).
- 자동 검사 명령 `body 0`(플레이어 몸 숨김, 환경 사진용) 추가.
- 사진: `ue/shots/2026-10-28_env_*.jpg`(거실 벽난로·창·책장·에이다 살펴보기, 선술집 문·술청·뒷방·작업대, 거리).

## 확인한 것 (어떻게)
- 두 길 모두 221B 같은 자리·같은 빛에서 사진: `ue/shots/2026-10-28_char_pair_{ada,holmes}.jpg` (왼쪽 로컬 AI, 오른쪽 메타휴먼, 살펴보기 시점 fov 58·2.25m).
- 내 눈(사용자 판정 아님): 같은 2.25m 시점에서 메타휴먼은 얼굴·손·피부가 사람으로 읽히고, 로컬 AI는 옷의 실루엣과 색만 읽히고 얼굴은 뭉개진 덩어리다. 메타휴먼의 약점은 옷(기본 티셔츠·반바지뿐)과 프리셋 얼굴이 이야기의 나이·인상과 다르다는 것(그레이스·올랜도 프리셋은 나이 든 얼굴·흰머리). 로컬 길의 강점은 그림 단계에서 옷·소품·시대가 자유롭다는 것.
- 따라서 섞는 길이 보인다: 메타휴먼 얼굴·몸(사실풍) + 빅토리아 옷은 그림→3D로 만든 옷 메시를 wardrobe item으로 입히기(공식 절차 있음) 또는 Fab 구매. 다만 이건 화풍 결정(사실풍인가)에 걸려 있다.

## 확인 못 한 것
- 직접 만든 옷의 애니메이션 변형(걷기)과 소매 뚫림의 원인(가중치 영향 수 제한인지, 빌드된 몸과 내보낸 몸의 미세 차이인지).
- 메타휴먼의 걷기·표정: 빌드 결과는 A포즈. 몸 애니메이션은 UE5 마네킹 → 메타휴먼 리타게팅(`Animation/Retargeting/RTG_MH_IKRig`) 또는 Core Data의 `UEFNAnimPreset/Locomotion`을 붙여야 한다. 입 모양(Animator 오디오)도 아직.
- 로컬 길의 리깅 품질(걷기 애니를 붙여 보지 않았다). UniRig 뼈 이름이 표준이 아니라 리타게팅 매핑이 필요하다.
- Stable Fast 3D(질감 포함, 8GB)는 HF 로그인 미완으로 안 돌렸다. TRELLIS.2(MIT)는 클라우드 GPU가 필요.
- Fab 옷 가격.

## 알려진 문제
- 메타휴먼 Core Data 설치와 Epic 로그인은 사람이 해야 한다(세션마다 로그인 1회).
- `Content/Baker/MH/`(817MB)·`Content/Baker/Char/`는 생성물. MH는 git 제외, Char는 작아서 커밋.
- 3인칭 넓은 사진(`c_wide`)은 플레이어 등이 가려 쓸모없었다 — 살펴보기 시점(`look ada`)만 씀.

## 다음 작업자에게
- 로컬 길 한 번에: scratchpad `char/local_pipeline.sh <이름> <정면 그림>` (사라지면 이 보고서의 단계대로 샌드박스 스크립트를 이어 부르면 된다: remove_bg → run_triposr → blender_cleanup → UniRig generate_skeleton/generate_skin/merge → check_rig). `HF_HOME=C:\ai\hf-cache`.
- 메타휴먼 한 번에: 에디터 열기 → `mh_remote.py mh_build.py`(scratchpad; 핵심은 duplicate_asset → try_add_item_from_wardrobe_item → request_auto_rigging(blocking) → request_texture_sources(blocking) → build_meta_human). 로그인 창은 사람이.
- 둘 중 무엇을 쓰든 `CHAR_TEST`로 221B에 세워 보고, 실제 채용 시 `case01_level.py`의 `npc()`가 `setup_body_asset`을 부르게 바꾼다.
