
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

api_key = os.getenv("SILICON_FLOW_API_KEY")
base_url = os.getenv("SILICON_FLOW_API_URL")

if not api_key or not base_url:
    raise ValueError(
        "没有读取到 SILICON_FLOW_API_KEY 或 SILICON_FLOW_API_URL，"
        "请检查旧项目的 .env 文件。"
    )

# 沿用之前使用过的模型
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4-Flash",
    api_key=api_key,
    base_url=base_url,
    temperature=0,
    extra_body={"enable_thinking": False},
)

response = llm.invoke("你好，请用中文简单介绍一下你自己。")

print("模型连接成功！")
print("模型回答：")
print(response.content)
