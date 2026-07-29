from fastapi import APIRouter, HTTPException
from app.schemas import AskRequest, AskResponse, SourceChunk
from app.rag_chain import get_qa_chain

router = APIRouter(prefix="/ask", tags=["QA"])


@router.post("", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        chain = get_qa_chain()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load RAG chain: {str(e)}")

    try:
        result = chain.invoke(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

    sources = []
    for doc in result.get("context", []):
        sources.append(
            SourceChunk(
                document_id=doc.metadata.get("document_id"),
                section_index=doc.metadata.get("section_index"),
                title=doc.metadata.get("title"),
            )
        )

    return AskResponse(answer=result["answer"], sources=sources)