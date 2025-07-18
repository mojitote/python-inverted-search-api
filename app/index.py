import re
import time
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class InvertedIndex:
    """
    Professional implementation of an inverted index for document search.
    
    This class provides efficient indexing and searching capabilities using
    term frequency-based ranking and document metadata storage.
    """
    
    def __init__(self):
        """Initialize an empty inverted index."""
        self.index: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.documents: Dict[str, Dict] = {}
        self.term_stats: Dict[str, int] = defaultdict(int)  # Document frequency per term
        self.total_documents = 0
        self.total_terms = 0
        
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by converting to lowercase and removing special characters.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase and remove special characters except spaces
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        return normalized
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into individual terms.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        normalized = self._normalize_text(text)
        tokens = normalized.split()
        # Filter out empty tokens and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [token for token in tokens if token and token not in stop_words]
    
    def _calculate_tf(self, term_count: int, total_terms: int) -> float:
        """
        Calculate term frequency score.
        
        Args:
            term_count: Number of occurrences of the term
            total_terms: Total number of terms in the document
            
        Returns:
            Term frequency score
        """
        if total_terms == 0:
            return 0.0
        return term_count / total_terms
    
    def add_document(self, doc_id: str, content: str, title: Optional[str] = None, 
                    author: Optional[str] = None) -> bool:
        """
        Add a document to the inverted index.
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            title: Optional document title
            author: Optional document author
            
        Returns:
            True if document was added successfully, False otherwise
        """
        try:
            if not content.strip():
                logger.warning(f"Empty content for document {doc_id}")
                return False
                
            # Tokenize the content
            tokens = self._tokenize(content)
            if not tokens:
                logger.warning(f"No valid tokens found for document {doc_id}")
                return False
            
            # Count term frequencies
            term_counts = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1
            
            # Update the inverted index
            for term, count in term_counts.items():
                self.index[term][doc_id] = count
                self.term_stats[term] += 1
            
            # Store document metadata
            self.documents[doc_id] = {
                'content': content,
                'title': title or f"Document {doc_id}",
                'author': author,
                'total_terms': len(tokens),
                'unique_terms': len(term_counts),
                'added_at': time.time()
            }
            
            self.total_documents += 1
            self.total_terms = len(self.index)
            
            logger.info(f"Successfully indexed document {doc_id} with {len(tokens)} tokens")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {str(e)}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float, Dict]]:
        """
        Search for documents containing the query terms.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of tuples containing (doc_id, score, metadata)
        """
        start_time = time.time()
        
        try:
            # Tokenize the query
            query_tokens = self._tokenize(query)
            if not query_tokens:
                return []
            
            # Find documents containing any of the query terms
            doc_scores = defaultdict(float)
            matching_docs = set()
            
            for token in query_tokens:
                if token in self.index:
                    for doc_id, term_freq in self.index[token].items():
                        matching_docs.add(doc_id)
                        # Calculate TF score for this term in this document
                        doc_metadata = self.documents.get(doc_id, {})
                        total_terms = doc_metadata.get('total_terms', 1)
                        tf_score = self._calculate_tf(term_freq, total_terms)
                        doc_scores[doc_id] += tf_score
            
            # Sort results by score (descending)
            results = []
            for doc_id in matching_docs:
                score = doc_scores[doc_id]
                metadata = self.documents.get(doc_id, {})
                results.append((doc_id, score, metadata))
            
            # Sort by score and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:limit]
            
            search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"Search completed in {search_time:.2f}ms, found {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Retrieve a document by its ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document metadata or None if not found
        """
        return self.documents.get(doc_id)
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove a document from the index.
        
        Args:
            doc_id: Document identifier to remove
            
        Returns:
            True if document was removed successfully, False otherwise
        """
        try:
            if doc_id not in self.documents:
                return False
            
            # Remove document from index
            for term in list(self.index.keys()):
                if doc_id in self.index[term]:
                    del self.index[term][doc_id]
                    # Remove term if no documents remain
                    if not self.index[term]:
                        del self.index[term]
                        del self.term_stats[term]
            
            # Remove document metadata
            del self.documents[doc_id]
            
            self.total_documents -= 1
            self.total_terms = len(self.index)
            
            logger.info(f"Successfully removed document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing document {doc_id}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get index statistics.
        
        Returns:
            Dictionary containing index statistics
        """
        return {
            'total_documents': self.total_documents,
            'total_terms': self.total_terms,
            'total_document_occurrences': sum(len(docs) for docs in self.index.values()),
            'average_terms_per_document': self.total_terms / max(self.total_documents, 1),
            'most_common_terms': sorted(
                self.term_stats.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
    
    def get_sample_terms(self, limit: int = 20) -> Dict[str, Dict[str, int]]:
        """
        Get a sample of indexed terms for debugging and learning purposes.
        
        Args:
            limit: Maximum number of terms to return
            
        Returns:
            Dictionary of terms and their document frequencies
        """
        sample = {}
        for i, (term, docs) in enumerate(self.index.items()):
            if i >= limit:
                break
            sample[term] = dict(docs)
        return sample
    
    def clear(self) -> None:
        """Clear all data from the index."""
        self.index.clear()
        self.documents.clear()
        self.term_stats.clear()
        self.total_documents = 0
        self.total_terms = 0
        logger.info("Index cleared") 