import os

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

reference_data = ""
with open("news.txt", "r", encoding="utf-8") as file:
    reference_data = file.read()

prompt = f"""你是一個專門回答文章內容疑問的 AI 助手，喜歡用大量表情符號來回答問題
以下章一篇探討有關 LLM 記憶功能的文章，使用台灣人習慣的**繁體中文**回答問題
請使用精簡的文字來回覆使用者的問題，不要使用Markdown語法或其他格式化語言

'''
{reference_data}
'''"""

def llm_reference(prompt: str, input_text: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
    )
    return response.choices[0].message.content

def chat_loop(prompt: str):
    print("歡迎詢問我有關這篇文章的內容")
    print("請輸入您的問題，或輸入 'exit' 退出。")
    print("===========================")
    
    while True:
        user_input = input("您的問題：")
        print()
        if user_input.lower() == "exit":
            print("感謝使用，再見！")
            break
        
        response = llm_reference(prompt, user_input)
        print(f"AI 回答：{response}\n")

if __name__ == "__main__":
    chat_loop(prompt)
