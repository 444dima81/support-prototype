from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rag.retriever import Retriever
from app.rag.answer import generate_answer


app = FastAPI(title="Support Prototype")

retriever = Retriever()


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    chunks: list
    last_step_scenario: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    chunks = retriever.retrieve(req.message, top_k=5, min_score=0.25)
    answer = generate_answer(req.message, chunks)

    return ChatResponse(
        conversation_id=req.conversation_id,
        answer=answer,
        chunks=chunks,
        last_step_scenario="",
    )