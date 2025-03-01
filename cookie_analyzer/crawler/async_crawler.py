"""
Asynchroner Playwright-basierter Crawler für die Cookie-Analyse.
"""

import logging
import asyncio
import tldextract
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
from typing import Dict, List, Set, Tuple, Any, Optional

from .base import PageProtocol
from ..utils.url import validate_url

logger = logging.getLogger(__name__)

class AsyncCookieCrawler:
    """Eine Klasse zum asynchronen Crawlen von Webseiten und Extrahieren von Cookies und Local Storage."""
    
    def __init__(self, start_url: str, max_pages: int = 1, 
                respect_robots: bool = True, interact_with_consent: bool = True,
                headless: bool = True):
        """
        Initialisiert den asynchronen Cookie-Crawler.
        
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
        self.rp = None
    
    async def _load_robots_txt(self) -> Optional[RobotFileParser]:
        """
        Lädt und analysiert die robots.txt-Datei der Website asynchron.
        
        Returns:
            Optional[RobotFileParser]: Ein Parser für die robots.txt-Datei oder None bei Fehlern.
        """
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        try:
            # Asynchroner HTTP-Request für robots.txt
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                try:
                    page = await context.new_page()
                    response = await page.goto(base_url)
                    
                    if response and response.status == 200:
                        robots_txt = await page.content()
                        rp.parse(robots_txt.splitlines())
                        logger.info(f"robots.txt erfolgreich geladen: {base_url}")
                    else:
                        logger.warning(f"robots.txt nicht verfügbar: {base_url}")
                        return None
                finally:
                    await browser.close()
                    
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
    async def get_local_storage(page: PageProtocol) -> Dict[str, str]:
        """
        Liest den localStorage einer Seite asynchron aus.
        
        Args:
            page (PageProtocol): Die Seite, von der localStorage gelesen werden soll.
            
        Returns:
            Dict[str, str]: Der Inhalt des localStorage.
        """
        try:
            local_storage = await page.evaluate("() => { const ls = {}; for (let i = 0; i < localStorage.length; i++) { const key = localStorage.key(i); ls[key] = localStorage.getItem(key); } return ls; }")
            return local_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    @staticmethod
    async def get_session_storage(page: PageProtocol) -> Dict[str, str]:
        """
        Liest den sessionStorage einer Seite asynchron aus.
        
        Args:
            page (PageProtocol): Die Seite, von der sessionStorage gelesen werden soll.
            
        Returns:
            Dict[str, str]: Der Inhalt des sessionStorage.
        """
        try:
            session_storage = await page.evaluate("() => { const ss = {}; for (let i = 0; i < sessionStorage.length; i++) { const key = sessionStorage.key(i); ss[key] = sessionStorage.getItem(key); } return ss; }")
            return session_storage
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des sessionStorage: {e}")
            return {}
    
    async def handle_consent(self, page: Page) -> bool:
        """
        Behandelt Cookie-Consent-Banner auf der Seite asynchron.
        
        Args:
            page (Page): Die Playwright-Seite.
            
        Returns:
            bool: True, wenn mit einem Banner interagiert wurde, sonst False.
        """
        if not self.interact_with_consent:
            return False
        
        try:
            # Verwende JavaScript, um mit bekannten Consent-Managern zu interagieren
            result = await page.evaluate("""() => {
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
    
    async def scan_single_page_async(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Scannt asynchron nur die eingegebene Seite auf Cookies und Local Storage.
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: Cookies und Local Storage.
        """
        logger.info(f"Scanne asynchron die eingegebene Seite: {self.start_url}")
        cookies = []
        local_storage = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            try:
                page = await context.new_page()
                await page.goto(self.start_url)
                
                # Mit Cookie-Consent-Bannern interagieren
                if self.interact_with_consent:
                    await self.handle_consent(page)
                    # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                    await page.wait_for_timeout(500)
                
                # Cookies und Storage abrufen
                cookies = await context.cookies()
                storage_data = {
                    "localStorage": await self.get_local_storage(page),
                    "sessionStorage": await self.get_session_storage(page)
                }
                
                # Seite schließen
                await page.close()
            except Exception as e:
                logger.error(f"Fehler beim asynchronen Scannen der Seite {self.start_url}: {e}")
            finally:
                await context.close()
                await browser.close()
                
        return cookies, {self.start_url: storage_data}
    
    async def crawl_async(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Crawlt eine Website asynchron und sammelt Cookies und Storage-Daten.
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: Cookies und Storage-Daten.
        """
        # Lade robots.txt, falls erforderlich
        if self.respect_robots:
            self.rp = await self._load_robots_txt()
            
            if self.rp and not self.is_allowed_by_robots(self.start_url):
                logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
                return await self.scan_single_page_async()
        
        visited = set()
        to_visit = [self.start_url]
        all_cookies = []
        all_storage = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            
            while to_visit and len(visited) < self.max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                    
                if self.respect_robots and self.rp and not self.is_allowed_by_robots(url):
                    logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                    continue
                    
                logger.info(f"Scanne asynchron: {url}")
                visited.add(url)
                
                try:
                    page = await context.new_page()
                    await page.goto(url)
                    
                    # Mit Cookie-Consent-Bannern interagieren
                    if self.interact_with_consent:
                        await self.handle_consent(page)
                        # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                        await page.wait_for_timeout(500)
                    
                    # Cookies und Storage abrufen
                    cookies = await context.cookies()
                    all_cookies.extend(cookies)
                    
                    storage_data = {
                        "localStorage": await self.get_local_storage(page),
                        "sessionStorage": await self.get_session_storage(page)
                    }
                    all_storage[url] = storage_data
                    
                    # Links extrahieren
                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if not href or href.startswith("#") or href.startswith("javascript:"):
                            continue
                            
                        full_url = urljoin(url, href)
                        if self.is_internal_link(full_url) and full_url not in visited:
                            to_visit.append(full_url)
                    
                    await page.close()
                    
                except Exception as e:
                    logger.error(f"Fehler beim asynchronen Scannen von {url}: {e}")
                    
            await context.close()
            await browser.close()
        
        # Entferne Duplikate aus der Liste der Cookies
        unique_cookies = {}
        for cookie in all_cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', ''))
            if key not in unique_cookies:
                unique_cookies[key] = cookie
        
        return list(unique_cookies.values()), all_storage
    
    # Aliase für die Schnittstelle, die auch von CookieCrawler verwendet wird
    async def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Aliasname für crawl_async.
        """
        return await self.crawl_async()