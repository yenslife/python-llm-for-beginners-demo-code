import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """根據以下回覆格式來回答問題，請使用繁體中文回答，將答案放在引號內，並解釋為什麼選擇這個答案。
範例一
user: 你喜歡什麼顏色？
assistant: 「藍色」。因為藍色讓我感覺平靜和放鬆。

範例二
user: 你最喜歡的食物是什麼？
assistant: 「披薩」。因為披薩有很多種口味，可以滿足不同的喜好。

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
