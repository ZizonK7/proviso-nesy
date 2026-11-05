# 2026-11-05 — agent_usage 계산기 해설서 (지시서 p237, 배치 69)

에이전트: 계산기 설명서 (Opus 5.5, effort high). 하위 에이전트 호출: 없음.
커밋·push: 안 함.

## 한 일
- 새 파일 `docs/agent-usage-calculator-explainer.html`: 계산기 해설서 원본(논문·비문학 지문 문체, 한국어). 절: 1 문제 설정 · 2 데이터(표 1–5, 그림 1 칸별 내력 시간표) · 3 계산기 구조(식 1–6, 그림 2 흐름도, 표 6 살아 있는 조각, p224 계산 예) · 4 맞추기(식 7–8, 표 7 다시 맞추기) · 5 시험과 장치(표 8) · 6 주변 모델(손 규칙·빗댄 기록·크기·비율 조각 표 9·보낼까) · 7 현재 성적(표 10–11, 파일 수 증거, 사용자 물음의 답) · 8 개입 지점(표 12 탐색 질문, 표 13 구조, 표 14 수집) · 부록 A 문서와 코드가 어긋난 곳 · 부록 B 용어. 글꼴은 Google Fonts `<link>`(본문 Noto Serif KR, 제목·표 Noto Sans KR, 대체 WenQuanYi Zen Hei), 그 밖은 HTML 안에 다 있다(SVG 그림 둘 포함).
- 새 파일 `docs/agent-usage-calculator-explainer.pdf`: A4 17쪽, 쪽 번호. Playwright Chromium으로 렌더 — 글꼴 요청을 가로채(`page.route`) 세션 스크래치에 받아 둔 Noto TTF 넷으로 채웠다. 렌더 스크립트·글꼴은 저장소 밖(`/tmp/claude-0/-home-user-proviso-nesy/ec76c9a9-00b3-54f7-8760-5d7a9e233ed8/scratchpad/explainer/render.js`, `fonts/`).
- `docs/CLAUDE.md`에 두 파일을 적은 줄 하나.
- 그 밖의 파일은 건드리지 않았다. `--write` 명령은 하나도 돌리지 않았다.

## 확인한 것 (어떻게)
모두 저장소 루트, `PYTHONIOENCODING=utf-8`. 직접 쓴 스크립트는 `PYTHONPATH=. python <경로>`이고 읽기만 한다(폴더 `…/scratchpad/explainer/`, 출력 `…/explainer/out/*.txt`). 메인 세션의 스크립트(`…/scratchpad/refit_dry.py` 등)도 다시 돌려 메인이 본 숫자와 같은지 확인했다 — 모두 같았다.

### 숫자 → 낸 명령
| 문서의 숫자 | 명령 |
|---|---|
| 기록 362(끝난 352, 멈춤 6, 모름 4), 출처 d 117·dR 8·p 237, 저장소별 수, 모델·effort 표, 날짜별·기간별 끝난 수와 실제 구간(표 3), 칸별 있음·처음 날짜(표 4), 상태별 적힘·값 분포(표 5), 기록당 상태 중앙 20(2–26), 파일 순서에서 날짜가 거꾸로인 49건, 먼 분야 묶음 28건(턴 34·분 14.8·분당 2.41), files 59·빈 표 18·after 11·결과 전 0 아닌 끝난 25(exam_grader 12·gemmin 11·stock-rader 2), turns 표 74·skip 25, why 분포(94·3·3·1), decide 69건 모두 보냄, agent 이름 54 | `explainer/eda.py` → `out/eda.txt` |
| 기록 문제 없음 362건, 말한 구간 228건 중 149 맞음, 손 vs 계산기 161건(47·55·17·42), 걸침 115건 등 | `python -m domains.agent_usage.dispatches` → `out/dispatches.txt` |
| 홀드아웃 뒤 62건: 39 %·50 %·손 63 %, 앞 64건, 최종본 142/352(모름 67) vs 손 233/352 | `python -m domains.agent_usage.holdout`, `python -m domains.agent_usage.predict --all` |
| 조각 범위와 맞춤 수(26/43 등, 표 6 '맞춤') | `python -m domains.agent_usage.fit final`(쓰기 없음) |
| 조각별 시험 크기·방향(24/151 등, 표 6), R_turns_analogy_v2 107/166·113/206, R_time_turns_v2 102/200, R_say_numbers_v3 60/66, R_send_or_not 55/66, m001 22.4M vs 9.4M | `python -m proviso check agent_usage` → `out/check.txt` |
| audit 오류 1(C_turns_files_scale 0/4)·경고 24(14·8·2), 예외 p06·p07·p130 | `python -m proviso audit agent_usage` |
| 크기 모델 시험 65건(1/65 모름 40 · 15/65 · 3/65 · 43/56 · 56/65) | `python -m domains.agent_usage.size` |
| 빗댄 기록 규칙 v2 시험 32건: 규칙 22 · AI 31 · 손 32 → 실패, 범위 ×0.759–1.51 | `python -m domains.agent_usage.analog` |
| p224 계산(45–116턴, 10.9–21.8분, 비유 6.74–13.5분), p237 계산 | `python -m domains.agent_usage.predict p224` · `p237` |
| 다시 맞춘 범위(표 7) | `…/scratchpad/refit_dry.py` |
| 날짜 나눔 시험(표 11: 10→50/89, 27→26/34, 손 61/88, 모름 25; 9→9/55, 25→23/30, 손 50/55) | `…/scratchpad/refit_test.py` |
| 새로 맞은 41 중 묶음 28, 다시 맞춘 계산기의 말한 구간(다른 일 46·잠깐 14·신경 끄기 4), 실제 구간 분포 | `…/scratchpad/refit_why.py` |
| 묶음 뺀 61건: 10→22, 손 54/61, 묶음 손 8/28 | `…/scratchpad/refit_excl.py` |
| 정해진 입력 배수 ≤11-02 ×0.234–0.465 · ≤11-03 ×0.117–0.234 | `…/scratchpad/refit_dbg.py` |
| files 19건 순위 상관 +0.72(분 +0.68), 파일당 턴 3–36(가운데 9), exam_grader +0.63, gemmin +0.75 | `…/scratchpad/size_data.py` |
| 비율 조각 4건의 비·비례·제곱근·실측(표 9), p185 after | `explainer/scale.py` → `out/scale.txt` |
| 모름 67건의 설정별 수, 11-03 이후 모름 25·11-04 이후 22의 설정, 스위치 경로가 말한 구간 분포 | `explainer/unknown.py` → `out/unknown.txt` |
| 다시 맞춘 C_min_light_model의 걸린 15건(Fable xhigh 8·Opus xhigh 7) | `explainer/light.py` → `out/light.txt` |
| '!예'를 모름으로 통과한 적용 70(34·23·9·4), 분을 낸 285 중 276 자름, 곱하기 개수별 턴 빗나감(×1.41·2.01·2.84·1.68·44.66) | `explainer/misc.py` → `out/misc.txt` |
| F 장치 89 ≥ 68, Haiku medium 12건 = gemmin, 규칙 44(살아 있음 23), 시험 기록 223, 턴 표 동작(Bash:cd 1,291 / 4,563) | `explainer/misc2.py` → `out/misc2.txt` |
| p05까지 126: 계산기 89·모름 6·손 85 / p05 뒤 226: 계산기 53·모름 61·손 148 | `explainer/split.py` → `out/split.txt` |
| batman 날짜 10-13–10-18, p05까지 126 중 batman 121, 턴 없는 끝난 43(클라우드 41·batman 2), 기간별 저장소, 묶음 28건을 ≤11-02/≤11-03 숫자로(모두 다른 일 맞음 / 모두 잠깐 틀림, 턴 가운데 75.9/38.1, 턴 범위 안 0/28) | `explainer/verify.py` → `out/verify.txt` |
| 테스트 149개 중 1 실패(test_audit_has_no_errors_now) | `python -m unittest discover -s tests -t .` |

- 옮겨 온 옛 숫자(날짜·출처를 문서에 붙임): p179 보고서(2026-11-04) — η² 0.42/0.30, 모름 1,735칸 중 74 %, in-sample 71 % vs out 27 %, calc 33·22·67; CLAUDE.md(2026-11-03) — p145 28줄=응답 15·×1.83, 256건 67 %/78 %, 크기 모델 첫 시험 88건 4–18 %·+0.21·−0.49; CLAUDE.md(2026-11-04) — 파일당 분 0.12–16.7.
- PDF: `pdfinfo` → 17쪽. `pdffonts` → Noto Sans/Serif KR 굵기 둘씩 묻힘. `pdftoppm -r 60`으로 모든 쪽을 그림으로 보고 고쳤다(표 4·6·7의 열 너비, 그림 1의 글자 겹침, 식 6 줄바꿈, 표 캡션이 앞 쪽에 홀로 남는 것). 마지막 판에서 한글 깨짐(빈 네모) 없음, 넘치는 표·그림 없음.

## 확인 못 한 것
- 브라우저(인터넷 글꼴)로 HTML을 연 모습은 보지 않았다. PDF는 같은 글꼴을 로컬에서 채워 렌더했다.
- p237(이 일 자신)은 결과 전이라 모든 성적에서 빠진다. 문서의 '기록 362건'에는 들어 있다.
- 메인 세션이 말한 '기록 361건'은 p237을 넣기 전의 수로 보인다(지금 362).
- 부록 A의 어긋남을 코드로 고쳤을 때 성적이 어떻게 바뀌는지는 돌려 보지 않았다(예: 빗댄 기록의 after를 보면 p189가 빠지는지 — 빠질 것으로 보이지만 실행하지 않음).
- 동작 섞임(전제 1)은 턴 표의 동작 이름을 셌을 뿐 턴 길이로 분석하지 않았다.

## 알려진 문제
- 해설서는 2026-11-05 스냅숏이라 숫자가 곧 낡는다. 문서 안의 명령으로 다시 뽑아야 한다.
- 근거 스크립트가 세션 스크래치에 있어 세션이 끝나면 사라진다. 다시 쓰려면 이 보고서의 표가 무엇을 셌는지 알려 준다.
- 본문 일부에 긴 식별자 때문에 양쪽 맞춤 간격이 벌어진 줄이 남아 있다(읽는 데 지장은 없음).

## 다음 작업자에게
- 문서와 코드가 어긋난 곳(해설서 부록 A) 중 주인이 판단할 것: ① 빗댄 기록 규칙 v2가 미리 정한 기준으로 실패(22/32 vs 31/32) — CLAUDE.md는 아직 '시험 전'. ② `holdout.piece_scores`가 비유 효과를 건너뛰어 C_turns_analog는 성적이 영영 '시험 전'. ③ `holdout._scale_scores`가 빗댄 기록 쪽 `files.after`를 안 봄(p189 → p185). ④ `--turns`의 Bash 분류가 첫 낱말이라 'Bash:cd'가 턴 표의 28 %. ⑤ S_many_turn_model 기본값 '아니오'로 Opus xhigh가 '가벼운 모델' 조각에 섞임. ⑥ `dispatches.py` 587행의 박힌 숫자(61건 62 %/51 %) vs 실제 62건 63 %/50 %.
- 다시 맞추기를 정할 때 표 11의 함정(같은 지시서 묶음이 새로 맞은 것의 28/41, 다시 맞춘 계산기가 다수 구간 '다른 일'로 몰림)을 같이 볼 것.
