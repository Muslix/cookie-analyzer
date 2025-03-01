"""
Factory für die Erstellung der verschiedenen Crawler-Typen.
"""

import logging
from typing import Dict, List, Any, Tuple

from .service_interfaces import CrawlerService

logger = logging.getLogger(__name__)

class CrawlerType:
    """Enum-like class for crawler types."""
    PLAYWRIGHT = "playwright"
    PLAYWRIGHT_ASYNC = "playwright_async"
    SELENIUM = "selenium"

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
    from ..crawler.cookie_crawler import CookieCrawler
    from ..crawler.async_crawler import AsyncCookieCrawler
    from ..crawler.selenium_crawler import SeleniumCookieCrawler
    
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