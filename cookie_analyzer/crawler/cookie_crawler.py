"""
Playwright-basierter Crawler für die Cookie-Analyse.
"""

import logging
import tldextract
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page
from typing import Dict, List, Set, Tuple, Any, Optional

from .base import PageProtocol
from .consent_manager import ConsentManager
from ..utils.url import validate_url

logger = logging.getLogger(__name__)

class CookieCrawler:
    """Eine Klasse zum Crawlen von Webseiten und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, 
                respect_robots: bool = True, interact_with_consent: bool = True,
                headless: bool = True):
        """
        Initialisiert den Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
            interact_with_consent (bool): Ob mit Cookie-Consent-Bannern interagiert werden soll.
            headless (bool): Ob der Browser im Headless-Modus laufen soll.
        """
        self.start_url = validate_url(start_url)
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.interact_with_consent = interact_with_consent
        self.headless = headless
        self.rp = self._load_robots_txt() if respect_robots else None
        
    def _load_robots_txt(self) -> Optional[RobotFileParser]:
        """
        Lädt und analysiert die robots.txt-Datei der Website.
        
        Returns:
            Optional[RobotFileParser]: Ein Parser für die robots.txt-Datei oder None bei Fehlern.
        """
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(base_url)
            rp.read()
            logger.info(f"robots.txt erfolgreich geladen: {base_url}")
            return rp
        except Exception as e:
            logger.warning(f"Fehler beim Laden der robots.txt: {e}")
            return None
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Prüft, ob eine URL laut robots.txt gecrawlt werden darf.
        
        Args:
            url (str): Die zu prüfende URL.
            
        Returns:
            bool: True, wenn das Crawlen erlaubt ist, sonst False.
        """
        if not self.respect_robots or self.rp is None:
            return True
        return self.rp.can_fetch("*", url)
    
    def is_internal_link(self, test_url: str) -> bool:
        """
        Prüft, ob ein Link intern ist.
        
        Args:
            test_url (str): Die zu prüfende URL.
            
        Returns:
            bool: True, wenn es ein interner Link ist, sonst False.
        """
        base_domain = tldextract.extract(self.start_url).registered_domain
        test_domain = tldextract.extract(test_url).registered_domain
        return base_domain == test_domain
    
    @staticmethod
    def get_local_storage(page: PageProtocol) -> Dict[str, str]:
        """
        Liest den localStorage einer Seite aus.
        
        Args:
            page (PageProtocol): Die Seite, von der localStorage gelesen werden soll.
            
        Returns:
            Dict[str, str]: Der Inhalt des localStorage.
        """
        try:
            local_storage = page.evaluate("() => { const ls = {}; for (let i = 0; i < localStorage.length; i++) { const key = localStorage.key(i); ls[key] = localStorage.getItem(key); } return ls; }")
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    @staticmethod
    def get_session_storage(page: PageProtocol) -> Dict[str, str]:
        """
        Liest den sessionStorage einer Seite aus.
        
        Args:
            page (PageProtocol): Die Seite, von der sessionStorage gelesen werden soll.
            
        Returns:
            Dict[str, str]: Der Inhalt des sessionStorage.
        """
        try:
            session_storage = page.evaluate("() => { const ss = {}; for (let i = 0; i < sessionStorage.length; i++) { const key = sessionStorage.key(i); ss[key] = sessionStorage.getItem(key); } return ss; }")
            return session_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des sessionStorage: {e}")
            return {}
    
    def handle_consent(self, page: Page) -> bool:
        """
        Behandelt Cookie-Consent-Banner auf der Seite.
        
        Args:
            page (Page): Die Playwright-Seite.
            
        Returns:
            bool: True, wenn mit einem Banner interagiert wurde, sonst False.
        """
        if not self.interact_with_consent:
            return False
        
        try:
            # Verwende JavaScript, um mit bekannten Consent-Managern zu interagieren
            result = page.evaluate("""() => {
                // OneTrust
                if (document.getElementById('onetrust-reject-all-handler')) {
                    document.getElementById('onetrust-reject-all-handler').click();
                    return true;
                }
                
                // Cookiebot
                if (document.getElementById('CybotCookiebotDialogBodyButtonDecline')) {
                    document.getElementById('CybotCookiebotDialogBodyButtonDecline').click();
                    return true;
                }
                
                // Andere generische Selektoren für "Ablehnen"-Buttons
                const rejectSelectors = [
                    'button[data-cui-consent-action="decline"]',
                    'button[aria-label="Ablehnen"]',
                    'button[aria-label="Deny"]',
                    'button[aria-label="Reject"]'
                ];
                
                for (const selector of rejectSelectors) {
                    const button = document.querySelector(selector);
                    if (button) {
                        button.click();
                        return true;
                    }
                }
                
                return false;
            }""")
            
            if result:
                logger.info("Mit Cookie-Consent-Banner interagiert")
            else:
                logger.debug("Kein bekanntes Cookie-Consent-Banner gefunden")
                
            return result
        except Exception as e:
            logger.error(f"Fehler bei der Interaktion mit dem Cookie-Consent-Banner: {e}")
            return False
    
    def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Scannt nur die eingegebene Seite auf Cookies und Local Storage.
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: Cookies und Local Storage.
        """
        logger.info(f"Scanne nur die eingegebene Seite: {self.start_url}")
        cookies = []
        local_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            try:
                page = context.new_page()
                page.goto(self.start_url)
                
                # Mit Cookie-Consent-Bannern interagieren
                if self.interact_with_consent:
                    self.handle_consent(page)
                    # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                    page.wait_for_timeout(500)
                
                # Cookies und Storage abrufen
                cookies = context.cookies()
                storage_data = {
                    "localStorage": self.get_local_storage(page),
                    "sessionStorage": self.get_session_storage(page)
                }
                
                # Seite schließen
                page.close()
            except Exception as e:
                logger.error(f"Fehler beim Scannen der Seite {self.start_url}: {e}")
            finally:
                context.close()
                browser.close()
                
        return cookies, {self.start_url: storage_data}
    
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Crawlt eine Website und sammelt Cookies und Storage-Daten.
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: Cookies und Storage-Daten.
        """
        if self.respect_robots and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            return self.scan_single_page()
        
        visited = set()
        to_visit = [self.start_url]
        all_cookies = []
        all_storage = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
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
                    page = context.new_page()
                    page.goto(url)
                    
                    # Mit Cookie-Consent-Bannern interagieren
                    if self.interact_with_consent:
                        self.handle_consent(page)
                        # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                        page.wait_for_timeout(500)
                    
                    # Cookies und Storage abrufen
                    cookies = context.cookies()
                    all_cookies.extend(cookies)
                    
                    storage_data = {
                        "localStorage": self.get_local_storage(page),
                        "sessionStorage": self.get_session_storage(page)
                    }
                    all_storage[url] = storage_data
                    
                    # Links extrahieren
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if not href or href.startswith("#") or href.startswith("javascript:"):
                            continue
                            
                        full_url = urljoin(url, href)
                        if self.is_internal_link(full_url) and full_url not in visited:
                            to_visit.append(full_url)
                    
                    page.close()
                    
                except Exception as e:
                    logger.error(f"Fehler beim Scannen von {url}: {e}")
                    
            context.close()
            browser.close()
        
        # Entferne Duplikate aus der Liste der Cookies
        unique_cookies = {}
        for cookie in all_cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', ''))
            if key not in unique_cookies:
                unique_cookies[key] = cookie
        
        return list(unique_cookies.values()), all_storage