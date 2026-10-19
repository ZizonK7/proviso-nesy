# 2026-10-19 — 비문학 기반 게임 사례 조사 (배치 G1)

에이전트: 웹 조사 작업자 여섯 (Haiku 5.5, effort high, 병렬). 하위 에이전트 호출: 없음.
커밋·push: 작업자는 안 함. 메인이 정리해서 커밋.
(작업자들은 지시서대로 `out/game-research/`에만 썼고 이 보고서는 메인이 대신 쓴다.)

## 한 일
- 작업자 여섯이 각도별 보고서를 `out/game-research/G1–G6-*.md`에 썼다(git 제외): 비문학 책 각색, 논문·이론, 개발자가 밝힌 영감, 보드게임, 다큐·교육·시민 과학, 문학(비교용). 정식 후보 72개.
- 메인이 핵심 연결을 원문과 대조해 [docs/nonfiction-games-v0.md](../nonfiction-games-v0.md)로 정리했다.

## 확인한 것 (어떻게)
- 영어 위키백과 원문(wikitext, `curl "https://en.wikipedia.org/w/index.php?title=<제목>&action=raw"`)에서 연결 문장 확인: SimCity–Forrester, SimEarth–Lovelock, SimAnt–Wilson, The Sims–Alexander, Landlord's Game–Henry George, Universal Paperclips–Bostrom, Walden–Thoreau(규칙·수상), Foldit(2011 논문), EteRNA(2020 논문), Oregon Trail(6,500만 장, 2011 기준), Pandemic–SARS, Wingspan–조류 데이터, Twilight Struggle–BGG 1위 기간, Freedom 설계자, This War of Mine–사라예보, Valiant Hearts–편지, Total War: Three Kingdoms–정사 모드, Plague Inc.–영감(영화), BioShock–Rand, S.T.A.L.K.E.R.–노변의 피크닉, Black Myth 판매.
- 제작자 페이지: `https://ncase.me/trust/notes/`(Axelrod 책 기반 명시), `https://ncase.me/polygons/`(Schelling 1971 논문).
- Steam 상점·평가 API(`store.steampowered.com/api/storesearch`, `/appreviews/<id>?json=1`): 긍정 비율과 평가 수 24개 게임, Bury Me, My Love의 Le Monde 기사 출처.
- `python -m proviso validate agent_usage`, `python -m proviso audit agent_usage` → 문제 없음, 점검 통과. `python -m unittest discover -s tests -t .` → OK.

## 확인 못 한 것
- 보고서의 △ 항목 전부(검색 요약만). 특히 Kingdom Come–Talhoffer, Kentucky Route Zero–Treverton, Spore–Powers of Ten, The Sims–매슬로: 원문에서 찾지 못함.
- Metacritic·BoardGameGeek·Game Developer·웹 아카이브: 이 환경의 프록시가 막음(403). WebFetch는 모든 호스트에서 DNS 실패.
- 망한 비문학 게임은 거의 모으지 못함. 비영어권 사례도 거의 없음.

## 알려진 문제
- `out/` 원자료는 클라우드 컨테이너가 정리되면 사라진다. 필요한 내용은 보고서로 옮겼다.
- 사례가 검색으로 모였으므로 유명한 성공작 쪽으로 기울어 있다(선택 편향).

## 다음 작업자에게
- 다음 단계는 사용자 결정대로: 성공 사례로 논리(조각 후보)를 세우고 → 망한 게임에 대 본다. 망한 비문학·문학 게임을 따로 모아야 한다.
- 원문 확인은 `curl`로(WebFetch 말고). 위키백과는 `action=raw`가 인용 출처까지 보여 줘서 빠르다.
