# domains/movie_game/ — 셜록 홈즈 추리 게임의 설계 판단

사용자의 게임 저장소 movie_game(github.com/ZizonK7/movie_game, 비공개 — 코드를 여기 옮겨 적지 않는다)에 대한 논리집. 2026-10-26에 만들었다.

## 역할과 기록 세 갈래 (사용자 결정 2026-10-26)
- 게임 저장소의 `CLAUDE.md`는 상태·맥락(메모리), `DECISIONS.md`는 사용자가 결정한 의도. **여기는 사용자나 Claude가 내린 판단의 논리 구조**(목표·조건·방법·이유·근거·시험 수단)다. 세 자리의 내용은 겹치지 않는다.
- 사용자 의도는 DECISIONS.md가 원문이고, 여기 목표 노드는 그것을 논리 구조에 올린 것이다. 의도가 바뀌면 DECISIONS.md가 먼저 바뀌고 이 파일이 따른다.
- 판단 중 Claude가 추정한 것은 `hypothesis`로, `source`를 밝혀 넣는다. 사용자가 말하지 않은 목표·관찰을 지어내 넣지 않는다.
- 다른 분야와 같이, 조각 문장에는 분야·앱 이름을 쓰지 않는다(다른 분야에서 다시 쓰게).

## 현재 상태 (2026-10-27 밤)
- 목표 9(G_game 아래 여덟: 디자인 우선·스토리·머리 쓰기·눈썰미·균형·논리·**공간 걷기**·**영어 음성·영국 느낌**), 상태 2, 조사 사실 22(배치 23 화풍·비용 9 + 배치 24 공간·음성·추리 장치 13), 관찰 5, 가설 9(살아 있는 것 8: 사용자 생각 둘 H_wrong_piece_is_pruning·H_two_stage_observation, AI 판단 여섯 H_own_art_with_code_frame·H_pieces_board_serves_reasoning·H_local_reaction_batch_confirm·H_observe_cost_and_question·H_ue5_fits_needs·H_voice_two_pass; H_code_made_look은 전제가 틀려 물림). 판정 기록 없음 — 모두 프로토타입 → 사용자 판정 대기(audit 경고 "시험 수단 없음"은 의도).
- 조사 원본: `out/research/2026-10-26-movie-game-design/`(화풍·비용), `out/research/2026-10-26-movie-game-needs/`(공간·음성·추리 장치, 모두 git 제외). 작업 보고서: [docs/worklog/2026-10-26-movie-game-design-research.md](../../docs/worklog/2026-10-26-movie-game-design-research.md), [docs/worklog/2026-10-26-movie-game-needs-research.md](../../docs/worklog/2026-10-26-movie-game-needs-research.md). 설계 문서 v0(필요한 것)는 비공개 아티팩트 https://claude.ai/artifact/A4V1CCN1n5Hm19Ko6Phq8q (저장소 md는 사용자 허락 대기).
- **판단 기준에서 뺀 것(사용자, O_user_no_solo_limit)**: 비용·기간·1인 선례. 사실 노드에는 남기되 가설의 근거로 쓰지 않는다 — "뭘 하려면 뭐가 필요한가"만.
- 2026-10-27: 사용자 PC 세션이 프로토타입 둘(Three.js·UE 5.8)을 만듦(F_proto_v0). 사용자 1차 반응은 "건물이 종이 쪼가리 같다"(O_user_paper_buildings) — "이 느낌인가" 판정은 아직. 엔진 결정도 아직.
- 2026-10-27 배치 26: 첫 사건 크기 조사(단편 4편 구조·관찰 조각·게임 사건 크기·대본 표본·입면 치수) → 사실 5, 가설 H_first_case_size. 사용자 결정: 추리 규칙의 첫 시험은 게임 안 플레이로, 사전 피드백은 크기만. 보고서 [docs/worklog/2026-10-27-movie-game-first-case-research.md](../../docs/worklog/2026-10-27-movie-game-first-case-research.md).
- 2026-10-27 사용자 결정 13–17: 크기 OK(H_first_case_size 첫 판정 지지, 플레이 판정은 아직), 실제 런던·빅토리아(G_real_london_victorian), 사건 단위 + 수렴(G_story_converges)이되 한 방식만으로 가지 않음(G_convergence_not_single_mode), 수렴점 한 장 + 사건 하나씩(H_story_fixed_end_open_cases, 사용자 채택), **지금은 플레이 장면 하나를 만드는 단계**(S_one_scene_stage). 명세는 movie_game `docs/first-case-v0.md`.
- 2026-10-27 저녁: 첫 장면 "젖은 왼쪽 소매" v0 설계(F_scene01_design) — 메인이 여기서 글로 끝까지 설계(핫스팟 12·빈칸 2·반응 8·대사 18), PC는 짓기만. 사용자 방침: "컴퓨터에서 못 하는 것은 미리 해 간다".
- 2026-10-27 밤, 첫 플레이 피드백(브라우저 플레이판): 사용자가 "홈즈가 왜 갑자기 '집에서 곧장 왔나'를 궁금해하는지 모르겠다"(O_user_q1_no_trigger). 질문이 대본(에이다의 말)만으로 켜졌던 것이 원인 → **질문 = 말 + 플레이어가 본 조각**으로 고치고 H_question_from_seen을 세움. H_observe_cost_and_question 첫 판정 '일부'(틀은 판정 전, 질문의 출처가 빠졌음). 판정 기록 3.
- 2026-10-27 밤, 플레이 피드백 3–5회차: 보드 막다른 길(H_no_fillable_dead_end), 단서 읽기(H_clue_one_reading), 확정 문장(H_conclusion_reads_as_sentence), 홈즈가 조사 전에 아는 순서(H_reason_findable 사용자 판정 '일부'). 플레이판 v4는 "질문 = 본 것 + 들은 말".
- 2026-10-27 밤, PC 밖 초안(배치 29): 수렴 사례(F_r_convergence_cases)·수렴 틀 가설 셋, 임시 음성(F_r_tts_local, H_temp_voice_kokoro). 보고서 [docs/worklog/2026-10-27-movie-game-drafts.md](../../docs/worklog/2026-10-27-movie-game-drafts.md). 사용자 판정 대기.
- 2026-10-27 밤, 플레이 피드백 5–6회차와 결정 18–20: 홈즈의 앞선 추리(같은 재료·홈즈만의 도약·컷씬, H_holmes_lead_same_info_leap), 시점(3인칭 걷기+1인칭 살펴보기), 수렴 방향(선택 분기 안 함·원작은 반영만). Q1은 되묻기+전보로 시선(H_doubt_shown_not_explained), 거짓말엔 설계된 이유(H_lie_has_reason_not_now). 실제 화면 10장에 대한 사용자 판정(O_user_ref_shots_1·2). 설계서·PC 지시서는 플레이판 v7 기준으로 갱신됨.
- 2026-10-27 밤, 수렴점 시안 넷(메인이 직접 씀, 비공개 아티팩트 https://claude.ai/artifact/6atfXRyzcC9zwDZDByiZ79 — 사용자가 "맡겨도 되는지 보겠다"고 해서 시험 쓰기). 피드백 대기. 남은 수렴 질문은 결정 20·21로 닫힘.
- 2026-10-27, 사용자 결정 21 **이야기 봉인**(O_user_story_sealed): 수렴점·사건 내용은 AI가 쓰고 사용자는 플레이로 판정. **이 논리집에는 이야기 내용을 적지 않는다**(공개 저장소) — 구조(방식·줄기 수·증상 유무·약점·결정 준수)만. 내용은 movie_game `docs/story/`(봉인, 사용자 안 읽음). 진짜 수렴점 v3까지 썼다(배치 33: 비평 2바퀴 p92·p94 + 역사 확인 p93, 메인 약품 확인). 구조: 줄기 넷+배경, 사람 넷, 사건 여섯, 증상 다섯, 재구성은 2번부터. 새 가설 H_question_leaves_eye_to_player(질문은 조각도 눈도 가리키지 않는다). 보고서 [docs/worklog/2026-10-27-movie-game-convergence-sealed.md](../../docs/worklog/2026-10-27-movie-game-convergence-sealed.md).
- 2026-10-27 밤, PC 세션: 사건 1(이야기 v2)이 UE 5.8 프로토타입에서 처음부터 끝까지 돈다(F_ue_case01, 보고서 [docs/worklog/2026-10-27-movie-game-case01-ue.md](../../docs/worklog/2026-10-27-movie-game-case01-ue.md)). C++ 감독이 플레이판의 상태 기계를 그대로 옮겼고, 거리 건물은 부품 10개로 다시 지었다. 자동 플레이 검사만 했고 사용자 플레이 판정은 아직 — 판정이 오면 가설 12개(H_first_case_size·H_two_stage_observation·H_observe_cost_and_question·H_wrong_piece_is_pruning·H_local_reaction_batch_confirm·H_ue5_fits_needs·H_clue_one_reading·H_conclusion_reads_as_sentence·H_no_fillable_dead_end·H_doubt_shown_not_explained·H_holmes_lead_same_info_leap·H_temp_voice_kokoro)에 `[[judgment]]`.
- 다음: 사용자가 `ue/play.cmd`로 플레이(처음 한 번이 판정, 결정 22) → 판정 기록 → 사건 2. 화풍은 그 뒤.
