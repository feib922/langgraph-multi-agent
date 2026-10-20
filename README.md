# LangGraph Multi-Agent Supervisor

基于 LangGraph 和 `langgraph-supervisor` 构建的多智能体协作项目。通过 Supervisor 统一调度 Research Agent 和 Review Agent，实现技术成本分析、计算工具调用、报告审查及结果整合。

## 项目功能

- **Supervisor 调度**：根据用户任务选择合适的子 Agent，并整合最终结果。
- **Research Agent**：开展技术研究与成本分析，可调用成本计算工具。
- **Review Agent**：独立审查报告，核对计算过程并指出错误。
- **成本计算工具**：根据每日请求量、Token 用量和输入输出单价，估算单次成本与 30 天成本。
- **双模式运行**：支持成本分析（`cost_analysis`）和错误审查（`review_error`）。
- **自动化测试**：使用 Python `unittest` 验证成本计算逻辑和 Supervisor 图结构。

## 技术栈

- Python 3.12
- LangChain
- LangGraph
- langgraph-supervisor
- langchain-openai
- python-dotenv
- SiliconFlow API（兼容 OpenAI API 的模型调用接口）

## 项目结构

```text
langgraph-multi-agent/
├── main.py
├── requirements.txt
├── test_cost_calculator.py
├── test_model.py
├── test_supervisor.py
├── .env.example
├── .gitignore
└── README.md
```

## 环境配置

建议使用 Python 3.12。

### 1. 创建虚拟环境

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
```

### 2. 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 配置模型 API

在项目根目录创建 `.env` 文件：

```dotenv
SILICON_FLOW_API_KEY=替换为自己的API密钥
SILICON_FLOW_API_URL=https://api.siliconflow.cn/v1
```

请使用自己的 API 密钥，不要将 `.env` 提交到版本控制系统。

## 运行项目

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe .\main.py --mode cost_analysis
```

运行成本分析模式。

```powershell
.\.venv\Scripts\python.exe .\main.py --mode review_error
```

运行报告错误审查模式。

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m unittest .\test_cost_calculator.py .\test_supervisor.py -v
```

当前开发环境中，成本计算工具测试与 Supervisor 基础测试共 8 项通过。

`test_model.py` 会调用真实模型 API，属于接口连通性测试；运行前需要配置有效的 API 密钥，并注意可能产生的 API 费用。

## 示例：成本分析

假设：

- 每天 200 次问答
- 每次输入 3,000 Token
- 每次输出 500 Token
- 输入价格为每百万 Token 2 元
- 输出价格为每百万 Token 8 元
- 每月按 30 天计算

计算结果：

| 项目 | 成本 |
|---|---:|
| 单次输入成本 | 0.006 元 |
| 单次输出成本 | 0.004 元 |
| 单次总成本 | 0.01 元 |
| 月度估算成本 | 60 元 |

以上仅为给定用量和价格假设下的模型调用成本估算，不包含向量化、检索服务、服务器、失败重试等其他费用。

## 项目验证

- 验证成本计算工具的正常输入、负数输入和零值输入。
- 验证 Supervisor 工作流的节点、边和 Agent 交接工具。
- 验证成本分析与错误审查两种实际运行模式。
- 在错误审查场景中，成功识别月度成本从 60 元误写为 600 元的数量级错误。

## 后续改进方向

- 增加异常处理、重试机制和结构化日志。
- 增加 Agent 路由与最终答案的一致性测试。
- 引入更多业务工具和任务类型。
- 完善模型调用成本、延迟及多智能体执行轨迹的评估。
