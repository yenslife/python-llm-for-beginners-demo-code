from rich import print

from Agent import Agent, SupervisorAgent

# 定義模擬的工具和 shcema
def get_dormitories(status: str) -> str:
    print("使用 get_dormitories 工具")
    if status == "研究所":
        return '"勝利第六宿舍", "敬業第三宿舍"'
    if status == "大學部":
        return '"光復一宿舍", "勝利一宿舍", "勝利八宿舍", "勝利九宿舍", "敬業第一宿舍"'
    return "請洽詢住宿服務組電話 (06)2757575 轉分機 86340。傳真 886-6-2003273。E-Mail: em86340@email.ncku.edu.tw"

get_dormitories_schema = {
    "type": "function",
    "function": {
        "name": "get_dormitories",
        "description": "根據學生身份，回傳成大可申請的宿舍清單",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "學生身份，研究所或大學部",
                    "enum": ["研究所", "大學部", "其他"],
                },
            },
            "required": ["status"],
        },
    }
}

def get_clubs(category: str) -> str:
    print("使用 get_clubs 工具")
    if category == "資訊類":
        return '"NCKU GDG on Campus (GDSC)", "成大電腦網路愛好社(CCNS)", "成大資安社"'
    return "成大社團查詢系統 https://sys.activity-osa.ncku.edu.tw/index.php?c=club0408"

get_clubs_schema = {
    "type": "function",
    "function": {
        "name": "get_clubs",
        "description": "根據社團類別，回傳成大相關社團清單",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "社團類別，例如 資訊類、體育類、音樂類、舞蹈類、服務類、學術類、其他",
                    "enum": ["資訊類", "體育類", "音樂類", "舞蹈類", "服務類", "學術類", "其他"],
                },
            },
            "required": ["category"],
        },
    }
}

# 宿舍 Agent
dormitory_agent = Agent(
    name="DormitoryAgent",
    system_prompt="你是一個專門回答成大宿舍問題的機器人。",
    tools_implementation=[get_dormitories],
    tools=[get_dormitories_schema],
)

# 社團 Agent
club_agent = Agent(
    name="ClubAgent",
    system_prompt="你是一個專門回答成大社團問題的機器人。",
    tools_implementation=[get_clubs],
    tools=[get_clubs_schema],
)

# 主管 Agent，負責選擇適合的 Agent 來回答使用者的問題
supervisor_agent = SupervisorAgent(
    name="SupervisorAgent",
    system_prompt="你是一個Supervisor Agent，負責選擇適合的子 Agent 來回答使用者的問題。使用者會問和成大相關的問題，如果和Agent的專長無關，請回答 '無法判斷'。",
    agents=[dormitory_agent, club_agent],
)
# dormitory_agent.add_message(
#     "user",
#     "請問成大宿舍有哪些？",
# )
#
# response = dormitory_agent.get_response()
# print("Dormitory Agent 回答:", response)

print(supervisor_agent.system_prompt)
print("========================================")
supervisor_agent.add_message(
    "user",
    "請問成大研究生宿舍有哪些？",
)
response = supervisor_agent.get_final_response()
print(f"[bold yellow]Supervisor Agent 回答:[/bold yellow] {response}")
