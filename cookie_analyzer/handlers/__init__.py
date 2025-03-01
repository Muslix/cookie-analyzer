"""
Handler-Komponenten für die Cookie-Verarbeitung und -Klassifikation.
"""

from .cookie_handler import CookieHandler, classify_cookies, remove_duplicate_cookies
from .cookie_classifier import CookieClassifier

__all__ = [
    'CookieHandler',
    'CookieClassifier',
    'classify_cookies',
    'remove_duplicate_cookies',
]