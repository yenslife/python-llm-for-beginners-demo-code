import os
import json

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.2

class Agent():
    def __init__(self, name, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, system_prompt="", tools_implementation=[], tools=[]):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.tools_implementation = tools_implementation # 函式的實作
        self.tools = tools # 函式的定義(給 LLM 看的)
        self.messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        self.response = None

    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
    def get_response(self, response_format = None) -> str:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=self.temperature,
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
        print(f"{self.name} message 紀錄:")
        print(self.messages)

        return response.choices[0].message.content

class SupervisorAgent(Agent):
    def __init__(self, name="Supervisor", model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, system_prompt="", agents: list[Agent]=[]):
        super().__init__(name=name, model=model, temperature=temperature, system_prompt=system_prompt)
        self.agents = agents
        # 加入 sub agent 的 name 和 description 到 system prompt
        self.system_prompt = f"""{system_prompt}

你有以下的 Agent 可以選擇，一次只能選擇一個 Agent，不能選擇多個：
{', '.join([f"{agent.name} (負責: {agent.system_prompt})" for agent in agents])}
"""
        self.messages = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []

    # 根據使用者的問題，選擇適合的 Agent 來回答
    def _select_agent(self) -> Agent | str:
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
                                "description": f"選擇的 Agent 名稱，一次只能選擇一個，你可以選擇 {[agent.name for agent in self.agents]}，若不需要使用任何 Agent，請回答 '不需要代理'。e.g. '{{'agent_name': 'XXXAgent'}}'",
                                "enum": [agent.name for agent in self.agents] + ["不需要代理"],
                            },
                        },
                        "required": ["agent_name"],
                    },
                },
            }
        )
        print(f"{self.name} 回答:{response}")
        if response is not None:
            # get first line of response
            target_agent = response.split("\n")[0]
            for agent in self.agents:
                if agent.name in target_agent:
                    return agent
        return "不需要代理"

    # get response from selected agent and think if the answer is good enough
    # if not good enough, select another agent
    def get_final_response(self) -> str | None:
        selected_agent = self._select_agent()
        if selected_agent == "不需要代理" or isinstance(selected_agent, str):
            final_answer = self.get_response()
            return final_answer
        print(f"選擇的 Agent 是: {selected_agent.name}")
        # 把使用者的問題傳給選擇的 Agent
        user_message = self.messages[-1]
        
        # check if the answer is good enough
        # if not good enough, select another agent
        self.add_message("developer", "判斷是否需要使用代理來回答使用者，若需要，請選擇**一個**適合的代理來回答。若不需要則直接回覆")
        while True:
            if selected_agent == "不需要代理" or isinstance(selected_agent, str):
                return self.get_response()
            selected_agent.add_message("user", user_message["content"])
            answer = selected_agent.get_response()
            print(f"{selected_agent.name} 回答:{answer}")
            self.add_message("assistant", f"{selected_agent.name} 回答:{answer}")
            self.add_message("user", f"請評目前所需資訊是否足夠，若不夠的話請回答 '否';如果足夠，請回答 '是'。")
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
            # get first line of evaluation
            evaluation = evaluation.split("\n")[0]
            print(f"{self.name} 評估:{evaluation}")
            if "是" in evaluation:
                self.add_message("assistant", "是")
                self.add_message("user", "將上下文做一個統整，回答使用者最初的提問")
                final_response = self.get_response()
                return final_response
            else:
                self.add_message("assistant", f"否")
                self.add_message("user", f"請選擇另一個 Agent 來回答。")
                selected_agent = self._select_agent()
                if selected_agent == "不需要代理" or isinstance(selected_agent, str):
                    return self.get_response()
                print(f"重新選擇的 Agent 是: {selected_agent.name}")
