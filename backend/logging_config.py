"""
Logging configuration for production & development.
Handles file logging, error tracking, and structured log formatting.
"""
import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(config):
    """
    Configure logging system.
    
    Args:
        config: Configuration object with LOG_LEVEL, LOG_FILE, etc.
    """
    # Create logs directory if needed
    if config.LOG_FILE:
        log_dir = Path(config.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    
    # Log format
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    if config.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
        logger.addHandler(file_handler)
    
    # Error file handler (if configured)
    if config.LOG_ERROR_FILE:
        error_dir = Path(config.LOG_ERROR_FILE).parent
        error_dir.mkdir(parents=True, exist_ok=True)
        
        error_handler = logging.handlers.RotatingFileHandler(
            config.LOG_ERROR_FILE,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name):
    """Get a logger for a specific module."""
    return logging.getLogger(name)
