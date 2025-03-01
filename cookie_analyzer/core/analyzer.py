"""
Kernfunktionalität des Cookie-Analyzers.
"""

import logging
import asyncio
from typing import Dict, List, Any, Tuple, Optional

from ..services.crawler_factory import CrawlerType, get_crawler_service
from ..services.initializer import get_database_service, get_cookie_classifier_service
from ..crawler.cookie_crawler import CookieCrawler
from ..crawler.async_crawler import AsyncCookieCrawler
from ..utils.config import Config

logger = logging.getLogger(__name__)

class CookieAnalyzer:
    """
    Hauptklasse zur Analyse von Cookies auf Websites.
    """
    
    def __init__(self, crawler_type: str = CrawlerType.PLAYWRIGHT, 
                 interact_with_consent: bool = True, headless: bool = True):
        """
        Initialisiert den CookieAnalyzer.
        
        Args:
            crawler_type: Art des zu verwendenden Crawlers (PLAYWRIGHT, PLAYWRIGHT_ASYNC oder SELENIUM)
            interact_with_consent: Ob mit Cookie-Consent-Bannern interagiert werden soll
            headless: Ob der Browser im Headless-Modus laufen soll
        """
        self.crawler_type = crawler_type
        self.interact_with_consent = interact_with_consent
        self.headless = headless
    
    def analyze_website(self, url: str, max_pages: int = 1, 
                        database_path: Optional[str] = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
        """
        Analysiert eine Website und klassifiziert die gefundenen Cookies.
        
        Args:
            url: URL der zu analysierenden Website
            max_pages: Maximale Anzahl der zu crawlenden Seiten
            database_path: Pfad zur Cookie-Datenbank
            
        Returns:
            Tuple mit klassifizierten Cookies und Web Storage Daten
        """
        # Services abrufen
        database_service = get_database_service()
        cookie_classifier = get_cookie_classifier_service()
        
        # Datenbank laden
        if database_path is None:
            database_path = Config.DEFAULT_DATABASE_PATH
        
        cookie_database = database_service.load_database(database_path)
        logger.info(f"{len(cookie_database)} Cookie-Einträge aus der Datenbank geladen")
        
        # Async Crawler verwenden wenn ausgewählt
        if self.crawler_type == CrawlerType.PLAYWRIGHT_ASYNC:
            return asyncio.run(crawl_website_async(
                url, 
                max_pages, 
                cookie_database
            ))
        
        # Website crawlen
        return crawl_website(
            url,
            max_pages,
            cookie_database,
            self.crawler_type,
            self.interact_with_consent,
            self.headless
        )

def crawl_website(url: str, max_pages: int, cookie_database: List[Dict[str, Any]], 
                 crawler_type: str = CrawlerType.PLAYWRIGHT,
                 interact_with_consent: bool = True, 
                 headless: bool = True) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
    """
    Crawlt eine Website und klassifiziert die gefundenen Cookies.
    
    Args:
        url: Die zu crawlende URL
        max_pages: Maximale Anzahl der zu crawlenden Seiten
        cookie_database: Die Cookie-Datenbank
        crawler_type: Art des zu verwendenden Crawlers
        interact_with_consent: Ob mit Cookie-Consent-Bannern interagiert werden soll
        headless: Ob der Browser im Headless-Modus laufen soll
        
    Returns:
        Tuple mit klassifizierten Cookies und Web Storage Daten
    """
    # Services abrufen
    cookie_classifier = get_cookie_classifier_service()
    
    # Crawler erstellen
    crawler = get_crawler_service(
        start_url=url,
        max_pages=max_pages,
        crawler_type=crawler_type,
        interact_with_consent=interact_with_consent,
        headless=headless
    )
    
    # Website crawlen
    logger.info(f"Starte Crawling von {url} mit {crawler.__class__.__name__}")
    cookies, local_storage = crawler.crawl()
    
    # Doppelte Cookies entfernen
    cookies = cookie_classifier.remove_duplicates(cookies)
    logger.info(f"Gefundene Cookies: {len(cookies)}")
    
    # Cookies klassifizieren
    classified_cookies = cookie_classifier.classify_cookies(cookies, cookie_database)
    
    return classified_cookies, local_storage

async def crawl_website_async(url: str, max_pages: int, 
                            cookie_database: List[Dict[str, Any]]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
    """
    Crawlt eine Website asynchron und klassifiziert die gefundenen Cookies.
    
    Args:
        url: Die zu crawlende URL
        max_pages: Maximale Anzahl der zu crawlenden Seiten
        cookie_database: Die Cookie-Datenbank
        
    Returns:
        Tuple mit klassifizierten Cookies und Web Storage Daten
    """
    # Services abrufen
    cookie_classifier = get_cookie_classifier_service()
    
    # Crawler erstellen
    crawler = get_crawler_service(
        start_url=url,
        max_pages=max_pages,
        crawler_type=CrawlerType.PLAYWRIGHT_ASYNC
    )
    
    # Website crawlen
    logger.info(f"Starte asynchrones Crawling von {url}")
    cookies, local_storage = await crawler.crawl_async()
    
    # Doppelte Cookies entfernen
    cookies = cookie_classifier.remove_duplicates(cookies)
    logger.info(f"Gefundene Cookies: {len(cookies)}")
    
    # Cookies klassifizieren
    classified_cookies = cookie_classifier.classify_cookies(cookies, cookie_database)
    
    return classified_cookies, local_storage