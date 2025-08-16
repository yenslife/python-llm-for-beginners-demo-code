import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

messages = [
    {"role": "system", "content": "使用繁體中文回答使用者的問題"},
]

def add_message(role, content):
    messages.append({"role": role, "content": content})

def get_chat_response():
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
    )
    return response.choices[0].message.content

def chat_loop():
    print("開始和 AI 聊天！ 輸入 'exit' 來結束對話")
    while True:
        user_input = input("你: ")
        if user_input.lower() == 'exit':
            break
        add_message("user", user_input)
        
        ai_response = get_chat_response()
        print(f"AI: {ai_response}")
        add_message("assistant", ai_response)

if __name__ == "__main__":
    chat_loop()
