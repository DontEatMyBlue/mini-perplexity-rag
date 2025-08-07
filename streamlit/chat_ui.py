import streamlit as st
import requests
import uuid

BACKEND_URL = "http://127.0.0.1:8000/api/ask"

st.set_page_config(page_title="LangGraph Chat", page_icon="💬")
st.title("💬 LangGraph Chatbot")

# 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None
if "show_temp_user_msg" not in st.session_state:
    st.session_state.show_temp_user_msg = False
if "last_state" not in st.session_state:  # ✅ 응답 상태 저장용
    st.session_state.last_state = {}
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# 사용자가 입력하면 상태에 저장하고 리렌더링
user_input = st.chat_input("질문을 입력하세요")
if user_input:
    st.session_state.pending_input = user_input
    st.session_state.show_temp_user_msg = True
    st.rerun()

# 대화 출력
for msg in st.session_state.messages:
    role = "user" if msg.get("type") == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["content"])

# 🔥 사용자 질문을 임시로 표시 (응답이 오기 전에!)
if st.session_state.show_temp_user_msg and st.session_state.pending_input:
    with st.chat_message("user"):
        st.markdown(st.session_state.pending_input)

# 백엔드 요청 처리
if st.session_state.pending_input and st.session_state.show_temp_user_msg:
    question = st.session_state.pending_input
    st.session_state.pending_input = None
    st.session_state.show_temp_user_msg = False

    with st.spinner("🤖 답변 생성 중..."):
        response = requests.post(
            BACKEND_URL,
            json={
                "question": question,
                "messages": st.session_state.messages,
                "summary": st.session_state.summary,
                "user_id": st.session_state.user_id,
            },
        )
        data = response.json()

        # ✅ 상태 저장 (추가 데이터도 함께 저장)
        st.session_state.last_state = data

        # 응답 메시지로 업데이트
        if "messages" in data:
            # 이전 대화 지우고 → 백엔드 응답 messages로 교체
            st.session_state.messages = data["messages"]
        if "summary" in data:
            st.session_state.summary = data["summary"]

        st.rerun()

# 요약 표시
if st.session_state.summary:
    with st.expander("🧠 대화 요약 보기"):
        st.markdown(st.session_state.summary)

# ✅ 사이드바에 상태 정보 출력 --------------------
sidebar_fields = [
    ("rewrite_question", "📝 재작성 질문"),
    ("summary", "📄 요약"),
    ("user_id", "🧑 사용자 ID"),
    ("question_type", "🔖 질문 유형"),
    ("keyword", "🏷️ 키워드"),
    ("search_results", "🔍 1차 검색 결과"),
    ("judge_search_results", "✅ 유용성 판단"),
    ("search_detail_results", "📚 상세 검색 결과"),
]

with st.sidebar:
    st.header("🧠 상태 정보 보기")
    for key, label in sidebar_fields:
        value = st.session_state.last_state.get(key)
        if not value:
            continue
        st.markdown(f"**{label}**")
        if isinstance(value, list):
            for i, item in enumerate(value, 1):
                st.markdown(f"- {i}. {item}")
        else:
            st.markdown(f"{value}")
        st.markdown("---")
