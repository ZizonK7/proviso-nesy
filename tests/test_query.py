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

    def test_search_finds_rule_by_words(self):
        self.assertIn("R_P1b", query.search(self.kbs, "가장 최근 칸"))


class McpProtocol(unittest.TestCase):
    def test_initialize_echoes_protocol_version(self):
        reply = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                   "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(reply["result"]["protocolVersion"], "2025-06-18")

    def test_notification_gets_no_reply(self):
        self.assertIsNone(mcp_server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_unknown_tool_is_error(self):
        reply = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                                   "params": {"name": "nope", "arguments": {}}})
        self.assertTrue(reply["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
