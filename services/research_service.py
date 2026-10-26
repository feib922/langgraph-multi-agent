
from graph import supervisor
from config.model import llm
from tools.cost_calculator import calculate_monthly_llm_cost


def run_supervisor_workflow(question: str) -> dict:
    """执行 Supervisor 工作流，并返回完整执行结果。"""

    if not question or not question.strip():
        raise ValueError("问题不能为空。")

    return supervisor.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question.strip(),
                }
            ]
        }
    )


def run_supervisor_task(question: str) -> str:
    """执行 Supervisor 任务，并返回最终回答文本。"""

    result = run_supervisor_workflow(question)
    return extract_final_answer(result)


def extract_final_answer(result: dict) -> str:
    """从完整的工作流结果中提取最终回答。"""

    messages = result.get("messages", [])

    if not messages:
        return "工作流已执行，但没有返回消息。"

    content = getattr(messages[-1], "content", "")

    if isinstance(content, str):
        return content or "工作流已执行，但最终消息内容为空。"

    return str(content)


def run_cost_analysis(question: str) -> str:
    """调用成本计算工具，再根据实际计算结果生成成本分析报告。"""

    if not question or not question.strip():
        raise ValueError("问题不能为空。")

    calculation = calculate_monthly_llm_cost.invoke(
        {
            "daily_queries": 200,
            "input_tokens_per_query": 3000,
            "output_tokens_per_query": 500,
            "input_price_per_million": 2,
            "output_price_per_million": 8,
        }
    )

    response = llm.invoke(
        [
            (
                "system",
                (
                    "你是严谨的 LLM 成本分析助手。"
                    "必须以成本计算工具返回的数值为准，不得擅自修改计算结果。"
                    "明确说明计算假设、单次成本、月度成本及潜在风险。"
                    "如果用户提出的数字与工具结果矛盾，应明确指出。"
                    "请使用中文回答。"
                ),
            ),
            (
                "human",
                (
                    f"成本计算工具的实际返回结果：\n{calculation}\n\n"
                    f"用户补充要求：\n{question.strip()}\n\n"
                    "请根据工具的实际返回结果生成成本分析报告。"
                ),
            ),
        ]
    )

    if isinstance(response.content, str):
        return response.content

    return str(response.content)
