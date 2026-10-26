
import re
from unittest.mock import patch

from graph import supervisor
from tools.web_search import tavily_search


QUESTION = (
    "请研究 2025 年全球生成式 AI 市场的主要发展趋势。"
    "请通过网页搜索收集资料，给出至少 3 条关键发现。"
    "每条发现尽可能提供来源标题、完整 URL 和对应的时间范围。"
    "请让审查 Agent 检查关键数据、来源可靠性、统计口径以及结论中的矛盾。"
    "最后输出整合报告，并明确指出存在争议或无法确认的数据。"
)


def test_supervisor_research_workflow():
    """验证 Supervisor 是否协调研究、搜索、审查并输出整合报告。"""

    # 跟踪 Tavily 的实际调用和返回结果
    tool_class = type(tavily_search)
    original_invoke = tool_class.invoke
    target_tool_name = tavily_search.name

    search_calls = []
    search_results = []

    def tracked_invoke(self, input, config=None, **kwargs):
        # 先执行原始工具，再记录成功返回的结果
        result = original_invoke(
            self,
            input,
            config=config,
            **kwargs,
        )

        if self.name == target_tool_name:
            search_calls.append(input)
            search_results.append(result)

        return result

    print("\n[阶段 1/3] 开始执行 Supervisor 工作流……", flush=True)

    with patch.object(tool_class, "invoke", new=tracked_invoke):
        result = supervisor.invoke(
            {
                "messages": [
                    {"role": "user", "content": QUESTION}
                ]
            },
            config={"recursion_limit": 20},
        )

    print(
        "[阶段 2/3] 工作流已结束，开始检查执行结果……",
        flush=True,
    )

    messages = result.get("messages", [])

    # 1. 工作流必须返回消息
    assert messages, "Supervisor 没有返回任何消息"

    # 2. 确认研究 Agent 和审查 Agent 都参与了流程
    agent_names = {
        getattr(message, "name", None)
        for message in messages
    }

    assert "research_agent" in agent_names, (
        "没有在 Supervisor 返回的消息中发现 research_agent"
    )
    assert "review_agent" in agent_names, (
        "没有在 Supervisor 返回的消息中发现 review_agent"
    )

    # 3. 确认 Tavily 实际执行并返回结果
    print(
        f"[诊断] Tavily 调用次数：{len(search_calls)}；"
        f"记录到的返回结果数：{len(search_results)}",
        flush=True,
    )

    assert search_calls, (
        "本次工作流没有实际调用 tavily_search"
    )
    assert search_results, (
        "没有记录到 Tavily 的工具返回结果"
    )

    for search_result in search_results:
        assert getattr(search_result, "status", "success") == "success", (
            "Tavily 搜索工具返回了失败状态"
        )

    # 4. 检查最终整合报告
    final_message = messages[-1]
    final_report = getattr(final_message, "content", "")

    assert isinstance(final_report, str) and final_report.strip(), (
        "最后一条消息没有包含有效的整合报告"
    )

    # 5. 检查报告的基本结构
    for keyword in ["关键发现", "审查", "来源"]:
        assert keyword in final_report, (
            f"最终报告缺少必要内容：{keyword}"
        )

    # 6. 检查报告是否包含来源链接
    urls = re.findall(r"https?://[^\s<>\"）)]+", final_report)

    assert urls, (
        "最终报告没有包含 HTTP/HTTPS 来源链接"
    )

    # 7. 检查是否明确说明争议或不确定性
    uncertainty_keywords = [
        "争议",
        "无法确认",
        "存疑",
        "不确定",
        "口径差异",
    ]

    assert any(
        keyword in final_report
        for keyword in uncertainty_keywords
    ), (
        "最终报告没有明确指出争议或无法确认的信息"
    )

    print("[阶段 3/3] 所有自动检查均已通过。", flush=True)
    print(f"\nSupervisor 返回消息数：{len(messages)}")
    print(f"Tavily 实际调用次数：{len(search_calls)}")
    print(f"报告中提取到的 URL 数量：{len(urls)}")
    print("\n========== 最终整合报告 ==========\n")
    print(final_report)


if __name__ == "__main__":
    test_supervisor_research_workflow()
