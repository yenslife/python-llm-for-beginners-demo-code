import os
import json
import uuid

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from rich import print

from llm_provider import LLMProvider

load_dotenv()

# 載入資料
with open("edited.json", "r", encoding="utf-8") as f:
    documents = json.load(f)
    print(f"Loaded {len(documents)} documents")

# 資料清理
for doc in documents:
    doc["html"] = doc["html"].replace("跳到主要內容區\n學生事務長信箱\n聯絡我們\n網站地圖\nEnglish\n本校首頁\n回首頁\n搜尋\n\n", "")
    doc["html"] = doc["html"].replace("瀏覽數:\n\n住宿服務組地址：701台南市東區大學路1號 勝利校區 勝利四舍1樓。\n\n電話 (06)2757575 轉分機 86340。傳真 886-6-2003273。\nE-Mail: em86340@email.ncku.edu.tw", "")
    doc["html"] = doc["html"].replace("Jump to the main content block\nOffice of Student Affairs\nContact us\nSite Map\n中文\nNCKU\n\n", "")
    doc["html"] = doc["html"].replace("跳到主要內容區\n學生事務長信箱\n聯絡我們\n網站地圖\nEnglish\n本校首頁\n回首頁\n搜尋\n\n \n\n主選單\n最新消息 \n新生專區 [*]\n行事曆 \n單位介紹 \n法規與SOP \n表單下載\n住宿知多少 \n宿委會 \n常見Q&A\n連繫方式\n防疫專區\n性別友善專區\n宿舍場地借用\n業務分類\n宿舍申請\n住宿費減免\n宿舍餐廳\n工程類進度\n東寧宿舍興建\n宿舍自修室\n宿舍簡易廚房\n服務學習三\n宿舍會議記錄\n活動花絮 \n宿舍財務資訊", "")

    # 把 title, url, html 三個欄位合併成一個字串的欄位
    doc["text"] = f"Title: {doc['title']}\nURL: {doc['url']}\nContent: {doc['html']}"

# 資料切 chunk
CHUNK_SIZE = 500  # 每個 chunk 大小
CHUNK_OVERLAP = 50  # chunk 重疊大小
new_documents = []
for doc in documents:
    text = doc["text"]
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = text[i:i + CHUNK_SIZE]
        new_documents.append({
            "title": doc["title"],
            "url": doc["url"],
            "text": chunk
        })

documents = new_documents
print(f"After chunking, we have {len(documents)} documents")

# 建立 ChromaDB client 端
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",  # 資料會存在這個資料夾
)

# 建立 collection，這邊我們直接用 OpenAI 的 embedding function
# 如果要用 Google 的 embedding function，可以參考 https://docs.trychroma.com/integrations/embedding-models/google-gemini
collection = chroma_client.get_or_create_collection(
    name="ncku_dormitory",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-large",
    )
)

# 把資料加入 collection
# 加過一次就好，之後不需要再加了，記得要註解掉
collection.add(
    ids=[str(uuid.uuid4()) for _ in range(len(documents))],
    metadatas=[{"title": doc["title"], "url": doc["url"]} for doc in documents], # 不一定要加
    documents=[doc["text"] for doc in documents],
)

# 測試檢索效果
results = collection.query(
    query_texts=["住宿費要去哪邊繳交？"], # Chroma will embed this for you
    n_results=10, # how many results to return
    include=["documents"]
)
print(results)


# 把檢索結果用 LLM 來回答
llm = LLMProvider()
context = "\n\n".join([result for result in results['documents'][0]])
question = "住宿費要去哪邊繳交？"

respnose = llm.generate_answer(question, context)
print(f"LLM 回答: {respnose}")
