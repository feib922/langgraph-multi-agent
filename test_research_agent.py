
from main import research_agent


def main():
    question = (
        "请研究 2025 年全球生成式 AI 市场的发展趋势。"
        "至少搜索网页资料，列出 3 条关键发现，"
        "并为每条发现提供来源标题和完整 URL。"
        "请区分来源中的事实与自己的分析，不要编造数据。"
    )

    print("===== 测试问题 =====")
    print(question)
    print("\n===== Research Agent 执行结果 =====")

    result = research_agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )

    messages = result.get("messages", [])

    for message in messages:
        message_type = type(message).__name__
        name = getattr(message, "name", None)
        content = str(getattr(message, "content", ""))

        # 只打印角色、工具调用情况和最终文本，不打印环境变量
        print(f"\n--- {message_type} | name={name} ---")

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                print(f"工具调用：{call.get('name', '未知工具')}")

        if content:
            print(content[:5000])

    tool_messages = [
        message
        for message in messages
        if type(message).__name__ == "ToolMessage"
    ]

    tavily_called = any(
        getattr(message, "name", None) == "tavily_search"
        for message in tool_messages
    )

    print("\n===== 验收结果 =====")
    print(f"Tavily 工具实际执行：{'是' if tavily_called else '未确认'}")

    if not tavily_called:
        print("请检查上方消息中的工具调用记录和执行错误。")


if __name__ == "__main__":
    main()
