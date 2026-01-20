def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []

    if chunk_size <= 0:
        return [text]

    overlap = max(0, min(chunk_overlap, chunk_size - 1))
    step = max(1, chunk_size - overlap)

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(n, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start += step

    return chunks