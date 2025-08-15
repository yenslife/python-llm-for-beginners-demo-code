import torch
from transformers.pipelines import pipeline
from rich import print
from typing import Any

pipe = pipeline(task="text-generation", model="openai-community/gpt2", torch_dtype=torch.float16, device=-1, pad_token_id=50256)
tokenizer: Any = pipe.tokenizer

# input_text = "I love you, but"
# input_text = "User: What is AI?\nAssistant:"
input_text = "Space Needle is in downtown"
ret = pipe(input_text, max_new_tokens=1)
print(ret)
# Output the generated text
full_generated_text = ret[0]['generated_text']
model_output = ret[0]['generated_text'][len(input_text):]

# see token_ids
token_ids = tokenizer(full_generated_text, return_tensors="pt")['input_ids'][0].tolist()
print(f"輸入的文字: {input_text}")
print(f"模型輸出的文字: {model_output}")
print(f"原始 Token ID: {token_ids}")

tokens = tokenizer.convert_ids_to_tokens(token_ids)
print("轉換後的 token")
for idx, tok in zip(token_ids, tokens):
    print(f"{idx:>5} → {tok}")
