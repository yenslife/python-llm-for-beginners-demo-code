import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from rich import print

load_dotenv()  # Load environment variables from .env file

@function_tool
def get_dormitories(status: str) -> str:
    """根據學生身份回傳成大宿舍資訊
    Args:
        status (str): 學生身份，可能值為 "研究所" 或 "大學部"
    Returns:
        str: 成大宿舍資訊
    """
    print(f"使用 get_dormitories 工具，status={status}")
    if status == "研究所":
        return '"勝利第六宿舍", "敬業第三宿舍"'
    if status == "大學部":
        return '"光復一宿舍", "勝利一宿舍", "勝利八宿舍", "勝利九宿舍", "敬業第一宿舍"'
    return "請洽詢住宿服務組電話 (06)2757575 轉分機 86340。傳真 886-6-2003273。E-Mail: em86340@email.ncku.edu.tw"

@function_tool
def get_clubs(category: str) -> str:
    """根據社團類別回傳成大社團資訊
    Args:
        category (str): 社團類別，可能值為 "資訊類" 或其他
    Returns:
        str: 成大社團資訊
    """
    print(f"使用 get_clubs 工具，category={category}")
    if category == "資訊類":
        return '"NCKU GDG on Campus (GDSC)", "成大電腦網路愛好社(CCNS)", "成大資安社"'
    return "成大社團查詢系統 https://sys.activity-osa.ncku.edu.tw/index.php?c=club0408"


dorm_agent = Agent(
    name="Dormitory agent",
    instructions="你是一個專門回答成大宿舍問題的機器人，你也只能回答和宿舍相關的問題。",
    handoff_description="處理成大宿舍相關問題",
    tools=[get_dormitories],
)

club_agent = Agent(
    name="Club agent",
    instructions="你是一個專門回答成大社團問題的機器人，你也只能回答和社團相關的問題。",
    handoff_description="處理成大社團相關問題",
    tools=[get_clubs],
)

triage_agent = Agent(
    name="Triage agent",
    instructions="你是一個Supervisor Agent，負責選擇適合的子 Agent 來回答使用者的問題，若問題在你能力範圍之內可以直接回答。使用者會問和成大相關的問題，如果和Agent的專長無關，請回答 '無法判斷'。",
    handoff_description="將使用者的問題分派給合適的子 Agent 來回答",
    handoffs=[dorm_agent, club_agent],
)

async def main():
    result = await Runner.run(triage_agent,
        input="成大有哪些資訊類社團？"
        # input="成大研究生宿舍有哪些？"
        # input="成大有哪些資訊類社團？請問成大研究生宿舍有哪些？" # 無法成功回答
    )
    print(result)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
