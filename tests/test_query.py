import unittest
from pathlib import Path

from proviso import mcp_server, query

ROOT = Path(__file__).resolve().parent.parent


class Query(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kbs = query.load_all(ROOT)
        cls.kn = cls.kbs["flowlog"]

    def test_goal_tree_nests_children(self):
        tree = query.goal_tree(self.kn)
        self.assertIn("- G_record: 기록을 꾸준히 한다", tree)
        self.assertIn("  - G_simple: 화면은 간결하게", tree)

    def test_explain_shows_incoming_links(self):
        text = query.explain(self.kn, "G_simple")
        self.assertIn("이 목표를 위해 받아들인 대가: [가설 H_alternate]", text)

    def test_explain_rule_shows_evidence_and_history(self):
        text = query.explain(self.kn, "R_P1b")
        self.assertIn("근거: [관찰 O_slow_recent]", text)
        self.assertIn("고치기 전 버전: [규칙 R_P1 v1", text)
        self.assertIn("판정 (실제 기록 재생, 2026-10-14): 일부", text)

    def test_search_finds_rule_by_words(self):
        self.assertIn("R_P1b", query.search(self.kbs, "가장 최근 칸"))


class McpProtocol(unittest.TestCase):
    def test_initialize_echoes_protocol_version(self):
        reply = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                   "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(reply["result"]["protocolVersion"], "2025-06-18")

    def test_notification_gets_no_reply(self):
        self.assertIsNone(mcp_server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_every_tool_runs_on_every_domain(self):
        # 2026-10-19 구조 개편 뒤에도 조회 도구가 세 분야에서 돈다
        for domain in ("flowlog", "music_player", "agent_usage"):
            for tool, extra in (("goal_tree", {}), ("audit", {}), ("scorecard", {}), ("explain", {"id": "G_x"})):
                reply = mcp_server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                           "params": {"name": tool, "arguments": {"domain": domain, **extra}}})
                self.assertFalse(reply["result"]["isError"], (domain, tool))
                self.assertTrue(reply["result"]["content"][0]["text"], (domain, tool))
        for tool, args in (("list_domains", {}), ("search", {"query": "분당 턴"})):
            reply = mcp_server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                       "params": {"name": tool, "arguments": args}})
            self.assertFalse(reply["result"]["isError"], tool)

    def test_scorecard_and_explain_show_grades(self):
        card = mcp_server.call_tool("scorecard", {"domain": "flowlog"})
        self.assertIn("★ 사용자 실사용", card)
        self.assertIn("R_P1a [규칙 v2 · 가설]", card)
        text = mcp_server.call_tool("explain", {"domain": "agent_usage", "id": "R_time_turns_v2"})
        self.assertIn("자동 검사: used_minutes, turn_rate_non_web", text)
        text = mcp_server.call_tool("explain", {"domain": "music_player", "id": "R_S1"})
        self.assertIn("시험 수단 없음", text)

    def test_unknown_tool_is_error(self):
        reply = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                   "params": {"name": "nope", "arguments": {}}})
        self.assertTrue(reply["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
