### ai_interlinq/utils/logging.py

"""Logging utilities for AI-Interlinq."""

import logging
import logging.handlers
import sys
from typing import Optional
from ..config import LoggingConfig


class AIInterlinqFormatter(logging.Formatter):
    """Custom formatter for AI-Interlinq logs."""
    
    def format(self, record):
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            record.msg = f"[{record.correlation_id}] {record.msg}"
        
        # Add agent ID if available
        if hasattr(record, 'agent_id'):
            record.msg = f"[{record.agent_id}] {record.msg}"
        
        return super().format(record)


def setup_logging(config: LoggingConfig, logger_name: str = "ai_interlinq") -> logging.Logger:
    """Setup logging with the given configuration."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config.level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = AIInterlinqFormatter(config.format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if config.file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"ai_interlinq.{name}")
