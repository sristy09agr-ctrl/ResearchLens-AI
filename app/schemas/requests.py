"""
Pydantic models for incoming API requests.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Research search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    candidate_k: int = Field(default=30, ge=1, le=100, description="Candidates before reranking")
    alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="BM25 vs dense balance")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional filter by document IDs")


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Research question to answer")
    document_ids: List[str] = Field(..., min_length=1, description="List of document IDs to analyze")
    top_k: int = Field(default=5, ge=1, le=20, description="Evidence passages to use")
    candidate_k: int = Field(default=30, ge=1, le=100, description="Candidates to retrieve per sub-question")
    alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="Hybrid retrieval alpha")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation session ID")


class ReportRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Research topic or question for structured report")
    document_ids: List[str] = Field(..., min_length=1, description="List of document IDs to analyze")
    candidate_k: int = Field(default=40, ge=1, le=100)
    top_k: int = Field(default=15, ge=1, le=30)
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)

