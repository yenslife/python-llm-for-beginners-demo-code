import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========= Stage 1: Classification (Department) =========
classification_system_prompt = """你將會收到一則來自成大學生或教職員的客服訊息，請將它分類成「處室」(primary) 與「次要類別」(secondary)，並以純 JSON 格式輸出，不能有多餘文字或 Markdown。

處室 (primary)：
- 住宿服務組
- 生活輔導組
- 註冊組

住宿服務組 (secondary)：
- 宿舍網路
- 宿舍報修
- 宿舍申請與退宿
- 宿舍費用

生活輔導組 (secondary)：
- 獎助學金
- 校園活動
- 輔導與諮商
- 交通與停車

註冊組 (secondary)：
- 選課加退
- 成績查詢
- 學籍異動
- 畢業申請

請只輸出有效 JSON，例如：{"primary":"住宿服務組","secondary":"宿舍網路"}。"""

# ========= Stage 2: Dormitory Service Section → Dormitory Network =========
dorm_network_system_prompt = """你是成大住宿服務組的客服人員，正在協助處理宿舍網路問題，請依下列流程回覆學生並以繁體中文輸出，語氣親切、精簡、可直接照做：

1) 請先確認網路線是否正確連接。
2) 請嘗試重新啟動電腦網卡或路由器（關閉 10 秒再開）。
3) 請同學找計算機網路中心的網路維護人員協助，並提供以下資訊
https://cc.ncku.edu.tw/
06-2757575 #61000(週一~五 8:00-17:00)
06-2368855
em61000@email.ncku.edu.tw

若學生改問與網路無關之問題，請先確認是否要結束本次網路排查並轉交其他處室處理。"""

# ========= Shared Functions =========
def classify_customer_message(customer_message: str) -> dict:
    """
    Call the model to classify the message into department (primary) and subcategory (secondary).
    Only accept pure JSON output; if parsing fails, return empty dict.
    """
    response_text = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": classification_system_prompt},
            {"role": "user", "content": customer_message},
        ],
    ).choices[0].message.content

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("⚠️ Classification result is not valid JSON:", response_text)
        return {}

def reply_dorm_network(customer_message: str) -> str:
    """
    Dormitory Service Section → Dormitory Network reply.
    """
    response_text = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": dorm_network_system_prompt},
            {"role": "user", "content": customer_message},
        ],
    ).choices[0].message.content
    return response_text

# ========= Example Flow =========
if __name__ == "__main__":
    # Example message
    customer_message = "我住在成功校區的男生宿舍，昨天開始房間的網路就連不上了，插網路線也沒有反應。"

    print("=== Stage 1: Classification (Department) ===")
    classification_result = classify_customer_message(customer_message)
    print(classification_result)  # Expected: {"primary":"住宿服務組","secondary":"宿舍網路"}

    if not classification_result:
        exit(0)

    primary = classification_result.get("primary", "")
    secondary = classification_result.get("secondary", "")

    print("\n=== Stage 2: Reply based on classification ===")
    if primary == "住宿服務組" and secondary == "宿舍網路":
        reply_text = reply_dorm_network(customer_message)
        print(reply_text)
    else:
        # You can extend other department/subcategory logic here
        print(f"Currently only demonstrating '住宿服務組 → 宿舍網路', got: {primary} / {secondary}")
