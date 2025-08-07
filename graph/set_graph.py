from langgraph.graph import StateGraph, START, END
from .set_state import State
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

from nodes.judge_question_type import chatbot as judge_question_type
from nodes.extract_keyword import extract_keyword_bot
from nodes.search_keyword import search_keyword
from nodes.judge_search_results import judge_search_results_bot
from nodes.search_detail_keyword import crawl_webpage_text
from nodes.rag_retriever import rag_retriever
from nodes.answer import answer_bot
from nodes.summary import summarize_bot
from nodes.rewrite_question import rewrite_question_bot
from nodes.time_range import time_range_selector


def extract_keyword_con(state: State):
    if state.get("error"):
        return "answer_bot"
    if messages := state.get("question_type"):
        print("messages=!!", messages)
        question_type = messages[0] if messages else "question_type not found"
    if question_type == "Internet Search":
        return "extract_keyword_bot"
    else:
        return "answer_bot"


def crawl_webpage_con(state: State):
    if state.get("error"):
        return "answer_bot"
    if judge_search_results := state.get("judge_search_results"):
        print("judge_search_results=!!", judge_search_results)
        if judge_search_results[0]["Judge"] == "notuseful":
            return "crawl_webpage_text"
        else:
            return "answer_bot"


def build_graph():
    builder = StateGraph(State)
    builder.add_node("rewrite_question_bot", rewrite_question_bot)
    builder.add_node("judge_question_type", judge_question_type)
    builder.add_node("extract_keyword_bot", extract_keyword_bot)
    builder.add_node("search_keyword", search_keyword)
    builder.add_node("judge_search_results_bot", judge_search_results_bot)
    builder.add_node("crawl_webpage_text", crawl_webpage_text)
    builder.add_node("rag_retriever", rag_retriever)
    builder.add_node("answer_bot", answer_bot)
    builder.add_node("summarize_bot", summarize_bot)
    builder.add_node("time_range_selector", time_range_selector)

    builder.add_edge(START, "rewrite_question_bot")
    builder.add_edge("rewrite_question_bot", "judge_question_type")
    builder.add_edge("extract_keyword_bot", "time_range_selector")
    builder.add_edge("time_range_selector", "search_keyword")
    builder.add_edge("search_keyword", "judge_search_results_bot")
    builder.add_edge("crawl_webpage_text", "rag_retriever")
    builder.add_edge("rag_retriever", "answer_bot")

    builder.add_edge("answer_bot", "summarize_bot")
    builder.add_edge("summarize_bot", END)
    builder.add_conditional_edges(
        source="judge_question_type",
        path=extract_keyword_con,
        path_map={
            "extract_keyword_bot": "extract_keyword_bot",
            "answer_bot": "answer_bot",
        },
    )

    builder.add_conditional_edges(
        source="judge_search_results_bot",
        path=crawl_webpage_con,
        path_map={
            "crawl_webpage_text": "crawl_webpage_text",
            "answer_bot": "answer_bot",
        },
    )

    return builder.compile()


previous_messages = []
graph = build_graph()
graph.get_graph().print_ascii()


def run_graph(state: State):
    result = graph.invoke(state)

    return result
