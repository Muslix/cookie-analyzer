"""
Logging-Funktionalität für den Cookie-Analyzer.
"""

import logging
from typing import Optional

def setup_logging(log_file: str = "cookie_analyzer.log", log_level: int = logging.INFO) -> None:
    """
    Richtet das Logging für die Anwendung ein.
    
    Args:
        log_file: Pfad zur Log-Datei
        log_level: Logging-Level (z.B. logging.INFO, logging.DEBUG)
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )