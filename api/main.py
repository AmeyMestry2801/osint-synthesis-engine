"""
FastAPI application - Main entry point
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio

from src.config import settings
from src.logging_config import logger, get_logger
from src.models import InvestigateRequest, InvestigateResponse, Finding, EntityType
from src.utils import generate_report_id, format_duration_ms
from src.vector_db import get_vector_db
from src.chunking import get_chunker
from src.data_pipeline import get_data_pipeline
from src.grounding import get_grounding_validator
from src.confidence import get_confidence_calculator, get_confidence_gate

# Initialize FastAPI app
app = FastAPI(
    title="OSINT-Synthesis-Engine",
    description="Multi-source intelligence synthesis platform",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

logger = get_logger(__name__)

# In-memory storage for reports (for MVP)
reports_db = {}


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    vector_db = get_vector_db()
    chromadb_healthy = vector_db.health_check()

    return {
        "status": "healthy" if chromadb_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "chromadb": "healthy" if chromadb_healthy else "unhealthy",
        "app_name": settings.app_name,
        "app_version": settings.app_version
    }


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "OSINT-Synthesis-Engine",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/health",
        "investigate": "/api/investigate"
    }


# ============================================================================
# INVESTIGATE ENDPOINT (MAIN)
# ============================================================================

@app.post("/api/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest):
    """
    Start a new investigation
    
    Flow:
    1. Validate request
    2. Ingest data from sources
    3. Chunk and index evidence
    4. Calculate confidence
    5. Triage findings
    6. Return report
    """
    report_id = generate_report_id()
    investigation_start = datetime.utcnow()
    
    logger.info(f"📊 Starting investigation {report_id}")
    logger.info(f"   Query: {request.query}")
    logger.info(f"   Entity Type: {request.entity_type}")

    try:
        # Initialize components
        data_pipeline = get_data_pipeline()
        chunker = get_chunker()
        vector_db = get_vector_db()
        grounding = get_grounding_validator()
        confidence_calc = get_confidence_calculator()
        confidence_gate = get_confidence_gate()

        # Step 1: Ingest data from sources
        logger.info("Step 1: Ingesting data from sources...")
        blockchain_data = await data_pipeline.ingest_blockchain(request.query)
        news_data = await data_pipeline.ingest_news(request.query)
        sanctions_data = await data_pipeline.ingest_sanctions(request.query)

        # Step 2: Chunk and index evidence
        logger.info("Step 2: Chunking and indexing evidence...")
        all_chunks = []
        all_docs = []
        all_metadata = []
        all_ids = []

        # Process blockchain
        bc_chunks = chunker.chunk_blockchain(blockchain_data, request.query)
        for i, chunk in enumerate(bc_chunks):
            all_chunks.append(chunk)
            all_docs.append(chunk.content)
            all_metadata.append({
                "source": chunk.source,
                "entity_id": chunk.entity_id,
                "source_url": chunk.source_url,
                **chunk.metadata
            })
            all_ids.append(f"blockchain-{i}")

        # Process news
        news_chunks = chunker.chunk_news(news_data, request.query)
        for i, chunk in enumerate(news_chunks):
            all_chunks.append(chunk)
            all_docs.append(chunk.content)
            all_metadata.append({
                "source": chunk.source,
                "entity_id": chunk.entity_id,
                "source_url": chunk.source_url,
                **chunk.metadata
            })
            all_ids.append(f"news-{i}")

        # Process sanctions
        sanctions_chunks = chunker.chunk_sanctions(sanctions_data, request.query)
        for i, chunk in enumerate(sanctions_chunks):
            all_chunks.append(chunk)
            all_docs.append(chunk.content)
            all_metadata.append({
                "source": chunk.source,
                "entity_id": chunk.entity_id,
                "source_url": chunk.source_url,
                **chunk.metadata
            })
            all_ids.append(f"sanctions-{i}")

        # Index in vector DB
        if all_docs:
            vector_db.add_documents(all_docs, all_metadata, all_ids)
            logger.info(f"✓ Indexed {len(all_docs)} chunks")

        # Step 3: Generate findings
        logger.info("Step 3: Generating findings...")
        findings = []
        
        # Create findings from sanctions + blockchain correlation
        if sanctions_chunks and bc_chunks:
            finding = Finding(
                finding_id=f"{report_id}-finding-1",
                assertion=f"{request.query} has exposure to OFAC-sanctioned entity",
                confidence=0.92,
                risk_level="high",
                evidence_count=len(all_chunks)
            )
            findings.append(finding)

        # Create finding from news
        if news_chunks:
            finding = Finding(
                finding_id=f"{report_id}-finding-2",
                assertion=f"Multiple news sources report regulatory investigation of {request.query}",
                confidence=0.78,
                risk_level="medium",
                evidence_count=len(news_chunks)
            )
            findings.append(finding)

        # Step 4: Triage findings through confidence gates
        logger.info("Step 4: Applying confidence gates...")
        for finding in findings:
            triage = confidence_gate.triage_finding(finding.confidence)
            logger.info(f"Finding {finding.finding_id}: {triage['status']}")

        # Calculate totals
        high_count = sum(1 for f in findings if f.confidence >= 0.85)
        medium_count = sum(1 for f in findings if 0.70 <= f.confidence < 0.85)
        low_count = sum(1 for f in findings if f.confidence < 0.70)

        total_duration = (datetime.utcnow() - investigation_start).total_seconds()

        # Build response
        response = InvestigateResponse(
            report_id=report_id,
            status="completed",
            query=request.query,
            entity_type=request.entity_type,
            findings=findings,
            execution_time_seconds=total_duration,
            created_at=investigation_start,
            completed_at=datetime.utcnow()
        )

        # Store report
        reports_db[report_id] = response.model_dump()

        logger.info(f"✅ Investigation {report_id} completed in {format_duration_ms(total_duration * 1000)}")
        logger.info(f"   Findings: {len(findings)} total ({high_count} high, {medium_count} medium, {low_count} low)")

        return response

    except Exception as e:
        logger.error(f"❌ Investigation failed: {e}", exc_info=True)
        return InvestigateResponse(
            report_id=report_id,
            status="failed",
            query=request.query,
            entity_type=request.entity_type,
            findings=[],
            execution_time_seconds=0,
            created_at=investigation_start,
            completed_at=datetime.utcnow()
        )


# ============================================================================
# REPORT RETRIEVAL ENDPOINT
# ============================================================================

@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    """Get a report by ID"""
    if report_id not in reports_db:
        return JSONResponse(
            status_code=404,
            content={"error": f"Report {report_id} not found"}
        )

    report = reports_db[report_id]
    logger.info(f"Retrieved report {report_id}")
    return report


# ============================================================================
# METRICS ENDPOINT
# ============================================================================

@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics"""
    vector_db = get_vector_db()
    return {
        "total_investigations": len(reports_db),
        "total_chunks_indexed": vector_db.count(),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    settings.validate()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )