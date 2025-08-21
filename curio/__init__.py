"""
CURIO package initializer.

Sets up a robust root logger under the "curio" namespace that writes to
curio/logs/curio.log (created on first import) and also to stderr.
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

__all__ = ["get_logger", "__version__"]
__version__ = "0.2.0"


def _ensure_logging() -> logging.Logger:
    pkg_root = Path(__file__).resolve().parent
    logs_dir = pkg_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("curio")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicating handlers when re-imported
    if logger.handlers:
        return logger

    # File handler (rotating)
    try:
        fh = RotatingFileHandler(
            logs_dir / "curio.log",
            maxBytes=2_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logger.addHandler(fh)
    except Exception as e:
        # Fall back to stream only if file can't be created
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logger.addHandler(sh)
        logger.warning("File logging disabled: %s", e)

    # Always also log to stderr for visibility in Streamlit/pytest
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    logger.addHandler(sh)

    # Make third-party libs less noisy
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logger.debug("CURIO logging initialized.")
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a child logger under 'curio'."""
    root = _ensure_logging()
    return root if not name else root.getChild(name)


# Initialize on import
_ensure_logging()
