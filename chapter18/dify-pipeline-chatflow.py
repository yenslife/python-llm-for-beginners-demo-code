## Dify 聊天流串接 Open WebUI Pipeline 腳本

import json
import requests
from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint

# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class Pipeline:
    def __init__(self):
        self.name = "Open WebUI Memory test"
        self.api_url = "http://host.docker.internal:80/v1/chat-messages" # 因為我們使用 docker 啟動 dify，所以 url 要用 host.docker.internal
        self.api_key= "app-8D9XGRLEYhqWNyHyhSXjKkTF" # 把 workflow 的 API Key 放這邊
        self.stream = True # 串流功能
        self.verify_ssl = False # 因為架在自己的電腦上，所以不需要這一項
        self.debug = False # 你可以在 orbstack 或者 docker desktop 看到 log
        self.current_chat_id = None # 紀錄 Open WebUI 的聊天室 ID
        self.id_map = {} # 以 Open WebUI 為 key，Dify conversation_id 為 value，確保一個聊天室的內容可以正確傳到 Dify 的一個 conversation
    
    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup: {__name__}")
        pass
    
    async def on_shutdown(self): 
        # This function is called when the server is shutdown.
        print(f"on_shutdown: {__name__}")
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called before the OpenAI API request is made. You can modify the form data before it is sent to the OpenAI API.
        print(f"inlet: {__name__}")
        # # 先把 OpenWebUI傳過來的 chat_id 雜湊成一個 uuid 格式
        openwebui_chat_id = body.get("metadata", {}).get("chat_id", "tmp")
        self.current_chat_id = openwebui_chat_id
        if self.debug:
            print(f"inlet: {__name__} - body:")
            pprint(body)
            print(f"inlet: {__name__} - user:")
            pprint(user)
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        print(f"outlet: {__name__}")
        if self.debug:
            print(f"outlet: {__name__} - body:")
            pprint(body)
            print(f"outlet: {__name__} - user:")
            pprint(user)
        return body

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe: {__name__}")
        
        if self.debug:
            print(f"pipe: {__name__} - received message from user: {user_message}")

        # Set reponse mode Dify API parameter
        if self.stream is True:
            response_mode = "streaming"
        else:
            response_mode = "blocking"

        # This function triggers the chatflow using the specified API.
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        user_info = (body or {}).get("user", {})
        user_identifier = user_info.get("email") or user_info.get("id") or "anonymous"
        inputs_payload = (body or {}).get("inputs", {})
        conversation_id = self.id_map.get(self.current_chat_id, "")
        data = {
            "inputs": inputs_payload,
            "query": user_message,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user_identifier,
        }

        files_payload = (body or {}).get("files")
        if files_payload:
            data["files"] = files_payload

        response = requests.post(
            self.api_url,
            headers=headers,
            json=data,
            stream=self.stream,
            verify=self.verify_ssl,
        )

        if response.status_code != 200:
            yield f"Chatflow request failed with status code: {response.status_code}"
            return

        if self.stream:
            for line in response.iter_lines():
                if not line:
                    continue

                decoded_line = line.decode('utf-8').strip()
                if not decoded_line:
                    continue

                if decoded_line.startswith('data:'):
                    decoded_line = decoded_line.split('data:', 1)[1].strip()

                try:
                    json_data = json.loads(decoded_line)
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {decoded_line}")
                    continue

                if 'conversation_id' in json_data and json_data['conversation_id']:
                    dify_id = json_data.get("conversation_id")
                    self.id_map[self.current_chat_id] = dify_id

                answer_chunk = json_data.get('answer')
                if not answer_chunk and 'data' in json_data and isinstance(json_data['data'], dict):
                    answer_chunk = json_data['data'].get('text')

                if answer_chunk:
                    yield answer_chunk
        else:
            try:
                json_data = response.json()
            except json.JSONDecodeError:
                yield "Chatflow response is not valid JSON"
                return

            # 更新 id_map，把目前的 Open WebUI chat_id 對應到 dify 的 conversation_id
            if 'conversation_id' in json_data and json_data['conversation_id']:
                dify_id = json_data.get("conversation_id")
                self.id_map[self.current_chat_id] = dify_id

            answer_text = json_data.get('answer')
            if not answer_text and 'data' in json_data and isinstance(json_data['data'], dict):
                answer_text = json_data['data'].get('text')

            if answer_text:
                yield answer_text
