# 2026-10-28 — 브랜치 정리

에이전트: Codex 메인. 하위 에이전트 호출: 없음.
커밋·push: 사용자 요청으로 main 병합 및 원격 브랜치 정리.

## 한 일
- 로컬 main을 최신 origin/main(b8d0811)으로 fast-forward.
- claude/busy-mccarthy-yzak4q의 사용량 기록 9커밋을 fast-forward로 반영.
- ccr-ae8e6087-ncdydt의 턴별 사용량 측정 기능 1커밋을 충돌 없이 병합.
- nonfiction_games 조사와 retrieval_v0 실험 원본(39499ea)은 원격 태그 archive/old-history-2026-10-19로 보존하고 동일한 옛 브랜치 둘을 삭제.
- 이미 번호를 바꾸어 반영한 claude/relaxed-babbage-11l0ha 원본은 archive/lecture-records-2026-10-20 태그로 보존한 뒤 정리. 반영 방식은 2026-10-25-branch-cleanup.md 참고.
- 나머지 브랜치는 main에 커밋이 포함되는지 확인하고 삭제. 원격 변경이 있으면 삭제가 거부되도록 각 브랜치의 확인한 커밋으로 lease를 지정.

## 확인한 것
- 정리 도중 원격에 추가된 p104 예측도 병합. 실측 칸 누락으로 완료로 취급되던 문제는 actual.status = "unknown"으로 명시하여 해결(실측 수치는 만들지 않음).
- python -m unittest discover -s tests -t .: 106개 통과.
- python -m domains.agent_usage.dispatches: 기록 문제 없음, 228건.
- python -m proviso validate agent_usage: 문제 없음.
- python -m proviso audit agent_usage: 오류 없음. 경고 22건은 개정 조건·시험 수단·바깥 상황 예외 관련.
- git diff --check origin/main..HEAD: 문제 없음.
- Windows에서는 PYTHONUTF8=1, PYTHONIOENCODING=utf-8로 실행. 최초 제한 환경의 테스트는 임시 폴더 접근 권한 때문에 실패하여 접근 가능한 환경에서 재실행.

## 다음 작업자에게
- 옛 실험은 보존 태그에서 복원 가능. main에 실험 코드를 다시 넣지는 않았음.
- 현재 작업을 별도 브랜치에서 계속하는 외부 세션은 정리된 main에서 다시 시작해야 함.
