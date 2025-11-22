import os
import asyncio

from dotenv import load_dotenv
from openai import AsyncOpenAI
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Static

# 載入 .env 的環境變數（例如 OPENAI_API_KEY）
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 紀錄整個對話歷史的全域變數
chat_history = [
    {"role": "system", "content": "你是一個用繁體中文回覆的聊天助理，自稱小海狸，喜歡用很多表情符號來回覆使用者的問題"},
]


class ChatHeader(Static):
    """標題列，顯示簡單說明"""

    def compose(self) -> ComposeResult:
        yield Static("OpenAI Chat (Textual)", id="title")
        yield Static("輸入訊息後按 Enter 或按 Send 送出", id="subtitle")


class MessageBubble(Static):
    """單一訊息的氣泡元件"""

    def __init__(self, text: str, role: str) -> None:
        super().__init__(text)
        self.role = role

    def on_mount(self) -> None:
        """根據角色設定 CSS 類別"""
        classes = ["message-bubble"]
        if self.role == "user":
            classes.append("user")
        elif self.role == "assistant":
            classes.append("assistant")
        elif self.role == "system":
            classes.append("system")
        self.add_class(*classes)


class ChatApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    ChatHeader {
        padding: 1 2;
        border-bottom: solid gray;
    }

    #chat-log-container {
        height: 1fr;
        border: solid gray;
        padding: 1;
    }

    #chat-log {
        height: 1fr;
        width: 1fr;
    }

    .message-row {
        width: 100%;
    }

    .message-row.user {
        align-horizontal: right;
    }

    .message-row.assistant,
    .message-row.system {
        align-horizontal: left;
    }

    .message-bubble {
        max-width: 80%;
        padding: 0 1;
        border: round gray;
    }

    .message-bubble.user {
        background: $accent;
        color: black;
    }

    .message-bubble.assistant {
        background: $boost;
    }

    .message-bubble.system {
        color: $text-muted;
    }

    #input-row {
        height: 3;
        padding: 0 1;
    }

    #user-input {
        width: 1fr;
        margin-right: 1;
    }

    #send-btn {
        width: 10;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """建立整個畫面佈局"""
        yield ChatHeader()
        with Static(id="chat-log-container"):
            yield Vertical(id="chat-log")
        with Horizontal(id="input-row"):
            yield Input(placeholder="輸入訊息...", id="user-input")
            yield Button("Send", id="send-btn")

    async def on_mount(self) -> None:
        """畫面載入完成後先顯示提示訊息"""
        await self._add_message("system", "歡迎使用 Textual OpenAI Chat！")

    async def action_quit(self) -> None:
        """離開應用程式"""
        self.exit()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """按下 Send 按鈕事件"""
        if event.button.id == "send-btn":
            await self._send_current_input()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """在輸入框按下 Enter"""
        if event.input.id == "user-input":
            await self._send_current_input()

    async def _send_current_input(self) -> None:
        """把目前輸入框的內容送給 OpenAI，並以串流方式更新畫面"""
        input_widget = self.query_one("#user-input", Input)

        user_text = input_widget.value.strip()
        if not user_text:
            return

        # 更新對話歷史：加入使用者訊息
        chat_history.append({"role": "user", "content": user_text})

        # 將使用者訊息顯示在畫面上
        await self._add_message("user", user_text)
        input_widget.value = ""  # 清空輸入框

        # 建立一個空的 assistant 氣泡，先顯示 loading 動畫，之後用串流內容慢慢填滿
        assistant_bubble = await self._add_message("assistant", "")

        loading = True

        async def loading_animation() -> None:
            """在收到第一個 token 之前顯示簡單的 loading 動畫"""
            nonlocal loading
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            # frames = ["(*-----)", "(-*----)", "(--*---)", "(---*--)", "(----*-)", "(-----*)", "(----*-)", "(---*--)", "(--*---)", "(-*----)"]
            index = 0
            while loading:
                assistant_bubble.update(frames[index % len(frames)])
                index += 1
                await asyncio.sleep(0.08)

        loading_task = asyncio.create_task(loading_animation())

        try:
            # 使用串流方式呼叫 OpenAI，逐步更新 assistant 氣泡內容
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history,
                temperature=0.7,
                stream=True,
            )

            full_reply = ""

            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if not delta:
                    continue

                # 第一次收到 token 時，停止 loading 動畫
                if loading:
                    loading = False
                full_reply += delta
                assistant_bubble.update(full_reply)

        except Exception as e:
            # 發生錯誤時顯示錯誤訊息
            loading = False
            await loading_task
            assistant_bubble.update("")
            await self._add_message("system", f"呼叫 OpenAI 失敗：{e}")
            return
        finally:
            # 確保離開時停止 loading 動畫
            loading = False
            if not loading_task.done():
                await loading_task

        # 將 assistant 真正回應加入對話歷史
        chat_history.append({"role": "assistant", "content": full_reply})

    async def _add_message(self, role: str, text: str) -> MessageBubble:
        """在畫面上加入一則訊息氣泡，並回傳該氣泡元件"""
        chat_log = self.query_one("#chat-log", Vertical)
        row = Horizontal(classes=f"message-row {role}")
        bubble = MessageBubble(text, role)
        await chat_log.mount(row)
        await row.mount(bubble)
        return bubble
    

if __name__ == "__main__":
    app = ChatApp()
    app.run()
