import os
import json

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_LENGTH = 10000
DEFAULT_MODEL = "gpt-4.1-mini"
SYSTEM_PROMPT = """你是一個能解數學與字元統計的小幫手
你可以使用兩種工具來得到正確答案：

- calculate: 計算數學表達式（四則運算、括號、整數/小數）。
- count_character: 統計文字中某個「目標字元」出現的次數（支援 Unicode）。

決策規則
1. 若問題包含可用四則運算求值的表達式，務必呼叫 calculate。
2. 若問題要統計字元次數（例如「'banana' 有幾個 a？」），務必呼叫 count_character。
3. 如同時有兩種需求，例如「先計算、再統計結果」，務必**先呼叫第一個工具並取得結果**，然後再將此結果作為輸入，呼叫第二個工具，最後彙整答案。
4. 遇到含糊/格式不合法的輸入（如表達式語法錯誤、target 不是單一字元等），先提出簡短澄清或回報錯誤訊息。

輸出風格
除非被要求，不要輸出長篇推導過程或無關的內容。

範例任務與處理方式
「請計算 12 * 34 - 56 / 7」→ 呼叫 calculate，回覆數值結果與一句話說明。
「在 'abracadabra' 裡，字母 'a' 出現幾次？」-> 呼叫 count_character，回覆次數與一句話說明。
「把 'hello' 裡的 l 數一數，然後計算 3*(5+2)」-> 依序呼叫 count_character 與 calculate，最後合併回答。
「計算 'apple' 裡的 p 數量，將其結果乘以5 + 3」-> 先呼叫 count_character，取得答案後，第二輪問答輸出帶入 calculate，最後回覆結果。"""


## Tools
def calculate(expression: str) -> dict:
    try:
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

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

# 定義兩個 function tool
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
    },
    {
        "type": "function",
        "function": {
            "name": "count_character",
            "description": "用來計算目標字串的字母的數量。輸入是一個字串和一個目標字母。",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_string": {
                        "type": "string",
                        "description": "要計算的字串。",
                    },
                    "target_character": {
                        "type": "string",
                        "description": "要計算的目標字母。",
                    },
                },
                "required": ["input_string", "target_character"],
            },
        },
    }
]

available_tools = {
    "calculate": calculate,
    "count_character": count_character,
}

## Memory
messages = []

def count_tokens(message: str) -> int:
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL)
    return len(encoding.encode(message))


def add_message(role: str, content: str) -> None:
    # 把 tools 的 JSON Schema 的 token 數也加進去
    # 如果你有觀察 API 回傳的 Token 數量
    # 會發現其實 tools 的 token 數量只有在一開始有被算進 total_tokens 裡
    # 所以這邊我們算一次就好
    tokens = count_tokens(content) 
    tool_token = count_tokens(json.dumps(tools, ensure_ascii=False, separators=(",", ":")))
    messages.append({"role": role, "content": content, "tokens": tokens + tool_token if role == "system" else tokens})


def check_message_length(max_length: int = 1000):
    total_tokens = sum([msg["tokens"] if isinstance(msg, dict) else 0 for msg in messages])
    while total_tokens > max_length:
    # 把 user 或 assistant 的第一筆 content 刪除 (避免刪到 system prompt)
        messages.pop(1)  
        total_tokens = sum(msg["tokens"]  if isinstance(msg, dict) else 0 for msg in messages)
    # print(f"目前訊息長度 (包含工具 JSON Schema Prompt) 約為: {total_tokens} tokens")


def get_chat_response(model_name: str = DEFAULT_MODEL):
    # 在請求之前把 messages 的 tokens 拿掉，避免錯誤
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response


def chat_loop():
    print("開始和 AI 聊天！ 輸入 'exit' 來結束對話")
    add_message("system", "使用繁體中文回答使用者的問題")
    while True:
        user_input = input("你: ")
        if user_input.lower() == "exit":
            break
        add_message("user", user_input)
        check_message_length(max_length=MAX_LENGTH)

        ai_response = get_chat_response()
        tool_calls = ai_response.choices[0].message.tool_calls
        response_message = ai_response.choices[0].message
        while tool_calls:
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
                        "tokens": count_tokens(json.dumps(tool_response)) # 把 tool 回傳的內容也記錄下來
                    })
            ai_response = get_chat_response()
            tool_calls = ai_response.choices[0].message.tool_calls
            response_message = ai_response.choices[0].message


        ai_response_text = format_string(response_message.content)
        print(f"AI: {ai_response_text}")
        add_message("assistant", ai_response_text)
        check_message_length(max_length=MAX_LENGTH)


if __name__ == "__main__":
    chat_loop()
