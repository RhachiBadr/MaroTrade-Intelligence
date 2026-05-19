# logging_config.py — Configuration centralisée du logging

import logging
import logging.handlers
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = "marotrade.log"):
    """
    Configure le logging structuré pour toute l'application.
    - Console pour développement
    - Fichier rotatif pour production
    - Format JSON optionnel pour monitoring
    """

    # Niveaux de log
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    level = level_map.get(log_level.upper(), logging.INFO)

    # Formatters
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )

    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Supprimer les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Handler fichier (rotatif)
    log_path = Path("logs") / log_file
    log_path.parent.mkdir(exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)  # Plus verbeux dans les fichiers
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Loggers spécifiques avec niveaux ajustés
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logger = logging.getLogger("marotrade")
    logger.info(f"Logging configuré — niveau {log_level} — fichier {log_path}")

    return logger