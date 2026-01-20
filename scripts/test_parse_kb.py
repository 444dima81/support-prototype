from app.parser.kb_html import parse_kb_html

with open("data/test.html", "r", encoding="utf-8") as f:
    html = f.read()

docs = parse_kb_html(html)

print("Docs parsed:", len(docs))
print()

for d in docs:
    print(f"[{d['id']}] {d['question']}")