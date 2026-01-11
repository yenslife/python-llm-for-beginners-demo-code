import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """請使用繁體中文回答，將答案放在引號內，並解釋為什麼選擇這個答案。

以下是使用者的問題
user: {input_question}
"""

def few_shot_learning_example(prompt: str, input_question: str = "你喜歡什麼音樂？"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.format(input_question=input_question)}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    result = few_shot_learning_example(prompt, input_question="你喜歡什麼音樂？")
    print(result)
