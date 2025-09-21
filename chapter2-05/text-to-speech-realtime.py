import os
import asyncio

from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
from dotenv import load_dotenv

load_dotenv()
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_llm_response():
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一個很會安慰人的朋友"},
            {"role": "user", "content": "海狸大師最近和女朋友分手了，他很難過，你要怎麼安慰他？"}
        ],
        stream=True,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta
        print(delta.content, end="", flush=True)
    print("\n\n安慰結束")

async def main() -> None:
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input="為什麼要分手...我...真的很難過，啊啊嗚嗚嗚嗚嗚",
        instructions="用難過的語氣來講這句話，最好是要哭出來那種，最後要大叫",
        response_format="wav",
    ) as response:
        await asyncio.gather(get_llm_response(), LocalAudioPlayer().play(response))

if __name__ == "__main__":
    asyncio.run(main())
