from duckduckgo_search import DDGS


def web_search(query):

    results = []

    with DDGS() as ddgs:

        for r in ddgs.text(
            query,
            max_results=3
        ):
            results.append(
                {
                    "title": r["title"],
                    "body": r["body"],
                    "url": r["href"]
                }
            )


    return results