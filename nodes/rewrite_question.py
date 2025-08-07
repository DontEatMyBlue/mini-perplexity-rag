from langchain_openai import ChatOpenAI
from graph.set_state import State
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
today = datetime.today().strftime("%Y년 %m월 %d일")
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are a question rewriter that generates a clear and self-contained question using long-term and short-term context.

🧠 Instructions:
- Use the provided *summary* as long-term background about the conversation.
- Use the recent *messages* as short-term conversational history.
- If the original question is ambiguous (e.g., "this", "that", "it", "he", "she", "what about that?"), rewrite it into a **specific and complete question** based on context.
- Ensure the final question is **clear**, **independent**, and **makes sense on its own**.
- Avoid using pronouns or vague references in the final rewritten question.
- Today is {today}.
🎯 Goal:
Return a complete and natural question that reflects the user's actual intent, as inferred from both summary and recent messages.
""",
        ),
        ("user", "Summary:\n{summary}"),
        MessagesPlaceholder("messages"),
        ("user", "Original Question:\n{question}"),
        ("user", f"Rephrase the question accordingly."),
    ]
)

chain = prompt | llm | StrOutputParser()


def rewrite_question_bot(state: State):
    if state.get("error"):
        return state
    try:

        question = state.get("question", ["No question provided"])[0]
        summary = state.get("summary", "No summary available.")
        recent_messages = state.get("messages", [])

        rewrite_question = chain.invoke(
            {"summary": summary, "messages": recent_messages, "question": question}
        )
        print("Original Question:", question)
        print("rewrite_question", rewrite_question)

        return {
            **state,
            "rewrite_question": rewrite_question,
            "messages": question,
        }
    except Exception as e:
        print(f"Error in rewrite_question_bot: {e}")
        return {
            **state,
            "error": {
                "node": "rewrite_question_bot",
                "message": str(e),
            },
        }
