"""
Wrapper-Funktionen für die einfache Nutzung des Cookie-Analyzers.
"""

import logging
import asyncio
from typing import Dict, List, Any, Tuple, Optional, Union

from ..core.analyzer import CookieAnalyzer
from ..utils.config import Config
from ..services.initializer import initialize_services
from ..services.crawler_factory import CrawlerType

logger = logging.getLogger(__name__)

def analyze_website(url: str, max_pages: Optional[int] = None, 
                   database_path: Optional[str] = None, 
                   use_async: bool = False,
                   use_selenium: bool = False,
                   interact_with_consent: bool = True,
                   headless: bool = True,
                   user_data_dir: Optional[str] = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
    """
    Analysiert eine Website und liefert klassifizierte Cookies zurück.
    
    Args:
        url (str): Die URL der Website, die analysiert werden soll.
        max_pages (Optional[int]): Maximale Anzahl von Seiten, die gecrawlt werden sollen.
        database_path (Optional[str]): Pfad zur Cookie-Datenbank (CSV-Datei).
        use_async (bool): Ob asynchrone Verarbeitung genutzt werden soll.
        use_selenium (bool): Ob Selenium für erweiterte Cookie-Erfassung genutzt werden soll.
        interact_with_consent (bool): Ob mit Cookie-Consent-Bannern interagiert werden soll.
        headless (bool): Ob der Browser im Headless-Modus ausgeführt werden soll.
        user_data_dir (Optional[str]): Pfad zum Chrome-Benutzerprofil (nur bei Selenium).
    
    Returns:
        Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]: 
            - Klassifizierte Cookies nach Kategorien.
            - Web Storage Daten und weitere Informationen.
    """
    # Stellen Sie sicher, dass die Services initialisiert sind
    initialize_services()
    
    # Standardwerte aus Config verwenden, wenn nicht angegeben
    if max_pages is None:
        max_pages = Config.DEFAULT_MAX_PAGES
    if database_path is None:
        database_path = Config.DEFAULT_DATABASE_PATH
    
    # Crawler-Typ bestimmen
    crawler_type = CrawlerType.PLAYWRIGHT
    if use_selenium:
        crawler_type = CrawlerType.SELENIUM
    elif use_async:
        crawler_type = CrawlerType.PLAYWRIGHT_ASYNC
    
    # Cookie-Analyzer erstellen und Website analysieren
    analyzer = CookieAnalyzer(
        crawler_type=crawler_type,
        interact_with_consent=interact_with_consent,
        headless=headless,
        user_data_dir=user_data_dir
    )
    
    # Die Standard-Methode für die normale Analyse verwenden
    classified_cookies, storage_data = analyzer.analyze_website(url, max_pages, database_path)
    return classified_cookies, storage_data

async def analyze_website_async(url: str, max_pages: Optional[int] = None, 
                              database_path: Optional[str] = None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]:
    """
    Analysiert eine Website asynchron und liefert klassifizierte Cookies zurück.
    
    Args:
        url (str): Die URL der Website, die analysiert werden soll.
        max_pages (Optional[int]): Maximale Anzahl von Seiten, die gecrawlt werden sollen.
        database_path (Optional[str]): Pfad zur Cookie-Datenbank (CSV-Datei).
    
    Returns:
        Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]: 
            - Klassifizierte Cookies nach Kategorien.
            - Web Storage Daten.
    """
    return analyze_website(url, max_pages, database_path, use_async=True)

def analyze_website_with_consent_stages(url: str, max_pages: Optional[int] = None, 
                   database_path: Optional[str] = None,
                   headless: bool = True,
                   user_data_dir: Optional[str] = None) -> Tuple[
                       Dict[str, List[Dict[str, Any]]], 
                       Dict[str, Dict[str, Any]], 
                       Dict[str, List[Dict[str, Any]]], 
                       Dict[str, Dict[str, Any]]]:
    """
    Analysiert eine Website mit zwei Phasen: vor und nach der Consent-Interaktion.
    
    Args:
        url (str): Die URL der Website, die analysiert werden soll.
        max_pages (Optional[int]): Maximale Anzahl von Seiten, die gecrawlt werden sollen.
        database_path (Optional[str]): Pfad zur Cookie-Datenbank (CSV-Datei).
        headless (bool): Ob der Browser im Headless-Modus ausgeführt werden soll.
        user_data_dir (Optional[str]): Pfad zum Chrome-Benutzerprofil.
    
    Returns:
        Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]], Dict[str, Dict[str, Any]]]: 
            - Klassifizierte Cookies vor Consent-Interaktion.
            - Web Storage Daten vor Consent-Interaktion.
            - Klassifizierte Cookies nach Consent-Interaktion.
            - Web Storage Daten nach Consent-Interaktion.
    """
    # Stellen Sie sicher, dass die Services initialisiert sind
    initialize_services()
    
    # Standardwerte aus Config verwenden, wenn nicht angegeben
    if max_pages is None:
        max_pages = Config.DEFAULT_MAX_PAGES
    if database_path is None:
        database_path = Config.DEFAULT_DATABASE_PATH
    
    # Cookie-Analyzer erstellen und Website mit dem zweistufigen Prozess analysieren
    analyzer = CookieAnalyzer(
        crawler_type=CrawlerType.SELENIUM,
        interact_with_consent=True,  # hier muss immer True sein für zweistufige Analyse
        headless=headless,
        user_data_dir=user_data_dir
    )
    
    return analyzer.analyze_website_with_consent_stages(url, max_pages, database_path)