from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from app.database import get_db
from app.models import Document
from app.schemas import DocumentOut

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentOut])
def get_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        return documents
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document