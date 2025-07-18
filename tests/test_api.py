import pytest
import httpx
import tempfile
import shutil
from pathlib import Path

from app.main import app


class TestAPI:
    """Integration tests for the FastAPI endpoints."""
    
    def setup_method(self):
        """Set up test client and temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.client = httpx.AsyncClient(app=app, base_url="http://test")
    
    def teardown_method(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test the root endpoint."""
        response = await self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Inverted Index Search API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = await self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "uptime_seconds" in data
    
    @pytest.mark.asyncio
    async def test_upload_document(self):
        """Test uploading a document."""
        document_data = {
            "doc_id": "test_doc_1",
            "content": "Python is a programming language used for web development and data science.",
            "title": "Python Introduction",
            "author": "Test Author"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Document uploaded successfully"
        assert data["doc_id"] == "test_doc_1"
        assert data["indexed_terms"] > 0
        assert data["total_documents"] == 1
    
    @pytest.mark.asyncio
    async def test_upload_duplicate_document(self):
        """Test uploading a document with duplicate ID."""
        document_data = {
            "doc_id": "test_doc_1",
            "content": "First document"
        }
        
        # Upload first document
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # Try to upload duplicate
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_upload_empty_content(self):
        """Test uploading a document with empty content."""
        document_data = {
            "doc_id": "test_doc_1",
            "content": ""
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 400
        assert "Failed to index document" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_search_documents(self):
        """Test searching for documents."""
        # Upload test documents
        documents = [
            {
                "doc_id": "doc1",
                "content": "Python is a programming language for web development",
                "title": "Python Web Dev"
            },
            {
                "doc_id": "doc2",
                "content": "Java is also a programming language",
                "title": "Java Programming"
            },
            {
                "doc_id": "doc3",
                "content": "Python is popular for data science and machine learning",
                "title": "Python Data Science"
            }
        ]
        
        for doc in documents:
            response = await self.client.post("/upload", json=doc)
            assert response.status_code == 200
        
        # Search for "python"
        response = await self.client.get("/search?query=python")
        assert response.status_code == 200
        
        data = response.json()
        assert data["query"] == "python"
        assert data["total_results"] == 2  # doc1 and doc3
        assert len(data["results"]) == 2
        assert data["search_time_ms"] > 0
        
        # Check results are sorted by score
        scores = [result["score"] for result in data["results"]]
        assert scores == sorted(scores, reverse=True)
        
        # Check document IDs
        doc_ids = [result["doc_id"] for result in data["results"]]
        assert "doc1" in doc_ids
        assert "doc3" in doc_ids
    
    @pytest.mark.asyncio
    async def test_search_multiple_terms(self):
        """Test searching with multiple terms."""
        # Upload test document
        document_data = {
            "doc_id": "doc1",
            "content": "Python programming language for web development",
            "title": "Python Programming"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # Search for "python programming"
        response = await self.client.get("/search?query=python programming")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_results"] == 1
        assert data["results"][0]["doc_id"] == "doc1"
        assert data["results"][0]["score"] > 0
    
    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test searching with no matching results."""
        # Upload a document
        document_data = {
            "doc_id": "doc1",
            "content": "Python programming",
            "title": "Python"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # Search for non-existent term
        response = await self.client.get("/search?query=javascript")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self):
        """Test searching with empty query."""
        response = await self.client.get("/search?query=")
        assert response.status_code == 400
        assert "Query cannot be empty" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_search_with_limit(self):
        """Test searching with result limit."""
        # Upload multiple documents
        for i in range(5):
            document_data = {
                "doc_id": f"doc{i}",
                "content": f"Document {i} about Python programming",
                "title": f"Document {i}"
            }
            response = await self.client.post("/upload", json=document_data)
            assert response.status_code == 200
        
        # Search with limit
        response = await self.client.get("/search?query=python&limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["results"]) <= 3
    
    @pytest.mark.asyncio
    async def test_view_index(self):
        """Test viewing index statistics."""
        # Upload a document first
        document_data = {
            "doc_id": "doc1",
            "content": "Python programming language",
            "title": "Python"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # View index
        response = await self.client.get("/index")
        assert response.status_code == 200
        
        data = response.json()
        assert "stats" in data
        assert "sample_terms" in data
        
        stats = data["stats"]
        assert stats["total_documents"] == 1
        assert stats["total_terms"] > 0
        assert stats["index_size_mb"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_document(self):
        """Test retrieving a specific document."""
        # Upload a document
        document_data = {
            "doc_id": "doc1",
            "content": "Python programming language",
            "title": "Python Programming",
            "author": "Test Author"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # Get the document
        response = await self.client.get("/documents/doc1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["doc_id"] == "doc1"
        assert data["title"] == "Python Programming"
        assert data["author"] == "Test Author"
        assert "Python programming language" in data["content"]
        assert data["total_terms"] > 0
        assert data["unique_terms"] > 0
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self):
        """Test retrieving a document that doesn't exist."""
        response = await self.client.get("/documents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test deleting a document."""
        # Upload a document
        document_data = {
            "doc_id": "doc1",
            "content": "Python programming language",
            "title": "Python"
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 200
        
        # Verify document exists
        response = await self.client.get("/documents/doc1")
        assert response.status_code == 200
        
        # Delete the document
        response = await self.client.delete("/documents/doc1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Document deleted successfully"
        assert data["doc_id"] == "doc1"
        assert data["total_documents"] == 0
        
        # Verify document is deleted
        response = await self.client.get("/documents/doc1")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self):
        """Test deleting a document that doesn't exist."""
        response = await self.client.delete("/documents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_json_upload(self):
        """Test uploading with invalid JSON."""
        response = await self.client.post("/upload", content="invalid json")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test uploading with missing required fields."""
        document_data = {
            "content": "Python programming"  # Missing doc_id
        }
        
        response = await self.client.post("/upload", json=document_data)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_search_with_invalid_limit(self):
        """Test searching with invalid limit parameter."""
        response = await self.client.get("/search?query=python&limit=0")
        assert response.status_code == 422
        
        response = await self.client.get("/search?query=python&limit=101")
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__]) 