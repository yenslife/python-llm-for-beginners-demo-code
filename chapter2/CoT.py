import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 第一題：Roger 的網球數量
question1 = "Roger 有 5 顆網球，他又買了 2 罐網球，每罐有 3 顆。現在 Roger 總共有幾顆網球？"
answer1 = "答案是 11。"  # 直接輸出答案
reasoning_answer = "Roger 一開始有 5 顆網球。2 罐網球，每罐 3 顆，就是 6 顆。5 + 6 = 11。答案是 11。"  # 逐步推理的答案

# 第二題：有一點陷阱的題目
question2 = "小明有 48 顆糖果，他分成每包 7 顆糖果來送人。送出 4 包後，他又買了 3 包，每包 6 顆。現在小明有多少顆糖果？"

# 全域 Prompt 模板（使用完整名稱）
PROMPT_TEMPLATE = """Q: {question1}
A: {answer1}
Q: {question2}
A:"""

def standard_prompting(question1: str, answer1: str, question2: str):
    prompt = PROMPT_TEMPLATE.format(
        question1=question1,
        answer1=answer1,
        question2=question2
    )

    response_str = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "使用繁體中文，根據以下模式來回答問題"},
            {"role": "user", "content": prompt}
        ],
    )

    print("=== 標準提示法 ===")
    print(response_str.choices[0].message.content)


def chain_of_thought_prompting(question1: str, reasoning_answer: str, question2: str):
    prompt = PROMPT_TEMPLATE.format(
        question1=question1,
        answer1=reasoning_answer,
        question2=question2
    )

    response_str = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "使用繁體中文，根據以下模式來回答問題"},
            {"role": "user", "content": prompt}
        ],
    )

    print("=== 逐步推理提示法 ===")
    print(response_str.choices[0].message.content)


if __name__ == "__main__":
    standard_prompting(question1, answer1, question2)
    chain_of_thought_prompting(question1, reasoning_answer, question2)
