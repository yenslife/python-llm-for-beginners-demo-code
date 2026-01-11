from rich import print

from Agent import Agent
from tools_and_schemas import (
    get_clubs,
    get_clubs_schema,
)

# 定義一個社團 Agent
club_agent = Agent(
    name="ClubAgent",
    system_prompt="你是一個專業的成大社團資訊助理，能夠根據使用者的需求，提供相關的社團資訊。",
    tools_implementation=[get_clubs],
    tools=[get_clubs_schema],
)
club_agent.add_message("user", "請問成大有哪些資訊類的社團？")
response = club_agent.get_response()
print(f"ClubAgent 回答: {response}")
