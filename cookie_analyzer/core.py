import logging
import asyncio
from typing import Dict, List, Tuple, Any, Optional, Union

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cookie_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CookieAnalyzer:
    """Main class for cookie analysis operations."""
    
    def __init__(self, crawler_type: str = "playwright", 
                interact_with_consent: bool = True,
                headless: bool = True):
        """
        Initialisiert den Cookie Analyzer.
        
        Args:
            crawler_type: Art des zu verwendenden Crawlers ("playwright", "playwright_async" oder "selenium")
            interact_with_consent: Ob mit Cookie-Consent-Bannern interagiert werden soll (nur für Selenium)
            headless: Ob der Browser im Headless-Modus ausgeführt werden soll (nur für Selenium)
        """
        self.crawler_type = crawler_type
        self.interact_with_consent = interact_with_consent
        self.headless = headless
    
    def crawl_website(self, start_url: str, max_pages: int = 1, 
                     respect_robots: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Crawlt eine Website und sammelt Cookies.
        
        Args:
            start_url: Die URL, von der aus das Crawling starten soll
            max_pages: Maximale Anzahl der zu crawlenden Seiten
            respect_robots: Ob robots.txt beachtet werden soll
            
        Returns:
            Tuple mit Liste von Cookies und Dictionary mit Web Storage-Daten
        """
        from .services import get_crawler_service
        
        crawler = get_crawler_service(
            start_url, 
            max_pages, 
            respect_robots, 
            crawler_type=self.crawler_type,
            interact_with_consent=self.interact_with_consent,
            headless=self.headless
        )
        
        if self.crawler_type == "playwright_async":
            # Run async crawler in an event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(crawler.crawl_async())
        else:
            return crawler.crawl()

    def analyze_website(self, url: str, max_pages: int = 1, 
                       database_path: Optional[str] = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
        """
        Führt eine vollständige Analyse einer Website durch.
        
        Args:
            url: Die URL der Website
            max_pages: Maximale Anzahl der zu crawlenden Seiten
            database_path: Pfad zur Cookie-Datenbank
            
        Returns:
            Tuple mit klassifizierten Cookies und Web Storage-Daten
        """
        from .services import get_database_service, get_cookie_classifier_service
        
        # Services abrufen
        db_service = get_database_service()
        cookie_classifier = get_cookie_classifier_service()
        
        # Cookie-Datenbank laden
        cookie_database = db_service.load_database(database_path)
        
        # Website crawlen
        raw_cookies, storage_data = self.crawl_website(url, max_pages)
        
        # Duplikate entfernen und Cookies klassifizieren
        unique_cookies = cookie_classifier.remove_duplicates(raw_cookies)
        classified_cookies = cookie_classifier.classify_cookies(unique_cookies, cookie_database)
        
        return classified_cookies, storage_data


# Legacy functions for backward compatibility
def crawl_website(start_url: str, max_pages: int = 1, 
                 respect_robots: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
    """
    Legacy-Funktion zum Crawlen einer Website.
    
    Args:
        start_url: Die URL, von der aus das Crawling starten soll
        max_pages: Maximale Anzahl der zu crawlenden Seiten
        respect_robots: Ob robots.txt beachtet werden soll
        
    Returns:
        Tuple mit Liste von Cookies und Dictionary mit Local-Storage-Daten
    """
    analyzer = CookieAnalyzer()
    return analyzer.crawl_website(start_url, max_pages, respect_robots)


async def crawl_website_async(start_url: str, max_pages: int = 1, 
                            respect_robots: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
    """
    Async-Funktion zum Crawlen einer Website.
    
    Args:
        start_url: Die URL, von der aus das Crawling starten soll
        max_pages: Maximale Anzahl der zu crawlenden Seiten
        respect_robots: Ob robots.txt beachtet werden soll
        
    Returns:
        Tuple mit Liste von Cookies und Dictionary mit Local-Storage-Daten
    """
    from .services import get_crawler_service, CrawlerType
    
    crawler = get_crawler_service(start_url, max_pages, respect_robots, crawler_type=CrawlerType.PLAYWRIGHT_ASYNC)
    return await crawler.crawl_async()
