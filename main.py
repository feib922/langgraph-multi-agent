
import argparse

from graph import supervisor
from services.result_reporter import print_execution_summary


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LangGraph 多智能体测试"
    )
    parser.add_argument(
        "--mode",
        choices=list(QUESTIONS.keys()),
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
        print_execution_summary(result)

    except Exception as e:
        print(f"\n运行失败：{type(e).__name__}: {e}")
        print("请检查 API 配置、网络连接或模型服务状态。")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
