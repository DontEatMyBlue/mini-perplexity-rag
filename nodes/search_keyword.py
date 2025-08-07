from graph.set_state import State
from langchain_tavily import TavilySearch
from pprint import pprint


tool = TavilySearch(
    max_results=3,
    topic="general",
)


def search_keyword(state: State):
    if state.get("error"):
        return state
    try:
        time_range = state.get("time_range", "day")
        parse_context = []
        for keyword in state.get("keyword", []):
            context = tool.invoke({"query": keyword, "time_range": time_range})
            for item in context["results"]:

                parse_context.append(
                    f"제목: {item['title']}\n링크: {item['url']}\n내용: {item['content']}\n"
                )
        return {"search_results": parse_context}
    except Exception as e:
        print(f"Error in search_keyword: {e}")
        return {
            **state,
            "error": {
                "node": "search_keyword",
                "message": str(e),
            },
        }
