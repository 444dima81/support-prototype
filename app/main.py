from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rag.retriever import Retriever
from app.rag.answer import generate_answer
from app.memory import MemoryStore
from app.scenario.runner import ScenarioRunner


app = FastAPI(title="Support Prototype")

retriever = Retriever()
memory = MemoryStore(max_history=20)
scenario_runner = ScenarioRunner(scenario_path="data/test_scenario.json")


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    chunks: list
    last_step_scenario: str


def is_who_are_you(msg: str) -> bool:
    s = msg.lower().strip()
    return s in {"кто ты?", "кто ты", "ты кто?", "ты кто"} or "кто ты" in s


def is_what_are_we_talking(msg: str) -> bool:
    s = msg.lower().strip()
    return "о чем мы" in s or "о чём мы" in s or s in {"о чем мы общаемся?", "о чем мы общаемся"}

def is_trivial(msg: str) -> bool:
    return msg.lower().strip() in {
        "спасибо", "спасибо!", "ок", "окей", "понял", "поняла", "ясно"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    st = memory.get(req.conversation_id)

    # сохраняем user-сообщение
    memory.add_user(req.conversation_id, req.message)

    # мета-вопросы
    if is_who_are_you(req.message):
        answer = (
            "Я агент поддержки. Я отвечаю на вопросы по базе знаний, "
            "а если информации недостаточно — предложу уточнить запрос или подключить специалиста."
        )
        memory.add_assistant(req.conversation_id, answer)
        memory.update_summary(req.conversation_id)
        return ChatResponse(
            conversation_id=req.conversation_id,
            answer=answer,
            chunks=[],
            last_step_scenario=st.last_step_scenario,
        )
    
    if is_what_are_we_talking(req.message):
        # summary всегда существует/обновляется
        if not st.summary:
            memory.update_summary(req.conversation_id)
        answer = st.summary or "Пока у нас нет истории диалога."
        memory.add_assistant(req.conversation_id, answer)
        memory.update_summary(req.conversation_id)
        return ChatResponse(
            conversation_id=req.conversation_id,
            answer=answer,
            chunks=[],
            last_step_scenario=st.last_step_scenario,
        )
    
    if is_trivial(req.message):
        answer = "Пожалуйста! Если появятся вопросы — обращайтесь."
        memory.add_assistant(req.conversation_id, answer)
        memory.update_summary(req.conversation_id)
        return ChatResponse(
            conversation_id=req.conversation_id,
            answer=answer,
            chunks=[],
            last_step_scenario=st.last_step_scenario,
        )
    

    # обычный RAG
    # сценарий ДР — только на первом сообщении в новом conversation_id
    scenario_context = ""
    if not st.scenario_ran:
        res = scenario_runner.run_first_message(req.message)
        st.scenario_ran = True
        st.last_step_scenario = res.last_step_scenario
        scenario_context = res.context_text

    # обычный RAG
    chunks = retriever.retrieve(req.message, top_k=5, min_score=0.25)
    answer = generate_answer(req.message, chunks, extra_context=scenario_context)
    memory.add_assistant(req.conversation_id, answer)
    memory.update_summary(req.conversation_id)

    return ChatResponse(
        conversation_id=req.conversation_id,
        answer=answer,
        chunks=chunks,
        last_step_scenario=st.last_step_scenario,
    )