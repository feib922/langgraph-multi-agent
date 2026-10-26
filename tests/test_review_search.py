
import re
from unittest.mock import patch

from agents.review_agent import review_agent
from tools.web_search import tavily_search


QUERY = """请核验以下待审查声明：OpenAI 于 2023 年 11 月 6 日正式发布了 GPT-4 Turbo，并在发布当天向所有 ChatGPT 用户开放。

请使用 tavily_search 搜索并核验：
1. GPT-4 Turbo 的正式发布或公布日期。
2. 发布时的可用对象和开放范围，区分 API 开发者、付费用户和所有 ChatGPT 用户。
3. 区分产品公布、API 预览、正式可用和 ChatGPT 端开放等不同事件。
4. 如果声明只有部分正确，请明确指出哪些内容正确、哪些内容不准确或缺乏证据。

最终只输出一份中文报告，使用以下四部分：
- 核验结论：已核实 / 存疑 / 尚未核实
- 关键发现：最多 3 条
- 证据来源：最多 3 个实际搜索到的来源标题、完整 URL，以及各来源支持的事实
- 修改建议：给出更准确的声明表述

正文尽量控制在 150 字以内，URL 不计入字数。不得编造来源，不得把不同的发布日期混为一谈；不得把向开发者开放等同于向所有 ChatGPT 用户开放。不要输出中间分析、搜索过程或重复结论。
"""


def extract_final_report(messages):
    """提取最终核验报告，避免把工具调用过程混入报告。"""
    for message in reversed(messages):
        content = getattr(message, "content", "")
        tool_calls = getattr(message, "tool_calls", [])

        if not content or tool_calls:
            continue

        if not isinstance(content, str):
            content = str(content)

        if "核验结论" in content and "证据来源" in content:
            return content.strip()

    return ""


def test_review_agent_uses_search_and_returns_report():
    """验证 Review Agent 实际搜索，并输出结构完整、带 URL 的报告。"""
    tool_class = type(tavily_search)
    original_invoke = tool_class.invoke
    target_name = tavily_search.name

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
        result = review_agent.invoke({
            "messages": [
                {"role": "user", "content": QUERY}
            ]
        })

    messages = result.get("messages", [])
    report = extract_final_report(messages)

    # 1. 验证 Tavily 确实被调用
    assert recorded_calls, (
        "Review Agent 没有实际调用 tavily_search"
    )

    # 2. 验证工具返回了成功结果
    assert recorded_results, (
        "检测到搜索工具调用，但没有记录到工具返回值"
    )

    for tool_result in recorded_results:
        assert getattr(tool_result, "status", "success") == "success", (
            f"Tavily 搜索执行失败：{getattr(tool_result, 'content', tool_result)}"
        )

    # 3. 验证最终报告及其必要结构
    assert report, "没有提取到包含核验结论和证据来源的最终报告"

    required_sections = [
        "核验结论",
        "关键发现",
        "证据来源",
        "修改建议",
    ]

    for section in required_sections:
        assert section in report, (
            f"最终报告缺少必要部分：{section}"
        )

    # 4. 验证报告中存在来源标题和 HTTP/HTTPS URL
    urls = re.findall(r"https?://[^\s<>\"）)]+", report)

    assert urls, "最终报告没有包含完整的 HTTP/HTTPS 来源链接"

    print("\n========== Review Agent 自动验收 ==========")
    print(f"Tavily 实际调用次数：{len(recorded_calls)}")
    print(f"报告提取成功：是")
    print(f"检测到的 URL 数量：{len(urls)}")
    print("\n========== 最终核验报告 ==========\n")
    print(report)


if __name__ == "__main__":
    test_review_agent_uses_search_and_returns_report()
