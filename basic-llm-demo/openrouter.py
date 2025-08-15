import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPEN_ROUTER_API_KEY')

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

system_prompt = "你是一個會說繁體中文，而且會使用大量表情符號互動的可愛機器人"

response = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "你好！你會說繁體中文嗎？你是誰呢？"},
    ],
    max_tokens=100,
    temperature=0.7,
)

print(response.choices[0].message.content)
