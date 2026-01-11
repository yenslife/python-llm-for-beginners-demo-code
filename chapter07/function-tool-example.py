import os
import json

from rich import print
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4o-mini"


def calculate(expression: str) -> dict:
    try:
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# 定義工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "用來計算數學表達式的值。輸入是一個數學表達式的字串，例如 '12 * 34 - 56 / 7'",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要計算的數學表達式。",
                    },
                },
                "required": ["expression"],
            },
        },
    }
]

messages = [
    {"role": "system", "content": "你是一個可以計算數學表達式的助手。"},
    {"role": "user", "content": "請計算 12 * 34 - 56 / 7 的值。"},
]

response = client.chat.completions.create(
    model=DEFAULT_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# 觀察LLM使用工具的情況
print(response.choices[0].message) # 建議用 rich 的 print 方法讓輸出變漂亮

tool_calls = response.choices[0].message.tool_calls
response_message = response.choices[0].message
available_tools = {
    "calculate": calculate,
}

if tool_calls:
    messages.append(response_message)
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        if tool_name in available_tools:
            tool_response = available_tools[tool_name](**tool_args)
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(tool_response),
            })

# 看看我們把工具的回應加進去之後，對話紀錄長怎樣
print(messages)


response = client.chat.completions.create(
    model=DEFAULT_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# 最終回答
print(response.choices[0].message)

