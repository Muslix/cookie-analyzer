"""
Weiterleitung zum utils-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem utils-Modul
from .utils.config import Config, load_config
from .utils.logging import setup_logging
from .utils.url import validate_url
from .utils.export import save_results_as_json

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'Config',
    'load_config',
    'setup_logging',
    'validate_url',
    'save_results_as_json',
]
