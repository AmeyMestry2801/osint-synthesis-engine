"""
Utility functions for OSINT Engine
"""

import uuid
import hashlib
from datetime import datetime


def generate_report_id() -> str:
    """Generate unique report ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    unique_hash = hashlib.md5(uuid.uuid4().bytes).hexdigest()[:8]
    return f"{timestamp}-{unique_hash}"


def generate_finding_id(report_id: str, index: int) -> str:
    """Generate finding ID"""
    return f"{report_id}-finding-{index}"


def format_duration_ms(duration_ms: float) -> str:
    """Format duration in milliseconds"""
    if duration_ms < 1000:
        return f"{duration_ms:.0f}ms"
    else:
        return f"{duration_ms / 1000:.1f}s"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def is_valid_entity_id(entity_id: str) -> bool:
    """Validate entity ID"""
    if not entity_id or len(entity_id) > 255:
        return False
    return True