"""
Configuration management for OSINT Engine
Loads settings from .env file
"""

import os
from typing import List


class Settings:
    """Application settings"""

    # App metadata
    app_name: str = "OSINT-Synthesis-Engine"
    app_version: str = "2.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # API configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))

    # LLM configuration (Groq)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "test-key-for-local-dev")
    groq_model: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    # ChromaDB configuration
    chromadb_path: str = os.getenv("CHROMADB_PATH", "./chroma_db")

    # Confidence thresholds
    confidence_high_threshold: float = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", 0.85))
    confidence_medium_threshold: float = float(os.getenv("CONFIDENCE_MEDIUM_THRESHOLD", 0.70))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self):
        """Validate settings on startup"""
        print(f"✓ Configuration loaded: {self.app_name} v{self.app_version}")
        print(f"  Environment: {self.environment}")
        print(f"  API: {self.api_host}:{self.api_port}")
        print(f"  ChromaDB: {self.chromadb_path}")


# Global settings instance
settings = Settings()