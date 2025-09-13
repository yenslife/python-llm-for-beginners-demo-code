import os
from openai import OpenAI
from dotenv import load_dotenv


class LLMProvider:
    def __init__(
        self, api_key=None, base_url=None, system_prompt=None, user_prompt=None
    ):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")

        client_kwargs = {"api_key": api_key}
        if base_url is not None:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.system_prompt = (
            system_prompt
            or "請使用繁體中文回答使用者的提問，請務必參考檢索到的上下文內容來回答"
        )
        self.user_prompt = (
            user_prompt
            or "基於以下資訊回答問題：\n\n檢索到的上下文:\n{context}\n\n使用者提問: {query}"
        )

    def generate_answer(self, query, context, model="gpt-4.1-mini"):
        user_message = self.user_prompt.format(context=context, query=query)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        return response.choices[0].message.content
