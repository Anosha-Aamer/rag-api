from fastapi import FastAPI
from app.routes import qa, documents

app = FastAPI(title="RAG ToDo/QA API")

app.include_router(qa.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return {"status": "ok"}