import os
import asyncio

from openai import AsyncOpenAI
from openai.helpers import Microphone
from dotenv import load_dotenv
from rich import print

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def main():
    mic = Microphone(timeout=5)
    print("Please say something...")
    wav_file_tuple = await mic.record()
    filenane, buffer, mime_type = wav_file_tuple

    # 可以寫入檔案
    with open("recorded.wav", "wb") as f:
        f.write(buffer.read())
    print("錄音結束")

    # 也可以直接傳給 OpenAI API
    transcript = await client.audio.transcriptions.create(
        file=wav_file_tuple,
        model="whisper-1",
    )
    print("Transcription:", transcript.text)

asyncio.run(main())
