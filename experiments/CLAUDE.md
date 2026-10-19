# experiments/ — 본체 실험 스크립트

LLM이 논리집을 도구로 쓸 때 답이 달라지는지 확인하는 실험. 실행은 저장소 루트에서 `python -m experiments.<스크립트>`.

- `run_body_v0.py`: 같은 질문을 Claude(헤드리스 `claude -p`)에게 A(논리집 없음) / B(proviso MCP 도구) 조건으로 묻고 `docs/experiments/`에 보고서를 쓴다. 원본 출력은 `out/experiments/`(git 제외).

- `retrieval_v0/`: 후보 뽑기 실험(1종·2종 오류, 조건부확률, 기대 효용). 외부 패키지는 그 폴더에서만. → [retrieval_v0/CLAUDE.md](retrieval_v0/CLAUDE.md)

## 규칙
- 실험 한 번 = Claude 구독 사용량을 쓴다. 돌리기 전에 몇 회 호출인지 사용자에게 알린다.
- 조건 간 공정성: 같은 모델, 같은 공통 지시, 빈 임시 폴더에서 실행, 파일·셸·웹 도구 차단. 다른 점은 논리집 도구 유무와 그 사용 지시뿐.
- 판정은 사용자가 한다(보고서의 "사용자 판정" 칸). AI가 판정을 대신 채우지 않는다.
- 실험을 바꾸면 새 버전 파일(`run_body_v1.py`)로. 이전 보고서와 비교할 수 있게.
