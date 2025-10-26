from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class SearchResult(BaseModel):
    id: int
    filename: str
    content: str
    chunk_id: int
    similarity: float
    metadata: Dict[str, Any]
    created_at: str

class QuestionAnswer(BaseModel):
    """Question-answer response model"""
    question: str
    answer: str
    context_chunks: List[SearchResult]
    sources: List[str]
    confidence: float = Field(ge=0.0, le=1.0)

class QuestionRequest(BaseModel):
    """Request model for asking a question"""
    question: str
    context_limit: int = 5
    similarity_threshold: Optional[float] = None


# Additional models for database representation
class DocumentChunk(BaseModel):
    id: int
    filename: str
    content: str
    chunk_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    similarity: Optional[float] = None

class DocumentInfo(BaseModel):
    filename: str
    chunks: int
    chunk_details: Optional[List[DocumentChunk]] = None
    embedding_model: Optional[str] = None
    database_path: Optional[str] = None


# Tool response models
class EmbedDocumentResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    chunks_added: Optional[int] = None
    total_characters: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None

class SearchDocumentsResponse(BaseModel):
    results: List[DocumentChunk]
    message: Optional[str] = None

class DatabaseStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    embedding_model: str
    database_path: str
    files: List[DocumentInfo]

class DeleteDocumentResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    chunks_deleted: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ListDocumentsResponse(BaseModel):
    total_documents: int
    files: List[DocumentInfo]
    message: Optional[str] = None

class GetDocumentResponse(BaseModel):
    document: Optional[DocumentChunk] = None
    error: Optional[str] = None
    document_id: Optional[str] = None

