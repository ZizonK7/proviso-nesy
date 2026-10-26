# domains/movie_game/ — 셜록 홈즈 추리 게임의 설계 판단

사용자의 게임 저장소 movie_game(github.com/ZizonK7/movie_game, 공개)에 대한 논리집. 2026-10-26에 만들었다.

## 역할과 기록 세 갈래 (사용자 결정 2026-10-26)
- 게임 저장소의 `CLAUDE.md`는 상태·맥락(메모리), `DECISIONS.md`는 사용자가 결정한 의도. **여기는 사용자나 Claude가 내린 판단의 논리 구조**(목표·조건·방법·이유·근거·시험 수단)다. 세 자리의 내용은 겹치지 않는다.
- 사용자 의도는 DECISIONS.md가 원문이고, 여기 목표 노드는 그것을 논리 구조에 올린 것이다. 의도가 바뀌면 DECISIONS.md가 먼저 바뀌고 이 파일이 따른다.
- 판단 중 Claude가 추정한 것은 `hypothesis`로, `source`를 밝혀 넣는다. 사용자가 말하지 않은 목표·관찰을 지어내 넣지 않는다.
- 다른 분야와 같이, 조각 문장에는 분야·앱 이름을 쓰지 않는다(다른 분야에서 다시 쓰게).

## 현재 상태 (2026-10-26 저녁)
- 목표 9(G_game 아래 여덟: 디자인 우선·스토리·머리 쓰기·눈썰미·균형·논리·**공간 걷기**·**영어 음성·영국 느낌**), 상태 2, 조사 사실 9, 관찰 5, 가설 5(살아 있는 것 4: H_own_art_with_code_frame, H_pieces_board_serves_reasoning, H_wrong_piece_is_pruning, H_two_stage_observation; H_code_made_look은 전제가 틀려 물림). 판정 기록 없음 — 모두 시안·프로토타입 → 사용자 판정 대기(audit 경고 "시험 수단 없음"은 의도).
- 조사 원본: `out/research/2026-10-26-movie-game-design/`(git 제외). 작업 보고서: [docs/worklog/2026-10-26-movie-game-design-research.md](../../docs/worklog/2026-10-26-movie-game-design-research.md).
- **판단 기준에서 뺀 것(사용자, O_user_no_solo_limit)**: 비용·기간·1인 선례. 사실 노드에는 남기되 가설의 근거로 쓰지 않는다 — "뭘 하려면 뭐가 필요한가"만.
- 다음: 공간(3D)·영어 음성·두 단계 관찰·가지치기 추리에 각각 무엇이 필요한지 조사 → 설계. 화풍은 그 위에서 다시.
