"""
Cookie-Analyzer: Ein Tool zur Analyse und Klassifizierung von Cookies auf Websites.
"""

from .core import CookieAnalyzer, crawl_website, crawl_website_async
from .handlers.cookie_handler import CookieHandler, classify_cookies, remove_duplicate_cookies
from .database.handler import DatabaseHandler, load_database, find_cookie_info
from .database.updater import update_cookie_database, get_alternative_cookie_databases
from .utils.config import Config, load_config
from .utils.logging import setup_logging
from .utils.url import validate_url
from .utils.export import save_results_as_json
from .services.initializer import initialize_services

__version__ = "1.0.0"
__all__ = [
    'CookieAnalyzer',
    'crawl_website',
    'crawl_website_async',
    'CookieHandler',
    'classify_cookies',
    'remove_duplicate_cookies',
    'DatabaseHandler',
    'load_database',
    'find_cookie_info',
    'update_cookie_database',
    'get_alternative_cookie_databases',
    'Config',
    'load_config',
    'setup_logging',
    'validate_url',
    'save_results_as_json',
    'initialize_services'
]

# Initialisiere die Standard-Services
initialize_services()
