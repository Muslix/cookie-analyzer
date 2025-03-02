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
                 interact_with_consent: bool = True, headless: bool = True,
                 user_data_dir: Optional[str] = None):
        """
        Initialisiert den Cookie-Analyzer.
        
        Args:
            crawler_type: Art des zu verwendenden Crawlers (PLAYWRIGHT, PLAYWRIGHT_ASYNC, SELENIUM)
            interact_with_consent: Ob mit Cookie-Consent-Bannern interagiert werden soll
            headless: Ob der Browser im Headless-Modus laufen soll
            user_data_dir: Pfad zum Chrome-Benutzerprofil (nur bei Selenium)
        """
        self.crawler_type = crawler_type
        self.interact_with_consent = interact_with_consent
        self.headless = headless
        self.user_data_dir = user_data_dir
        
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
            self.headless,
            self.user_data_dir
        )
        
    def analyze_website_with_consent_stages(self, url: str, max_pages: int = 1, 
                        database_path: Optional[str] = None) -> Tuple[
                            Dict[str, List[Dict[str, Any]]], 
                            Dict[str, Dict[str, Any]], 
                            Dict[str, List[Dict[str, Any]]], 
                            Dict[str, Dict[str, Any]]
                        ]:
        """
        Analysiert eine Website in zwei Phasen: vor und nach der Consent-Interaktion.
        Diese Methode arbeitet nur mit dem Selenium-Crawler.
        
        Args:
            url: URL der zu analysierenden Website
            max_pages: Maximale Anzahl der zu crawlenden Seiten
            database_path: Pfad zur Cookie-Datenbank
            
        Returns:
            Tuple mit klassifizierten Cookies (vor Consent),
            Web Storage Daten (vor Consent),
            klassifizierten Cookies (nach Consent),
            Web Storage Daten (nach Consent)
        """
        # Services abrufen
        database_service = get_database_service()
        cookie_classifier = get_cookie_classifier_service()
        
        # Datenbank laden
        if database_path is None:
            database_path = Config.DEFAULT_DATABASE_PATH
        
        cookie_database = database_service.load_database(database_path)
        logger.info(f"{len(cookie_database)} Cookie-Einträge aus der Datenbank geladen")
        
        # Prüfen ob Selenium verwendet wird
        if self.crawler_type != CrawlerType.SELENIUM:
            logger.warning("Zweistufige Cookie-Analyse ist nur mit dem Selenium-Crawler möglich. "
                        "Wechsle automatisch zu Selenium.")
        
        # Crawler erstellen
        crawler = get_crawler_service(
            start_url=url,
            max_pages=max_pages,
            crawler_type=CrawlerType.SELENIUM,  # Hier immer Selenium verwenden
            interact_with_consent=True,  # Hier muss True sein für zweistufige Analyse
            headless=self.headless,
            user_data_dir=self.user_data_dir
        )
        
        # Website crawlen mit zweistufigem Prozess
        logger.info(f"Starte zweistufiges Crawling von {url} mit {crawler.__class__.__name__}")
        pre_consent_cookies, pre_consent_storage, post_consent_cookies, post_consent_storage = crawler.scan_single_page()
        
        # Doppelte Cookies entfernen
        pre_consent_cookies = cookie_classifier.remove_duplicates(pre_consent_cookies)
        post_consent_cookies = cookie_classifier.remove_duplicates(post_consent_cookies)
        
        logger.info(f"Gefundene Cookies vor Consent: {len(pre_consent_cookies)}")
        logger.info(f"Gefundene Cookies nach Consent: {len(post_consent_cookies)}")
        
        # Cookies klassifizieren
        pre_classified_cookies = cookie_classifier.classify_cookies(pre_consent_cookies, cookie_database)
        post_classified_cookies = cookie_classifier.classify_cookies(post_consent_cookies, cookie_database)
        
        # In pre_consent_storage und post_consent_storage noch eine "phase" Eigenschaft hinzufügen
        for url, storage_data in pre_consent_storage.items():
            storage_data["phase"] = "pre-consent"
        
        for url, storage_data in post_consent_storage.items():
            storage_data["phase"] = "post-consent"
        
        # Identifiziere neu hinzugekommene Cookies nach Consent
        new_cookies_after_consent = self._identify_new_cookies(pre_consent_cookies, post_consent_cookies)
        if len(new_cookies_after_consent) > 0:
            logger.info(f"Nach der Consent-Interaktion wurden {len(new_cookies_after_consent)} neue Cookies gefunden")
            
            # Füge eine neue Kategorie für Cookies hinzu, die erst nach Consent erscheinen
            post_classified_cookies["Nach Consent gesetzt"] = cookie_classifier.classify_cookies(
                new_cookies_after_consent, cookie_database
            ).get("Unbekannt", [])  # Die neu gesetzten Cookies in eine eigene Kategorie einordnen
        
        return pre_classified_cookies, pre_consent_storage, post_classified_cookies, post_consent_storage
    
    def _identify_new_cookies(self, pre_cookies: List[Dict[str, Any]], post_cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifiziert Cookies, die erst nach der Consent-Interaktion hinzugekommen sind.
        
        Args:
            pre_cookies: Cookies vor Consent-Interaktion
            post_cookies: Cookies nach Consent-Interaktion
            
        Returns:
            Liste der neu hinzugekommenen Cookies
        """
        # Erstelle einen Set von Tupeln mit eindeutigen Cookie-Identifikatoren vor der Interaktion
        pre_cookie_keys = {(cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', '/')) 
                          for cookie in pre_cookies}
        
        # Finde Cookies, die nach der Interaktion neu sind
        new_cookies = []
        for cookie in post_cookies:
            cookie_key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', '/'))
            if cookie_key not in pre_cookie_keys:
                cookie['is_new_after_consent'] = True
                new_cookies.append(cookie)
                
        return new_cookies

def crawl_website(url: str, max_pages: int, cookie_database: List[Dict[str, Any]], 
                 crawler_type: str = CrawlerType.PLAYWRIGHT,
                 interact_with_consent: bool = True, 
                 headless: bool = True,
                 user_data_dir: Optional[str] = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
    """
    Crawlt eine Website und klassifiziert die gefundenen Cookies.
    
    Args:
        url: Die zu crawlende URL
        max_pages: Maximale Anzahl der zu crawlenden Seiten
        cookie_database: Die Cookie-Datenbank
        crawler_type: Art des zu verwendenden Crawlers
        interact_with_consent: Ob mit Cookie-Consent-Bannern interagiert werden soll
        headless: Ob der Browser im Headless-Modus laufen soll
        user_data_dir: Pfad zum Chrome-Benutzerprofil (nur bei Selenium)
        
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
        headless=headless,
        user_data_dir=user_data_dir
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