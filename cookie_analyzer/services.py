"""
Weiterleitung zum services-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem services-Modul
from .services.service_interfaces import CookieDatabaseService, CookieClassifierService, CrawlerService
from .services.provider import ServiceProvider
from .services.crawler_factory import CrawlerType, get_crawler_service
from .services.initializer import initialize_services, get_database_service, get_cookie_classifier_service

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'CookieDatabaseService',
    'CookieClassifierService',
    'CrawlerService',
    'ServiceProvider',
    'CrawlerType',
    'get_crawler_service',
    'initialize_services',
    'get_database_service',
    'get_cookie_classifier_service',
]