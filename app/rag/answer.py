from app.llm.client import LLMClient


SYSTEM_PROMPT = """Ты агент технической поддержки.
Отвечай ТОЛЬКО на основе предоставленных фрагментов базы знаний (CHUNKS).
Если в CHUNKS нет точного ответа, скажи, что информации нет и предложи уточнить вопрос или передать специалисту.
Не выдумывай факты и не добавляй то, чего нет в CHUNKS.
Пиши коротко и по делу, по-русски.
"""


def generate_answer(user_message: str, chunks: list[dict]) -> str:
    if not chunks:
        return (
            "Не нашёл точной информации в базе знаний по вашему запросу. "
            "Можете переформулировать вопрос или я передам его специалисту."
        )

    ctx_lines = []
    for c in chunks:
        ctx_lines.append(f"[{c['chunk_id']}] {c['text']}")

    context = "\n\n".join(ctx_lines)

    llm = LLMClient()
    return llm.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Вопрос пользователя:\n{user_message}\n\nCHUNKS:\n{context}"},
        ],
        max_tokens=800,
        temperature=0.2,
    )