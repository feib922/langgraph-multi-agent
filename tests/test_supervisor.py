
import unittest
from unittest.mock import patch


class TestSupervisorSetup(unittest.TestCase):
    """验证多智能体项目的基础测试环境。"""

    @patch.dict(
        "os.environ",
        {
            "SILICON_FLOW_API_KEY": "tests-api-key",
            "SILICON_FLOW_API_URL": "https://api.siliconflow.cn/v1",
        },
    )
    def test_import_cost_tool_without_api_request(self):
        """导入成本工具时，不应发起真实模型请求。"""
        with patch("langchain_openai.ChatOpenAI") as mock_chat:
            from tools.cost_calculator import calculate_monthly_llm_cost

            self.assertEqual(
                calculate_monthly_llm_cost.name,
                "calculate_monthly_llm_cost",
            )

            result = calculate_monthly_llm_cost.invoke(
                {
                    "daily_queries": 200,
                    "input_tokens_per_query": 3000,
                    "output_tokens_per_query": 500,
                    "input_price_per_million": 2,
                    "output_price_per_million": 8,
                }
            )

            self.assertEqual(result["monthly_cost_30_days"], 60.0)
            self.assertEqual(result["currency"], "CNY")


    def test_supervisor_graph_structure(self):
        """验证 Supervisor 的节点、连接和交接工具。"""
        from graph import supervisor

        # 验证外层工作流包含两个 Agent
        graph = supervisor.get_graph()
        expected_nodes = {
            "__start__",
            "supervisor",
            "research_agent",
            "review_agent",
            "__end__",
        }
        self.assertTrue(expected_nodes.issubset(set(graph.nodes.keys())))

        # 验证两个 Agent 都会返回 Supervisor
        edges = {(edge.source, edge.target) for edge in graph.edges}
        self.assertIn(("research_agent", "supervisor"), edges)
        self.assertIn(("review_agent", "supervisor"), edges)

        # 验证 Supervisor 内部注册了两个交接工具
        inner_graph = graph.nodes["supervisor"].data.get_graph()
        tool_node = inner_graph.nodes["tools"].data
        tool_names = set(tool_node.tools_by_name.keys())

        self.assertIn("transfer_to_research_agent", tool_names)
        self.assertIn("transfer_to_review_agent", tool_names)


if __name__ == "__main__":
    unittest.main()
