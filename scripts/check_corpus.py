import json

with open("data/pdf/arxiv/corpus/2410.14077v2.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

print(list(doc.keys()))
print("---")
print(json.dumps(doc, indent=2)[:1500])   # pehle 1500 characters preview