from fastapi import APIRouter
from graph.set_graph import run_graph
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    messages: list
    summary: str
    user_id: str


router = APIRouter()


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    state = {
        "question": [request.question],
        "summary": request.summary,
        "messages": request.messages,
        "user_id": request.user_id,
    }
    print("Received request:", state)

    result = run_graph(state)
    print("Graph result:", result)
    return {
        "messages": result.get("messages", []),
        "summary": result.get("summary", ""),
        "rewrite_question": result.get("rewrite_question", ""),
        "answer": result.get("answer", ""),
        "keyword": result.get("keyword", ""),
        "question_type": result.get("question_type", ""),
        "judge_search_results": result.get("judge_search_results", []),
        "search_detail_results": result.get("search_detail_results", []),
    }
