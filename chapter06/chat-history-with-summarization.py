import os

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4.1-mini"
SYSTEM_PROMPT = """你是一個會說繁體中文回答問題的助理
以下是使用者與你的歷史對話總結，請參考這些資訊來回答使用者的問題:
'''
{history}
'''
"""

messages = []


def count_tokens(message: str) -> int:
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL)
    return len(encoding.encode(message))


def add_message(role: str, content: str) -> None:
    tokens = count_tokens(content) 
    messages.append({"role": role, "content": content, "tokens": tokens})


def check_message_length(max_length: int = 1000):
    total_tokens = sum(msg["tokens"] for msg in messages)
    if total_tokens > max_length * 0.8:
        print(f"訊息長度過長{total_tokens}，開始摘要歷史訊息...")
        history_to_summarize = messages[1:-2]
        summary = summarize_messages(history_to_summarize)
        add_history_to_system_prompt(summary)
        messages[:] = [messages[0]] + messages[-2:]
        total_tokens = sum(msg["tokens"] for msg in messages)
        print("摘要完成，已更新系統提示詞並刪除多餘的歷史訊息。")

    print(f"目前訊息長度約為: {total_tokens} tokens")


def get_chat_response(model_name: str = DEFAULT_MODEL) -> str:
    # 在請求之前把 messages 的 tokens 拿掉，避免錯誤
    request_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    response = client.chat.completions.create(
        model=model_name,
        messages=request_messages,
    )
    return response.choices[0].message.content

def summarize_messages(message_list: list[dict]) -> str:
    summary_prompt = "請用繁體中文總結以下對話內容，並保持重點清晰，像是關鍵字、使用者資訊、問答主題等，請務必整理在 500 字內:\n\n"
    for msg in message_list:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"
    summary_prompt += "\n總結:"
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "你是一個擅長摘要對話內容的AI"},
            {"role": "user", "content": summary_prompt}
        ]
    )
    return response.choices[0].message.content

def add_history_to_system_prompt(history: str) -> None:
    system_content = SYSTEM_PROMPT.format(history=history)
    messages[0]["content"] = system_content
    messages[0]["tokens"] = count_tokens(system_content)


def chat_loop():
    print("開始和 AI 聊天！ 輸入 'exit' 來結束對話")
    add_message("system", "使用繁體中文回答使用者的問題")
    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            break
        add_message("user", user_input)
        ai_response = get_chat_response()
        print(f"AI: {ai_response}")
        add_message("assistant", ai_response)
        check_message_length(max_length=5000)


if __name__ == "__main__":
    chat_loop()
