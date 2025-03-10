"""Logging configuration and setup for the Tío Pepe system."""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure and setup logging for the system."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup file handler
    log_file = os.path.join(logs_dir, 'system.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger