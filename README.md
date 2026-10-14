# proviso-nesy

**SELA: Self-Evolving Neuro-Symbolic Logic Architecture**

비싼 클라우드 LLM을 부를 때마다 그 결과를 로컬에 영구 자산으로 남겨서, 쓸수록 로컬 소형 모델이 스스로 처리하는 범위가 넓어지게 만드는 실험 프로젝트입니다.

## 아이디어

- **경험 논리집**: 수학 증명처럼 딱 떨어지는 논리가 아니라, "대체로 맞지만 예외가 있는" 실제 경험을 규칙으로 저장합니다. 규칙마다 목표, 조건, 방법, 이유, 근거, 부작용, 예외가 있고, 실패에서 배운 *단서 조항(proviso)*이 붙습니다.
- **로컬 우선, 막히면 클라우드**: 평소에는 로컬 소형 모델이 논리집을 써서 답하고, 막힐 때만 클라우드 LLM을 부릅니다.
- **클라우드는 가르치고 떠난다**: 불려 온 클라우드 LLM은 답만 주지 않고, 빠진 규칙을 논리집에 기록해 둡니다.
- **쓰면서 자란다**: 사용자가 결과를 보고 "잘됐다, 아쉽다"와 그 이유를 말하면, 규칙이 고쳐지거나 새 가설이 생깁니다.

원안: [논문 초안](docs/sela-paper-draft.md) · 원안에서 바뀐 점과 이유: [지식 양식 설계 기록](docs/knowledge-format-v0.md)

## 지금 되는 것

- 사람이 쓴 경험 규칙을 파일로 저장하고 검사합니다. 첫 분야는 Flowlog 앱의 제목 추천입니다.
- 규칙을 그래프로 자동으로 그립니다. 아래가 근거, 가운데가 규칙, 위가 목표입니다.
- 가설을 시뮬레이션이나 실제 사용 기록 재생으로 확인합니다.
- 의도와 실제가 어긋난 곳을 찾습니다. 목표를 해치는 동작인데 "대가로 받아들인다"는 기록이 없으면 문제로 표시합니다. 첫 발견: 뮤직 플레이어의 알아서 틀기에서 같은 곡이 다시 나올 수 있음.
- 논리집을 LLM 도구(MCP)로 내놓습니다. 첫 실험에서는 논리집을 쓴 Claude가 세 질문 중 둘에서 사용자 판단에 더 가까웠습니다. → [실험 보고서](docs/experiments/2026-10-14-body-v0.md)

아직 로컬 모델과 자동 학습은 없습니다.

## 실행

Python 3.11 이상이 필요하고, 추가 패키지는 필요 없습니다. 저장소 루트에서 실행합니다.

```powershell
python -m proviso validate flowlog   # 지식 파일 검사
python -m proviso graph flowlog      # out/flowlog-graph.html 생성 (브라우저로 열기)
python -m proviso check flowlog      # 가설 확인
python -m proviso audit music_player # 점검: 목표를 해치는데 받아들인 기록이 없는 것
python -m unittest discover -s tests -t .
python -m experiments.run_body_v0    # 논리집 유무에 따른 Claude 답 비교 (Claude Code 필요)
```

논리집을 Claude Code의 도구로 쓰려면 MCP 서버를 등록합니다. 방법은 `proviso/mcp_server.py` 맨 위에 있습니다.

## 구조

| 폴더 | 내용 |
|---|---|
| `proviso/` | 코어. 지식 파일 읽기·검사, 그래프, 조회, MCP 서버 |
| `domains/<분야>/` | 분야별 지식 파일(`knowledge.toml`)과 검사·시뮬레이션 |
| `experiments/` | 본체 실험 스크립트 |
| `docs/` | 원안 논문, 설계 기록, 실험 보고서 |
| `tests/` | 테스트 |
