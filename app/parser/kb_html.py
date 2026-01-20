from bs4 import BeautifulSoup


def parse_kb_html(html: str) -> list[dict]:
    """
    Возвращает документы:
    {
      "id": str,
      "question": str,
      "answer": str,
      "text": "question\\nanswer",
      "metadata": {"source": str, "date": str}
    }
    """
    soup = BeautifulSoup(html, "lxml")
    articles = soup.select("article.kb-item")

    docs = []
    for art in articles:
        doc_id = (art.get("data-id") or "").strip()
        source = (art.get("data-source") or "").strip()
        date = (art.get("data-date") or "").strip()

        h2 = art.select_one("h2")
        question = h2.get_text(" ", strip=True) if h2 else ""

        ans = art.select_one("div.answer")
        answer = ans.get_text(" ", strip=True) if ans else ""

        if not question and not answer:
            continue

        docs.append({
            "id": doc_id,
            "question": question,
            "answer": answer,
            "text": f"{question}\n{answer}".strip(),
            "metadata": {"source": source, "date": date},
        })

    return docs