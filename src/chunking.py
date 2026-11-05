"""
Domain-aware text chunking for different data sources
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    content: str
    source: str
    entity_id: str
    source_url: str
    metadata: Dict[str, Any]
    chunk_index: int


class DomainChunker:
    """Domain-aware chunking for different sources"""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_blockchain(self, data: Dict[str, Any], entity_id: str) -> List[Chunk]:
        """Chunk blockchain transaction data"""
        chunks = []
        transactions = data.get("transactions", [])

        for tx_index, tx in enumerate(transactions):
            tx_text = f"""
Transaction {tx.get('hash', 'N/A')}:
From: {tx.get('from', 'N/A')}
To: {tx.get('to', 'N/A')}
Amount: {tx.get('amount', 'N/A')} {tx.get('currency', 'ETH')}
Date: {tx.get('timestamp', 'N/A')}
""".strip()

            chunk = Chunk(
                content=tx_text,
                source="blockchain",
                entity_id=entity_id,
                source_url=tx.get("url", ""),
                metadata={
                    "tx_hash": tx.get("hash", ""),
                    "from_address": tx.get("from", ""),
                    "to_address": tx.get("to", ""),
                    "amount": tx.get("amount", ""),
                },
                chunk_index=tx_index
            )
            chunks.append(chunk)

        logger.info(f"✓ Chunked {len(chunks)} blockchain transactions")
        return chunks

    def chunk_news(self, data: Dict[str, Any], entity_id: str) -> List[Chunk]:
        """Chunk news articles"""
        chunks = []
        articles = data.get("articles", [])

        for idx, article in enumerate(articles):
            article_text = f"""
Headline: {article.get('headline', 'N/A')}
Source: {article.get('source', 'N/A')}
Date: {article.get('date', 'N/A')}
Content: {article.get('content', 'N/A')}
""".strip()

            chunk = Chunk(
                content=article_text,
                source="news",
                entity_id=entity_id,
                source_url=article.get("url", ""),
                metadata={
                    "headline": article.get("headline", ""),
                    "source": article.get("source", ""),
                    "sentiment": article.get("sentiment", "neutral"),
                },
                chunk_index=idx
            )
            chunks.append(chunk)

        logger.info(f"✓ Chunked {len(chunks)} news articles")
        return chunks

    def chunk_sanctions(self, data: Dict[str, Any], entity_id: str) -> List[Chunk]:
        """Chunk sanctions list entries"""
        chunks = []
        entries = data.get("entries", [])

        for idx, entry in enumerate(entries):
            entry_text = f"""
Entity: {entry.get('name', 'N/A')}
Jurisdiction: {entry.get('jurisdiction', 'N/A')}
List: {entry.get('list', 'N/A')}
Date Listed: {entry.get('date_listed', 'N/A')}
""".strip()

            chunk = Chunk(
                content=entry_text,
                source="sanctions",
                entity_id=entity_id,
                source_url=entry.get("url", ""),
                metadata={
                    "entity_name": entry.get("name", ""),
                    "jurisdiction": entry.get("jurisdiction", ""),
                    "list": entry.get("list", "SDN"),
                },
                chunk_index=idx
            )
            chunks.append(chunk)

        logger.info(f"✓ Chunked {len(chunks)} sanctions entries")
        return chunks


# Global chunker
_chunker: Optional[DomainChunker] = None


def get_chunker() -> DomainChunker:
    """Get global chunker instance"""
    global _chunker
    if _chunker is None:
        _chunker = DomainChunker()
    return _chunker