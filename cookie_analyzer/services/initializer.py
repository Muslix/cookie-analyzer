"""
Funktionen zur Initialisierung der Services.
"""

import logging
from typing import Optional

from .provider import ServiceProvider
from .service_interfaces import CookieDatabaseService, CookieClassifierService

logger = logging.getLogger(__name__)

def initialize_services() -> None:
    """Initialisiert alle Standard-Services."""
    from ..database.handler import DatabaseHandler
    from ..handlers.cookie_handler import CookieHandler
    
    # Registriere Standard-Implementierungen
    ServiceProvider.register("database", DatabaseHandler())
    ServiceProvider.register("cookie_classifier", CookieHandler())
    
    logger.info("Services initialized with default implementations")

def get_database_service() -> CookieDatabaseService:
    """Gibt den aktuell registrierten Datenbank-Service zurück."""
    return ServiceProvider.get("database")

def get_cookie_classifier_service() -> CookieClassifierService:
    """Gibt den aktuell registrierten Cookie-Classifier-Service zurück."""
    return ServiceProvider.get("cookie_classifier")