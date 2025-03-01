"""
Weiterleitung zum interface-Modul für Abwärtskompatibilität.
"""

# Importiere alle Komponenten aus dem interface-Modul
from .interface.wrapper import analyze_website, analyze_website_async
from .interface.cli import cli_main

# Füge alle zu exportierenden Namen hinzu
__all__ = [
    'analyze_website',
    'analyze_website_async',
    'cli_main',
]
