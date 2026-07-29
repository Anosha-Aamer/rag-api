import os
import sys
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models import Chunk, Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument

db = SessionLocal()

try:
    chunks = db.query(Chunk).join(Document).all()
    print(f"Found {len(chunks)} chunks in database")

    lc_documents = []
    for chunk in chunks:
        lc_documents.append(
            LCDocument(
                page_content=chunk.text,
                metadata={
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "section_index": chunk.section_index,
                    "title": chunk.document.title,
                },
            )
        )
except Exception as e:
    print(f"Error reading from database: {e}")
    db.close()
    sys.exit(1)

db.close()

print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Building FAISS index (yeh thoda time lega)...")
vectorstore = FAISS.from_documents(lc_documents, embeddings)

os.makedirs("faiss_index", exist_ok=True)
vectorstore.save_local("faiss_index")

print("Done. Index saved to faiss_index/")