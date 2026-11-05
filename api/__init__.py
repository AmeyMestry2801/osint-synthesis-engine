"""
FastAPI application for OSINT Engine
"""

from fastapi import FastAPI

app = FastAPI(
    title="OSINT-Synthesis-Engine",
    description="Multi-source intelligence synthesis platform",
    version="2.0.0"
)

print("✓ FastAPI app initialized")