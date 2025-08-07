from langchain_openai import ChatOpenAI
from graph.set_state import State
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from datetime import datetime
import tiktoken
from langchain_core.messages import BaseMessage


def truncate_messages_by_token_limit(
    messages: list[BaseMessage], max_tokens: int = 1000, model_name: str = "gpt-4o-mini"
) -> list[BaseMessage]:
    encoding = tiktoken.encoding_for_model(model_name)
    total_tokens = 0
    selected_messages = []

    # 뒤에서부터 메시지를 추가 (가장 최신부터)
    for msg in reversed(messages):
        content = msg.content
        token_count = len(encoding.encode(content))

        if total_tokens + token_count > max_tokens:
            break
        selected_messages.insert(0, msg)  # 원래 순서 유지
        total_tokens += token_count

    return selected_messages


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
output_parser = StrOutputParser()
today = datetime.today().strftime("%Y년 %m월 %d일")

# 프롬프트 구성
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"Today is {today}.You are a helpful AI assistant. Use the given context to answer the user's question as accurately and clearly as possible. Answer in Korean.",
        ),
        MessagesPlaceholder("messages"),
        ("user", "Context:\n{context}\n{search_results}\n\nQuestion:\n{question}"),
    ]
)

chain = prompt | llm | output_parser


def answer_bot(state: State):
    if state.get("error"):
        print("실행됨")
        return {
            "messages": [
                AIMessage(content="An error occurred while generating the answer.")
            ],
            "answer": "An error occurred while generating the answer.",
        }
    try:
        search_results = state.get("search_results", [])

        rewrite_question = state.get("rewrite_question", "No question provided")
        retrieved_docs = state.get("search_detail_results", [])

        messages = state.get("messages", [])
        truncated_messages = truncate_messages_by_token_limit(messages, max_tokens=1000)

        # 문서들을 하나의 문자열로 합치기
        context = (
            "\n\n".join([doc.page_content for doc in retrieved_docs])
            if retrieved_docs
            else "No context found."
        )

        answer = chain.invoke(
            {
                "question": rewrite_question,
                "context": context,
                "search_results": search_results,
                "messages": truncated_messages,  # 최근 메시지 포함
            }
        )
        print("number", truncated_messages)
        print("🧠 Generated Answer:", answer)

        return {**state, "messages": [AIMessage(content=answer)], "answer": answer}
    except Exception as e:
        print(f"Error in answer_bot: {e}")
        return {
            **state,
            "error": {
                "node": "answer_bot",
                "message": str(e),
            },
            "messages": [
                AIMessage(content="An error occurred while generating the answer.")
            ],
            "answer": "An error occurred while generating the answer.",
        }
