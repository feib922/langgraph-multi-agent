
from test_fixed_workflow import check_report_consistency

research = "2025 年生成式 AI 市场研究报告。"

review = """
Wharton 的年份数据存在问题：72% 和增加 35 个百分点属于上一轮调查，
2025 年数据为 82%，增加 10 个百分点。
编码工具数据：50% 开发者和 2.3 亿美元代码补全市场的数据待核实。
"""

# 测试一：完整保留两个问题
final_pass = """
上一轮 Wharton 调查每周使用比例为 72%，增加 35 个百分点；
2025 年为 82%，增加 10 个百分点。
编码工具的 50% 开发者数据和 2.3 亿美元市场数据待核实。
"来源：https://example.com/source".
"""

# 测试二：只保留 Wharton 问题，遗漏编码工具问题
final_partial = """
上一轮 Wharton 调查每周使用比例为 72%，增加 35 个百分点；
2025 年为 82%，增加 10 个百分点。
"""

# 测试三：只写了泛泛的“待核实”，没有保留具体问题
final_fail = "部分数据待核实。"


cases = [
    ("完整保留", final_pass, True),
    ("部分遗漏", final_partial, False),
    ("只保留泛泛标记", final_fail, False),
    ("缺少来源 URL", final_pass.replace(
        "https://example.com/source", ""
    ), False),
]

for name, final_report, expected in cases:
    print(f"\n===== 测试：{name} =====")
    actual = check_report_consistency(
        research,
        review,
        final_report,
    )
    print(f"预期：{expected}；实际：{actual}")
    assert actual == expected, f"{name}测试未达到预期"

print("\n全部本地测试通过。")
