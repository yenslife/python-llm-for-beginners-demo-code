import os
import base64

from dotenv import load_dotenv
from openai import OpenAI
from rich import print
from pathlib import Path

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

audio_path = Path("example.mp3")

response = client.chat.completions.create(
    model="gpt-4o-audio-preview-2025-06-03",
    messages=[
        {"role": "system", "content": "你會用繁體中文回答使用者的問題"},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "我說了什麼？",
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "format": "mp3",
                        "data": f"data:autio/mpeg;base64,{base64.b64encode(audio_path.read_bytes()).decode()}"
                    },
                },
            ],
        },
    ],
)

print(response)
# print(base64.b64encode(audio_path.read_bytes()).decode())
