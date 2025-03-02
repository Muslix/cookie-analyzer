"""
Factory für die Erstellung von Crawler-Objekten.
"""

import logging
from typing import Dict, List, Any, Optional
from ..services.service_interfaces import CrawlerService
from ..crawler.cookie_crawler import CookieCrawler
from ..crawler.async_crawler import AsyncCookieCrawler
from ..crawler.selenium_crawler import SeleniumCookieCrawler

logger = logging.getLogger(__name__)

class CrawlerType:
    """Aufzählung der verfügbaren Crawler-Typen."""
    PLAYWRIGHT = "playwright"
    PLAYWRIGHT_ASYNC = "playwright_async"
    SELENIUM = "selenium"

def get_crawler_service(start_url: str, max_pages: int = 1, 
                       respect_robots: bool = True, crawler_type: str = CrawlerType.PLAYWRIGHT,
                       interact_with_consent: bool = True, headless: bool = True,
                       user_data_dir: Optional[str] = None) -> CrawlerService:
    """
    Factory-Methode zum Erstellen eines Crawler-Services.
    
    Args:
        start_url (str): Die Start-URL für das Crawling
        max_pages (int): Maximale Anzahl der zu crawlenden Seiten
        respect_robots (bool): Ob robots.txt respektiert werden soll
        crawler_type (str): Welcher Crawler-Typ verwendet werden soll
        interact_with_consent (bool): Ob mit Cookie-Consent-Bannern interagiert werden soll
        headless (bool): Ob der Browser im Headless-Modus ausgeführt werden soll
        user_data_dir (Optional[str]): Pfad zum Chrome-Benutzerprofil (nur bei Selenium)
        
    Returns:
        CrawlerService: Der konfigurierte Crawler-Service.
    """
    logger.debug(f"Erstelle Crawler-Service vom Typ {crawler_type} für {start_url}")
    
    if crawler_type == CrawlerType.SELENIUM:
        return SeleniumCookieCrawler(
            start_url, 
            max_pages, 
            respect_robots, 
            interact_with_consent, 
            headless,
            user_data_dir=user_data_dir
        )
    elif crawler_type == CrawlerType.PLAYWRIGHT_ASYNC:
        return AsyncCookieCrawler(
            start_url, 
            max_pages, 
            respect_robots,
            interact_with_consent,
            headless
        )
    else:  # Default to PLAYWRIGHT
        return CookieCrawler(
            start_url, 
            max_pages, 
            respect_robots,
            interact_with_consent,
            headless
        )