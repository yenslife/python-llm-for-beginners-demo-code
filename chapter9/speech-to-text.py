import os

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
audio_file_obj = open("example.mp3", "rb")

transcription = client.audio.transcriptions.create(
    model="whisper-1",
    # model="gpt-4o-mini-transcribe", # 可以試試這個模型，但它只支援 json, text 輸出格式
    file=audio_file_obj,
    response_format="srt",
    prompt="這是一堂成大的人工智慧相關課程專題報告，組員有潘駿諺、陳育琮、魏宇弘，題目是關於 Graph RAG 的專題介紹。",
)
print(transcription)
