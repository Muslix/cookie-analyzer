"""
Weiterleitung zum database-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem database-Modul
from .database.handler import DatabaseHandler, load_database, find_cookie_info
from .database.updater import update_cookie_database, get_alternative_cookie_databases

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'DatabaseHandler',
    'load_database',
    'find_cookie_info',
    'update_cookie_database',
    'get_alternative_cookie_databases',
]
