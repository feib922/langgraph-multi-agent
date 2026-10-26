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
