import os

import tiktoken
from rich import print
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def count_tokens_with_tiktoken(
    input_text: str = "hello world", model_name: str = "gpt-4.1-mini"
) -> tuple:
    tokenizer = tiktoken.encoding_for_model(model_name)  # 取得指定模型的 tokenizer
    encodings = tokenizer.encode(input_text)
    return len(encodings), encodings, tokenizer


def get_usage_with_api(
    input_text: str = "hello world", model_name: str = "gpt-4.1-mini"
) -> tuple:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model_name, messages=[{"role": "user", "content": input_text}]
    )
    usage = response.usage
    response_text = response.choices[0].message.content
    if response_text is None:
        return "", usage
    return response_text, usage


if __name__ == "__main__":
    input_text = "hello world"
    model_name = "gpt-4.1-mini"
    input_tokens_length, _, tokenizer = count_tokens_with_tiktoken(
        input_text, model_name
    )
    response_text, usage = get_usage_with_api(input_text, model_name)
    output_tokens_length, _, _ = count_tokens_with_tiktoken(response_text, model_name)
    print(f"使用的 tokenizer: {tokenizer}")
    print(f"Input tokens length: {input_tokens_length}")
    print(f"Output tokens length: {output_tokens_length}")
    print(f"Total tokens length from usage: {usage.total_tokens}")
    print("usage", usage)
    special_tokens_length, special_token_encodings, _ = count_tokens_with_tiktoken(
        "<|im_start|>", model_name
    )
    print(f"Special tokens length: {special_tokens_length}")
    print(f"Special token encodings: {special_token_encodings}")
