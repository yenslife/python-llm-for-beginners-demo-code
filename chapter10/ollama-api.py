from openai import OpenAI
from rich import print

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 手動保留完整對話
messages = [
    {"role": "user", "content": "你叫什麼名字？"},
]

response = client.chat.completions.create(
    model="llama3.1-finetuned",
    # model="qwen2.5",
    messages=messages,
)

print(response.choices[0].message.content)
