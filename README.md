# RAG ToDo/QA API — Week 3

A FastAPI service that answers questions using a LangChain-based Retrieval-Augmented Generation (RAG) pipeline, backed by a Postgres database and a local FAISS vector index.

## Overview

This project combines the ToDo API foundations (FastAPI + Postgres + Docker + Alembic) from Week 1 with the RAG concepts (embeddings, retrieval, generation) from Week 2, applied to a real-world dataset: [vectara/open_ragbench](https://huggingface.co/datasets/vectara/open_ragbench).

Given the free-tier API constraints, a **subset** of the dataset (35 documents, 827 sections/chunks) is used instead of the full corpus, and open-source embeddings are used to avoid API costs.

## Architecture

```
Question
   │
   ▼
Embed question (HuggingFace: all-MiniLM-L6-v2)
   │
   ▼
FAISS similarity search → top-3 relevant chunks
   │
   ▼
Prompt = context (retrieved chunks) + question
   │
   ▼
Gemini (gemini-flash-latest) generates answer
   │
   ▼
JSON response: { answer, sources }
```

### RAG pipeline stages

| Stage | Where | How |
|---|---|---|
| **Ingestion** | `scripts/download_corpus_subset.py`, `scripts/load_data.py` | Downloads a 35-document subset from Hugging Face and loads title/abstract/metadata into the `documents` table |
| **Chunking** | `scripts/load_data.py` | Dataset is pre-split into sections; each section is stored as a row in the `chunks` table |
| **Embedding** | `scripts/build_index.py` | Each chunk is embedded using `sentence-transformers/all-MiniLM-L6-v2` (open-source, no API cost) |
| **Retrieval** | `app/rag_chain.py` | Embeddings are indexed in FAISS (saved locally to `faiss_index/`); top-3 similar chunks are retrieved per query |
| **Generation** | `app/rag_chain.py` | Retrieved chunks + question are passed to Gemini via a prompt template restricting answers to the given context |

## Why Postgres instead of a persistent vector store

Chunk text and document metadata are stored in Postgres (relational tables), not in a vector database. The vector index (FAISS) is built from this data and kept as a local, rebuildable artifact — Postgres remains the source of truth.

## Tech stack

- **FastAPI** — REST API
- **PostgreSQL + SQLAlchemy + Alembic** — relational storage & migrations
- **LangChain (LCEL)** — RAG orchestration
- **FAISS** — local vector similarity search
- **HuggingFace `sentence-transformers`** — embeddings
- **Google Gemini (`gemini-flash-latest`)** — answer generation
- **Docker & Docker Compose** — containerization

## Project structure

```
app/
  main.py            # FastAPI app entrypoint
  database.py         # DB engine/session setup
  models.py            # SQLAlchemy models (Document, Chunk)
  schemas.py            # Pydantic request/response models
  rag_chain.py            # LangChain RAG pipeline (retriever + LLM)
  routes/
    qa.py                  # POST /ask
    documents.py             # GET /documents, GET /documents/{id}
scripts/
  download_data.py            # Downloads queries/qrels/answers metadata
  download_corpus_subset.py     # Downloads a 35-doc subset of the corpus
  load_data.py                    # Loads subset into Postgres
  build_index.py                    # Builds and saves the FAISS index
alembic/                               # DB migrations
faiss_index/                             # Saved FAISS index (generated)
Dockerfile
docker-compose.yml
requirements.txt
```

## Setup & running

### 1. Environment variables (`.env`)

```
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpass123
POSTGRES_DB=ragdb
DATABASE_URL=postgresql://raguser:ragpass123@db:5432/ragdb
APP_PORT=8000
GOOGLE_API_KEY=your_google_ai_studio_key
```

### 2. Run with Docker

```bash
docker-compose up --build
```

This starts Postgres, applies Alembic migrations, and launches the API at `http://localhost:8000`.

### 3. Load data (one-time, before first run)

```bash
python scripts/download_data.py
python scripts/download_corpus_subset.py
python scripts/load_data.py
python scripts/build_index.py
```

### 4. API docs

Interactive Swagger UI: `http://localhost:8000/docs`

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/ask` | Answers a question using the RAG pipeline |
| GET | `/documents` | Lists loaded documents (paginated) |
| GET | `/documents/{id}` | Returns a single document's metadata |

### Example request

```json
POST /ask
{
  "question": "What is inverter output impedance estimation?"
}
```

```json
{
  "answer": "...",
  "sources": [
    { "document_id": 1, "section_index": 1, "title": "..." }
  ]
}
```

## Error handling

Database operations are wrapped in try/except blocks (`SQLAlchemyError`) and return proper `HTTPException`s (404 for missing resources, 500 for DB/pipeline failures) instead of leaking raw errors to the client.

## Postman collection

A Postman collection covering `/ask` and `/documents` endpoints is included in the repository root, using a `base_url` environment variable (`http://localhost:8000`).

---
## Author

**Anosha** — AI Engineer Intern, Venturenox (Venture Works LLP)
