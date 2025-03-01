"""
Funktionen zum Aktualisieren der Cookie-Datenbank.
"""

import logging
from typing import Dict, Optional

from ..utils.config import Config
from .handler import DatabaseHandler

logger = logging.getLogger(__name__)

def update_cookie_database(output_path: Optional[str] = None, url: Optional[str] = None) -> bool:
    """
    Aktualisiert die Cookie-Datenbank aus einer Online-Quelle.
    
    Args:
        output_path: Pfad, unter dem die aktualisierte Datenbank gespeichert werden soll.
        url: URL zur aktuellen Datenbank (optional, sonst wird die Standard-URL verwendet).
        
    Returns:
        True, wenn die Aktualisierung erfolgreich war, sonst False.
    """
    handler = DatabaseHandler()
    return handler.update_database(output_path, url)

def get_alternative_cookie_databases() -> Dict[str, str]:
    """
    Liefert eine Liste alternativer Cookie-Datenbanken.
    
    Returns:
        Dictionary mit Namen und URLs zu alternativen Cookie-Datenbanken
    """
    return {
        "Open Cookie Database (GitHub)": Config.GITHUB_DATABASE_URL,
    }