"""
Système de logging.
"""

import sys
from pathlib import Path
from loguru import logger

from config.settings import settings, LOGS_DIR


def setup_logger():
    """Configure le logger."""
    logger.remove()
    
    # Console
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level=settings.app.log_level,
        colorize=True
    )
    
    # Fichier
    logger.add(
        LOGS_DIR / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )
    
    return logger


log = setup_logger()


def log_agent_action(agent_name: str, action: str, details: dict = None):
    """Log une action d'agent."""
    details_str = f" | {details}" if details else ""
    log.info(f"🤖 [{agent_name}] {action}{details_str}")