from langchain_openai import ChatOpenAI
from graph.set_state import State
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


output_parser = CommaSeparatedListOutputParser()

# 출력 형식 지침 가져오기
format_instructions = output_parser.get_format_instructions()
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are a smart search query generator. Your job is to take a user's question and convert it into a *concise set* of powerful, Google-style search keyword phrases.

Guidelines:
- Extract only 1 to 4 keyword phrases that are most important for answering the question.
- Focus on specific keyword phrases that directly reflect the user's intent.
- Avoid generic or overly broad keywords such as "investment strategy", "stock", or "news".
- Each keyword phrase must be complete and self-contained. For example:
  - ❌ Bad: "배우", "줄거리"
  - ✅ Good: "광화문연가 배우", "광화문연가 줄거리"
- Avoid repeating the same word across multiple keywords unless it reflects a different context (e.g., comparison).
- Do not include single words unless they are clearly meaningful alone (e.g., "GPT-4").
- Use complete phrases that would make sense in a real Google search.
- Output only the keyword list. No markdown, no explanations, no quotes.
- Output format: {format_instructions}
""",
        ),
        ("user", "{user_message}"),
    ]
)
chain = prompt | llm | output_parser


def extract_keyword_bot(state: State):
    if state.get("error"):
        return state
    try:
        user_message = state.get("rewrite_question", "No question provided")

        print("chain=", chain.invoke({"user_message": user_message}))
        return {
            "keyword": chain.invoke(
                {
                    "user_message": user_message,
                }
            )
        }
    except Exception as e:
        print(f"Error in extract_keyword_bot: {e}")
        return {
            **state,
            "error": {
                "node": "extract_keyword_bot",
                "message": str(e),
            },
        }
