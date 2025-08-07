from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from graph.set_state import State
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from chromadb.config import Settings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def rag_retriever(state: State):
    if state.get("error"):
        return state
    try:
        user_id = state.get("user_id", "default_user")
        collection_name = f"collection_{user_id}"

        # 유저 전용 vector store
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db",
        )

        base_retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        compressor = LLMChainExtractor.from_llm(llm)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )

        # 검색어 추출
        rewrite_question = state.get("rewrite_question", "No question provided")
        print("rewrite_question=", rewrite_question)
        # 검색 수행
        results = retriever.invoke(rewrite_question)
        print("RAG results:", results)
        plain_results = base_retriever.invoke(rewrite_question)
        print("🔍 base_retriever results (압축 없음):", plain_results)
        return {"search_detail_results": results}

    except Exception as e:
        print(f"Error in rag_retriever: {e}")
        return {
            **state,
            "error": {
                "node": "rag_retriever",
                "message": str(e),
            },
        }
