# 2026-10-27 — movie_game: PC 밖 초안 넷 (배치 29)

메인: 클라우드 세션(이 세션 도중 사용자가 모델을 Fable 5.1 → Opus 5.5로 바꿈). 사용자 요청: "잠깐 못 오는데 PC에서 안 해도 되는 다른 것들 초안 만들어 보고 있을래?"
에이전트: 클라우드 'searching' Haiku 둘(p79·p80), 세션 안 Opus 둘(p81·p82). 수렴 틀 작업자(p82)의 보고서는 따로 있다: [2026-10-27-movie-game-convergence-draft.md](2026-10-27-movie-game-convergence-draft.md).
커밋: 메인만. movie_game 저장소 파일은 하나도 고치지 않았다(모두 제안).

movie_game은 비공개 저장소라 대사·예시 스토리 내용은 여기 옮기지 않고 구조와 위치만 적는다.

## 한 일
- **p79 수렴 방식 사례 조사**(클라우드 Haiku): 사건 단위로 가다 끝에서 모이는 작품 14편, 방식 여덟 갈래, 억지/납득 조건. 원본 `out/research/2026-10-27-movie-game-drafts/p79-convergence.md`(git 제외, 수정판).
- **p80 임시 영어 음성 조사**(클라우드 Haiku): 로컬 TTS 13개·API 4개, 라이선스, PC에서 돌릴 순서, UE 가져오기. 원본 `.../p80-temp-voice.md`.
- **p81 첫 장면 영어 대사 검수**(Opus): 고칠 안 33건(확신 높음 4·중간~높음 3). 원본 `.../p81-dialogue-review.md`.
- **p82 수렴 방식 예시판 + 수렴점 한 장 틀**(Opus): 비공개 아티팩트 https://claude.ai/artifact/VSGa73nvh5aZjiT1Lc6Nmr .
- **메인 — 설계서·PC 지시서 갱신 제안본**: movie_game `docs/first-case-scene-v0.md`와 `docs/briefs/case01-ue-brief.md`를 플레이판 v4 규칙(질문 = 본 것 + 들은 말, 보드는 질문의 관찰 뒤, 확정 문장에 증거의 뜻, 찾은 단서 다시 보기, 막히지 않게)으로 고친 전체본과 차이. 세션 scratchpad에만 있고, 사용자 허락 뒤 덮어쓴다(movie_game md 규칙).
- **메인 — 정리 페이지** "PC 밖 초안 묶음": 비공개 아티팩트 https://claude.ai/artifact/MM1P1Zfgz9xzBr7ksEtkXJ (정할 것 다섯, 대사 검수 표, 음성 추천, 제안 차이).
- **논리집**: 사실 `F_r_convergence_cases`, `F_r_tts_local`, 가설 `H_temp_voice_kokoro`(메인), `H_strand_stands_alone`·`H_reuse_confirmed_conclusions`·`H_convergence_faces_early`(p82 제안).

## 확인한 것 (어떻게)
- p79 1차 보고서를 읽고 줄거리 사실 7곳을 짚어 같은 작업자에게 원문 문장 인용으로 재확인시킴(send_message 1회) → 역전재판 3 Dahlia "살아 있음"(실제는 사형 뒤 영혼 빙의), Armando가 쓰러진 사건, 단간론파 얼터 에고 결말, 출처 번호 어긋남이 고쳐짐. p82는 수정판만 입력으로 받음.
- p80의 1순위 MeloTTS를 메인이 원문으로 확인: `curl https://raw.githubusercontent.com/myshell-ai/MeloTTS/main/README.md` → 영국 화자 EN-BR 하나(화자 목록 EN-Default·EN-US·EN-BR·EN_INDIA·EN-AU), "MIT License ... free for both commercial and non-commercial use". Kokoro README → "British English" lang_code 'b', "Apache-licensed weights". 그래서 인물 다섯을 나누려면 Kokoro가 낫다고 판단해 추천을 바꿈.
- 정리 페이지: Playwright로 1280(밝게)·390(어둡게) 렌더 → 가로 넘침 없음, 확신 거르기 버튼 동작(높음 → 7행), 콘솔 오류 0.
- p82 페이지는 작업자가 1280·390에서 렌더 확인했다고 보고. 메인은 텍스트를 뽑아 [원문 확인] 사실만 쓰였는지와 "사용자 결정 아님" 표시(4곳)를 확인.

## 확인 못 한 것
- 대사 검수는 원어민 감수가 아니다. 시대 어휘(these three days, odd jobs 등)는 사전으로 확인하지 않았다.
- Kokoro 영국 목소리 여덟의 이름 목록(bf_*·bm_*)은 p80 작업자가 Hugging Face에서 확인했다고 보고했고, 이 환경에서는 Hugging Face가 막혀 메인이 다시 확인하지 못했다.
- UE 5.8의 Dialogue Wave·자막 현지화는 공식 문서 본문을 못 열어 검색 요약만.
- p82 예시의 역사 사실(검시 절차, 전당포 등)은 "역사 확인 필요"로 표시된 채다.
- p79에서 대역전재판·레이튼·코난·몬크는 원문을 못 열어 빠졌다.

## 알려진 문제
- 설계서 md에는 "해커 부인", JSON에는 "Mrs Harker"(검수 제안은 "하커"). 설계서 갱신 허락 때 같이 정한다.
- p82 예시 B의 첫 사건 씨앗(왓슨이 발표한 이야기 한 장)은 지금 첫 장면에 없다(페이지에 "붙인다면"으로 표시).

## 다음 작업자에게
- 사용자가 돌아오면 정리 페이지의 "정할 것" 다섯을 차례로 받는다: 설계서·지시서 덮어쓰기 허락 → 대사 고침 반영(scene01.json은 바로 고칠 수 있음) → 설계 확인 넷 → 임시 음성(PC 세션 일) → 수렴 질문 다섯.
- 대사를 고치면 플레이판 자동 시험(`proto/scene01-play/src/playtest.js`)의 문장 비교(D1·D2 확정 문장, holmes_01 시작 문장)도 같이 고쳐야 한다.
