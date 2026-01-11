import os
import asyncio

from openai import AsyncOpenAI
from openai.helpers import Microphone
from dotenv import load_dotenv
from rich import print

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

stop_flag = False

def should_record():
    return not stop_flag

async def keyboard_listener():
    global stop_flag
    print("Press Enter to stop recording...")
    user_input = await asyncio.to_thread(input, "輸入 q 並按 Enter 鍵停止錄音: ")
    if user_input.strip().lower() == 'q':
        stop_flag = True

async def main():
    mic = Microphone(should_record=should_record)
    print("Please say something...")
    task_return_value = await asyncio.gather(
        mic.record(),
        keyboard_listener()
    )
    filenane, buffer, mime_type = task_return_value[0]

    # 可以寫入檔案
    with open("recorded.wav", "wb") as f:
        f.write(buffer.read())
    print("錄音結束")

    # 也可以直接傳給 OpenAI API
    transcript = await client.audio.transcriptions.create(
        file=task_return_value[0],
        model="whisper-1",
    )
    print("Transcription:", transcript.text)

if __name__ == "__main__":
    asyncio.run(main())
