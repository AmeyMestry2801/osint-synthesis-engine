"""
Structured logging configuration
"""

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)


def setup_logging():
    """Configure logging"""
    logger = logging.getLogger("osint")
    logger.setLevel(logging.INFO)

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    return logger


# Global logger
logger = setup_logging()


def get_logger(name: str):
    """Get logger instance"""
    return logging.getLogger(name)