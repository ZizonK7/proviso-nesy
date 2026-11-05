"""git 숫자([dispatch.git])와 클라우드 숫자([dispatch.cloud]) — domains/agent_usage/measure.py · record.py · dispatches.py (2026-11-05)"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from domains.agent_usage import dispatches as dp, measure as ms, record as rc

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "domains" / "agent_usage"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          capture_output=True, text=True, check=True).stdout


def make_repo(tmp: Path) -> Path:
    repo = tmp / "work"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "a.py").write_text("1\n2\n3\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("x\n", encoding="utf-8")
    (repo / "gone.md").write_text("old\nold\n", encoding="utf-8")
    (repo / "dirty.md").write_text("keep\n", encoding="utf-8")
    (repo / "same.md").write_text("keep\n", encoding="utf-8")
    (repo / ".gitignore").write_text("out/\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    return repo


class GitNumbers(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_repo(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_worker_changes_are_what_changed_after_the_snapshot(self):
        r = self.repo
        (r / "dirty.md").write_text("keep\nmain\n", encoding="utf-8")       # 메인이 보내기 전에 고친 파일
        (r / "same.md").write_text("keep\nmain\n", encoding="utf-8")        # 메인이 고쳤고 작업자는 안 건드림
        (r / "out").mkdir()
        (r / "out" / "raw.txt").write_text("ignored\n", encoding="utf-8")   # .gitignore — 기준에도 비교에도 안 든다
        snap = ms.snapshot(r)
        self.assertEqual((snap["repo"], snap["dirty"], len(snap["dirty_hashes"])), ("work", 2, 2))
        self.assertTrue(all(ms.HASH_ITEM.match(h) for h in snap["dirty_hashes"]))
        self.assertFalse(any("dirty" in h or "/" in h for h in snap["dirty_hashes"]))  # 경로는 해시로만
        # 작업자: 깨끗한 파일 고침(Bash sed처럼), 새 파일, 지움, 더러웠던 파일 다시 고침
        (r / "src" / "a.py").write_text("1\nTWO\n3\n4\n", encoding="utf-8")   # +2 −1
        (r / "src" / "new.py").write_text("n1\nn2\nn3", encoding="utf-8")     # 새 파일 3줄(끝 줄바꿈 없음)
        (r / "gone.md").unlink()                                              # −2
        (r / "dirty.md").write_text("keep\nmain\nworker\n", encoding="utf-8")  # 보낼 때 내용에서 +1
        (r / "out" / "more.txt").write_text("ignored\n", encoding="utf-8")
        got = ms.compare(r, snap)
        self.assertEqual({k: got[k] for k in ms.GIT_KEYS[:6]},
                         {"git_write": 1, "git_edit": 2, "git_delete": 1, "git_lines_added": 6, "git_lines_removed": 3, "git_commits": 0})

    def test_committed_files_are_not_counted_but_commits_are(self):
        snap = ms.snapshot(self.repo)
        (self.repo / "src" / "b.py").write_text("y\n", encoding="utf-8")
        git(self.repo, "commit", "-qam", "작업자가 커밋")
        got = ms.compare(self.repo, snap)
        self.assertEqual((got["git_edit"], got["git_commits"]), (0, 1))

    def test_named_files_are_sized_at_head_even_after_the_worker_changes_them(self):
        head = git(self.repo, "rev-parse", "HEAD").strip()
        (self.repo / "src" / "a.py").write_text("much\nlonger\nfile\nnow\nyes\n", encoding="utf-8")
        brief = (f"고칠 것: `src/a.py`, {self.repo}/src/b.py, 그리고 b.py(같은 파일). 폴더 src/ 를 본다. "
                 f"없는 파일 src/none.py, 무시 out/raw.txt, 낱말 e.g. 2026-11-05")
        self.assertEqual(ms.named(self.repo, head, brief), {"named_files": 2, "named_lines": 4, "named_bytes": 8, "named_dirs": 1})

    def test_send_then_finish_in_a_temp_repo(self):
        """record send가 기준을 찍고(기록 파일 자신은 기준 표 전 내용으로), 작업자가 Bash로 고친 뒤 record finish가 숫자를 채운다."""
        r = self.repo
        shutil.copy(HERE / "dispatches.toml", r / "d.toml")
        shutil.copy(ROOT / "docs" / "AGENT-LOG.md", r / "log.md")
        git(r, "add", "-A")
        git(r, "commit", "-qm", "records")
        job = (ROOT / "tests" / "test_decide.py").read_text(encoding="utf-8").split('write_text("""', 1)[1].split('"""', 1)[0]
        (self.tmp / "job.toml").write_text(job.replace("batch = 999", f'batch = 999\nrepo = "{r.as_posix()}"'), encoding="utf-8")
        rc.send(self.tmp / "job.toml", r / "d.toml", r / "log.md")
        d = dp.load(r / "d.toml")[-1]
        self.assertEqual((d["git"]["repo"], d["git"]["dirty"]), ("work", 2))  # 기록 파일과 배치 머리
        subprocess.run(f"cd {r} && sed -i 's/^2$/22/' src/a.py && printf 'z\\n' > src/c.py", shell=True, check=True)
        lines = [{"type": "user", "timestamp": "2026-11-05T01:00:00Z", "message": {"content": "src/a.py 를 고친다"}},
                 {"type": "assistant", "timestamp": "2026-11-05T01:01:00Z", "message": {"id": "m1", "usage": {}, "content": []}}]
        (self.tmp / "agent.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lines), encoding="utf-8")
        rc.finish(d["id"], self.tmp / "agent.jsonl", report="docs/worklog/CLAUDE.md", path=r / "d.toml")
        g = dp.load(r / "d.toml")[-1]["git"]
        self.assertEqual({k: g[k] for k in ("git_write", "git_edit", "git_delete", "git_lines_added", "git_lines_removed", "named_files", "named_lines")},
                         {"git_write": 1, "git_edit": 1, "git_delete": 0, "git_lines_added": 2, "git_lines_removed": 1, "named_files": 1, "named_lines": 3})
        self.assertEqual(dp.git_errors(dp.load(r / "d.toml")[-1]), [])


class CloudNumbers(unittest.TestCase):
    def numbers(self):
        u = {"inputTokens": 10, "outputTokens": 20, "cacheReadInputTokens": 30, "cacheCreationInputTokens": 40,
             "thinkingTokens": 5, "webSearchRequests": 2, "costUSD": 0.5}
        return {"session": "session_01Abc", "results": 1, "duration_ms": 60000, "duration_api_ms": 50000, "num_turns": 7,
                "total_cost_usd": 0.5, "web_search_requests": 0, "web_fetch_requests": 0, "subagents_spawned": 1,
                "stop_reason": "end_turn", "subtype": "success", "models": {"claude-haiku-5-5": u}}

    def test_keys_are_checked(self):
        n = self.numbers()
        self.assertEqual(ms.cloud_errors(n), [])
        self.assertTrue(ms.cloud_errors({**n, "result": "글"}))                          # 결과 글은 받지 않는다
        self.assertTrue(ms.cloud_errors({k: v for k, v in n.items() if k != "num_turns"}))
        self.assertTrue(ms.cloud_errors({**n, "duration_ms": -1}))
        self.assertTrue(ms.cloud_errors({**n, "models": {"claude-haiku-5-5": {"inputTokens": 1}}}))
        self.assertTrue(ms.cloud_errors({**n, "session": "/home/x"}))

    def test_events_are_summed_without_double_counting_cumulative_fields(self):
        """사건 둘(p211 모양): modelUsage·total_cost_usd·duration_api_ms·spawned는 누적, 나머지는 사건마다."""
        def ev(ts, dur, turns, api, spawned, since, cum_cost):
            return {"created_at": ts, "result": {"internal_anthropic_catchall": {
                "duration_ms": dur, "duration_api_ms": api, "num_turns": turns, "total_cost_usd": cum_cost,
                "subagent_stats": {"spawned": spawned}, "usage": {"server_tool_use": {"web_search_requests": 1, "web_fetch_requests": 0}},
                "model_usage_since_last_result": {"m": since}, "modelUsage": {"m": {k: v * 9 for k, v in since.items()}},
                "stop_reason": "end_turn", "subtype": "success", "result": "결과 글"}}}
        one = dict.fromkeys(ms.CLOUD_MODEL_KEYS, 1) | {"costUSD": 0.25}
        raw = {"ccr": {"data": [ev("2026-11-05T07:37:29Z", 1000, 3, 900, 2, one, 0.25),
                                ev("2026-11-05T07:37:37Z", 100, 1, 950, 2, one, 0.5),
                                ev("2026-11-05T07:50:00Z", 100, 1, 990, 2, one, 0.75)]}}
        n = ms.cloud_from_events(raw, until="2026-11-05T07:38:00Z")
        self.assertEqual((n["results"], n["duration_ms"], n["num_turns"], n["duration_api_ms"], n["subagents_spawned"]),
                         (2, 1100, 4, 950, 2))
        self.assertEqual((n["total_cost_usd"], n["models"]["m"]["outputTokens"], n["web_search_requests"]), (0.5, 2, 2))
        self.assertEqual(ms.cloud_errors(n), [])

    def test_record_cloud_writes_the_block_and_session(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            d_path = tmp / "d.toml"
            shutil.copy(HERE / "dispatches.toml", d_path)
            d_path.write_text(d_path.read_text(encoding="utf-8") + """
[[dispatch]]
id = "zc1"
project = "proviso"
batch = 999
date = 2026-11-06
task = "조사(클라우드)"
model = "Haiku 5.5"
effort = "medium"
agent = "z"
round = 1
[dispatch.situation]
S_cloud_session = "예"
S_other_model = "예"
[dispatch.predicted]
minutes = [1, 3]
[dispatch.actual]
status = "done"
minutes = 2.0
""", encoding="utf-8")
            (tmp / "n.json").write_text(json.dumps(self.numbers()), encoding="utf-8")
            rc.cloud("zc1", tmp / "n.json", path=d_path)
            d = dp.load(d_path)[-1]
            self.assertEqual((d["session"], d["cloud"]["num_turns"], d["cloud"]["models"]["claude-haiku-5-5"]["output_tokens"]),
                             ("session_01Abc", 7, 20))
            self.assertEqual(dp.cloud_record_errors(d), [])
            with self.assertRaises(SystemExit):
                rc.cloud("zc1", tmp / "n.json", path=d_path)  # 이미 있으면 다시 쓰지 않는다
            with self.assertRaises(SystemExit):
                rc.cloud(dp.load(d_path)[0]["id"], tmp / "n.json", path=d_path)  # 로컬 일에는 안 쓴다
        finally:
            shutil.rmtree(tmp)


class Requirements(unittest.TestCase):
    base = {"id": "zz9", "project": "proviso", "batch": 99, "date": dp.GIT_REQUIRED_FROM, "task": "t",
            "predicted": {}, "actual": {"status": "done", "minutes": 5}, "situation": {"S_cloud_session": "아니오"}}

    def test_local_records_from_nov_6_need_git_numbers(self):
        new = self.base
        self.assertTrue(any("git 숫자" in e for e in dp.git_errors(new)))
        self.assertEqual(dp.git_errors({**new, "git": {"skip": "저장소 밖 일"}}), [])
        snap = {"repo": "proviso-nesy", "head": "a" * 40, "dirty": 1, "dirty_hashes": ["0123abcd:0123456789ab"]}
        self.assertTrue(dp.git_errors({**new, "git": snap}))                                   # 기준만 있고 숫자 없음
        self.assertEqual(dp.git_errors({**new, "git": {**snap, **dict.fromkeys(ms.GIT_KEYS, 0)}}), [])
        self.assertEqual(dp.git_errors({**new, "git": snap, "actual": {"status": "unknown"}}), [])  # 보낸 뒤 끝나기 전
        self.assertEqual(dp.git_errors({**new, "date": "2026-11-05"}), [])                      # 그 전 날짜는 없어도 된다
        self.assertEqual(dp.git_errors({**new, "situation": {"S_cloud_session": "예"}}), [])     # 클라우드 일은 git 대신 cloud
        self.assertTrue(dp.git_errors({**new, "git": {**snap, "repo": "/home/x/repo", **dict.fromkeys(ms.GIT_KEYS, 0)}}))
        self.assertTrue(dp.git_errors({**new, "git": {"skip": "x", **dict.fromkeys(ms.GIT_KEYS, 0)}}))

    def test_cloud_records_from_nov_6_need_session_and_cloud_numbers(self):
        new = {**self.base, "situation": {"S_cloud_session": "예"}}
        errs = dp.cloud_record_errors(new)
        self.assertTrue(any("session" in e for e in errs) and any("[dispatch.cloud]" in e for e in errs))
        ok = {**new, "session": "session_01Abc", "cloud": {"skip": "세션이 지워짐"}}
        self.assertEqual(dp.cloud_record_errors(ok), [])
        block = {k: 0 for k in ms.CLOUD_NUM_KEYS} | {"stop_reason": "end_turn", "subtype": "success",
                                                      "models": {"claude-opus-5-5": dict.fromkeys(ms.CLOUD_MODEL_KEYS.values(), 0)}}
        self.assertEqual(dp.cloud_record_errors({**ok, "cloud": block}), [])
        self.assertTrue(dp.cloud_record_errors({**ok, "cloud": {**block, "result": "글"}}))
        self.assertEqual(dp.cloud_record_errors({**new, "date": "2026-11-05"}), [])            # 그 전 날짜는 없어도 된다


if __name__ == "__main__":
    unittest.main()
