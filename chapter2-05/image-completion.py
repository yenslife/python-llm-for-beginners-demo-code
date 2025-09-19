import os
import base64

from dotenv import load_dotenv
from openai import OpenAI
from rich import print
from pathlib import Path

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

image_path = Path("example.jpg")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你會用繁體中文回答使用者的問題"},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "活動名稱是什麼",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(image_path.read_bytes()).decode()}"
                        # "url": "https://raw.githubusercontent.com/yenslife/python-llm-for-beginners-demo-code/refs/heads/main/chapter2-05/example.jpg" # 也可以用圖片網址
                    },
                },
            ],
        },
    ],
)

print(response)
