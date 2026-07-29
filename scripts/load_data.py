import json
import os
import sys

sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models import Document, Chunk

CORPUS_DIR = "data/pdf/arxiv/corpus"

with open("data/subset_doc_ids.json", "r", encoding="utf-8") as f:
    subset_doc_ids = json.load(f)

db = SessionLocal()

loaded_count = 0
failed_count = 0

for doc_id in subset_doc_ids:
    filepath = os.path.join(CORPUS_DIR, f"{doc_id}.json")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            doc_data = json.load(f)

        # agar yeh document pehle se DB mein hai, skip karo (duplicate se bachne ke liye)
        existing = db.query(Document).filter(Document.paper_id == doc_data["id"]).first()
        if existing:
            print(f"Skipping {doc_id} — already in DB")
            continue

        categories = doc_data.get("categories")
        category_str = ", ".join(categories) if isinstance(categories, list) else categories

        new_doc = Document(
            paper_id=doc_data["id"],
            title=doc_data["title"],
            category=category_str,
            abstract=doc_data.get("abstract"),
        )
        db.add(new_doc)
        db.flush()  # taake new_doc.id mil jaye insert se pehle commit ke

        for section in doc_data.get("sections", []):
            chunk = Chunk(
                document_id=new_doc.id,
                section_index=section["section_id"],
                text=section["text"],
            )
            db.add(chunk)

        db.commit()
        loaded_count += 1
        print(f"Loaded {doc_id} ({len(doc_data.get('sections', []))} sections)")

    except FileNotFoundError:
        print(f"File not found for {doc_id}, skipping.")
        failed_count += 1
        continue
    except KeyError as e:
        db.rollback()
        print(f"Missing expected field {e} in {doc_id}, skipping.")
        failed_count += 1
        continue
    except Exception as e:
        db.rollback()
        print(f"Failed to load {doc_id}: {e}")
        failed_count += 1
        continue

db.close()
print(f"\nDone. Loaded: {loaded_count}, Failed: {failed_count}")