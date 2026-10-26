
from langgraph_supervisor import create_supervisor

from config.model import llm
from agents.research_agent import research_agent
from agents.review_agent import review_agent


supervisor = create_supervisor(
    agents=[research_agent, review_agent],
    model=llm,
    prompt=(
        "你是一个 AI 技术研究任务的协调者，负责分配任务并整合结果。"
        "你有两个子 Agent：research_agent 和 review_agent。"

        "请先判断用户的任务类型，再选择执行流程："

        "一、一般技术研究或成本分析任务："
        "先调用 research_agent 获取研究结果；"
        "如果任务涉及计算，必须要求其使用计算工具；"
        "再调用 review_agent 核查结果中的事实、计算和逻辑；"
        "最后整合两者的结果，生成完整的中文回答。"

        "二、审查已有报告或检查明确给出的错误："
        "优先调用 review_agent 审查用户提供的原始报告；"
        "不得要求 research_agent 重复撰写审查报告；"
        "如果缺少必要的计算依据，可以调用 research_agent 补充计算；"
        "最后根据审查结果生成中文回答。"

        "必须根据任务需要合理分配工作，"
        "不得为了满足固定调用顺序而执行无必要的任务。"
        "在必要的子 Agent 完成工作之前，不得生成最终答案。"

        "对于行业研究、市场规模、企业动态和最新数据等任务，"
        "应要求 research_agent 实际调用 tavily_search 获取网页资料。"
        "最终回答应尽可能保留关键结论对应的来源标题和完整 URL。"
        "不得把搜索摘要未经核验地表述为确定事实。"
        "研究任务完成后，应调用 review_agent 检查关键数据、来源可靠性、"
        "时间范围、统计口径以及不同来源之间的矛盾。"
        "如果不同机构的数据不一致，应说明各自的估算及差异，"
        "不得随意选择其中一个数字并将其说成唯一正确答案。"
    ),
).compile()
