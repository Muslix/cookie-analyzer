"""
Weiterleitung zum handlers-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem handlers-Modul
from .handlers.cookie_handler import CookieHandler, classify_cookies, remove_duplicate_cookies
from .handlers.cookie_classifier import CookieClassifier

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'CookieHandler',
    'CookieClassifier',
    'classify_cookies',
    'remove_duplicate_cookies',
]
