from .crawler import CookieCrawler
from .cookie_handler import remove_duplicate_cookies
import logging
from typing import Dict, List, Tuple, Any

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

def crawl_website(start_url: str, max_pages: int = 1) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
    """
    Crawlt eine Website und sammelt Cookies.
    
    Args:
        start_url (str): Die URL der Website, die gecrawlt werden soll.
        max_pages (int): Maximale Anzahl zu crawlender Seiten.
        
    Returns:
        Tuple: Liste von Cookies, Dictionary mit Local Storage-Daten nach URLs.
    """
    crawler = CookieCrawler(start_url, max_pages=max_pages)
    all_cookies, all_local_storage = crawler.crawl()
    
    # Doppelte Cookies entfernen
    all_cookies = remove_duplicate_cookies(all_cookies)
    
    return all_cookies, all_local_storage
