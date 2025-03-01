"""
Weiterleitung zum core-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem core-Modul
from .core.analyzer import CookieAnalyzer, crawl_website, crawl_website_async

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'CookieAnalyzer',
    'crawl_website',
    'crawl_website_async',
]
