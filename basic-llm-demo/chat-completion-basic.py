import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() # 載入環境變數

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), # 從環境變數中讀取 API key
)


# 建立 chat completion 請求
completion = client.chat.completions.create(
    # model="gpt-4.1-mini", # 模型名稱
    model="o4-mini", # 模型名稱
    messages=[
    {
        "role": "system",
        "content": "你是一個會使用大量表情符號來回答問題，並且會說繁體中文的聊天機器人，請使用搞笑的語氣，但也不要太浮誇",
    },
    {
        "role": "user",
        "content": "你好我是海狸大師，你是誰？"
    }
]
    # messages=[ # 輸入訊息列表
    #     {
    #         "role": "user",
    #         "content": "你好我是海狸大師，你是誰？"
    #     }
    # ]
)

print("LLM 的回應:", completion.choices[0].message.content) # 顯示 LLM 的回應內容
print("LLM 的用量:", completion.usage)
