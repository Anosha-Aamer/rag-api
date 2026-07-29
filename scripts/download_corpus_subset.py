import json
from huggingface_hub import hf_hub_download
import os

REPO_ID = "vectara/open_ragbench"
LOCAL_DIR = "data"
SUBSET_SIZE = 35  # kitne documents chahiye

# qrels load karo
with open("data/pdf/arxiv/qrels.json", "r", encoding="utf-8") as f:
    qrels = json.load(f)

# unique doc_ids nikalo (order preserve karte hue)
seen = set()
doc_ids = []
for query_id, info in qrels.items():
    doc_id = info["doc_id"]
    if doc_id not in seen:
        seen.add(doc_id)
        doc_ids.append(doc_id)

subset_doc_ids = doc_ids[:SUBSET_SIZE]
print(f"Total unique docs in qrels: {len(doc_ids)}")
print(f"Downloading subset of {len(subset_doc_ids)} documents...")

for doc_id in subset_doc_ids:
    filename = f"pdf/arxiv/corpus/{doc_id}.json"
    try:
        hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename=filename,
            local_dir=LOCAL_DIR,
        )
    except Exception as e:
        print(f"Failed for {doc_id}: {e}")

# subset ke doc_ids ko save kar lo, taake baad mein filtering ke liye use ho sakein
with open("data/subset_doc_ids.json", "w", encoding="utf-8") as f:
    json.dump(subset_doc_ids, f, indent=2)

print("Done. Subset doc IDs saved to data/subset_doc_ids.json")