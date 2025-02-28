# __init__.py
from .core import CookieAnalyzer, crawl_website, crawl_website_async
from .crawler import CookieCrawler, AsyncCookieCrawler
from .cookie_handler import CookieHandler
from .interface import analyze_website, analyze_website_async
from .database import DatabaseHandler
from .utils import setup_logging, save_results_as_json, load_config, validate_url, Config
from .services import initialize_services, ServiceProvider, get_database_service, get_cookie_classifier_service, get_crawler_service

# Initialize services at package import
initialize_services()

# Exportiere die wichtigsten Funktionen und Klassen
__all__ = [
    # Main API
    'analyze_website',
    'analyze_website_async',
    'CookieAnalyzer',
    
    # Core components
    'crawl_website',
    'crawl_website_async',
    
    # Services
    'initialize_services',
    'ServiceProvider',
    'get_database_service',
    'get_cookie_classifier_service',
    'get_crawler_service',
    
    # Service implementations
    'CookieCrawler',
    'AsyncCookieCrawler',
    'CookieHandler',
    'DatabaseHandler',
    
    # Utility functions
    'setup_logging',
    'save_results_as_json',
    'load_config',
    'validate_url',
    'Config',
]
