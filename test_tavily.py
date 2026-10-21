
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_tavily import TavilySearch


# 明确从项目根目录加载 .env
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


def main():
    search_tool = TavilySearch(
        max_results=3,
        topic="general",
        search_depth="basic",
    )

    query = "2025 global generative AI industry market trends"
    result = search_tool.invoke({"query": query})

    results = result.get("results", [])
    print(f"查询：{query}")
    print(f"搜索结果数量：{len(results)}")

    valid_results = 0

    for index, item in enumerate(results, start=1):
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "")

        parsed_url = urlparse(url)
        valid_url = (
            parsed_url.scheme in ("http", "https")
            and bool(parsed_url.netloc)
        )

        print(f"\n[{index}] {title or '无标题'}")
        print(f"URL：{url or '无 URL'}")
        print(f"摘要：{(content or '无摘要')[:300]}")

        if title.strip() and valid_url and content.strip():
            valid_results += 1

    if not results:
        raise RuntimeError("没有返回搜索结果，请检查 API Key、网络和 Tavily 配置。")

    if valid_results == 0:
        raise RuntimeError("有搜索结果，但没有结果同时具备标题、有效 URL 和摘要。")

    print(f"\n测试通过：{valid_results} 条结果具备标题、有效 URL 和摘要。")


if __name__ == "__main__":
    main()
