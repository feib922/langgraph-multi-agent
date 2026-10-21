
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from main import llm, research_agent, review_agent
import re


class ResearchState(TypedDict):
    question: str
    research_report: str
    review_report: str
    final_report: str


def research_node(state: ResearchState):
    """第一步：调用 Research Agent 联网搜索并生成报告。"""
    print("\n[1/3] 开始执行 Research Agent……")

    result = research_agent.invoke({
        "messages": [
            {"role": "user", "content": state["question"]}
        ]
    })

    report = str(result["messages"][-1].content)

    print("[1/3] Research Agent 已返回研究报告。")

    return {"research_report": report}


def review_node(state: ResearchState):
    """第二步：把研究报告交给 Review Agent 审查。"""
    print("\n[2/3] 开始执行 Review Agent……")

    review_request = (
        "请审查下面这份行业研究报告。\n\n"
        "重点检查：关键数据及其时间范围、来源标题和 URL 是否完整、"
        "不同机构的统计口径是否一致、结论是否有足够依据、"
        "是否存在相互矛盾或无法确认的信息。\n"
        "你没有联网搜索工具，因此不要声称已经独立打开网页核实来源。"
        "对于无法直接确认的内容，请明确标记为待核实。\n\n"
        "用户原始问题：\n"
        f"{state['question']}\n\n"
        "待审查的研究报告：\n"
        f"{state['research_report']}"
    )

    result = review_agent.invoke({
        "messages": [
            {"role": "user", "content": review_request}
        ]
    })

    report = str(result["messages"][-1].content)

    print("[2/3] Review Agent 已返回审查报告。")

    return {"review_report": report}


def final_node(state: ResearchState):
    """第三步：整合研究报告和审查意见。"""
    print("\n[3/3] 正在整合最终报告……")

    prompt = (
        "你是一名严谨的行业研究报告编辑，负责整合研究报告与审查意见。"
        "请生成一份中文最终报告，并严格遵守以下规则：\n"
        "1. 区分已被来源支持的事实、来源给出的预测和模型推断，不得混为一谈。\n"
        "2. 保留有依据的关键发现，不得擅自修改原始数据、年份、单位或统计口径。\n"
        "3. 对审查意见中指出的关键错误、证据不足、来源不完整和数据口径差异，"
        "必须逐项处理；无法解决的，明确标注“待核实”，不得直接删除。\n"
        "4. 每项关键数据尽可能保留来源标题、原始 URL、发布日期和统计时间范围；"
        "原始材料未提供的信息不得自行编造。\n"
        "5. 不得仅凭相似的搜索摘要或未经确认的说法声称数据已被证实。\n"
        "6. 保留有依据的来源 URL；若来源与结论不匹配，或无法确认来源是否支持结论，"
        "应明确说明核验局限。\n"
        "7. 最终报告应包含关键发现、数据口径差异、审查发现的未解决问题，"
        "以及必要的待核实事项。\n\n"
        "原始研究报告：\n"
        f"{state['research_report']}\n\n"
        "审查意见：\n"
        f"{state['review_report']}\n\n"
        "请先依据审查意见逐项修正或标记问题，再输出最终报告。"
    )

    response = llm.invoke(prompt)
    final_report = str(response.content)

    print("[3/3] 最终报告已生成。")

    return {"final_report": final_report}


builder = StateGraph(ResearchState)

builder.add_node("research", research_node)
builder.add_node("review", review_node)
builder.add_node("final", final_node)

builder.add_edge(START, "research")
builder.add_edge("research", "review")
builder.add_edge("review", "final")
builder.add_edge("final", END)

fixed_workflow = builder.compile()


def check_report_consistency(
    research_report: str,
    review_report: str,
    final_report: str,
) -> bool:
    """检查报告完整性，以及具体审查问题是否得到保留。"""

    checks = {
        "研究报告非空": bool(research_report.strip()),
        "审查意见非空": bool(review_report.strip()),
        "最终报告非空": bool(final_report.strip()),
        "最终报告包含来源 URL": (
                "https://" in final_report or "http://" in final_report
        ),
    }

    # 仅当审查报告确实提到对应问题时，才检查最终报告
    issue_requirements = {
        "Wharton 年份与比例问题": [
            ["72%", "72％"],
            ["35 个百分点", "35个百分点"],
            ["82%", "82％"],
            ["10 个百分点", "10个百分点"],
        ],
        "编码工具数据待核实": [
            ["50% 开发者", "50%的开发者", "50%"],
            ["2.3 亿美元", "2.3亿美元"],
            ["待核实", "无法确认", "证据不足"],
        ],
    }

    missing_issues = []
    checked_issues = 0

    for issue_name, groups in issue_requirements.items():
        # 只有审查报告提及该问题的关键内容，才触发检查
        if not any(
            variant in review_report
            for group in groups
            for variant in group
        ):
            continue

        checked_issues += 1

        # 每组至少匹配一个表达方式
        issue_preserved = all(
            any(variant in final_report for variant in group)
            for group in groups
        )

        if not issue_preserved:
            missing_issues.append(issue_name)

    checks["存在可检查的具体审查问题"] = checked_issues > 0
    checks["最终报告保留具体审查问题"] = (
        checked_issues > 0 and not missing_issues
    )

    print("\n===== 报告一致性检查 =====")
    for name, passed in checks.items():
        print(f"{name}：{'通过' if passed else '未通过'}")

    if missing_issues:
        print("遗漏或未完整保留的问题：" + "、".join(missing_issues))

    return all(checks.values())


def main():
    question = (
        "请研究 2025 年全球生成式 AI 市场的主要发展趋势。"
        "通过网页搜索收集资料，给出至少 3 条关键发现。"
        "尽可能为每条发现提供来源标题、完整 URL 和时间范围。"
        "说明市场规模数据之间的差异，并指出无法确认的信息。"
    )

    result = fixed_workflow.invoke({
        "question": question,
        "research_report": "",
        "review_report": "",
        "final_report": "",
    })

    """
    print("\n" + "=" * 25)
    print("Review Agent 审查意见")
    print("=" * 25)
    print(result["review_report"])

    print("\n" + "=" * 25)
    print("最终研究报告")
    print("=" * 25)
    print(result["final_report"])
    """
    # 基础流程验收
    research_ok = bool(result["research_report"].strip())
    review_ok = bool(result["review_report"].strip())
    final_ok = bool(result["final_report"].strip())

    # 检查最终报告是否保留了至少一个完整的 HTTP(S) URL
    import re

    urls = re.findall(
        r"https?://[^\s)\]，。；]+",
        result["final_report"],
    )
    source_ok = bool(urls)

    print("\n===== 流程验收 =====")
    print(f"Research Agent 已产生报告：{research_ok}")
    print(f"Review Agent 已产生审查意见：{review_ok}")
    print(f"最终报告已生成：{final_ok}")
    print(f"最终报告包含来源 URL：{source_ok}")
    print(f"提取到的 URL 数量：{len(urls)}")

    consistency_ok = check_report_consistency(
        result["research_report"],
        result["review_report"],
        result["final_report"],
    )

    print(f"\n报告一致性检查总结果：{consistency_ok}")

    # 关键计算示例：370 亿相较于 115 亿
    previous_value = 115
    current_value = 370
    growth_rate = (current_value - previous_value) / previous_value * 100
    multiple = current_value / previous_value

    print("\n===== 计算校验示例 =====")
    print(f"同比增长率：{growth_rate:.1f}%")
    print(f"增长后的规模是上年的：{multiple:.2f} 倍")


if __name__ == "__main__":
    main()
