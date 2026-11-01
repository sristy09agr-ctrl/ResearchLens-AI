"""
Pydantic models for outgoing API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from app.schemas.agent import ComparisonMatrix, VerificationReport


class Citation(BaseModel):
    citation_number: int
    document_id: str
    filename: str
    chunk_id: Optional[int] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    section: Optional[str] = None
    text_snippet: Optional[str] = None


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    stored_path: Optional[str] = None
    sha256: Optional[str] = None
    total_pages: int
    total_chunks: int
    uploaded_at: Optional[str] = None
    chunks_url: Optional[str] = None
    download_url: Optional[str] = None


class DocumentListResponse(BaseModel):
    status: str = "success"
    total_documents: int
    documents: List[DocumentInfo]


class IngestionJobStatus(BaseModel):
    job_id: str
    status: str  # queued | parsing | chunking | embedding | ready | failed
    filename: str
    document_id: Optional[str] = None
    total_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    error_message: Optional[str] = None


class AskResponse(BaseModel):
    status: str = "success"
    query: str
    selected_documents: List[Dict[str, str]]
    total_evidence_passages: int
    answer: str
    citations: List[Citation]
    research_plan: List[str]
    verification: Optional[VerificationReport] = None
    confidence: str = "high"  # high | medium | low | abstained
    abstained: bool = False
    iterations_run: int = 1


class ReportResponse(BaseModel):
    status: str = "success"
    query: str
    selected_documents: List[Dict[str, str]]
    total_evidence_passages: int
    research_plan: List[str]
    report: str
    comparison_matrix: Optional[ComparisonMatrix] = None
    citations: List[Citation]
    confidence: str = "high"


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    qdrant_connected: bool
    models_loaded: bool

