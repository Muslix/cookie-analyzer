"""
Weiterleitung zum crawler-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem crawler-Modul
from .crawler.base import BrowserContextProtocol, PageProtocol
from .crawler.cookie_crawler import CookieCrawler
from .crawler.async_crawler import AsyncCookieCrawler
from .crawler.selenium_crawler import SeleniumCookieCrawler
from .crawler.consent_manager import ConsentManager

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'BrowserContextProtocol',
    'PageProtocol',
    'CookieCrawler',
    'AsyncCookieCrawler',
    'SeleniumCookieCrawler',
    'ConsentManager',
]