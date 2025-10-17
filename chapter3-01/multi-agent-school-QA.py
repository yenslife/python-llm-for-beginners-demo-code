from rich import print

from Agent import Agent, SupervisorAgent
from tools_and_schemas import (
    get_dormitories,
    get_dormitories_schema,
    get_clubs,
    get_clubs_schema,
)

# 宿舍 Agent
dormitory_agent = Agent(
    name="DormitoryAgent",
    system_prompt="你是一個專門回答成大宿舍問題的機器人，你也只能回答和宿舍相關的問題。",
    tools_implementation=[get_dormitories],
    tools=[get_dormitories_schema],
)

# 社團 Agent
club_agent = Agent(
    name="ClubAgent",
    system_prompt="你是一個專門回答成大社團問題的機器人，你也只能回答和社團相關的問題。",
    tools_implementation=[get_clubs],
    tools=[get_clubs_schema],
)

# 主管 Agent，負責選擇適合的 Agent 來回答使用者的問題
supervisor_agent = SupervisorAgent(
    name="SupervisorAgent",
    system_prompt="你是一個Supervisor Agent，負責選擇適合的子 Agent 來回答使用者的問題，若問題在你能力範圍之內可以直接回答。使用者會問和成大相關的問題，如果和Agent的專長無關，請回答 '無法判斷'。",
    agents=[dormitory_agent, club_agent],
)

print(supervisor_agent.system_prompt)
print("========================================")
supervisor_agent.add_message(
    "user",
    "請問成大大學部宿舍有哪些？成大有哪些資訊類社團？",
    # "成大有哪些資訊類社團？請問成大大學部宿舍有哪些？",
    # "你好",
)
response = supervisor_agent.get_final_response()
print("###########################")
print(f"[bold yellow]Supervisor Agent 回答:[/bold yellow] {response}")
print("###########################")
