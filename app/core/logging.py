"""
Structured logging module for ResearchLens AI.
Supports correlation IDs (request_id) and clean terminal formatting.
"""

import logging
import sys


class RequestIdFormatter(logging.Formatter):
    """
    Custom formatter ensuring request_id is always present on the LogRecord,
    preventing KeyError or ValueError when logging from child loggers.
    """
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = getattr(record, "request_id", "-")
        return super().format(record)


# Base logger configuration
logger = logging.getLogger("researchlens")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = RequestIdFormatter(
        fmt="%(asctime)s [%(levelname)s] [req:%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str = "researchlens") -> logging.Logger:
    """Return a logger instance under the researchlens hierarchy."""
    log = logging.getLogger(name)
    # Ensure handlers don't duplicate if already propagated
    return log
