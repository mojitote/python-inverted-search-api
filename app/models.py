from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class DocumentUpload(BaseModel):
    """Schema for document upload requests."""
    doc_id: str = Field(..., description="Unique document identifier", min_length=1, max_length=100)
    content: str = Field(..., description="Document text content", min_length=1, max_length=100000)
    title: Optional[str] = Field(None, description="Document title", max_length=200)
    author: Optional[str] = Field(None, description="Document author", max_length=100)


class SearchResult(BaseModel):
    """Schema for individual search results."""
    doc_id: str = Field(..., description="Document identifier")
    score: float = Field(..., description="Relevance score based on term frequency")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    snippet: Optional[str] = Field(None, description="Text snippet containing search terms")


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Ranked search results")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")


class IndexStats(BaseModel):
    """Schema for index statistics."""
    total_documents: int = Field(..., description="Total number of indexed documents")
    total_terms: int = Field(..., description="Total number of unique terms")
    index_size_mb: float = Field(..., description="Index file size in megabytes")
    last_updated: datetime = Field(..., description="Last index update timestamp")


class IndexResponse(BaseModel):
    """Schema for index view response."""
    stats: IndexStats = Field(..., description="Index statistics")
    sample_terms: Dict[str, Dict[str, int]] = Field(..., description="Sample of indexed terms and their document frequencies")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds") 