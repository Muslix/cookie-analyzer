"""
Services module for dependency injection pattern implementation.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Protocol, Optional, runtime_checkable, Type, TypeVar, Generic

logger = logging.getLogger(__name__)

T = TypeVar('T')

@runtime_checkable
class CookieDatabaseService(Protocol):
    """Interface for cookie database interactions."""
    
    def load_database(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Loads the cookie database."""
        ...
    
    def find_cookie_info(self, cookie_name: str, cookie_database: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Finds information about a cookie in the database."""
        ...
    
    def update_database(self, output_path: Optional[str] = None, url: Optional[str] = None) -> bool:
        """Updates the cookie database from a source."""
        ...

@runtime_checkable
class CookieClassifierService(Protocol):
    """Interface for cookie classification."""
    
    def classify_cookies(self, cookies: List[Dict[str, Any]], 
                        cookie_database: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Classifies cookies according to their purpose."""
        ...
    
    def remove_duplicates(self, cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicate cookies from a list."""
        ...
    
    def get_consent_categories(self, cookies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyzes cookies and returns the number of cookies per consent category."""
        ...
    
    def identify_fingerprinting(self, cookies: List[Dict[str, Any]], 
                              local_storage: Dict[str, Dict[str, str]]) -> Dict[str, bool]:
        """Identifies potential fingerprinting techniques."""
        ...

class CrawlerService(ABC, Generic[T]):
    """Base abstract class for all crawler services."""
    
    @abstractmethod
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Crawls a website and collects cookies."""
        pass

class CrawlerType:
    """Enum-like class for crawler types."""
    PLAYWRIGHT = "playwright"
    PLAYWRIGHT_ASYNC = "playwright_async"
    SELENIUM = "selenium"


class ServiceProvider:
    """A service provider container for dependency injection."""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_type: str, implementation) -> None:
        """Registers a service implementation."""
        cls._instances[service_type] = implementation
    
    @classmethod
    def get(cls, service_type: str):
        """Gets a service implementation."""
        if service_type not in cls._instances:
            raise KeyError(f"Service {service_type} not registered")
        return cls._instances[service_type]
    
    @classmethod
    def has(cls, service_type: str) -> bool:
        """Checks if a service is registered."""
        return service_type in cls._instances


def initialize_services() -> None:
    """Initializes all default services."""
    from .database import DatabaseHandler
    from .cookie_handler import CookieHandler
    
    # Register default implementations
    ServiceProvider.register("database", DatabaseHandler())
    ServiceProvider.register("cookie_classifier", CookieHandler())
    
    logger.info("Services initialized with default implementations")


def get_database_service() -> CookieDatabaseService:
    """Gets the currently registered database service."""
    return ServiceProvider.get("database")


def get_cookie_classifier_service() -> CookieClassifierService:
    """Gets the currently registered cookie classifier service."""
    return ServiceProvider.get("cookie_classifier")


def get_crawler_service(start_url: str, max_pages: int = 1, 
                       respect_robots: bool = True, crawler_type: str = CrawlerType.PLAYWRIGHT,
                       interact_with_consent: bool = True, headless: bool = True) -> CrawlerService:
    """
    Creates and returns an appropriate crawler service.
    
    Args:
        start_url: The URL to start crawling from
        max_pages: Maximum number of pages to crawl
        respect_robots: Whether to respect robots.txt
        crawler_type: Type of crawler to use (playwright, playwright_async, selenium)
        interact_with_consent: Whether to interact with cookie consent banners (only for selenium)
        headless: Whether to use headless mode (only for selenium)
        
    Returns:
        A crawler service implementation
    """
    from .crawler import CookieCrawler, AsyncCookieCrawler, SeleniumCookieCrawler
    
    if crawler_type == CrawlerType.SELENIUM:
        return SeleniumCookieCrawler(
            start_url, 
            max_pages, 
            respect_robots, 
            interact_with_consent, 
            headless
        )
    elif crawler_type == CrawlerType.PLAYWRIGHT_ASYNC:
        return AsyncCookieCrawler(start_url, max_pages, respect_robots)
    else:  # Default to PLAYWRIGHT
        return CookieCrawler(start_url, max_pages, respect_robots)