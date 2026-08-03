import os
from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from app.database import SessionLocal
from app.models import Chunk

_rag_chain = None
_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_context(question: str):
    model = get_embedding_model()
    query_vector = model.encode(question).tolist()

    db = SessionLocal()
    try:
        results = (
            db.query(Chunk)
            .order_by(Chunk.embedding.cosine_distance(query_vector))
            .limit(3)
            .all()
        )
        docs = [
            Document(
                page_content=chunk.text,
                metadata={
                    "document_id": chunk.document_id,
                    "section_index": chunk.section_index,
                    "title": chunk.document.title,
                },
            )
            for chunk in results
        ]
        return docs
    finally:
        db.close()


def get_qa_chain():
    global _rag_chain
    if _rag_chain is not None:
        return _rag_chain

    retriever = RunnableLambda(get_context)

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only the following context. "
        "If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )

    answer_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
        | prompt
        | llm
        | StrOutputParser()
    )

    _rag_chain = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=answer_chain)

    return _rag_chain