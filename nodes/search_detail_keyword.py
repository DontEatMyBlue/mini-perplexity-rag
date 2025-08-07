import requests
from bs4 import BeautifulSoup
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from graph.set_state import State
from langchain.text_splitter import TokenTextSplitter

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def split_text_into_documents(
    text: str, url: str, chunk_size: int = 500, chunk_overlap: int = 50
) -> list[Document]:
    splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)

    return [
        Document(page_content=chunk, metadata={"source": url, "chunk_index": idx})
        for idx, chunk in enumerate(chunks)
    ]


def crawl_webpage_text(state: State) -> State:
    if state.get("error"):
        return state

    try:
        url_list = state.get("judge_search_results", [])[0].get("url", [])
        all_documents = []

        user_id = state.get("user_id", "default_user")
        print(f"User ID: {user_id}")
        collection_name = f"collection_{user_id}"

        # 유저 전용 vector store
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db",
        )

        for url in url_list:
            try:
                print(f"Processing URL: {url}")
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/115.0.0.0 Safari/537.36"
                    )
                }

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style", "noscript"]):
                    script.decompose()

                text = soup.get_text(separator="\n")
                clean_lines = [
                    line.strip() for line in text.splitlines() if line.strip()
                ]
                clean_text = "\n".join(clean_lines)

                documents = split_text_into_documents(clean_text, url, chunk_size=500)
                all_documents.extend(documents)

            except Exception as e:
                print(f"[⚠️ Error] Failed to crawl {url}: {e}")
                continue  # 다음 URL로 넘어감

        # 루프 밖에서 한 번만 저장
        vector_store.add_documents(all_documents)
        print(f"[{collection_name}]에 문서 {len(all_documents)}개 저장 완료")

        return state

    except Exception as e:
        print(f"[❌ Error] crawl_webpage_text 전체 실패: {e}")
        return {
            **state,
            "error": {
                "node": "crawl_webpage_text",
                "message": str(e),
                "type": type(e).__name__,
                "level": "critical",
            },
        }
