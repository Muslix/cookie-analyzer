"""
Crawler-Komponenten für den Cookie-Analyzer.
"""

from .base import BrowserContextProtocol, PageProtocol
from .cookie_crawler import CookieCrawler
from .async_crawler import AsyncCookieCrawler
from .consent_manager import ConsentManager

__all__ = [
    'BrowserContextProtocol',
    'PageProtocol',
    'CookieCrawler',
    'AsyncCookieCrawler',
    'ConsentManager',
]