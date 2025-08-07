from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages
from typing import Any


search_detail_results: Annotated[Any, "상세 검색 결과 목록"]


class ErrorState(TypedDict):
    node: str
    message: str


class State(TypedDict):
    # 메시지 정의(list type 이며 add_messages 함수를 사용하여 메시지를 추가)
    messages: Annotated[list, add_messages]
    rewrite_question: Annotated[str, "질문 재작성 내용"]
    summary: Annotated[str, "요약 내용"]
    user_id: Annotated[str, "사용자 ID"]
    question: Annotated[str, "질문 내용"]
    question_type: Annotated[str, "질문 유형"]
    keyword: Annotated[str, "추출된 키워드"]
    search_results: Annotated[list, "검색 결과 목록"]
    judge_search_results: Annotated[list, "검색 결과 유용성 판단 목록"]
    search_detail_results: Annotated[list, "상세 검색 결과 목록"]
    answer: Annotated[str, "최종 답변 내용"]
    time_range: Annotated[str, "검색 시간 범위"]
    error: Annotated[Optional[ErrorState], "오류 상태 정보"]
