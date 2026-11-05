# proviso-nesy

**지난 실수에서 배워 나아지는 AI 작업 기록 장치**

## 목적

이 저장소의 목적은 **이전의 실수들을 통해 발전해 나가는 것**입니다(2026-11-05부터). 여기서 "실수"는 틀린 답만이 아니라 "그때로 돌아가면 그렇게 하지 않을 것"을 모두 뜻합니다 — 결과는 괜찮았어도 돌아갔거나 비쌌던 선택, 사용자가 싫어하거나 좋아한 것. 곧 **피드백**(일을 해 본 뒤 남기는 "다음엔 이렇게")입니다.

AI가 일을 시작하기 전에 그 일에 걸리는 피드백을 읽고 들어갑니다. 꼭 읽을 짧은 목록(메인 피드백)과, 전부를 모아 목차로 찾아보는 백서(whitepaper) 두 층입니다. 그때 알 수 없었던 것은 피드백으로 남기지 않습니다. 바뀐 이유: [목적 변경 기록](docs/purpose-2026-11-05.md)

출발점은 [SELA 원안 논문](docs/sela-paper-draft.md)(경험을 규칙으로 모아 로컬 소형 모델이 독립하게 한다)이었고, 비용 절감 목표는 접었습니다.

## 무엇이 있나

- **피드백**: 지난 실수에서 나온 "다시 하면" 문장. 일의 종류별 메인 파일과 백서.
- **논리집**(경험을 목표·조건·방법·이유·근거로 적은 파일): 모든 주장은 가설이고 성적표를 받습니다. "확인됨" 딱지는 없고, 틀리면 조건을 더해 쪼갭니다. 판정 중에는 사용자의 실사용 판단이 가장 무겁습니다.
- **점검**(`audit`): 목표를 해치는 동작인데 "대가로 받아들인다"는 기록이 없으면 문제로 표시합니다. 의도와 실제가 어긋난 곳이 실패 전에 드러납니다.
- **하위 에이전트 시간 예측**: AI가 일을 나눠 맡긴 다른 AI가 얼마나 걸릴지 미리 말하고, 실측과 견줘 스스로 고칩니다.

## 구조

| 폴더 | 내용 |
|---|---|
| `proviso/` | 엔진. 분야를 모르고, 지식 파일을 읽고 검사하고, 성적표·점검·그래프·조회를 만들고, Claude가 도구로 쓸 수 있게(MCP 서버) 내놓습니다 |
| `domains/<분야>/` | 분야별 논리집과 그 분야 전용 검사·계산 |
| `feedback/` | 피드백: 일의 종류별 메인 파일(`main/`)과 백서, 검사·찾기 명령 |
| `experiments/` | 논리집이 있을 때와 없을 때 Claude의 답을 비교한 실험 |
| `docs/` | 원안 논문, 설계 기록, 실험 보고서, 하위 에이전트 작업 보고서 |
| `scripts/` | 하위 에이전트 대화 기록에서 사용량 숫자를 뽑는 도구 |
| `eda/` | 쌓인 데이터를 표로 펼쳐 둘러보는 노트북(탐색적 데이터 분석) |
| `tests/` | 테스트 |

## 분야

| 분야 | 무엇 |
|---|---|
| `flowlog` | 활동 기록 앱 Flowlog의 제목 추천. 실제 사용 기록을 되감아 추천 적중률을 셉니다 |
| `music_player` | 음악 앱의 '알아서 틀기'와 재생 순서. 점검이 같은 곡이 다시 나오는 문제를 잡아 앱을 고친 첫 사례 |
| `agent_usage` | 하위 에이전트가 걸릴 시간과 쓸 토큰을 예측해 이유와 함께 말하기. 사용자 대신 실측이 판정합니다 |
| `language_learning` | 일본어를 전혀 모르는 사용자가 여행용 일본어를 꾸준히 공부할 시스템의 설계 근거 |
| `movie_game` | 추리 게임을 만들며 내린 설계 판단의 논리 구조(게임 저장소는 비공개라 판단만 둡니다) |
| `far_fields` | 사용자가 모르는 먼 분야의 현장 경험칙을 분야 이름 없는 조각으로 모은 것(창의 연결의 재료, 보류 후보) |
| `study_time` | 수업 정리·복습 한 회차에 걸릴 공부 시간을 근거와 함께 예상하고 실측과 견줘 고치기 |

## 실행

Python 3.11 이상, 추가 패키지 없음. 저장소 루트에서 실행합니다.

```powershell
python -m feedback check                   # 피드백 모양 검사
python -m feedback topics "<일 설명>"       # 그 일에 읽을 메인 피드백
python -m feedback find <낱말>             # 색인 낱말로 백서 찾기
python -m proviso validate flowlog         # 지식 파일 검사
python -m proviso graph flowlog            # out/flowlog-graph.html 생성 (브라우저로 열기)
python -m proviso check flowlog            # 성적표: 가설마다 확인과 판정을 출처별로
python -m proviso audit music_player       # 점검: 목표를 해치는데 받아들인 기록이 없는 것
python -m domains.agent_usage.dispatches   # 하위 에이전트 예측과 실측 비교
python -m domains.agent_usage.predict p04  # 계산기: 상황 값으로 시간 계산과 근거
python -m domains.agent_usage.holdout      # 앞 기록으로 세운 조각을 뒤 기록으로 시험
python -m domains.flowlog.replay <백업 파일> # 실제 Flowlog 백업으로 추천 적중률 (백업은 저장소 밖)
python -m eda.export                       # 논리집·작업 기록·피드백을 out/eda/*.csv로 (EDA용)
python -m unittest discover -s tests -t .
python -m experiments.run_body_v0          # 본체 실험 (Claude Code 필요, 사용량을 쓰고 보고서를 다시 씀)
```

Windows Git Bash에서 한글이 깨지면 `PYTHONIOENCODING=utf-8`을 앞에 붙입니다. EDA 노트북 `eda/start.ipynb`는 `pip install -r eda/requirements.txt`(pandas·matplotlib·jupyterlab) 뒤 `jupyter lab`으로 엽니다. 논리집을 Claude Code 도구로 쓰려면 `proviso/mcp_server.py` 맨 위의 등록 방법을 따릅니다.

## 논리 조각

규칙을 앱 이름 없는 작은 조각으로 쪼개 조합하는 방향([논리 조각 v0](docs/pieces-v0.md))은 새 목적의 줄기 밖이라 보류 후보입니다(사용자 결정 전).
