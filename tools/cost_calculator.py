from langchain.tools import tool

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
