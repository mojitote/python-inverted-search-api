import pickle
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .index import InvertedIndex

logger = logging.getLogger(__name__)


class IndexStorage:
    """
    Handles persistence of the inverted index using pickle serialization.
    
    Provides save/load functionality with error handling, backup creation,
    and automatic recovery mechanisms.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the storage manager.
        
        Args:
            data_dir: Directory to store index files
        """
        self.data_dir = Path(data_dir)
        self.index_file = self.data_dir / "index.pkl"
        self.backup_dir = self.data_dir / "backups"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"Storage initialized with data directory: {self.data_dir}")
    
    def save_index(self, index: InvertedIndex) -> bool:
        """
        Save the inverted index to disk.
        
        Args:
            index: InvertedIndex instance to save
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Create backup of existing index if it exists
            if self.index_file.exists():
                self._create_backup()
            
            # Prepare data for serialization
            index_data = {
                'index': dict(index.index),
                'documents': index.documents,
                'term_stats': dict(index.term_stats),
                'total_documents': index.total_documents,
                'total_terms': index.total_terms,
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Save to temporary file first
            temp_file = self.index_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Atomic move to final location
            temp_file.replace(self.index_file)
            
            logger.info(f"Index saved successfully to {self.index_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            # Clean up temporary file if it exists
            temp_file = self.index_file.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def load_index(self) -> Optional[InvertedIndex]:
        """
        Load the inverted index from disk.
        
        Returns:
            InvertedIndex instance if successful, None otherwise
        """
        try:
            if not self.index_file.exists():
                logger.info("No existing index found, creating new one")
                return InvertedIndex()
            
            with open(self.index_file, 'rb') as f:
                index_data = pickle.load(f)
            
            # Create new index instance
            index = InvertedIndex()
            
            # Restore index data
            index.index = index_data['index']
            index.documents = index_data['documents']
            index.term_stats = index_data['term_stats']
            index.total_documents = index_data['total_documents']
            index.total_terms = index_data['total_terms']
            
            logger.info(f"Index loaded successfully from {self.index_file}")
            logger.info(f"Loaded {index.total_documents} documents with {index.total_terms} terms")
            
            return index
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            # Try to restore from backup
            return self._restore_from_backup()
    
    def _create_backup(self) -> bool:
        """
        Create a backup of the current index file.
        
        Returns:
            True if backup was created successfully, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"index_backup_{timestamp}.pkl"
            
            shutil.copy2(self.index_file, backup_file)
            
            # Keep only the last 5 backups
            self._cleanup_old_backups()
            
            logger.info(f"Backup created: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return False
    
    def _restore_from_backup(self) -> Optional[InvertedIndex]:
        """
        Attempt to restore index from the most recent backup.
        
        Returns:
            InvertedIndex instance if successful, None otherwise
        """
        try:
            backup_files = list(self.backup_dir.glob("index_backup_*.pkl"))
            if not backup_files:
                logger.warning("No backup files found")
                return None
            
            # Get the most recent backup
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
            
            logger.info(f"Attempting to restore from backup: {latest_backup}")
            
            with open(latest_backup, 'rb') as f:
                index_data = pickle.load(f)
            
            # Create new index instance
            index = InvertedIndex()
            
            # Restore index data
            index.index = index_data['index']
            index.documents = index_data['documents']
            index.term_stats = index_data['term_stats']
            index.total_documents = index_data['total_documents']
            index.total_terms = index_data['total_terms']
            
            logger.info(f"Successfully restored index from backup")
            return index
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {str(e)}")
            return None
    
    def _cleanup_old_backups(self, keep_count: int = 5) -> None:
        """
        Remove old backup files, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
        """
        try:
            backup_files = list(self.backup_dir.glob("index_backup_*.pkl"))
            if len(backup_files) <= keep_count:
                return
            
            # Sort by modification time and remove old ones
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {str(e)}")
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get information about the stored index.
        
        Returns:
            Dictionary containing index file information
        """
        info = {
            'exists': False,
            'size_mb': 0.0,
            'last_modified': None,
            'backup_count': 0
        }
        
        if self.index_file.exists():
            stat = self.index_file.stat()
            info.update({
                'exists': True,
                'size_mb': stat.st_size / (1024 * 1024),
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Count backup files
        backup_files = list(self.backup_dir.glob("index_backup_*.pkl"))
        info['backup_count'] = len(backup_files)
        
        return info
    
    def delete_index(self) -> bool:
        """
        Delete the index file and all backups.
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Delete main index file
            if self.index_file.exists():
                self.index_file.unlink()
                logger.info("Main index file deleted")
            
            # Delete all backup files
            backup_files = list(self.backup_dir.glob("index_backup_*.pkl"))
            for backup_file in backup_files:
                backup_file.unlink()
                logger.info(f"Backup file deleted: {backup_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return False 