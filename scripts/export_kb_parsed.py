import json
from app.parser.kb_html import parse_kb_html


INPUT_PATH = "data/test.html"
OUTPUT_PATH = "data/kb_parsed.jsonl"


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    docs = parse_kb_html(html)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for d in docs:
            out.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Exported {len(docs)} docs -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()