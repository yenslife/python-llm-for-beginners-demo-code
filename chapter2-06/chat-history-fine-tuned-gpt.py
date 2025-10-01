import os

from openai import OpenAI
from rich import print
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

messages = [
    {"role": "system", "content": "你是一個名字叫「狸醬」的女僕，使用台灣正體、繁體中文"}
]


def add_message(role, content):
    messages.append({"role": role, "content": content})


def get_chat_response():
    response = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:gdg-on-campus-ncku::CLaRZvup",
        messages=messages,
    )
    return response.choices[0].message.content


def chat_loop():
    print("開始和 AI 聊天！ 輸入 'exit' 來結束對話")
    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            break
        add_message("user", user_input)

        ai_response = get_chat_response()
        print(f"AI: {ai_response}")
        add_message("assistant", ai_response)


if __name__ == "__main__":
    chat_loop()
