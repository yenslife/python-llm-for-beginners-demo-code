import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = """你的任務是幫助使用者計算字母的數量。
在你要表達數字的地方用 <API>input_string, target_character</API> 來表達。
把 input_string 改成要計算的字串，target_character 改成目標字母。
注意：
1. 不要用引號來包住 input_string 和 target_character。
2. 不要在 input_string 和 target_character 之間加任何符號，例如逗號、空格或其他符號。
3. 不用額外說明計算過程，可以加上自然語言潤飾句子
4. 使用**繁體中文**回答問題。
"""
USER_PROMPT = "在 'strawberry' 這個單字中，有幾個字母 'r' 呢？"

response = client.chat.completions.create(
    model=DEFAULT_MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT,
        },
    ],
)


def count_character(input_string: str, target_character: str) -> int:
    return input_string.count(target_character)


def format_string(input_string: str) -> str:
    start_tag = "<API>"
    end_tag = "</API>"
    start_index = input_string.find(start_tag)
    end_index = input_string.find(end_tag)
    if start_index != -1 and end_index != -1:
        api_content = input_string[start_index + len(start_tag) : end_index].strip()
        try:
            input_str, target_char = map(str.strip, api_content.split(","))
            count = count_character(input_str, target_char)
            return (
                input_string[:start_index]
                + str(count)
                + input_string[end_index + len(end_tag) :]
            )
        except ValueError:
            return (
                "API 語法錯誤，請確認格式為 <API>input_string, target_character</API>。"
            )
    return input_string


print(f"原始回應: {response.choices[0].message.content}")
final_response = format_string(response.choices[0].message.content)
print(f"最終回應: {final_response}")
