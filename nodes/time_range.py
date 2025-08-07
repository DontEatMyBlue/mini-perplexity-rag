from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
today = datetime.today().strftime("%Y-%m-%d")
time_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are a classifier that determines how recent the user's question is.

Today's date is {today}. Use this to interpret relative terms like "today", "this week", "last month", or "recently".

Your job is to classify the *time range* that the user is asking about into one of these 4 categories:

- "day" → If the question is asking about today's or real-time information.
- "week" → If the question is asking about something that happened in the past few days or this week.
- "month" → If it's about this month or a few weeks ago.
- "year" → If it's historical, old, not time-sensitive, **or if the time range is unclear or ambiguous**.

⚠️ If you are uncertain, or the time range is not clearly specified, default to "year".

Respond only with one of the following words (no quotes, no explanation):
day, week, month, year.
""",
        ),
        ("user", "{question}"),
    ]
)

time_range_chain = time_prompt | llm | StrOutputParser()


# LangGraph 노드 함수
def time_range_selector(state):
    if state.get("error"):
        return state
    try:
        question = state.get("rewrite_question", "No question provided")
        time_range = time_range_chain.invoke({"question": question})
        print("🧠 LLM 판단된 time_range:", time_range)
        return {"time_range": time_range.strip().lower()}

    except Exception as e:
        print(f"Error in time_range_selector: {e}")
        return {
            **state,
            "error": {
                "node": "time_range_selector",
                "message": str(e),
            },
        }
