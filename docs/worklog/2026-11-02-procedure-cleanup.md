# 2026-11-02 — 절차 정리: 빠지던 단계를 검사로, 루트 CLAUDE.md 줄이기

에이전트: 메인(클라우드 세션) 직접. 하위 에이전트 호출: 없음.
커밋·push: 함(브랜치 `ccr-c6ac578b-w4b0vj`).

## 왜
사용자: "애들이 이 레포 읽어도 보고서 먼저 안 쓰거나 할 때도 많더라." 기록으로 세어 보니(p65 이후 73건, main + 브랜치 셋):
- 검사가 막는 단계는 지켜졌다: 구간이 빗나가면 `review.wrong`·`why` 72/73.
- 문서에만 적힌 단계는 빠졌다: `--turns` 턴 길이 표는 세션 안 하위 에이전트 53건 중 4건(p105·p106, 브랜치 두 곳의 p107). 수능 분석 22건(배치 35–36, `claude/busy-mccarthy-yzak4q`)은 이 저장소에 보고서가 없다(수능 저장소 쪽은 확인 못 함).
- 문서는 길고 일기처럼 쌓였다: 루트 2.8만 자(가장 긴 절이 "지금 상태"의 경위), agent_usage 3.8만 자(배치별 "현재 상태"와 "지난 고리"). 꼭 할 절차가 그 사이에 묻혀 있었다.

사용자 결정: 이전 기록은 다시 재지 않는다. 빠지던 단계는 기존 양식(칸 + 이유 문장)에 칸을 더해 검사가 막게 하고, 메인 md를 줄여 작업마다 그 폴더 문서를 읽게 한다. 브랜치 합치기는 정리 뒤에.

## 한 일
- `scripts/agent_usage.py`: `--turns --toml`(기록에 그대로 붙일 `[dispatch.turns]` 블록: 동작마다 n·sum_s·turn_s·tool_s·out_chars·ctx_k), `--after <시각>`(이어 보낸 회차만).
- `domains/agent_usage/dispatches.py`: 2026-11-03부터 끝난 기록은 `[dispatch.turns]`(또는 `skip = "이유"`)와 `review.report`(이 저장소 경로면 파일이 있어야 함, 다른 저장소면 `"저장소:경로"`)가 없으면 오류. 번호가 아니라 날짜로 자른다 — 브랜치를 합치며 번호를 다시 매겨도 지난 기록이 걸리지 않게.
- 테스트 3개 추가(`tests/test_agent_usage.py` 2, `tests/test_agent_usage_domain.py` 1).
- 루트 `CLAUDE.md`(2.8만 → 1.7만 자): 지도·공통 규칙·확정된 결정·분야 표·체크리스트만. 문서 규칙에 "루트는 짧게", "꼭 할 단계는 검사가 막게"를 더함. 다음 할 일 0번에 브랜치 합치기.
- 옮김(옮기기 전 글 그대로): 루트의 agent_usage·stock-rader·언어 학습·지금 상태 절 → `docs/history.md`. 하위 에이전트 운영의 자세한 것과 웹 조사 주의 → `docs/dispatch.md`. agent_usage의 배치별 현재 상태·지난 고리 → `domains/agent_usage/history.md`.
- `domains/agent_usage/CLAUDE.md`(3.8만 → 2.8만 자): 고리 3단계를 "사용자에게 말하기 전에 기록부터 + 턴 길이 표 + 보고서 경로"로, 전제 1 측정 현황, 짧은 "지금 상태", 흩어져 있던 다음 정리 후보를 "다음 정리에서 할 것" 일곱으로 모음.
- 루트에서만 있던 내용을 분야 문서로: movie_game "그 저장소 md는 제안 → 허락 뒤 수정", language_learning 여행 앱 설계 문서 위치, flowlog 출시 준비 기준 문서. `docs/CLAUDE.md`·`scripts/CLAUDE.md`·`dispatches.toml` 머리말에 새 파일·칸 설명.

## 확인한 것 (어떻게)
- `python -m unittest discover -s tests -t .` → 109개 통과.
- `python -m domains.agent_usage.dispatches` → 기록 문제 없음(231건). 브랜치 셋의 `dispatches.toml`도 새 검사에서 오류 0(모두 11-02까지의 기록).
- `python -m proviso validate <분야>` 다섯 분야 모두 문제 없음.
- 옮기다 빠진 문장 없음: 정리 전 루트의 줄마다 새 루트·`docs/history.md`·`docs/dispatch.md` 중 어딘가에 그대로 있는지 대조 → 다른 줄은 일부러 고친 제목·표 4줄뿐. agent_usage도 같은 대조 → 고쳐 쓴 2줄뿐.

## 확인 못 한 것
- 실제 대화 기록으로 `--turns --toml`을 돌려 보지 못했다(이 컨테이너에는 하위 에이전트 기록이 없다). 테스트의 가짜 기록으로만 확인.
- 다른 세션이 새 체크리스트를 실제로 따르는지는 다음 보내기부터 본다.

## 알려진 문제
- 말한 구간(`predicted.told`)과 빗댄 기록(`analog`)은 여전히 칸 모양만 검사한다(빠져도 안 막음). 지금까지는 told 73/73으로 지켜졌다.
- `README.md` 구조 표는 분야 셋만 적혀 있다(사람용, 이번 범위 밖).
- 브랜치 `claude/inspiring-edison-igoees`가 루트 CLAUDE.md의 movie_game 줄을 고쳤다 — 합칠 때 이 정리본을 따르고 그 내용(스토리 줄거리 층)은 `domains/movie_game/CLAUDE.md`(그 브랜치도 고침)에 있는지 확인.

## 다음 작업자에게
- 하위 에이전트를 보낸 뒤 기록에 `[dispatch.turns]`와 `review.report`를 안 넣으면 2026-11-03부터 테스트가 실패한다. 클라우드 세션은 `skip = "클라우드 세션: 대화 기록 없음"`.
- 브랜치 셋 합치기: `dispatches.toml`의 p107–p121 번호를 다시 매긴다(2026-10-25 p40–p64 방식, `docs/worklog/2026-10-25-branch-cleanup.md`).
