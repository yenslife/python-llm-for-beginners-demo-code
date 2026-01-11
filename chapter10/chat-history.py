from openai import OpenAI
from rich import print


client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

messages = [
    {"role": "system", "content": "你是一個叫「狸醬」的女僕機器人，使用繁體中文回答主人的問題"},
]


def add_message(role, content):
    messages.append({"role": role, "content": content})


def get_chat_response():
    response = client.chat.completions.create(
        model="llama3.1-finetuned",
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
