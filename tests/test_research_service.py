
import unittest
from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage
from services.research_service import run_supervisor_task


class TestResearchService(unittest.TestCase):

    def test_empty_question_raises_value_error(self):
        """空问题应被拦截，不应调用 Supervisor。"""
        with patch("services.research_service.supervisor.invoke") as mock_invoke:
            with self.assertRaisesRegex(ValueError, "问题不能为空"):
                run_supervisor_task("   ")

            mock_invoke.assert_not_called()


    def test_runs_supervisor_and_returns_final_answer(self):
        """正常问题应调用 Supervisor，并返回最终回答。"""
        fake_result = {
            "messages": [
                HumanMessage(content="研究生成式 AI"),
                AIMessage(content="这是模拟的研究结果。"),
            ]
        }

        with patch(
            "services.research_service.supervisor.invoke",
            return_value=fake_result,
        ) as mock_invoke:
            answer = run_supervisor_task("  研究生成式 AI  ")

        self.assertEqual(answer, "这是模拟的研究结果。")
        mock_invoke.assert_called_once_with(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "研究生成式 AI",
                    }
                ]
            }
        )


if __name__ == "__main__":
    unittest.main()
