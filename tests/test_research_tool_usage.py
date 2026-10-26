
from unittest.mock import patch
import json
from langchain.messages import ToolMessage
from agents.research_agent import research_agent
from tools.cost_calculator import calculate_monthly_llm_cost


def test_research_agent_calls_cost_tool():
    """验证 Research Agent 实际调用成本工具，且参数和结果正确。"""
    tool_class = type(calculate_monthly_llm_cost)
    original_invoke = tool_class.invoke
    target_name = calculate_monthly_llm_cost.name
    recorded_calls = []
    recorded_results = []

    def tracked_invoke(self, input, config=None, **kwargs):
        result = original_invoke(
            self, input, config=config, **kwargs
        )

        if self.name == target_name:
            recorded_calls.append(input)
            recorded_results.append(result)

        return result

    with patch.object(tool_class, "invoke", new=tracked_invoke):
        research_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "请计算每月 LLM 调用成本。每日请求量 200 次，"
                            "每次输入 3000 Token、输出 500 Token，"
                            "输入单价为每百万 Token 2 元，"
                            "输出单价为每百万 Token 8 元。"
                            "必须调用 calculate_monthly_llm_cost 工具计算。"
                        ),
                    }
                ]
            }
        )

    assert recorded_calls, (
        "Research Agent 没有实际调用 calculate_monthly_llm_cost"
    )

    assert len(recorded_calls) == 1, (
        f"预期调用一次成本工具，实际调用 {len(recorded_calls)} 次"
    )

    assert recorded_calls[0]["args"] == {
        "daily_queries": 200,
        "input_tokens_per_query": 3000,
        "output_tokens_per_query": 500,
        "input_price_per_million": 2,
        "output_price_per_million": 8,
    }

    assert len(recorded_results) == 1
    result = recorded_results[0]

    print("工具返回值类型：", type(result))
    print("工具返回值 content 类型：", type(result.content))
    print("工具返回值 content：", repr(result.content))
    assert isinstance(result, ToolMessage), (
        f"预期返回 ToolMessage，实际为 {type(result).__name__}"
    )

    assert result.status == "success", (
        f"成本工具执行失败：{result.content}"
    )

    import json
    cost_result = json.loads(result.content)

    assert cost_result["input_cost_per_query"] == 0.006
    assert cost_result["output_cost_per_query"] == 0.004
    assert cost_result["total_cost_per_query"] == 0.01
    assert cost_result["monthly_cost_30_days"] == 60.0
    assert cost_result["currency"] == "CNY"