import os
from dotenv import load_dotenv
from app.llm.client import LLMClient

load_dotenv()

llm = LLMClient()

answer = llm.chat([
    {"role": "system", "content": "Ты агент технической поддержки."},
    {"role": "user", "content": "Как написать хороший код?"}
])

print(answer)