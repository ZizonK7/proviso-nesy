# 2026-10-27 — movie_game 사건 1을 UE 5.8 프로토타입에 넣기 + 거리 건물 손질 (PC 세션)

메인: PC 세션(Fable 5.1)이 직접 구현. 하위 에이전트 호출: 없음 — 같은 UE 프로젝트·GPU를 둘이 동시에 쓰면 빌드 산출물(맵·DLL)이 겹쳐서 메인이 순서대로 했다.
커밋·push: movie_game main(아래 "커밋"), 이 저장소는 이 보고서·논리집 사실 1(F_ue_case01)과 함께(worktree에서 origin/main 위에).
지시서: movie_game `docs/briefs/case01-ue-brief.md`, `docs/briefs/facade-kit-brief.md`. 이야기 내용은 봉인(결정 21) — 여기는 구조·동작만.

## 한 일
- **C++ 게임 모듈** `ue/MovieGame/Source/MovieGame/`(새로, 약 2,400줄). 에디터 Python으로는 블루프린트 그래프를 만들 수 없어 장면 로직을 전부 C++로 두고, 레벨은 그대로 Python(`build_level.py`)이 만든다. 선택 이유: 손으로 만든 블루프린트는 build.cmd가 지우는 규칙과 맞지 않고, C++은 컴파일러(VS Build Tools 2022)가 이미 있었다.
  - `AMGDirector` — scene01.json을 읽어 플레이판 `template.html`의 상태 기계를 그대로 옮김(함수 이름도 맞춤: say/interject/advance, playCutscene/csFocus, qOn/qOpenStage, clickHotspot/pieceCard, observe(3초 잠금), openBoard/judge/pickReaction/confirmBoard(fill·한글 조사), conclude/showEnd, 플레이 로그 12칸 → `Saved/PlayLogs/case01_<날짜>.json`). `flow`(묶음·on_find·on_stage1_done·on_observe_first·after_reaction·skip_if_D1_confirmed·ask_requires_found·street_door_from)와 `staging`(C_first_insert 반 박자, on_find_K 하커 부인이 찻잔 쪽으로 한 걸음)을 처리.
  - `AMGHotspot`(상자 + 전용 트레이스 채널 Hotspot), `AMGAnchor`(살펴보기·관찰·컷씬 카메라 자리), `AMGTrigger`(221B 현관 밖·그레이프스 문 앞·통로 — 통로는 어둠 뒤 뒷방으로 옮김), `AMGDoor`(거리 문·안쪽 문, 경첩 회전), `AMGBlocker`(추리 ① 전 거실 문), `AMGNpc`(마네킹 + 뼈에 붙는 소품, 따라다님(빵부스러기)/앞서 걷기(웨이포인트)/서 있기/숨기; 플레이어를 막지 않음), `AMGKit`(건물 부품 인스턴스드 메시), `AMGCharacter`(3인칭 어깨 너머 걷기, Enhanced Input), `AMGPlayerController`(E·Q·B·T·Space·Esc·클릭·Tab).
  - `SMGHud`(Slate) — 자막 띠(영어 Georgia·한글 맑은 고딕을 글꼴 파일로 바로 읽음), 질문, 주머니, 보드(빈칸 버튼·카드·확정 뒤 fill + 작은 증거 이름·한글 조사), 카운트다운, 컷씬 띠·어둡게·금빛 고리(비춘 자리를 화면에 투영), 찾은 단서의 얇은 고리(살펴보는 중에만), 결론 큰 글자, 복도의 어둠, 시작·도움말·끝 화면.
  - 시점(결정 19): 걸을 땐 3인칭, E로 앵커(에이다·문턱·작업대)에 다가가 살펴볼 땐 1인칭 고정 시점 + 커서로 누름(찾기 전 표시 없음). 관찰(Q)은 그 시점으로 당겨 3초 잠근 뒤 2단계 핫스팟만 켠다. 컷씬도 같은 시점으로 당긴다.
  - 대사는 `secs_est`(음성이 있으면 음성 길이)만큼 머물다 저절로 넘어가고 Space로 먼저 넘긴다.
  - 자동 플레이 검사 `-mgauto=<대본>`: 줄마다 `<초> <명령>`(start·key·click·walk·tp·cam·shot·slot·adv·advto·flush·state·quit). 걷는 동안 대본 시계는 멈추고, 3초 제자리면 무엇에 막혔는지 적고 목적지로 옮긴다.
- **레벨** `ue/tools/case01_level.py`(새로, 약 330줄): 그레이프스(오른쪽 R10 자리) — 상점 전면(필라스터·파시아 THE GRAPES·콘솔·코니스·큰 유리·움푹한 문·허가 이름판·문 등·문턱 톱밥 G) + 술청(카운터·탁자·피아노·등) + 통로 + 뒷방(작업대·서랍 J·상자 H·메모 I·쪽지 L.·찻잔 K(김은 관찰 뒤)·천과 끌 L(관찰 뒤)·연장 줄·가방·대팻밥·석유등·높은 창·의자) + 벽장과 안쪽 문. 인물 넷 + 톰(+ 거리의 에이다, 끝 장면의 에이다): 마네킹(Quinn/Manny) + 코트 재질 + 소품(치마 3단, 소매 원통 — 왼쪽은 어둡고 번들거리는 젖은 천·오른쪽은 무광, 오른손 장갑·왼손 맨손+전보, 분필 M, 제비꽃 D, 읽기 책 N, 진흙 E·톱밥 F는 관찰 뒤에만, 톰의 헝겊, 하커 부인 앞치마, 우산). 핫스팟 12+2, 앵커 4(ada·grapes_door·bench·end), 트리거 3, 문 2, 차단막 1, 감독.
- **221B 고침**: 원래 프로토타입의 17계단은 현관 복도에서 올라갈 수 없었다(계단의 낮은 끝이 집 뒤쪽 막힌 자리에 있었고 복도 벽이 거실 문을 덮었다). 계단을 현관 쪽에서 뒤로 올라가게, 층계참을 뒤로, 거실 문을 오른쪽 벽 뒤쪽으로 옮겼다. 빗줄기 판은 충돌이 꺼지지 않아 보이지 않는 벽이었다(`no_collision` 도우미로 고치고 확인).
- **건물 손질** `ue/tools/facade_kit.py`(새로, 약 260줄): 부품 10개 — 창 모듈(구멍 + 10cm 후퇴 sash 틀·유리·턱·평아치 상인방), 문 모듈(반원 팬라이트·문·계단 2단·철책·등), 상점 전면, 1층 스터코 띠(홈 45cm)·경계 트림, 코니스·블로킹 코스·파라펫 45.7·숨은 슬레이트 지붕·굴뚝과 토관, 배수관·거터·받침·철책·지하 창살. 층고 370/330/300, 창 220×125/198×100/184×108/170×100. `FACADE_STAGE`(환경변수 0~4)로 단계마다 켠다. 작은 부품은 `AMGKit`에 재질별 인스턴스로 모아 액터 수를 억제(2,381 액터). 벽 구멍 자르기(`_wall_pieces`)를 구멍이 가로로 겹쳐도 되게 다시 썼다(문 위 창이 문을 막던 원인).
- 임시 음성(선택): `ue/tools/gen_voice.py` — Kokoro-82M(ONNX, Apache 가중치)로 75줄을 인물별 영국 목소리(bm_george·bm_lewis·bf_emma·bf_isabella·bm_daniel)로 뽑아 `tools/voice/`(git 제외) → 빌드가 `/Game/Baker/Voice`(8 MB, 커밋)로 가져오고 감독이 줄마다 튼다.
- 환경: `.NET Framework SDK`가 없어 에디터 타깃 규칙이 막힘 → 사용자 영역(HKCU) 레지스트리에 경로만 등록해 넘김(설치 엔진은 그 모듈이 이미 컴파일돼 있어 경로만 필요). 메모리에 적음.
- `ue/build.cmd`(C++ 빌드 → scene01.json 복사 → 레벨 생성), `ue/play.cmd`(221B 거실 `#Case`에서 시작), `DefaultEngine.ini`(게임 모드 → MGGameMode, Hotspot 트레이스 채널).

## 확인한 것 (어떻게)
- C++: `Engine\Build\BatchFiles\Build.bat MovieGameEditor Win64 Development -Project=…` → Result: Succeeded(경고를 오류로 보는 설정에서 0 오류).
- 레벨: `UnrealEditor-Cmd.exe … -run=pythonscript -script=build_level.py` → `[build] done: 2381 actors`, `[build] no problems`(음성 75줄 가져옴).
- 자동 플레이(PowerShell로 `UnrealEditor.exe <uproject> /Game/Baker/Maps/BakerStreet#Case -game -windowed -mgauto=auto1.txt`, 대본 106줄): 처음부터 끝까지 갔다. 로그(`Saved/Logs/MovieGame.log`의 `[mgauto]`)와 플레이 로그 `Saved/PlayLogs/case01_2026-10-27_2243.json`(사본 `ue/shots/2026-10-27_case01_autoplay_playlog.json`):
  - 시작 컷씬(M·N 비춤) → 살펴보기 A·B·C·D → Q 없이 관찰 = "Nothing to ask yet." → ada_03 뒤 시선 연출(B 비춤, 띠 없음) → Q1 + 2단계 → 관찰 3초 잠금 → E·F → 보드 ① 틀린 묶음(C·A·D) 반응 셋(place|C, time|A, thing|D), 장갑 반 박자 → 맞는 묶음 확정 → fill 문장(영·한, '선술집의', '전보를') → holmes_05 → ada_05로 Q2 → d1 끝에 거실 문 열림 → 계단 → 현관 트리거로 거리 묶음(에이다 앞서 걷기, 왓슨 따라옴) → 문 앞 트리거는 걷는 줄이 끝난 뒤에만 문 앞 줄 + 문 열림 → 통로 트리거 → 어둠 + harker_01 → 뒷방 → H·I·J(on_find 줄, 1단계 끝 줄) → T 묻기 → 관찰(harker_11 잠금 중, holmes_26 풀릴 때) → K(하커 부인 한 걸음)·L → 보드 ②(watson_05…) 틀린 묶음(H·A·J) 반응 + after_reaction watson_19 → 확정 → 2.2초 → 컷씬 가(H·I → 하커 부인) → 결론 큰 글자 → 안쪽 문 열림·톰 등장 → 끝 묶음(tom_02에 에이다 문간, harker_13에 들어옴) → 끝 화면. 로그 12칸: q1_open 29.0초, D1 44.4, D2 119.7, 끝 173.8(대본 속도), 틀린 삽입 3·3, 관찰 1·1, 스스로 찾음 1단계 7/10(G는 안 눌렀음)·2단계 4/4, 컷씬이 먼저 비춤 2.
  - 스크린샷(`ue/shots/2026-10-27_case01_*.jpg` 13장): 시작 컷씬, 살펴보기, Q1 시선, 관찰, 보드 ① 열림·확정, 그레이프스 문 앞, 뒷방 들어가기, 작업대 관찰, 보드 ② 확정, 컷씬 가, 톰, 끝 화면.
- 건물 손질: 단계 0(예전)·①·②·③·④를 같은 시점 셋(`?shot=street` 자리 / 보도에서 올려다보기 / 거리 끝) + 221B 옆에서 찍음 → `ue/shots/2026-10-28_facade_stage<n>_*.jpg`(20장, 화면 글자는 자동 검사 명령 `hud 0`으로 감춤). 본 것: ①(창 후퇴·틀·턱·상인방)만으로 '납작한 종이' 느낌의 큰 몫이 사라진다 — 창이 벽 안에 들어가 그림자가 생기고 밤에 꺼진 창도 창으로 보인다. ②는 1층(스터코 띠·상점 전면·문 모듈)이 거리의 눈높이를 채우고, ③은 지붕선(코니스·파라펫·굴뚝)이 하늘과 건물을 가르고, ④는 철책·배수관이 보도와 벽 사이를 잇는다. 지시서의 '①에서 멈출 조건'(①만으로 부족하면 보고)에는 걸리지 않았다. 액터 수 1,710 → 2,381(인스턴스 제외). 첫 촬영(stage ③)에서 GPU 드라이버 오류(Aftermath 페이지 폴트, VirtualShadowMapProjection) 한 번 — 오류 보고 창이 7시간 떠 있었다. 재현되지 않았고(다섯 단계 다시 찍어 모두 정상) 자동 검사 실행에는 `-unattended`를 붙였다.
- 마지막 빌드(건물 ④ + 결론 시점 넓힘 + 왓슨 자리)로 전체 검사 6회차(2026-10-28 06:07, 로그 `case01_2026-10-28_0607.json`): 막힘 없음, 결론 장면에서 하커 부인·톰·왓슨이 모두 화면 안에 들어오고 아무도 카메라를 가리지 않는다(왓슨은 벽장 문간에 서 있어 자리가 조금 어색함 — 아래 알려진 문제).
- 세션 중 돌린 전체 플레이 검사 다섯 번에서 고친 것: 왓슨이 문간을 막음(인물은 플레이어를 막지 않게), 거실 문·복도 벽·계단 방향(위), 빗줄기 판 충돌, 문 위 창이 선술집 문을 덮음(벽 구멍 알고리즘), 술청 등 높이·가구 위치, 마네킹에 재질이 안 입혀짐(재질 사용 플래그 used_with_skeletal_mesh / used_with_instanced_static_meshes), 벽 메모 글자 거울상.

## 확인 못 한 것
- 사람이 실제로 하는 플레이(사용자 몫). 마우스로 핫스팟을 실제로 누르는 손맛과 표시 없는 1단계를 스스로 찾는지(검사는 id로 눌렀다). 걷는 속도·공간 크기의 느낌.
- 음성 품질(듣지 못함) — 길이만 확인(75줄 합 약 5.5분). 원어민 감수 전.
- FPS 실측(자동 검사에서 안 쟀다). 액터 2,381 + 인스턴스 수천.
- MetaHuman·입 모양·얼굴 클로즈업(지시서 11의 '얼굴 연기')은 하지 않았다 — 마네킹.

## 알려진 문제
- 인물은 마네킹에 원통 소매·치마라 '눈으로 구분'은 되지만 거칠다. 젖은 왼쪽 소매는 번들거리는 어두운 천(무광 오른쪽과 대비) — 사용자가 알아보는지는 플레이 판정 몫.
- 컷씬의 '비추기'는 비춘 자리들을 감싸는 네모 밖을 어둡게 하는 방식이라, 자리가 둘이면 밝은 네모가 보인다.
- 2단계 관찰 중에도 살펴보기 시점이 고정이라 둘러볼 수 없다(설계대로 '시야 고정').
- 거리에서 에이다는 웨이포인트 6개를 따라 앞서 걷는데 길이 막히면 기다린다(내비메시 없음). 왓슨은 빵부스러기 추적이라 계단·문에서 가끔 뒤처진다.
- 자동 검사의 `walk`는 직선이라 가구에 걸리면 순간이동으로 넘긴다(사람은 돌아가면 된다).
- 보드의 카드 '끌어 놓기'는 없다(누르고 누르기).
- 결론 장면에서 왓슨이 벽장 문간에 서 있다(카메라를 안 가리는 자리를 고르다 보니). 자리는 `MGDirector.cpp` `Conclude()`의 한 줄.

## 다음 작업자에게
- 빌드·실행: `ue/build.cmd`(C++ → JSON 복사 → 레벨), `ue/play.cmd`(#Case). 코드만 바꿨으면 Build.bat만 다시. **게임 실행은 PowerShell로** — Git Bash는 `/Game/...` 맵 경로를 `C:/Program Files/Git/Game/...`로 바꾼다.
- 자동 검사: `-mgauto=<대본>`(scratchpad의 auto1.txt는 세션과 함께 사라지니 필요하면 이 보고서의 흐름대로 다시 쓴다). 막히면 로그의 `STUCK … blocked by <액터>`를 본다.
- 사용자 플레이 뒤: 끝 화면의 플레이 로그 JSON을 대화창에 붙이면 논리집 `[[judgment]]`(H_first_case_size 30분, H_two_stage_observation, H_observe_cost_and_question, H_wrong_piece_is_pruning, H_local_reaction_batch_confirm, H_ue5_fits_needs, H_clue_one_reading, H_conclusion_reads_as_sentence, H_no_fillable_dead_end, H_doubt_shown_not_explained, H_holmes_lead_same_info_leap, H_temp_voice_kokoro)로 옮긴다.
- 음성을 다시 뽑으려면 kokoro-onnx venv + 모델 둘(메모리 ue-cpp-build에 경로). `tools/voice/`가 있으면 빌드가 가져온다.
- 건물 손질 다음 단계(지시서 (나)): Fab/Megascans 기성 세트 한두 개를 옆에 놓고 비교 — 이번엔 안 했다.
