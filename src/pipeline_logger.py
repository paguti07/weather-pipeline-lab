import logging
import logging.handlers
from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get LOG_LEVEL from .env, default to INFO if not set
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Get log file path from .env or use default
LOG_FILE = "pipeline.log"


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with both file and console handlers.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    # Set logger level
    logger.setLevel(LOG_LEVEL)

    # Define log format
    log_format = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler - writes to pipeline.log
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file handler: {e}")

    # Console handler - writes to stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger
