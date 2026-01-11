import json

def convert_instruction_to_chat(instruction_data):
    chat_data = []
    system_prompt = "你是一個名字叫「狸醬」的女僕，使用台灣正體、繁體中文"
    for item in instruction_data:
        messages = [{"role": "system", "content": system_prompt}]
        user_content = item["instruction"]
        if item["input"].strip() != "":
            user_content += "\n" + item["input"]
        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": item["output"]})
        chat_data.append({"messages": messages})
    return chat_data



if __name__ == "__main__":
    # 讀取 instruction 格式的 JSONL 檔案
    with open("tanichan_dataset_full.jsonl", "r", encoding="utf-8") as f:
        instruction_data = [json.loads(line) for line in f]

    # 轉換成 chat 格式
    chat_data = convert_instruction_to_chat(instruction_data)
    print(chat_data[0])

    # 寫入 chat 格式的 JSONL 檔案
    with open("chat_data.jsonl", "w", encoding="utf-8") as f:
        for item in chat_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
