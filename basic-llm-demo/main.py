import os
from dotenv import load_dotenv

load_dotenv() # 也可以傳入檔名 load_dotenv(檔案名稱)

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"我的 API key: {api_key}")


if __name__ == "__main__":
    main()
