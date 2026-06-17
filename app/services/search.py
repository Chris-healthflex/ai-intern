from app.config import settings


def search_medical_context(query: str, max_results: int = 3) -> str:
    if settings.tavily_api_key:
        return _search_tavily(query, max_results)
    return _search_duckduckgo(query, max_results)


def _search_tavily(query: str, max_results: int) -> str:
    from tavily import TavilyClient

    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(
        query=f"medical triage red flags urgency: {query}",
        search_depth="basic",
        max_results=max_results,
    )
    snippets = [
        f"- {item.get('title', 'Result')}: {item.get('content', '')}"
        for item in response.get("results", [])
    ]
    return "\n".join(snippets) if snippets else "No search results found."


def _search_duckduckgo(query: str, max_results: int) -> str:
    from duckduckgo_search import DDGS

    search_query = f"medical emergency red flags symptoms {query}"
    with DDGS() as ddgs:
        results = list(ddgs.text(search_query, max_results=max_results))

    snippets = [
        f"- {item.get('title', 'Result')}: {item.get('body', '')}"
        for item in results
    ]
    return "\n".join(snippets) if snippets else "No search results found."
