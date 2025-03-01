"""
Selenium-basierter Crawler für erweiterte Cookie-Analyse und Consent-Banner-Interaktion.
"""

import logging
import time
import tldextract
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Set, Tuple, Any, Optional

from .consent_manager import ConsentManager
from ..utils.url import validate_url

logger = logging.getLogger(__name__)

class SeleniumCookieCrawler:
    """Eine Klasse zum Crawlen von Webseiten mit Selenium und erweiterten Cookie-Funktionen."""
    
    def __init__(self, start_url: str, max_pages: int = 1, 
                respect_robots: bool = True, interact_with_consent: bool = True,
                headless: bool = True, webdriver_path: Optional[str] = None):
        """
        Initialisiert den Selenium-basierten Cookie-Crawler.
        
        Args:
            start_url (str): Die Start-URL für das Crawling.
            max_pages (int): Maximale Anzahl der zu crawlenden Seiten.
            respect_robots (bool): Ob robots.txt respektiert werden soll.
            interact_with_consent (bool): Ob mit Cookie-Consent-Bannern interagiert werden soll.
            headless (bool): Ob der Browser im Headless-Modus laufen soll.
            webdriver_path (Optional[str]): Pfad zum Chromedriver.
        """
        self.start_url = validate_url(start_url)
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.interact_with_consent = interact_with_consent
        self.headless = headless
        self.webdriver_path = webdriver_path
        self.rp = self._load_robots_txt() if respect_robots else None
        self.consent_manager = ConsentManager()
        
    def _load_robots_txt(self) -> Optional[RobotFileParser]:
        """
        Lädt und analysiert die robots.txt-Datei der Website.
        
        Returns:
            Optional[RobotFileParser]: Ein Parser für die robots.txt-Datei oder None bei Fehlern.
        """
        parsed_url = tldextract.extract(self.start_url)
        base_url = f"https://{parsed_url.registered_domain}/robots.txt"
        rp = RobotFileParser()
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            # Chromedriver konfigurieren
            if self.webdriver_path:
                service = Service(self.webdriver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            driver.get(base_url)
            robots_txt = driver.page_source
            
            if "404" not in driver.title and "not found" not in robots_txt.lower():
                rp.parse(robots_txt.splitlines())
                logger.info(f"robots.txt erfolgreich geladen: {base_url}")
            else:
                logger.warning(f"robots.txt nicht verfügbar: {base_url}")
                rp = None
                
            driver.quit()
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
    
    def get_local_storage(self, driver: webdriver.Chrome) -> Dict[str, str]:
        """
        Liest den localStorage eines Browsers aus.
        
        Args:
            driver (webdriver.Chrome): Der Selenium WebDriver.
            
        Returns:
            Dict[str, str]: Der Inhalt des localStorage.
        """
        try:
            local_storage = driver.execute_script("""
                var ls = {};
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    ls[key] = localStorage.getItem(key);
                }
                return ls;
            """)
            return local_storage or {}
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des localStorage: {e}")
            return {}
    
    def get_session_storage(self, driver: webdriver.Chrome) -> Dict[str, str]:
        """
        Liest den sessionStorage eines Browsers aus.
        
        Args:
            driver (webdriver.Chrome): Der Selenium WebDriver.
            
        Returns:
            Dict[str, str]: Der Inhalt des sessionStorage.
        """
        try:
            session_storage = driver.execute_script("""
                var ss = {};
                for (var i = 0; i < sessionStorage.length; i++) {
                    var key = sessionStorage.key(i);
                    ss[key] = sessionStorage.getItem(key);
                }
                return ss;
            """)
            return session_storage or {}
        except Exception as e:
            logger.error(f"Fehler beim Auslesen des sessionStorage: {e}")
            return {}
    
    def get_dynamic_cookies(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """
        Überwacht die dynamischen Cookie-Änderungen.
        
        Args:
            driver (webdriver.Chrome): Der Selenium WebDriver.
            
        Returns:
            List[Dict[str, Any]]: Die dynamisch gesetzten Cookies.
        """
        try:
            # JavaScript-Code zur Überwachung von Cookie-Änderungen
            driver.execute_script("""
                if (!window._cookieMonitor) {
                    window._cookieMonitor = {
                        originalSetCookie: document.cookie.__lookupSetter__('cookie'),
                        dynamicCookies: [],
                        init: function() {
                            var self = this;
                            document.__defineGetter__('cookie', function() {
                                return document._actualCookie;
                            });
                            document.__defineSetter__('cookie', function(val) {
                                document._actualCookie = val;
                                var cookie = {};
                                var parts = val.split(';');
                                var nameValue = parts[0].split('=');
                                cookie.name = nameValue[0].trim();
                                cookie.value = nameValue[1] ? nameValue[1].trim() : '';
                                
                                // Füge weitere Cookie-Attribute hinzu
                                for (var i = 1; i < parts.length; i++) {
                                    var attr = parts[i].trim().split('=');
                                    if (attr[0].toLowerCase() === 'expires') {
                                        cookie.expires = attr[1];
                                    } else if (attr[0].toLowerCase() === 'path') {
                                        cookie.path = attr[1];
                                    } else if (attr[0].toLowerCase() === 'domain') {
                                        cookie.domain = attr[1];
                                    }
                                }
                                
                                self.dynamicCookies.push(cookie);
                                return val;
                            });
                        },
                        getCookies: function() {
                            return this.dynamicCookies;
                        }
                    };
                    window._cookieMonitor.init();
                }
            """)
            
            # Warte einen Moment, damit dynamische Cookies gesetzt werden können
            time.sleep(2)
            
            # Abrufen der dynamischen Cookies
            dynamic_cookies = driver.execute_script("return window._cookieMonitor.getCookies();")
            return dynamic_cookies or []
        except Exception as e:
            logger.error(f"Fehler beim Überwachen dynamischer Cookies: {e}")
            return []

    def get_cookies_and_storage(self, driver: webdriver.Chrome, url: str) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Erfasst Cookies und Storage-Daten einer Seite.
        
        Args:
            driver (webdriver.Chrome): Der Selenium WebDriver.
            url (str): Die URL der Seite.
            
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: Cookies und Storage-Daten.
        """
        # Cookies abrufen
        selenium_cookies = driver.get_cookies()
        cookies = [
            {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expiry", -1),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False)
            }
            for cookie in selenium_cookies
        ]
        
        # Storage-Daten abrufen
        local_storage = self.get_local_storage(driver)
        session_storage = self.get_session_storage(driver)
        dynamic_cookies = self.get_dynamic_cookies(driver)
        
        # Storage-Daten zusammenfassen
        storage = {
            "localStorage": local_storage,
            "sessionStorage": session_storage,
            "dynamicCookies": dynamic_cookies
        }
        
        all_storage = {url: storage}
        
        return cookies, all_storage
    
    def scan_single_page(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Scannt nur die eingegebene Seite auf Cookies und Storage-Daten, vor und nach der Consent-Interaktion.
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]: 
            Cookies vor Consent, Storage vor Consent, Cookies nach Consent, Storage nach Consent.
        """
        logger.info(f"Scanne nur die eingegebene Seite mit Selenium: {self.start_url}")
        pre_consent_cookies = []
        pre_consent_storage = {}
        post_consent_cookies = []
        post_consent_storage = {}
        
        # Chrome-Optionen konfigurieren
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Chromedriver konfigurieren
        if self.webdriver_path:
            service = Service(self.webdriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        try:
            # Seite laden
            driver.get(self.start_url)
            
            # Warten, damit die Seite und mögliche Cookies geladen werden
            time.sleep(2)
            
            # PHASE 1: Cookies und Storage vor der Consent-Interaktion erfassen
            logger.info("Erfasse Cookies vor der Consent-Interaktion")
            pre_consent_cookies, pre_consent_storage = self.get_cookies_and_storage(driver, self.start_url)
            
            # Identifizieren des Consent-Managers (nur für Logging-Zwecke)
            consent_manager_name = self.consent_manager.detect_consent_manager(driver)
            if consent_manager_name != "Unknown":
                logger.info(f"Consent-Manager erkannt: {consent_manager_name}")
            
            # Mit Cookie-Consent-Bannern interagieren
            if self.interact_with_consent:
                interaction_succeeded = self.consent_manager.interact_with_consent(driver)
                if interaction_succeeded:
                    logger.info("Erfolgreich mit dem Consent-Banner interagiert")
                else:
                    logger.warning("Keine Interaktion mit dem Consent-Banner möglich oder kein Banner gefunden")
                
                # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                time.sleep(2)
                
                # PHASE 2: Cookies und Storage nach der Consent-Interaktion erfassen
                logger.info("Erfasse Cookies nach der Consent-Interaktion")
                post_consent_cookies, post_consent_storage = self.get_cookies_and_storage(driver, self.start_url)
            else:
                logger.info("Consent-Interaktion ist deaktiviert, überspringe Phase 2")
                # Setze die Post-Consent-Daten auf die Pre-Consent-Daten, wenn keine Interaktion stattfindet
                post_consent_cookies = pre_consent_cookies
                post_consent_storage = pre_consent_storage
        
        except Exception as e:
            logger.error(f"Fehler beim Scannen der Seite mit Selenium: {e}")
        
        finally:
            # Browser schließen
            driver.quit()
            
        return pre_consent_cookies, pre_consent_storage, post_consent_cookies, post_consent_storage
    
    def crawl(self) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Crawlt eine Website mit Selenium und sammelt Cookies und Storage-Daten. Diese Methode gibt nur den
        finalen Status zurück (nach der Consent-Interaktion).
        
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
            Cookies nach Consent, Storage nach Consent.
            
        Hinweis:
            Für eine detaillierte Analyse vor und nach der Consent-Interaktion verwenden Sie scan_single_page().
        """
        if self.respect_robots and self.rp and not self.is_allowed_by_robots(self.start_url):
            logger.warning("Crawling ist laut robots.txt verboten. Es wird nur die eingegebene Seite gescannt.")
            # Für kompatibilität mit der standard-API nur die Nach-Consent-Daten zurückgeben
            _, _, post_consent_cookies, post_consent_storage = self.scan_single_page()
            return post_consent_cookies, post_consent_storage
        
        visited = set()
        to_visit = [self.start_url]
        pre_consent_cookies = []
        pre_consent_storage = {}
        post_consent_cookies = []
        post_consent_storage = {}
        
        # Chrome-Optionen konfigurieren
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Chromedriver konfigurieren
        if self.webdriver_path:
            service = Service(self.webdriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        try:
            # Erst nur die Startseite scannen mit dem zweistufigen Prozess
            logger.info(f"Starte zweistufigen Scan der Startseite: {self.start_url}")
            
            # Seite laden
            driver.get(self.start_url)
            visited.add(self.start_url)
            
            # Warten, damit die Seite und mögliche Cookies geladen werden
            time.sleep(2)
            
            # PHASE 1: Cookies und Storage vor der Consent-Interaktion erfassen
            logger.info("Erfasse Cookies vor der Consent-Interaktion")
            page_pre_cookies, page_pre_storage = self.get_cookies_and_storage(driver, self.start_url)
            pre_consent_cookies.extend(page_pre_cookies)
            pre_consent_storage.update(page_pre_storage)
            
            # Identifizieren des Consent-Managers (nur für Logging-Zwecke)
            consent_manager_name = self.consent_manager.detect_consent_manager(driver)
            if consent_manager_name != "Unknown":
                logger.info(f"Consent-Manager erkannt: {consent_manager_name}")
            
            # Mit Cookie-Consent-Bannern interagieren
            if self.interact_with_consent:
                interaction_succeeded = self.consent_manager.interact_with_consent(driver)
                if interaction_succeeded:
                    logger.info("Erfolgreich mit dem Consent-Banner interagiert")
                else:
                    logger.warning("Keine Interaktion mit dem Consent-Banner möglich oder kein Banner gefunden")
                
                # Warte kurz, um sicherzustellen, dass Cookies aktualisiert werden
                time.sleep(2)
            
            # Links von der Startseite sammeln
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                    
                full_url = urljoin(self.start_url, href)
                if self.is_internal_link(full_url) and full_url not in visited and len(visited) < self.max_pages:
                    to_visit.append(full_url)
            
            # Crawl weitere Seiten nach Consent-Interaktion (nur, wenn Consent bereits erfolgt ist)
            while to_visit and len(visited) < self.max_pages:
                url = to_visit.pop(0)
                if url in visited:
                    continue
                    
                if self.respect_robots and self.rp and not self.is_allowed_by_robots(url):
                    logger.warning(f"robots.txt verbietet das Crawlen von: {url}")
                    continue
                    
                logger.info(f"Scanne mit Selenium (nach Consent): {url}")
                visited.add(url)
                
                try:
                    # Seite laden
                    driver.get(url)
                    
                    # Warte kurz, damit die Seite geladen wird
                    time.sleep(2)
                    
                    # Cookies und Storage nach der Consent-Interaktion erfassen
                    page_cookies, page_storage = self.get_cookies_and_storage(driver, url)
                    post_consent_cookies.extend(page_cookies)
                    post_consent_storage.update(page_storage)
                    
                    # Links extrahieren für weitere Seiten
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if not href or href.startswith("#") or href.startswith("javascript:"):
                            continue
                            
                        full_url = urljoin(url, href)
                        if self.is_internal_link(full_url) and full_url not in visited and len(visited) < self.max_pages:
                            to_visit.append(full_url)
                
                except Exception as e:
                    logger.error(f"Fehler beim Scannen von {url} mit Selenium: {e}")
            
            # PHASE 2: Cookies und Storage nach der Consent-Interaktion und dem Crawling erfassen
            # Dies erfasst den letzten Stand der Cookies nach dem Besuch aller Seiten
            logger.info("Erfasse endgültige Cookies nach der Consent-Interaktion und dem Crawling")
            final_cookies, final_storage = self.get_cookies_and_storage(driver, self.start_url)
            post_consent_cookies.extend(final_cookies)
            post_consent_storage.update(final_storage)
        
        finally:
            # Browser schließen
            driver.quit()
        
        # Entferne Duplikate aus den Listen der Cookies
        unique_pre_cookies = {}
        for cookie in pre_consent_cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', ''))
            if key not in unique_pre_cookies:
                unique_pre_cookies[key] = cookie
        
        unique_post_cookies = {}
        for cookie in post_consent_cookies:
            key = (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', ''))
            if key not in unique_post_cookies:
                unique_post_cookies[key] = cookie
        
        # Bei der Standard-Methode geben wir nur die Post-Consent-Daten zurück
        # für Kompatibilität mit der Standard-API
        return list(unique_post_cookies.values()), post_consent_storage