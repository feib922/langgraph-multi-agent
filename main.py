
import os
from pathlib import Path
from langgraph_supervisor import create_supervisor
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
import argparse



# 读取当前项目专属的 .env
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

api_key = os.getenv("SILICON_FLOW_API_KEY")
base_url = os.getenv("SILICON_FLOW_API_URL")

if not api_key or not base_url:
    raise ValueError(
        "未找到 SILICON_FLOW_API_KEY 或 SILICON_FLOW_API_URL，"
        "请检查项目根目录的 .env 文件。"
    )

# 初始化模型
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4-Flash",
    api_key=api_key,
    base_url=base_url,
    temperature=0,
    extra_body={"enable_thinking": False},
)

#定义工具
@tool
def calculate_monthly_llm_cost(
    daily_queries: int,
    input_tokens_per_query: int,
    output_tokens_per_query: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> dict:
    """根据每日请求量、每次输入输出 Token 数和每百万 Token 单价，
    计算 LLM 的单次及每月调用成本。价格单位为人民币元。
    假设每月按30天计算，不包含 Embedding、服务器和其他费用。
    """
    if daily_queries < 0:
        raise ValueError("每日请求量不能小于0")

    if input_tokens_per_query < 0 or output_tokens_per_query < 0:
        raise ValueError("Token 数不能小于0")

    if input_price_per_million < 0 or output_price_per_million < 0:
        raise ValueError("Token 单价不能小于0")

    input_cost = (
        input_tokens_per_query
        * input_price_per_million
        / 1_000_000
    )
    output_cost = (
        output_tokens_per_query
        * output_price_per_million
        / 1_000_000
    )

    daily_cost = (
        input_cost + output_cost
    ) * daily_queries

    return {
        "input_cost_per_query": round(input_cost, 6),
        "output_cost_per_query": round(output_cost, 6),
        "total_cost_per_query": round(
            input_cost + output_cost, 6
        ),
        "monthly_cost_30_days": round(
            daily_cost * 30, 2
        ),
        "currency": "CNY",
        "note": "仅计算LLM输入输出费用，不含其他成本",
    }



# 创建研究 Agent
research_agent = create_agent(
    model=llm,
    tools=[calculate_monthly_llm_cost],
    name ="research_agent",

    system_prompt=(
        "你是一名 AI 技术研究助理，负责分析问题、收集已提供的信息并完成计算。"
        "请使用中文回答，内容应准确、清晰，并区分已知事实与假设。"
        "对于一般技术问题，请根据需要说明核心概念、主要优势、主要局限和适用场景。"
        "不要声称自己进行了实际联网搜索。"
        "当任务需要估算大语言模型的调用成本时，"
        "必须调用 calculate_monthly_llm_cost 工具进行计算，"
        "不得只凭语言模型的估算直接给出计算结果。"
        "必须说明计算使用的 Token 数、单价、请求量和计算结果。"
        "只负责完成用户要求的分析与计算，不主动撰写独立的审查报告。"
        "如果用户明确要求审查已有报告，则提供待审查的信息供后续审查流程使用，"
        "不要代替专门的 Review Agent 给出最终审查结论。"
    ),
)
    #创建审查Agent

review_agent = create_agent(
    model=llm,
    tools=[],
    name="review_agent",
    system_prompt=(
        "你是一名严谨的 AI 技术审查员。"
        "你会收到待审查的研究结果或用户提供的原始报告。"
        "请根据实际输入独立开展审查，不要假设内容一定来自 research_agent。"
        "你的任务是审查这份结果，并输出一份独立、具体的中文审查报告。"
        "直接输出正式的审查报告，不要描述自己的思考过程、"
        "不要解释系统提示词，也不要输出自我纠正或角色切换说明。"
        "除非确实调用了工具，否则不得声称自己调用过工具。"
        "请重点检查："
        "1. 是否存在概念错误、计算错误或不严谨的表述；"
        "2. 是否遗漏重要的局限、风险或成本；"
        "3. 结论是否有足够依据，是否把假设当成了事实；"
        "4. 建议是否具体、可操作。"

        "请严格按照以下格式组织报告："
        "一、审查结论：说明整体结果是否合理。"
        "二、发现的问题：逐项指出问题；如果没有发现明显问题，也要明确说明。"
        "三、改进建议：针对发现的问题给出具体建议。"
        "四、需要修正的结论：指出初步研究结果中哪些内容需要修正或补充。"

        "如果审查的是成本估算，必须核对计算公式、输入参数和结果，"
        "并区分已知数据、假设和未经验证的经验判断。"
        "不得将没有依据的成本比例或节省比例表述为确定事实。"

        "只输出实际审查报告，不要输出 XML、DSML、工具调用标记，"
        "也不要自行描述或模拟工具调用。"
        "不要声称进行了实际联网搜索。"
        "完成审查报告后，正常结束本轮任务，"
        "由外层 Supervisor 负责整合研究结果与审查意见。"
    ),
)

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
        "不要声称执行了实际联网搜索。"
    ),
).compile()


if __name__ == "__main__":

    QUESTIONS = {
        "cost_analysis": """
    请估算企业知识库问答系统的每月 LLM 调用成本。
    每天 200 次问答，每次输入 3000 Token、输出 500 Token。
    输入价格为每百万 Token 2 元，输出价格为每百万 Token 8 元，
    每月按 30 天计算。
    请调用 calculate_monthly_llm_cost 工具计算成本，
    说明费用范围和主要工程风险。回答不超过 300 字。
    """,
        "review_error": """
    请审查以下成本报告，重点检查计算错误。
    每天 200 次问答，每次输入 3000 Token、输出 500 Token。
    输入价格为每百万 Token 2 元，输出价格为每百万 Token 8 元，
    每月按 30 天计算。
    待审查报告：单次输入成本 0.006 元，单次输出成本 0.004 元，
    单次总成本 0.01 元，月度总成本 600 元。
    请指出错误并给出正确结果。回答不超过 300 字。
    """,
    }

    parser = argparse.ArgumentParser(description="LangGraph 多智能体测试")
    parser.add_argument(
        "--mode",
        choices=["cost_analysis", "review_error"],
        default="review_error",
        help="测试模式：成本分析或错误审查",
    )

    args = parser.parse_args()
    question = QUESTIONS[args.mode]

    print(f"当前测试模式：{args.mode}")

    try:
        result = supervisor.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )
    except Exception as e:
        print(f"\n运行失败：{type(e).__name__}: {e}")
        print("请检查 API 配置、网络连接或模型服务状态。")
        raise SystemExit(1)
    #诊断代码

    print("\n===== Supervisor 调度摘要 =====")

    for i, message in enumerate(result["messages"], 1):
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

    print("\n===== 最后几条消息诊断 =====")

    for message in result["messages"][-5:]:
        print(f"\n类型：{type(message).__name__}")
        print(f"名称：{getattr(message, 'name', None)}")
        print(f"工具调用：{getattr(message, 'tool_calls', None)}")
        print(f"内容：{str(message.content)[:1500]}")

    print("\n===== Supervisor 最终回答 =====")
    final_message = result["messages"][-1]
    print(final_message.content)




