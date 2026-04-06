import logging
import os
from logging.handlers import RotatingFileHandler
from backend.core.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # File handler — rotates at 5MB, keeps 3 backups
    file_handler = RotatingFileHandler(
        os.path.join(settings.LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Audit log — classification decisions only
    audit_handler = RotatingFileHandler(
        os.path.join(settings.LOG_DIR, "audit.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    if name == "audit":
        logger.addHandler(audit_handler)

    return logger


logger = get_logger("app")
audit_logger = get_logger("audit")
