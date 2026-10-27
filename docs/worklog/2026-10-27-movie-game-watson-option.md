# 2026-10-27 — movie_game "플레이어 = 왓슨" 2안 그림 (설계 비교 한 장)

에이전트: 설계 보조 (Opus 5.5, effort high), 지시서 p77. 하위 에이전트 호출: 없음.
커밋·push: 안 함.

## 한 일
- 첫 장면 scene01("젖은 왼쪽 소매")을 재료로 두 안을 나란히 그린 HTML 한 장을 만들었다:
  `/tmp/claude-0/-home-user/4c61238f-f399-5c21-adf6-a32a67daf323/scratchpad/watson01/watson-option.html` (약 48 KB, 제목 "홈즈냐 왓슨이냐"). 메인이 비공개 아티팩트로 올림: https://claude.ai/artifact/J5JcZjXqky9GwM81jAsSzJ.
  - 1안 플레이어 = 홈즈: 사용자가 좋다고 한 흐름 (나) "먼저 제시 → 찾기". 핵심 장치는 의심 카드의 빈칸 **"걸린 것: [ ]"** — 홈즈 속말이 이유 없이 의심만 던지고(holmes_q1a), 플레이어가 본 조각(A)을 넣으면 holmes_01 + "Then where has she been?"(holmes_q1b)이 나오고 그때 2단계 관찰이 열린다. 지금 플레이판의 방식은 변형 (가)로 따로 적었다.
  - 2안 플레이어 = 왓슨: "홈즈가 주장하고, 나는 증명한다." 홈즈(같이 걷는 NPC)가 되묻고("Straight from home, Miss Pryce?"), 왓슨에게 "Not at her face"만 귓속말, 왓슨이 A를 찾으면 "Quite so. Now — where was she, and for how long?"으로 2단계가 열린다. 현장에서는 "She knows him, Watson. Prove it to me." 보드 확정이 홈즈 결론 줄의 열쇠. 의사만 읽는 조각(L). watson_05는 대본이 아니라 플레이어가 J를 넣을 때만 나간다.
  - 페이지 구성: 한눈에(두 카드 + 단계별로 누가 하는지 흐름도 SVG) / 박자 1–5 나란히(역할 6칸 + 대사, 추가 줄 표시) / "그러네?"가 생기는 자리 / 목표 대조표(G_player_reason·G_player_observe·G_balance·G_logic·G_walk_space·G_english_british, 전부 추정 표시) / 위험과 장치 / 선례 5 / 제3안 / 판정 질문 5.
- 새로 쓴 대사(영어 + 한글, 페이지에 "추가"로 표시): 1안 holmes_q1a, holmes_q1b, holmes_q1x, holmes_g(선택), holmes_q2a(선택), holmes_q2b. 2안 holmes_w1, ada_w1, holmes_w2, watson_t1(holmes_01 문장을 왓슨이 생각), holmes_w3, holmes_w4("Excellent, Watson." — 원작 Silver Blaze 말버릇에서), holmes_w6, watson_t2, watson_t3, watson_end(선택). 후보: "What is it, Holmes?", "Your department, Doctor.", "Why do you say so, Holmes?"(제3안).
- 지시서 밖: 없음.

## 확인한 것 (어떻게)
- 재료를 읽음: movie_game `DECISIONS.md`(1–17), `docs/first-case-scene-v0.md`, `content/case01/scene01.json`(대사 18줄·반응 8·Q1 trigger), proviso-nesy `domains/movie_game/knowledge.toml`(G_*, H_reason_findable, O_user_holmes_first_ok, H_question_from_seen 반박 판정 등). 플레이판 `proto/scene01-play/src/template.html`에서 holmes_01이 Q1 열릴 때 끼어드는 구조를 grep으로 확인.
- 페이지 태그 짝: Python `html.parser`로 열고 닫힘 검사 → 짝 안 맞는 태그 없음.
- 렌더: 전역 Playwright(`/opt/node22/lib/node_modules/playwright`)로 1280px 밝은 화면, 390px 어두운 화면 전체 스크린샷 → `scrollWidth`가 각각 1280·390(가로 넘침 없음). 화면을 한 번 보고 박자 번호 글꼴만 고침(IM Fell의 "1"이 "I"처럼 보여서).
- 선례 확인(WebSearch mode standard, 4회):
  - "Great Ace Attorney Dance of Deduction …" → 결과 en.wikipedia.org/wiki/The_Great_Ace_Attorney:_Adventures, twinfinite.net(가이드), aceattorney.fandom.com, destructoid.com. 요약: 숌즈가 관찰로 틀린 추리를 펼치고 플레이어가 현장을 다시 봐서 고친다.
  - "Frogwares … play as Watson …" → Watson 관련 결과 없음.
  - "Sherlock Holmes Versus Jack the Ripper playable Watson …" → store.steampowered.com/app/11190, arthur-conan-doyle.com 위키. 요약: 홈즈와 왓슨을 바꿔 조작.
  - "Testament of Sherlock Holmes playable Watson Toby …" → en.wikipedia.org, destructoid.com, outcyders.net 등 리뷰. 요약: 홈즈·왓슨·토비 조작.
  - "Disco Elysium Kim Kitsuragi …" → en.wikipedia.org/wiki/Kim_Kitsuragi, gamebanshee.com, GDC 2023 PDF. 요약: NPC 파트너, 기록·심문, 반응자.
- 원문 열기(curl, 15초): en.wikipedia.org(두 문서), aceattorney.fandom.com, twinfinite.net, media.gdcvault.com PDF → 모두 응답 000. store.steampowered.com, www.gutenberg.org → 프록시가 connect_rejected.
- 도일 원작 두 대목("You have been in Afghanistan, I perceive." — A Study in Scarlet 1·2장 / "most of your conclusions were erroneous" — Hound 1장)은 앞선 조사 p74의 `out/research/2026-10-27-movie-game-case/p74-script-material.md`(Gutenberg 원문에서 복사했다고 적힘)에서 가져왔다. 이번 세션에서 Gutenberg를 직접 열지는 못했다.

## 확인 못 한 것
- 선례 원문 전부(대역전재판·디스코 엘리시움·Frogwares 두 편): **검색 요약만**. 이 저장소 규칙상 근거로 약하다. Frogwares 두 편에서 왓슨 구간이 어떻게 나뉘고 추리를 하는지는 확인 못 함.
- "You see, but you do not observe"(Scandal in Bohemia) 같은 원작 대사는 확인 못 해서 쓰지 않았다.
- 페이지의 아티팩트 게시(메인 몫), 아티팩트 뷰어 안에서의 실제 모양(로컬 Playwright로만 봄).
- 두 안 모두 플레이로 시험하지 않았다. 목표 대조표·느낌 서술은 전부 추정.
- 변형 (가)(지금 플레이판)를 고친 뒤 사용자가 플레이 판정을 했는지: worklog `2026-10-27-movie-game-scene01-play.md`에 Q1 언급이 없어 기록을 못 찾음.

## 알려진 문제
- **2안은 결정 7과 충돌한다**: DECISIONS 7은 "플레이어가 셜록이 되어 … 돌아다니며". 2안을 고르면 사용자가 이 결정을 바꿔야 한다. 결정 3의 "셜록의 눈썰미를 직접 발휘"도 2안에서는 "셜록이 본 것을 왓슨이 찾는다"로 다시 읽어야 한다(해석은 추정). 페이지에 둘 다 적었다.
- 2안의 "Quite so. Now — where was she, and for how long?"은 D1의 빈칸 종류(장소·시간)를 미리 알려 준다. 힌트 세기가 적당한지는 플레이로만 안다.
- 1안의 새 대사 holmes_q1x("A violet says nothing about the road from home.")는 걸림 칸 전용이다. 기존 반응표(D1 장소 칸의 D 반응)와 문장이 겹치지 않게 썼지만, 같은 장면에서 제비꽃 반응이 두 번 나올 수 있다.
- AI가 쓴 영어 대사는 원어민 검토 전.

## 다음 작업자에게
- 사용자 판정이 필요한 것은 페이지 끝 "판정 질문" 5개. 답하려면 같은 scene01을 **1안 (나)와 2안 두 판**으로 해 봐야 한다. 플레이판(`proto/scene01-play/`)에 시점 전환 스위치를 넣는 것이 가장 짧은 길로 보인다(추정). 1안 (나)는 걸림 칸 + holmes_q1a/q1b, 2안은 홈즈 줄을 소리 대사로 바꾸고 watson_05를 J 입력에 묶는 정도. movie_game 쪽 md·content·proto는 이번에 고치지 않았다.
- 논리집에 올릴 가설 후보(사용자 판정 전, source = "ai"로):
  - **H_watson_prove**: "플레이어를 왓슨으로 두고 홈즈가 주장(의심·질문·결론)을, 왓슨이 증명(조각 찾기·보드)을 맡게 하면 '먼저 제시 → 이유 찾기'가 자연스럽게 서고 홈즈의 몫이 화면에 보여 균형을 맞추기 쉽다. 다만 결론을 홈즈가 말하면 플레이어가 '뺏겼다'고 느낄 수 있다." serves G_player_reason, G_balance, G_logic. evidence O_user_holmes_first_ok + 도일 원작(왓슨 서술). against: G_walk_space(결정 7의 "셜록이 되어"). 시험: 판정 질문 2·5.
  - **H_doubt_slot**: "인물이 먼저 던진 의심에 '걸린 것' 빈칸을 붙여 플레이어가 이미 본 조각을 넣게 하면, '왜 궁금한지 알겠다'가 그 입력 순간에 생기고 그 뒤 2단계 관찰이 목적을 갖는다." H_reason_findable의 방법 쪽. 시험: 판정 질문 1.
  - **H_wrong_piece_in_companion_mouth**: "플레이어 = 홈즈일 때 틀린 조각을 왓슨 입으로 먼저 말하게 하고 홈즈가 쳐내면, 홈즈의 날카로움을 지키면서 가지치기가 산다." H_wrong_piece_is_pruning의 방법 쪽. 시험: 판정 질문 4.
  - **H_companion_marker_risk**: "동행 홈즈의 멈춤·시선이 정답 표지가 되면 '다 보여 주는 탐정 시야'의 사람 판이 된다." evidence F_r_detective_vision_failures. 시험: 판정 질문 3.
- 선례를 근거로 쓰려면 원문을 열 수 있는 환경(클라우드 `searching` 환경)에서 대역전재판 추리 무도·Frogwares 왓슨 구간을 다시 확인해야 한다.
