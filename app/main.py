import time
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .models import (
    DocumentUpload, SearchResponse, SearchResult, IndexResponse, 
    IndexStats, ErrorResponse, HealthResponse
)
from .index import InvertedIndex
from .storage import IndexStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for index and storage
index: Optional[InvertedIndex] = None
storage: Optional[IndexStorage] = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global index, storage
    
    # Startup
    logger.info("Starting Inverted Index Search API...")
    storage = IndexStorage()
    index = storage.load_index()
    if index is None:
        index = InvertedIndex()
        logger.info("Created new inverted index")
    
    logger.info(f"API started successfully. Index contains {index.total_documents} documents")
    yield
    
    # Shutdown
    logger.info("Shutting down Inverted Index Search API...")
    if index and storage:
        storage.save_index(index)
        logger.info("Index saved successfully")


# Create FastAPI app
app = FastAPI(
    title="Inverted Index Search API",
    description="""
    A professional document search service that demonstrates inverted index implementation.
    
    ## Features
    
    * **Document Upload**: Add documents to the search index
    * **Keyword Search**: Search documents by keywords with relevance ranking
    * **Index Management**: View and manage the inverted index
    * **Health Monitoring**: Check API status and performance
    
    ## Learning Outcomes
    
    This API demonstrates core information retrieval concepts:
    * Inverted index data structures
    * Term frequency-based ranking
    * Document indexing and search algorithms
    * REST API design with FastAPI
    """,
    version="1.0.0",
    contact={
        "name": "Inverted Index Search API",
        "url": "https://github.com/your-repo/inverted-index-api",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_index() -> InvertedIndex:
    """Dependency to get the current index instance."""
    if index is None:
        raise HTTPException(status_code=503, detail="Index not initialized")
    return index


def get_storage() -> IndexStorage:
    """Dependency to get the storage instance."""
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    return storage


@app.get("/", response_model=dict)
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Inverted Index Search API",
        "version": "1.0.0",
        "description": "A professional document search service using inverted indexes",
        "endpoints": {
            "upload": "/upload - POST - Upload documents",
            "search": "/search - GET - Search documents",
            "index": "/index - GET - View index statistics",
            "health": "/health - GET - Health check",
            "docs": "/docs - API documentation"
        }
    }


@app.post("/upload", response_model=dict)
async def upload_document(
    document: DocumentUpload,
    index_instance: InvertedIndex = Depends(get_index),
    storage_instance: IndexStorage = Depends(get_storage)
):
    """
    Upload a document to the search index.
    
    This endpoint accepts a document with ID, content, and optional metadata,
    then indexes it for search. The document content is tokenized and stored
    in the inverted index for efficient retrieval.
    """
    try:
        # Check if document already exists
        if index_instance.get_document(document.doc_id):
            raise HTTPException(
                status_code=409,
                detail=f"Document with ID '{document.doc_id}' already exists"
            )
        
        # Add document to index
        success = index_instance.add_document(
            doc_id=document.doc_id,
            content=document.content,
            title=document.title,
            author=document.author
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to index document. Please check the content."
            )
        
        # Save index to disk
        if not storage_instance.save_index(index_instance):
            logger.warning("Failed to save index after document upload")
        
        return {
            "message": "Document uploaded successfully",
            "doc_id": document.doc_id,
            "indexed_terms": index_instance.documents[document.doc_id]['unique_terms'],
            "total_documents": index_instance.total_documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Search query", min_length=1, max_length=200),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=100),
    index_instance: InvertedIndex = Depends(get_index)
):
    """
    Search for documents containing the specified query terms.
    
    The search uses term frequency-based ranking to return the most relevant
    documents first. Results are sorted by relevance score in descending order.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        start_time = time.time()
        
        # Perform search
        results = index_instance.search(query, limit=limit)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Format results
        search_results = []
        for doc_id, score, metadata in results:
            # Create snippet (first 200 characters of content)
            content = metadata.get('content', '')
            snippet = content[:200] + "..." if len(content) > 200 else content
            
            search_results.append(SearchResult(
                doc_id=doc_id,
                score=round(score, 4),
                title=metadata.get('title'),
                author=metadata.get('author'),
                snippet=snippet
            ))
        
        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/index", response_model=IndexResponse)
async def view_index(
    index_instance: InvertedIndex = Depends(get_index),
    storage_instance: IndexStorage = Depends(get_storage)
):
    """
    View the current state of the inverted index.
    
    Returns statistics about the index including document count, term count,
    and a sample of indexed terms for debugging and learning purposes.
    """
    try:
        # Get index statistics
        stats = index_instance.get_stats()
        index_info = storage_instance.get_index_info()
        
        # Create index stats response
        from datetime import datetime
        
        # Handle last_updated field - convert string to datetime or use current time
        last_updated = index_info['last_modified']
        if last_updated:
            try:
                last_updated = datetime.fromisoformat(last_updated)
            except (ValueError, TypeError):
                last_updated = datetime.now()
        else:
            last_updated = datetime.now()
        
        index_stats = IndexStats(
            total_documents=stats['total_documents'],
            total_terms=stats['total_terms'],
            index_size_mb=round(index_info['size_mb'], 2),
            last_updated=last_updated
        )
        
        # Get sample terms for learning purposes
        sample_terms = index_instance.get_sample_terms(limit=20)
        
        return IndexResponse(
            stats=index_stats,
            sample_terms=sample_terms
        )
        
    except Exception as e:
        logger.error(f"Error viewing index: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the API.
    
    Returns information about the service status, version, and uptime.
    """
    try:
        uptime = time.time() - start_time
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime_seconds=round(uptime, 2)
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    index_instance: InvertedIndex = Depends(get_index),
    storage_instance: IndexStorage = Depends(get_storage)
):
    """
    Delete a document from the index.
    
    Removes the specified document and all its associated terms from the index.
    """
    try:
        if not index_instance.get_document(doc_id):
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID '{doc_id}' not found"
            )
        
        success = index_instance.remove_document(doc_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to remove document"
            )
        
        # Save index to disk
        if not storage_instance.save_index(index_instance):
            logger.warning("Failed to save index after document deletion")
        
        return {
            "message": "Document deleted successfully",
            "doc_id": doc_id,
            "total_documents": index_instance.total_documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    index_instance: InvertedIndex = Depends(get_index)
):
    """
    Retrieve a specific document by its ID.
    
    Returns the document metadata and content if it exists in the index.
    """
    try:
        document = index_instance.get_document(doc_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID '{doc_id}' not found"
            )
        
        return {
            "doc_id": doc_id,
            "title": document.get('title'),
            "author": document.get('author'),
            "content": document.get('content'),
            "total_terms": document.get('total_terms'),
            "unique_terms": document.get('unique_terms'),
            "added_at": document.get('added_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for HTTP errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"HTTP {exc.status_code} error occurred"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom exception handler for general errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 