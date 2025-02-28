# __init__.py
from .core import crawl_website
from .crawler import CookieCrawler
from .cookie_handler import classify_cookies, remove_duplicate_cookies
from .interface import analyze_website
from .database import load_cookie_database, find_cookie_info, update_cookie_database, get_alternative_cookie_databases
from .utils import setup_logging, save_results_as_json, load_config, validate_url

# Exportiere die wichtigsten Funktionen und Klassen
__all__ = [
    'crawl_website',
    'CookieCrawler',
    'classify_cookies',
    'analyze_website',
    'load_cookie_database',
    'find_cookie_info',
    'remove_duplicate_cookies',
    'setup_logging',
    'save_results_as_json',
    'load_config',
    'validate_url',
    'update_cookie_database',
    'get_alternative_cookie_databases'
]
