from dataclasses import dataclass, field
from typing import Literal


Role = Literal["user", "assistant"]


@dataclass
class ConversationState:
    messages: list[dict] = field(default_factory=list)   
    summary: str = ""
    scenario_ran: bool = False
    last_step_scenario: str = ""


class MemoryStore:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._store: dict[str, ConversationState] = {}

    def get(self, conversation_id: str) -> ConversationState:
        if conversation_id not in self._store:
            self._store[conversation_id] = ConversationState()
        return self._store[conversation_id]

    def add_user(self, conversation_id: str, text: str):
        st = self.get(conversation_id)
        st.messages.append({"role": "user", "content": text})
        st.messages = st.messages[-self.max_history:]

    def add_assistant(self, conversation_id: str, text: str):
        st = self.get(conversation_id)
        st.messages.append({"role": "assistant", "content": text})
        st.messages = st.messages[-self.max_history:]

    def update_summary(self, conversation_id: str):
        """
        Лёгкое summary без LLM:
        - берем последние 3 реплики
        - и коротко фиксируем “темы” по user-сообщениям
        """
        st = self.get(conversation_id)
        last = st.messages[-6:]  
        last_lines = []
        for m in last:
            role = "Пользователь" if m["role"] == "user" else "Агент"
            last_lines.append(f"{role}: {m['content']}")

        # последние user-сообщения
        topics = [m["content"] for m in st.messages if m["role"] == "user"][-3:]
        topics_text = " | ".join(topics)

        st.summary = (
            "Краткое резюме диалога:\n"
            f"Темы: {topics_text}\n\n"
            "Последние реплики:\n" + "\n".join(last_lines)
        )