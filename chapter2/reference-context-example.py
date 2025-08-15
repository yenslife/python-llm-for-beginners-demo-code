import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

reference_data = ""
with open("reference-data.txt", "r", encoding="utf-8") as file:
    reference_data = file.read()

prompt = """請根據以下文本提供的 OpenAI API 價格來回答使用者的提問，使用繁體中文回答問題
文本內容如下：
{reference_data}

以下是使用者的問題
{input_question}
"""

def reference_context_example(prompt: str, reference_data: str, input_question: str = "請問 gpt-5 的價格怎麼算？"):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.format(reference_data=reference_data, input_question=input_question)}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    result = reference_context_example(prompt, reference_data=reference_data, input_question="請問 gpt-5 的 input 價格怎麼算？")
    print(result)
