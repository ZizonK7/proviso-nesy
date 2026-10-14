# proviso-nesy

**SELA: Self-Evolving Neuro-Symbolic Logic Architecture**

비싼 클라우드 LLM을 부를 때마다 그 결과를 로컬의 영구 자산으로 남겨서, 쓸수록 로컬 소형 모델이 스스로 처리하는 범위가 넓어지게 만드는 실험 프로젝트입니다.

## 아이디어

- **경험 논리집**: 성공한 경험에서 얻은 추론 규칙과, 실패한 경험에서 얻은 *단서 조항(proviso)*, 즉 "이럴 때는 이 규칙이 안 통한다"를 함께 저장합니다.
- **로컬 우선, 막히면 클라우드**: 평소에는 로컬 소형 모델이 논리집을 써서 답합니다. 말을 못 알아듣거나 쓸 규칙이 없을 때만 클라우드 LLM을 부릅니다.
- **클라우드는 가르치고 떠난다**: 호출된 클라우드 LLM은 답만 주지 않습니다. 빠진 규칙과 번역 사례를 로컬 논리집에 기록해 두고 떠납니다.
- **3단계 성장**: 즉시 캐시에 반영하고, 야간에 미세조정하고, 프로젝트가 성공했는지 실패했는지에 따라 규칙 신뢰도를 갱신합니다.

자세한 내용은 [논문 초안](docs/sela-paper-draft.md)을 참고하세요.

## 상태

초기 실험 단계입니다. 사람이 쓴 경험 규칙을 파일로 저장하고, 그래프로 그리고, 가설을 시뮬레이션으로 확인하는 데까지 됩니다. 아직 언어 모델은 붙어 있지 않습니다.

## 실행

Python 3.11 이상이 필요하고, 추가로 설치할 패키지는 없습니다. 저장소 루트에서 실행합니다.

```powershell
python -m proviso validate flowlog   # 지식 파일 검사
python -m proviso graph flowlog      # out/flowlog-graph.html 생성 (브라우저로 열기)
python -m proviso check flowlog      # 가설 확인
python -m unittest discover -s tests -t .
python -m experiments.run_body_v0    # 논리집 유무에 따른 Claude 답 비교 (Claude Code 필요)
```

논리집을 Claude Code의 도구로 쓰려면 MCP 서버를 등록합니다. 자세한 방법은 `proviso/mcp_server.py` 맨 위에 있습니다.

## 구조

| 폴더 | 내용 |
|---|---|
| `proviso/` | 코어. 지식 파일 읽기·검사·그래프 |
| `domains/<분야>/` | 분야별 지식 파일(`knowledge.toml`)과 검사·시뮬레이션 |
| `docs/` | 원안 논문, 설계 기록, 실험 보고서 |
| `experiments/` | 본체 실험 스크립트 |
| `tests/` | 테스트 |
