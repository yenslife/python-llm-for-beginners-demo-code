import os
import json

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4o-mini"

class Agent():
    def __init__(self, name, model=DEFAULT_MODEL, system_prompt="", tools_implementation=[], tools=[]):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools_implementation = tools_implementation # 函式的實作
        self.tools = tools # 函式的定義(給 LLM 看的)
        self.messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        self.response = None
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
    def get_response(self, response_format = None) -> str | None:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
            response_format=response_format,
        )

        tool_calls = response.choices[0].message.tool_calls
        response_message = response.choices[0].message
        available_tools = {}
        for i, schema in enumerate(self.tools):
            tool_name = schema["function"]["name"]
            available_tools[tool_name] = self.tools_implementation[i]

        if tool_calls:
            self.messages.append(response_message)
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                if tool_name in available_tools:
                    tool_response = available_tools[tool_name](**tool_args)
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_response,
                    })
            return self.get_response()
        print(f"{self.name} message 紀錄: {self.messages}")

        return response.choices[0].message.content

class SupervisorAgent(Agent):
    def __init__(self, name="Supervisor", model=DEFAULT_MODEL, system_prompt="", agents: list[Agent]=[]):
        super().__init__(name, model, system_prompt)
        self.agents = agents
        # 加入 sub agent 的 name 和 description 到 system prompt
        self.system_prompt = f"""{system_prompt}

你有以下的 Agent 可以選擇：
{', '.join([f"{agent.name} (負責: {agent.system_prompt})" for agent in agents])}
你的任務是根據使用者的問題，選擇適合的 Agent 來回答。如果無法判斷，請回答 '無法判斷'。
"""

    # 根據使用者的問題，選擇適合的 Agent 來回答
    def _select_agent(self) -> Agent | None:
        response = self.get_response(
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "agent_name",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "選擇的 Agent 名稱，如果無法判斷，請回答 '無法判斷'。",
                                "enum": [agent.name for agent in self.agents] + ["無法判斷"],
                            },
                        },
                        "required": ["agent_name"],
                    },
                },
            }
        )
        print(f"{self.name} 回答:{response}")
        for agent in self.agents:
            if agent.name in response:
                return agent
        return None

    # get response from selected agent and think if the answer is good enough
    # if not good enough, select another agent
    def get_final_response(self) -> str | None:
        selected_agent = self._select_agent()
        if selected_agent is None or selected_agent.name == "無法判斷":
            return "此問題不在我們代理群的專業範圍內，無法回答。"
        print(f"選擇的 Agent 是: {selected_agent.name}")
        # 把使用者的問題傳給選擇的 Agent
        user_message = self.messages[-1] if self.messages and self.messages[-1]["role"] == "user" else None
        
        # check if the answer is good enough
        # if not good enough, select another agent
        while True:
            self.add_message("user", user_message['content'])
            selected_agent.add_message("user", user_message["content"])
            answer = selected_agent.get_response()
            print(f"{selected_agent.name} 回答:{answer}")
            self.add_message("assistant", answer)
            self.add_message("user", f"請評估這個答案是否足夠好？如果不夠好，請選擇另一個 Agent 來回答。")
            evaluation = self.get_response(
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "is_good_enough",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "is_good_enough": {
                                    "type": "string",
                                    "description": "回答是否足夠好？請回答 '是' 或 '否'。",
                                    "enum": ["是", "否"],
                                },
                            },
                            "required": ["is_good_enough"],
                        },
                    },
                }
            )
            print(f"{self.name} 評估:{evaluation}")
            if "是" in evaluation:
                return answer
            else:
                self.add_message("user", f"請選擇另一個 Agent 來回答。")
                selected_agent = self._select_agent()
                if selected_agent is None or selected_agent.name == "無法判斷":
                    return "此問題不在我們代理群的專業範圍內，無法回答。"
                print(f"重新選擇的 Agent 是: {selected_agent.name}")
