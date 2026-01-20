import json
from dotenv import load_dotenv

from app.llm.embeddings import EmbeddingsClient


INPUT_PATH = "data/kb_chunks.jsonl"
OUTPUT_PATH = "data/kb_vectors.jsonl"

BATCH_SIZE = 64


def main():
    load_dotenv()
    emb = EmbeddingsClient()

    # читаем все чанки
    chunks = []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))

    total = len(chunks)
    if total == 0:
        print("No chunks found.")
        return

    print(f"Loaded {total} chunks. Embedding with batch_size={BATCH_SIZE}...")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for i in range(0, total, BATCH_SIZE):
            batch = chunks[i:i+BATCH_SIZE]
            texts = [c["text"] for c in batch]
            vectors = emb.embed(texts)

            for c, v in zip(batch, vectors):
                row = {
                    "chunk_id": c["chunk_id"],
                    "doc_id": c["doc_id"],
                    "vector": v,
                    "text": c["text"],
                    "metadata": c.get("metadata", {}),
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")

            print(f"Embedded {min(i+BATCH_SIZE, total)}/{total}")

    print(f"Done -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()