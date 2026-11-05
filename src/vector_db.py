"""
ChromaDB vector database wrapper
"""

import chromadb
from typing import List, Dict, Any, Optional
from src.logging_config import get_logger

logger = get_logger(__name__)


class VectorDB:
    """Wrapper around ChromaDB"""

    def __init__(self):
        """Initialize ChromaDB connection"""
        try:
            # Local persistent ChromaDB
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.client.get_or_create_collection(
                name="osint_evidence",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("✓ ChromaDB initialized")
        except Exception as e:
            logger.error(f"ChromaDB init failed: {e}")
            raise

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Add documents to collection"""
        try:
            if ids is None:
                ids = [f"doc-{i}" for i in range(len(documents))]

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✓ Added {len(documents)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def search(
        self,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Search collection"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"documents": [], "metadatas": []}

    def count(self) -> int:
        """Get document count"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0

    def health_check(self) -> bool:
        """Check if ChromaDB is healthy"""
        try:
            self.collection.count()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global instance
_vector_db: Optional[VectorDB] = None


def get_vector_db() -> VectorDB:
    """Get global vector DB instance"""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDB()
    return _vector_db