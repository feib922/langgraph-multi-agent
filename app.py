
import gradio as gr

from services.research_service import (
    run_supervisor_workflow,
    run_cost_analysis,
    extract_final_answer,
)
from services.result_reporter import print_execution_summary


TASK_PROMPTS = {
    "行业研究": None,
    "成本分析": """
估算企业知识库问答系统的每月 LLM 调用成本。
日均 200 次问答，每次输入 3000 Token、输出 500 Token；
输入价格为每百万 Token 2 元，输出价格为每百万 Token 8 元；
按 30 天计算。必须使用成本计算工具，并说明计算结果、费用范围和风险。
""",
    "报告审查": """
请审查用户提供的报告，重点检查计算结果、事实依据、逻辑错误和数据来源。
明确指出错误，给出正确计算或核查结论，并区分已确认的信息与尚待核实的信息。
""",
}


def chat(task_type: str, question: str) -> str:
    """根据任务类型调用对应的业务服务。"""

    if task_type not in TASK_PROMPTS:
        return "请选择有效的任务类型。"

    if not question or not question.strip():
        return "请输入你的问题或补充说明。"

    try:
        question = question.strip()

        # 成本分析由服务层负责工具计算和报告生成。
        if task_type == "成本分析":
            return run_cost_analysis(question)

        # 行业研究使用用户原始问题。
        if task_type == "行业研究":
            final_question = question

        # 报告审查在用户问题前添加审查要求。
        else:
            prompt = TASK_PROMPTS[task_type]
            final_question = (
                f"{prompt.strip()}\n\n"
                f"用户补充要求：\n{question}"
            )

        result = run_supervisor_workflow(final_question)
        print_execution_summary(result)

        return extract_final_answer(result)

    except Exception as exc:
        print(f"执行失败：{type(exc).__name__}: {exc}")
        return f"执行失败：{type(exc).__name__}: {exc}"


demo = gr.Interface(
    fn=chat,
    inputs=[
        gr.Dropdown(
            choices=list(TASK_PROMPTS.keys()),
            value="行业研究",
            label="任务类型",
        ),
        gr.Textbox(
            label="输入问题或补充要求",
            placeholder="例如：分析 2025 年全球生成式 AI 行业的发展趋势，并列出可靠来源。",
            lines=5,
        ),
    ],
    outputs=gr.Textbox(
        label="回答结果",
        lines=18,
    ),
    title="Multi-Agent 研究助理",
    description="基于 LangGraph Supervisor，支持行业研究、成本分析与报告审查。",
    submit_btn="提交问题",
    clear_btn="清空",
)


if __name__ == "__main__":
    demo.launch()
