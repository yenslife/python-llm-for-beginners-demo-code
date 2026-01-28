import os

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4.1-mini"

messages = []


def count_tokens(message: str) -> int:
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL)
    return len(encoding.encode(message))


def add_message(role: str, content: str) -> None:
    tokens = count_tokens(content) 
    messages.append({"role": role, "content": content, "tokens": tokens})


def check_message_length(max_length: int = 1000):
    total_tokens = sum(msg["tokens"] for msg in messages)
    while total_tokens > max_length:
    # 把 user 或 assistant 的第一筆 content 刪除 (避免刪到 system prompt)
        messages.pop(1)  
        total_tokens = sum(msg["tokens"] for msg in messages)
    print(f"目前訊息長度約為: {total_tokens} tokens")


def get_chat_response(model_name: str = DEFAULT_MODEL) -> str:
    # 在請求之前把 messages 的 tokens 拿掉，避免錯誤
    request_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    response = client.chat.completions.create(
        model=model_name,
        messages=request_messages,
    )
    return response.choices[0].message.content


def chat_loop():
    print("開始和 AI 聊天！ 輸入 'exit' 來結束對話")
    add_message("system", "使用繁體中文回答使用者的問題")
    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            break
        add_message("user", user_input)
        check_message_length(max_length=100)

        ai_response = get_chat_response()
        print(f"AI: {ai_response}")
        add_message("assistant", ai_response)
        check_message_length(max_length=100)


if __name__ == "__main__":
    chat_loop()
