# 2026-11-05 — README.md 갱신

에이전트: 하위 에이전트 (Opus 5.5, effort 낮음). 하위 에이전트 호출: 없음.
커밋·push: 안 함.

## 한 일
- `README.md`를 다시 썼다. 절: 목적(2026-11-05 새 목적, 원안은 출발점 한 줄) · 무엇이 있나 · 구조(`feedback/` 포함 7폴더) · 분야(7개) · 실행 · 논리 조각(보류 후보 한 줄).
- 루트 CLAUDE.md와 겹치지 않게 결정 경위·체크리스트·날짜별 상태는 빼고 사람용 소개만 남겼다. 비공개 저장소(movie_game, music_player)의 코드·이야기 내용은 적지 않았다.

## 확인한 것 (어떻게)
- `ls domains` → 7개 분야가 README 표와 일치. 루트 폴더(`docs domains experiments feedback proviso scripts tests`) 일치.
- 저장소 루트에서 돌림: `feedback check`(문제 없음), `feedback topics`, `feedback --help`, `proviso validate/graph/check flowlog`, `proviso audit music_player`, `agent_usage.dispatches`, `predict p04`, `holdout` → 모두 종료 코드 0. `flowlog.replay`는 인자 없이 종료 코드 2(사용법 안내, 백업 파일이 필요).
- `python -m unittest discover -s tests -t .` → 실패 1: `tests.test_computable.Devices.test_audit_has_no_errors_now` (계산 조각 `C_turns_files_scale`의 방향 주장 관련 audit 오류). README 변경과 무관, 고치지 않음.

## 확인 못 한 것
- `feedback find`는 돌리지 않았다.
- `experiments.run_body_v0`는 `--help`가 없어 실제로 실행됐다(Claude 호출 6회, 끝까지 돎). 그 결과 `docs/experiments/2026-10-14-body-v0.md`를 덮어써서 `git checkout`으로 되돌렸다. README에 "사용량을 쓰고 보고서를 다시 씀"을 적었다.

## 알려진 문제
- 위 테스트 실패 1건(메인 확인 필요).

## 다음 작업자에게
- `run_body_v0`는 인자 없이도 바로 실험을 돌린다. 확인용으로 돌리지 말 것.

## 읽은 피드백
- 읽은 파일: `feedback/main/common.md`, `feedback/main/docs.md`, `feedback/main/brief.md`.
- 따른 항목: F080(비공개 저장소 내용·식별자 안 옮김), F077(README에 경위·날짜 기록을 쌓지 않음), F010(파일 못 쓰면 답장 — 해당 없었음, 파일에 씀).
