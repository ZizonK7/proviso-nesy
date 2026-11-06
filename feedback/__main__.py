"""피드백 명령 (저장소 루트).

  python -m feedback check                 백서·메인 모양 검사 (문제가 있으면 종료 코드 1)
  python -m feedback index [--write]       색인 표를 보여 준다 / 백서의 표지 사이에 다시 쓴다
  python -m feedback topics "<일 설명>"     키워드가 고른 메인 파일 (참고 — 2026-11-07부터 [feedback] read에는 메인 파일 전부)
  python -m feedback find <낱말>...         색인 낱말로 백서 항목 찾기 (보낼 일 파일의 [feedback] searched 줄도 찍는다)
  python -m feedback labels [--out 경로] [--brief-root 저장소=폴더 ...]
                                           보낸 기록·직접 한 일의 read·searched·hit·missed·brief(지시서 경로)를 JSON Lines로
                                           (기본 out/feedback/labels.jsonl). --brief-root(여러 번 가능)를 주면 그 저장소 경로의
                                           지시서 글을 brief_text로 붙인다(없으면 null). 지시서 글은 이 공개 저장소에 저장하지 않는다
"""
from __future__ import annotations

import sys

from pathlib import Path

from . import LABELS_OUT, MAIN_DIR, VOCAB, check, entries, find, index, index_write, labels_write, main_files, mains, topics


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "check":
        errors = check()
        if errors:
            print(f"피드백 모양 문제 {len(errors)}건:")
            for e in errors:
                print("  -", e)
            return 1
        print(f"피드백 검사: 문제 없음 (백서 항목 {len(entries())}개, 메인 파일 {len(mains())}개)")
        return 0
    if cmd == "index":
        if "--write" in rest:
            print("색인 표를 다시 썼다 (whitepaper.md)" if index_write() else "색인 표가 이미 최신이다")
        else:
            print(index())
        return 0
    if cmd == "topics" and rest:
        stems = topics(" ".join(rest))
        print("키워드가 고른 메인 피드백(참고): " + ", ".join(stems))
        for s in stems:
            print(f"  {(MAIN_DIR / (s + '.md')).relative_to(MAIN_DIR.parent.parent).as_posix()}")
        every = main_files()
        print(f"2026-11-07부터 [feedback] read에는 메인 파일 전부({len(every)}개)를 읽고 적는다 — 키워드 고르기는 거칠다(F102)")
        print(f'보낼 일 파일에: [feedback]\nread = [{", ".join(chr(34) + s + chr(34) for s in every)}]')
        return 0
    if cmd == "find" and rest:
        vocab = VOCAB()
        unknown = [w for w in rest if w not in vocab]
        if unknown:
            print(f"색인 낱말이 아님: {', '.join(unknown)} (목록: feedback/CLAUDE.md '색인 낱말')")
        hits = find(rest)
        print(f"백서 항목 {len(hits)}개:")
        for e in hits:
            print(f"  {e['id']} · {e['title']} — 색인 {', '.join(e.get('색인', []))} · 자리 {e.get('자리', '?')}")
        known = [w for w in rest if w in vocab]
        if known:
            print(f'보낼 일 파일의 [feedback]에: searched = [{", ".join(chr(34) + w + chr(34) for w in known)}]'
                  " — 걸리는 항목은 백서에서 읽고 hit = [...]에")
        return 0
    if cmd == "labels":
        out = Path(rest[rest.index("--out") + 1]) if "--out" in rest and rest.index("--out") + 1 < len(rest) else LABELS_OUT
        roots = {}
        for i, a in enumerate(rest):
            if a == "--brief-root":
                val = rest[i + 1] if i + 1 < len(rest) else ""
                name, sep, folder = val.partition("=")
                if not (sep and name and folder):
                    print("--brief-root는 저장소=폴더 꼴 (예: --brief-root gemmin=../gemmin)", file=sys.stderr)
                    return 2
                roots[name] = Path(folder)
        missing: list[str] = []
        n = labels_write(out, brief_roots=roots or None, missing=missing)
        print(f"피드백 정답 {n}줄을 썼다: {out}")
        if missing:
            print(f"지시서 글을 못 찾은 기록 {len(missing)}건(brief 경로가 없거나 파일이 없음, brief_text = null): {', '.join(missing)}", file=sys.stderr)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
