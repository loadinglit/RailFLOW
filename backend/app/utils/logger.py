"""
RailMind Logger — Centralized logging for all engines.

Logs go to both console (colored) and file (backend/logs/railmind.log).
"""

import logging
import os
from pathlib import Path
from datetime import datetime

# Create logs directory
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "railmind.log"


class ColorFormatter(logging.Formatter):
    """Colored console output."""
    COLORS = {
        logging.DEBUG: "\033[36m",     # cyan
        logging.INFO: "\033[32m",      # green
        logging.WARNING: "\033[33m",   # yellow
        logging.ERROR: "\033[31m",     # red
        logging.CRITICAL: "\033[41m",  # red bg
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger with console + file handlers.

    Usage:
        from app.utils.logger import get_logger
        log = get_logger("jansuraksha.agent")
        log.info("Loading user context for %s", user_id)
    """
    logger = logging.getLogger(f"railmind.{name}")

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler — colored, INFO+
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(ColorFormatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(console)

    # File handler — full detail, DEBUG+
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    return logger