import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

# 定位项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 加载当前项目的环境变量
load_dotenv(PROJECT_ROOT / ".env", override=True)

# 初始化 Tavily 网页搜索工具
tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
)