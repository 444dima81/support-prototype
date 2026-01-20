# app/llm/client.py
import os
from openai import OpenAI


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"]
        )
        self.model = os.environ["QWEN_CHAT_MODEL"]

    def chat(self, messages, max_tokens=2500, temperature=0.3):
        """
        messages: list[{"role": "system|user|assistant", "content": str}]
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            presence_penalty=0
        )
        return response.choices[0].message.content