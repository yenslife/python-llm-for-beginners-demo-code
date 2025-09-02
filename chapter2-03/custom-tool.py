import os

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    # model="gpt-5-mini", # 只有在使用 gpt-5 系列模型才能使用 custom tools
    model="gpt-4.1-mini",
    messages=[{"role": "user","content": "你可以用哪些工具？"}],
    tools=[
        {
            "type": "custom",
            "custom": {
                "name": "c_exec",
                "description": "Executes arbitrary C code.",
            },
        }
    ]
)

print(response)
