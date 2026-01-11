import os
from base64 import b64decode
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="為什麼要分手...我...真的很難過",
    instructions="用難過的語氣來講這句話，最好是要哭出來那種",
    response_format="mp3"
)

# 寫入 MP3 檔案
response.write_to_file("output.mp3")
