from langchain_openai import ChatOpenAI
from graph.set_state import State
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a chatbot that determines whether the user's question requires an internet search.

Rules:
- If the question contains proper nouns (people, places, products, current events, etc.) or asks for **factual information that may change over time**, it likely needs an internet search.
- If the question is vague, ambiguous, or very short (e.g. "1", "that", "yes", "lol", "go", etc.), assume it does **NOT** need an internet search.
- If it's a general greeting or everyday knowledge (e.g., "What's 2+2?", "Hello", "How are you?"), also respond with: "No Internet Search".

Responses:
- "Internet Search" → if the question needs live data or real-time info.
- "No Internet Search" → if the answer can be handled locally or the question has no clear meaning.
            """,
        ),
        ("user", "{user_message}"),
    ]
)

chain = prompt | llm | StrOutputParser()


def chatbot(state: State):
    if state.get("error"):

        return state
    try:

        print("state=", state)
        rewrite_question = state.get("rewrite_question", "No rewrite question found")

        return {
            **state,
            "question_type": [chain.invoke({"user_message": rewrite_question})],
        }
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return {
            **state,
            "error": {
                "node": "chatbot",
                "message": str(e),
            },
        }
