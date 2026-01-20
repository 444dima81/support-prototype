import json
from app.parser.chunker import chunk_text


INPUT_PATH = "data/kb_parsed.jsonl"
OUTPUT_PATH = "data/kb_chunks.jsonl"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 120


def main():
    total_chunks = 0

    with open(INPUT_PATH, "r", encoding="utf-8") as inp, \
         open(OUTPUT_PATH, "w", encoding="utf-8") as out:

        for line in inp:
            doc = json.loads(line)

            parts = chunk_text(
                doc["text"],
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )

            for idx, part in enumerate(parts):
                chunk = {
                    "chunk_id": f'{doc["id"]}:{idx}',
                    "doc_id": doc["id"],
                    "text": part,
                    "metadata": {
                        **doc.get("metadata", {}),
                        "question": doc.get("question", ""),
                        "chunk_index": idx,
                    }
                }
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                total_chunks += 1

    print(f"Exported {total_chunks} chunks -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()