from pydantic import BaseModel
from typing import Optional


class ChunkOut(BaseModel):
    id: int
    section_index: int
    text: str

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: int
    paper_id: str
    title: str
    category: Optional[str]
    abstract: Optional[str]

    class Config:
        from_attributes = True

class AskRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    document_id: int
    section_index: int
    title: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]