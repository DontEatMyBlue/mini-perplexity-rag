from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from graph.set_state import State  # 기존 State 형식 그대로 사용

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# 프롬프트 정의
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a summarizer for a conversation between a user and an assistant.

Your job is to update the summary of the conversation based on the most recent messages.

Instructions:
- Start from the previous summary and merge the new messages into it.
- Ensure every discussed topic is preserved — do not skip or compress too aggressively.
- Retain important facts, specific numbers, references to sources or URLs.
- Write the summary in a neutral tone, clearly and in one paragraph.
- The summary should still make sense even without seeing the full conversation.
- ⚠️ Limit the result to around **2000 characters** or **3000 tokens** at most to prevent exceeding context length in future steps.
""",
        ),
        ("user", "Previous Summary:\n{previous_summary}"),
        MessagesPlaceholder("new_messages"),
        ("system", "Summarize all of the above without omitting any part."),
        ("user", "Update the summary."),
    ]
)

chain = prompt | llm | StrOutputParser()


# 노드 함수 정의
def summarize_bot(state: State) -> State:
    if state.get("error"):
        return state
    try:
        previous_summary = state.get("summary", "There is no previous summary.")
        recent_messages = state.get("messages", [])

        new_summary = chain.invoke(
            {
                "previous_summary": previous_summary,
                "new_messages": recent_messages,
            }
        )
        print("Previous Summary:", previous_summary)
        print("Recent Messages:", recent_messages)
        print("📝 Generated Summary:", new_summary)
        return {
            "summary": new_summary,
            "messages": [],  # 최근 메시지도 반환
        }
    except Exception as e:
        print(f"Error in summarize_bot: {e}")
        return {
            **state,
            "error": {
                "node": "summarize_bot",
                "message": str(e),
            },
        }
