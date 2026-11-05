"""
Data models for API requests and responses
Using Pydantic for validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Entity types for investigation"""
    PERSON = "person"
    COMPANY = "company"
    WALLET = "wallet"
    ADDRESS = "address"


class SourceType(str, Enum):
    """Data source types"""
    BLOCKCHAIN = "blockchain"
    SEC = "sec"
    NEWS = "news"
    SANCTIONS = "sanctions"
    BUSINESS_REGISTRY = "business_registry"


# ============================================================================
# REQUEST MODELS
# ============================================================================


class InvestigateRequest(BaseModel):
    """Request to start an investigation"""
    query: str = Field(..., min_length=1, max_length=500, description="Investigation query")
    entity_type: EntityType = Field(..., description="Type of entity")
    confidence_threshold: Optional[float] = Field(default=0.70, ge=0.0, le=1.0)


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class Finding(BaseModel):
    """Investigation finding"""
    finding_id: str
    assertion: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: str  # "low", "medium", "high", "critical"
    evidence_count: int = 0


class InvestigateResponse(BaseModel):
    """Response from investigation"""
    report_id: str
    status: str  # "completed", "pending", "failed"
    query: str
    entity_type: EntityType
    findings: List[Finding]
    execution_time_seconds: float
    created_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    app_version: str
    timestamp: datetime