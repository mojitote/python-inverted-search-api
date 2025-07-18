import pytest
import tempfile
import shutil
from pathlib import Path

from app.index import InvertedIndex
from app.storage import IndexStorage


class TestInvertedIndex:
    """Test cases for the InvertedIndex class."""
    
    def setup_method(self):
        """Set up a fresh index for each test."""
        self.index = InvertedIndex()
    
    def test_empty_index(self):
        """Test that a new index is empty."""
        assert self.index.total_documents == 0
        assert self.index.total_terms == 0
        assert len(self.index.index) == 0
        assert len(self.index.documents) == 0
    
    def test_add_single_document(self):
        """Test adding a single document."""
        success = self.index.add_document(
            doc_id="doc1",
            content="Python is a programming language",
            title="Python Introduction",
            author="John Doe"
        )
        
        assert success is True
        assert self.index.total_documents == 1
        assert self.index.total_terms > 0
        
        # Check that terms are indexed
        assert "python" in self.index.index
        assert "programming" in self.index.index
        assert "language" in self.index.index
        
        # Check document metadata
        doc = self.index.get_document("doc1")
        assert doc is not None
        assert doc['title'] == "Python Introduction"
        assert doc['author'] == "John Doe"
        assert "Python is a programming language" in doc['content']
    
    def test_add_document_with_empty_content(self):
        """Test adding a document with empty content."""
        success = self.index.add_document(doc_id="doc1", content="")
        assert success is False
        assert self.index.total_documents == 0
    
    def test_add_document_with_special_characters(self):
        """Test adding a document with special characters."""
        content = "Python 3.10+ is awesome! It's the best language."
        success = self.index.add_document(doc_id="doc1", content=content)
        
        assert success is True
        assert "python" in self.index.index
        assert "awesome" in self.index.index
        assert "best" in self.index.index
        assert "language" in self.index.index
    
    def test_search_single_term(self):
        """Test searching for a single term."""
        # Add test documents
        self.index.add_document("doc1", "Python is a programming language")
        self.index.add_document("doc2", "Java is also a programming language")
        self.index.add_document("doc3", "Python is popular for data science")
        
        # Search for "python"
        results = self.index.search("python", limit=10)
        
        assert len(results) == 2  # doc1 and doc3 contain "python"
        
        # Check that results are sorted by score (descending)
        scores = [result[1] for result in results]
        assert scores == sorted(scores, reverse=True)
        
        # Check document IDs
        doc_ids = [result[0] for result in results]
        assert "doc1" in doc_ids
        assert "doc3" in doc_ids
    
    def test_search_multiple_terms(self):
        """Test searching for multiple terms."""
        # Add test documents
        self.index.add_document("doc1", "Python programming language")
        self.index.add_document("doc2", "Java programming language")
        self.index.add_document("doc3", "Python data science")
        
        # Search for "python programming"
        results = self.index.search("python programming", limit=10)
        
        assert len(results) == 1  # Only doc1 contains both terms
        assert results[0][0] == "doc1"
        assert results[0][1] > 0  # Score should be positive
    
    def test_search_no_results(self):
        """Test searching for terms that don't exist."""
        self.index.add_document("doc1", "Python programming")
        
        results = self.index.search("javascript", limit=10)
        assert len(results) == 0
    
    def test_search_empty_query(self):
        """Test searching with empty query."""
        self.index.add_document("doc1", "Python programming")
        
        results = self.index.search("", limit=10)
        assert len(results) == 0
    
    def test_remove_document(self):
        """Test removing a document from the index."""
        # Add a document
        self.index.add_document("doc1", "Python programming")
        assert self.index.total_documents == 1
        
        # Remove the document
        success = self.index.remove_document("doc1")
        assert success is True
        assert self.index.total_documents == 0
        assert self.index.get_document("doc1") is None
        
        # Check that terms are also removed
        assert "python" not in self.index.index
        assert "programming" not in self.index.index
    
    def test_remove_nonexistent_document(self):
        """Test removing a document that doesn't exist."""
        success = self.index.remove_document("nonexistent")
        assert success is False
    
    def test_get_stats(self):
        """Test getting index statistics."""
        # Add some documents
        self.index.add_document("doc1", "Python programming")
        self.index.add_document("doc2", "Java programming")
        
        stats = self.index.get_stats()
        
        assert stats['total_documents'] == 2
        assert stats['total_terms'] > 0
        assert 'most_common_terms' in stats
        assert len(stats['most_common_terms']) <= 10
    
    def test_get_sample_terms(self):
        """Test getting sample terms."""
        # Add documents with many terms
        self.index.add_document("doc1", "Python programming language data science")
        self.index.add_document("doc2", "Java programming language web development")
        
        sample = self.index.get_sample_terms(limit=5)
        assert len(sample) <= 5
        
        # Check that sample contains actual terms
        if sample:
            term = list(sample.keys())[0]
            assert isinstance(sample[term], dict)
    
    def test_clear_index(self):
        """Test clearing the entire index."""
        # Add some documents
        self.index.add_document("doc1", "Python programming")
        self.index.add_document("doc2", "Java programming")
        
        assert self.index.total_documents == 2
        
        # Clear the index
        self.index.clear()
        
        assert self.index.total_documents == 0
        assert self.index.total_terms == 0
        assert len(self.index.index) == 0
        assert len(self.index.documents) == 0
    
    def test_term_frequency_calculation(self):
        """Test that term frequency is calculated correctly."""
        # Add document with repeated terms
        self.index.add_document("doc1", "Python Python Python programming")
        
        # Search for "python"
        results = self.index.search("python", limit=10)
        
        assert len(results) == 1
        assert results[0][0] == "doc1"
        # Score should reflect the high frequency of "python"
        assert results[0][1] > 0
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        self.index.add_document("doc1", "Python programming")
        
        # Search with different cases
        results1 = self.index.search("python", limit=10)
        results2 = self.index.search("PYTHON", limit=10)
        results3 = self.index.search("Python", limit=10)
        
        assert len(results1) == len(results2) == len(results3) == 1
        assert results1[0][0] == results2[0][0] == results3[0][0] == "doc1"


class TestIndexStorage:
    """Test cases for the IndexStorage class."""
    
    def setup_method(self):
        """Set up a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = IndexStorage(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_index(self):
        """Test saving and loading an index."""
        # Create and populate an index
        index = InvertedIndex()
        index.add_document("doc1", "Python programming")
        index.add_document("doc2", "Java programming")
        
        # Save the index
        success = self.storage.save_index(index)
        assert success is True
        
        # Load the index
        loaded_index = self.storage.load_index()
        assert loaded_index is not None
        assert loaded_index.total_documents == 2
        assert loaded_index.total_terms > 0
        
        # Verify documents are preserved
        doc1 = loaded_index.get_document("doc1")
        doc2 = loaded_index.get_document("doc2")
        assert doc1 is not None
        assert doc2 is not None
        assert "Python programming" in doc1['content']
        assert "Java programming" in doc2['content']
    
    def test_load_nonexistent_index(self):
        """Test loading when no index file exists."""
        loaded_index = self.storage.load_index()
        assert loaded_index is not None
        assert loaded_index.total_documents == 0
    
    def test_get_index_info(self):
        """Test getting index file information."""
        # Create and save an index
        index = InvertedIndex()
        index.add_document("doc1", "Python programming")
        self.storage.save_index(index)
        
        info = self.storage.get_index_info()
        
        assert info['exists'] is True
        assert info['size_mb'] > 0
        assert info['last_modified'] is not None
        assert info['backup_count'] >= 0
    
    def test_backup_creation(self):
        """Test that backups are created when saving."""
        # Create and save an index
        index = InvertedIndex()
        index.add_document("doc1", "Python programming")
        self.storage.save_index(index)
        
        # Save again to trigger backup creation
        self.storage.save_index(index)
        
        info = self.storage.get_index_info()
        assert info['backup_count'] > 0
    
    def test_delete_index(self):
        """Test deleting the index."""
        # Create and save an index
        index = InvertedIndex()
        index.add_document("doc1", "Python programming")
        self.storage.save_index(index)
        
        # Verify index exists
        info = self.storage.get_index_info()
        assert info['exists'] is True
        
        # Delete the index
        success = self.storage.delete_index()
        assert success is True
        
        # Verify index is deleted
        info = self.storage.get_index_info()
        assert info['exists'] is False
        assert info['backup_count'] == 0


if __name__ == "__main__":
    pytest.main([__file__]) 