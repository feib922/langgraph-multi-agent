
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 项目根目录，而不是 config 目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 读取当前项目专属的 .env
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
