
def print_execution_summary(result: dict) -> None:
    """打印 Supervisor 的调度过程摘要和最终回答。"""
    messages = result.get("messages", [])

    print("\n===== Supervisor 调度摘要 =====")

    for i, message in enumerate(messages, 1):
        sender = getattr(message, "name", None) or type(message).__name__
        tool_calls = getattr(message, "tool_calls", [])

        if tool_calls:
            for call in tool_calls:
                print(f"[{i}] {sender} -> 工具: {call.get('name')}")

        elif type(message).__name__ == "ToolMessage":
            content = str(message.content).replace("\n", " ")
            print(f"[{i}] 工具结果: {content[:100]}")

        elif sender in {"research_agent", "review_agent"}:
            content = str(message.content).replace("\n", " ")
            print(f"[{i}] {sender}: {content[:120]}...")

    print("\n===== 执行结果摘要 =====")

    agent_names = set()
    tool_names = set()

    for message in messages:
        name = getattr(message, "name", None)
        if name in {"research_agent", "review_agent"}:
            agent_names.add(name)

        for call in getattr(message, "tool_calls", []) or []:
            tool_name = call.get("name")
            if tool_name:
                tool_names.add(tool_name)

    print(f"消息总数：{len(messages)}")
    print(f"参与的 Agent：{', '.join(sorted(agent_names)) or '未识别'}")

    search_tools = sorted(
        name for name in tool_names if "tavily" in name.lower()
    )
    handoff_tools = sorted(
        name for name in tool_names
        if name.startswith("transfer_to_")
        or name.startswith("transfer_back_to_")
    )
    other_tools = sorted(
        tool_names - set(search_tools) - set(handoff_tools)
    )

    print(f"网页搜索工具：{', '.join(search_tools) or '未调用'}")
    print(f"Agent 转交工具：{', '.join(handoff_tools) or '未调用'}")
    print(f"其他工具：{', '.join(other_tools) or '未调用'}")

    final_message = messages[-1] if messages else None
    final_content = str(getattr(final_message, "content", "")).strip()

    print(f"最终回答已生成：{'是' if final_content else '否'}")

    if final_content:
        preview = " ".join(final_content.split())
        print(f"最终回答预览：{preview[:200]}...")

    print("\n===== Supervisor 最终回答 =====")
    if final_content:
        print(final_content)
    else:
        print("未生成最终回答。")
