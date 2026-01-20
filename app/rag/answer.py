from app.llm.client import LLMClient


SYSTEM_PROMPT = """Ты агент технической поддержки.
Отвечай ТОЛЬКО на основе предоставленных фрагментов базы знаний (CHUNKS)
и текста сценария (SCENARIO), если он присутствует.

Если в CHUNKS нет точного ответа, скажи, что информации нет и предложи
уточнить вопрос или передать его специалисту.

Не выдумывай факты и не добавляй то, чего нет в CHUNKS или SCENARIO.
Пиши по-русски, вежливо и по делу.
"""


def generate_answer(
    user_message: str,
    chunks: list[dict],
    extra_context: str = "",
) -> str:
    # fallback если вообще нет знаний
    if not chunks:
        return (
            "Не нашёл точной информации в базе знаний по вашему запросу. "
            "Можете переформулировать вопрос или я передам его специалисту."
        )

    # собираем чанки
    ctx_lines = []
    for c in chunks:
        ctx_lines.append(f"[{c['chunk_id']}] {c['text']}")

    chunks_block = "\n\n".join(ctx_lines)

    scenario_block = extra_context.strip() or "(нет сценарного контекста)"

    llm = LLMClient()
    return llm.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Сообщение пользователя:\n{user_message}\n\n"
                    f"SCENARIO:\n{scenario_block}\n\n"
                    f"CHUNKS:\n{chunks_block}"
                ),
            },
        ],
        max_tokens=900,
        temperature=0.2,
    )