from langchain_openai import ChatOpenAI
from graph.set_state import State
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from pprint import pprint

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


class Result(BaseModel):
    Judge: str = Field(description="Keyword search result is useful or notuseful")
    url: List[str] = Field(
        default_factory=list, description="list of URLs to search more"
    )
    explain: str = Field(
        description="Explanation of the search result usefulness, concise and clear"
    )


parser = JsonOutputParser(pydantic_object=Result)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an assistant that evaluates the usefulness of search results based on a user's question.

Instructions:
- If the search results contain enough information to answer the question, set "Judge" to "useful".
- If the search results are insufficient or missing critical information, set "Judge" to "notuseful".
- If "notuseful", include a short list of specific URLs from the provided results that should be further explored.
- Only include URLs that are clearly relevant to the user’s question. Avoid general or duplicate URLs.
- Keep the explanation short and clear, in natural language.

""",
        ),
        (
            "user",
            "# Search Results: {search_results}\n\n# User Question: {question}\n\n# Format: {format_instructions}",
        ),
    ]
)
chain = prompt | llm | parser


# 챗봇 함수 정의
def judge_search_results_bot(state: State):
    if state.get("error"):
        return state
    # 메시지 호출 및 반환
    try:
        rewrite_question = state.get("rewrite_question", ["No question provided"])[0]
        search_results = state["search_results"]
        print("search_results=", search_results)
        return {
            "judge_search_results": [
                chain.invoke(
                    {
                        "question": rewrite_question,
                        "search_results": search_results,
                        "format_instructions": parser.get_format_instructions(),
                    }
                )
            ],
        }
    except Exception as e:
        print(f"Error in judge_search_results_bot: {e}")
        return {
            **state,
            "error": {
                "node": "judge_search_results_bot",
                "message": str(e),
            },
        }
