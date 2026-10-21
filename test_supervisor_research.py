
from main import supervisor


def main():
    question = (
        "请研究 2025 年全球生成式 AI 市场的主要发展趋势。"
        "请通过网页搜索收集资料，给出至少 3 条关键发现。"
        "每条发现尽可能提供来源标题、完整 URL 和对应的时间范围。"
        "请让审查 Agent 检查关键数据、来源可靠性、统计口径以及结论中的矛盾。"
        "最后输出整合报告，并明确指出存在争议或无法确认的数据。"
    )

    print("开始测试 Supervisor 多智能体研究流程……")

    result = supervisor.invoke({
        "messages": [
            {"role": "user", "content": question}
        ]
    })

    messages = result.get("messages", [])

    print(f"\n流程结束，共返回 {len(messages)} 条消息。\n")

    for i, message in enumerate(messages, start=1):
        name = getattr(message, "name", None) or type(message).__name__
        content = getattr(message, "content", "")
        tool_calls = getattr(message, "tool_calls", []) or []

        print(f"\n{'=' * 20} 消息 {i} | {name} {'=' * 20}")

        if tool_calls:
            print("工具调用：")
            for call in tool_calls:
                print(f"  - {call.get('name', '未知工具')}")

        if isinstance(content, str):
            print(content[:2500])
            if len(content) > 2500:
                print("……（内容过长，已截断）")
        else:
            print(str(content)[:2500])

    print("\n测试结束。请检查上面的消息，确认是否出现研究结果和审查结果。")


if __name__ == "__main__":
    main()
