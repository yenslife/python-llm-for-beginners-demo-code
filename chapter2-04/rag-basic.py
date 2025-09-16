import os

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from rich import print
from rich.progress import track

from vector_store import VectorStore
from llm_provider import LLMProvider

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"

# 若要使用別家的模型，記得修改 base_url 和 api_key
load_dotenv()
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# 載入資料
document = ""
with open("dong-ning-dorm-rule.md", "r", encoding="utf-8") as file:
    document = file.read()


# 資料切 chunk
def chunk_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# 客製化的切 Chunk 版本
def chunk_text_customize(text, delimiter="\n"):
    chunks = []
    chinese_number = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    chunks = text.split(delimiter)  # 先用換行切
    chunks = [chunk for chunk in chunks if chunk.strip() != ""]  # 移除空白

    for chunk in chunks:
        try:
            # 第一種：開頭中文數字表示為「條」，下一個是（表示為「款」
            if chunk[0] in chinese_number and chunks[chunks.index(chunk) + 1][0] == "（":
                chunks.remove(chunk)
            # 第二種：開頭是（表示為「款」，下一個是數字表示為「條」
            if chunk[0] == "（" and chunks[chunks.index(chunk) + 1][0].isdigit():
                chunks.remove(chunk)
        except IndexError:
            pass

    return chunks


# 向量化
def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model=GEMINI_EMBEDDING_MODEL,
    )
    return response.data[0].embedding


def get_similarity(vec1, vec2):
    result = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return result


# 建立向量儲存庫
def build_vector_store(chunks):
    store = VectorStore()
    for chunk in track(chunks):
        embedding = get_embedding(chunk)
        store.add_chunk(chunk, embedding)
    return store


if __name__ == "__main__":
    # 切塊
    chunks = chunk_text_customize(document)

    # 建立並儲存向量資料庫
    print("正在建立向量資料庫...")
    vector_store = build_vector_store(chunks)
    vector_store.save_to_json("chunk_vectors.json")
    print(f"向量資料庫建立完成，共 {len(vector_store)} 個文本塊")
    ## 若已建立好向量庫，可直接載入 (記得把上面的程式碼註解掉)
    # vector_store = VectorStore.load_from_json("chunk_vectors.json") 

    # 測試相似度搜尋
    query = "東寧宿舍的訪客留宿時間是幾點到幾點"
    query_embedding = get_embedding(query)
    similar_chunks = vector_store.search_similar(query_embedding, top_k=10)

    print(f"\n查詢內容: {query}")
    print("最相似的文本塊:")
    for chunk, similarity in similar_chunks:
        print(f"相似度: {similarity:.4f}")
        print(f"內容: {chunk[:100]}...\n")

    # 使用 LLMProvider 進行 RAG 回答
    print("=" * 50)
    print("使用 RAG 生成回答:")
    print("=" * 50)

    # 建立 LLM Provider
    llm_provider = LLMProvider()

    # 將檢索到的文本合併為 context
    context = "\n\n".join([chunk for chunk, _ in similar_chunks])

    # 生成回答
    answer = llm_provider.generate_answer(query, context)
    print(f"\n問題: {query}")
    print(f"回答: {answer}")
