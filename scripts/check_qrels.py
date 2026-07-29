import json

with open("data/pdf/arxiv/qrels.json", "r", encoding="utf-8") as f:
    qrels = json.load(f)

print(type(qrels))
print(qrels[:2] if isinstance(qrels, list) else list(qrels.items())[:2])