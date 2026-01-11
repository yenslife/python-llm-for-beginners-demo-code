import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Give model time to think by using a prompt that encourages reasoning
prompt = """使用繁體中文回答以下問題
請在回答前先思考一下，然後再給出你的答案。問題是：{input_question}"""

def answer_with_think_process(prompt: str, input_question: str = "小明有 48 顆糖果，他分成每包 7 顆糖果來送人。送出 4 包後，他又買了 3 包，每包 6 顆。現在小明有多少顆糖果？"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.format(input_question=input_question)}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    result = answer_with_think_process(prompt)
    print(result)  # Output the model's response
