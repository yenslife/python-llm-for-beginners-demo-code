import os

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def different_penalty(frequency_penalty, presence_penalty):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一個很會寫詩的人，就像李白"},
            {"role": "user", "content": "寫一首關於美女蘇珊的七言律詩"},
        ],
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_completion_tokens=200,
    )
    print(f"\n[bold yellow]frequency_penalty={frequency_penalty}, presence_penalty={presence_penalty}[/bold yellow]")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    different_penalty(0, 0)
    different_penalty(2, 0)
    different_penalty(-2, 0)
    different_penalty(0, 2)
    different_penalty(0, -2)
    different_penalty(2, 2)
    different_penalty(2, -2)
    different_penalty(-2, 2)
    different_penalty(-2, -2)
