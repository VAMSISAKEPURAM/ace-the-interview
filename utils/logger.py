"""
Logging module providing structured application-wide logger instances.
"""

import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE_PATH

def setup_logger(name: str = "VoiceChatbot") -> logging.Logger:
    """
    Creates and configures a logger instance with console and file output handlers.
    
    Args:
        name (str): The logger instance name.
        
    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Log Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        console_handler.write(f"Failed to setup file logging handler: {e}\n")

    return logger

# Global default logger instance
logger = setup_logger()
