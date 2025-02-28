from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import tldextract
import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

class CookieCrawler:
    """Eine Klasse zum Crawlen von Webseiten und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, respect_robots: bool = True):
        """
        Initialisiert den Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.rp = self._load_robots_txt() if respect_robots else None
        
    def _load_robots_txt(self) -> RobotFileParser:
        """Lädt und analysiert die robots.txt-Datei der Website."""
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(base_url)
            rp.read()
            logger.info(f"robots.txt erfolgreich geladen: {base_url}")
        except Exception as e:
            logger.warning(f"Fehler beim Laden der robots.txt: {e}")
        return rp
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """Prüft, ob eine URL laut robots.txt gecrawlt werden darf."""
        if not self.respect_robots or self.rp is None:
            return True
        return self.rp.can_fetch("*", url)
    
    def is_internal_link(self, test_url: str) -> bool:
        """Prüft, ob ein Link intern ist."""
        base_domain = tldextract.extract(self.start_url).registered_domain
        test_domain = tldextract.extract(test_url).registered_domain
        return base_domain == test_domain
    
    @staticmethod
    def get_local_storage(page) -> Dict[str, str]:
        """Liest den localStorage einer Seite aus."""
        try:
            local_storage = page.evaluate("() => { return window.localStorage; }")
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Scannt nur die eingegebene Seite auf Cookies und Local Storage."""
        logger.info(f"Scanne nur die eingegebene Seite: {self.start_url}")
        cookies = []
        local_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            try:
                with context.new_page() as page:
                    page.goto(self.start_url)
                    cookies = context.cookies()
                    local_storage = self.get_local_storage(page)
            except Exception as e:
                logger.error(f"Fehler beim Scannen der Seite {self.start_url}: {e}")
            finally:
                browser.close()
                
        return cookies, local_storage
    
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
        """Crawlt eine Website und sammelt Cookies."""
        if self.respect_robots and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            cookies, local_storage = self.scan_single_page()
            return cookies, {self.start_url: local_storage}
        
        visited = set()
        to_visit = [self.start_url]
        all_cookies = []
        all_local_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            while to_visit and len(visited) < self.max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                    
                if self.respect_robots and not self.is_allowed_by_robots(url):
                    logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                    continue
                    
                logger.info(f"Scanne: {url}")
                visited.add(url)
                
                try:
                    with context.new_page() as page:
                        page.goto(url)
                        
                        cookies = context.cookies()
                        all_cookies.extend(cookies)
                        
                        local_storage = self.get_local_storage(page)
                        all_local_storage[url] = local_storage
                        
                        html = page.evaluate("() => document.documentElement.outerHTML")
                        soup = BeautifulSoup(html, "html.parser")
                        for link in soup.find_all("a", href=True):
                            full_url = urljoin(url, link["href"])
                            if self.is_internal_link(full_url):
                                to_visit.append(full_url)
                except Exception as e:
                    logger.error(f"Fehler beim Scannen von {url}: {e}")
            
            browser.close()
        
        return all_cookies, all_local_storage