"""피드백 명령 (저장소 루트).

  python -m feedback check                 백서·메인 모양 검사 (문제가 있으면 종료 코드 1)
  python -m feedback index [--write]       색인 표를 보여 준다 / 백서의 표지 사이에 다시 쓴다
  python -m feedback topics "<일 설명>"     그 일에 읽을 메인 파일 (키워드 매칭, common은 늘)
  python -m feedback find <낱말>...         색인 낱말로 백서 항목 찾기
"""
from __future__ import annotations

import sys

from . import MAIN_DIR, VOCAB, check, entries, find, index, index_write, mains, topics


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
        print("읽을 메인 피드백: " + ", ".join(stems))
        for s in stems:
            print(f"  {(MAIN_DIR / (s + '.md')).relative_to(MAIN_DIR.parent.parent).as_posix()}")
        print(f'보낼 일 파일에: [feedback]\nread = [{", ".join(chr(34) + s + chr(34) for s in stems)}]')
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
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
